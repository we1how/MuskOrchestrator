"""
HMM 市场制度识别 — 沪深300指数 2015-2025
==============================================
零外部依赖版本（仅需 numpy + pandas + matplotlib）
自带 Gaussian HMM 实现：Baum-Welch (EM) + Viterbi 解码

验证目标：
  1. 拟合 3 状态 Gaussian HMM（牛市 / 震荡 / 熊市）
  2. 可视化状态序列，对比已知牛熊分界点
  3. 按制度状态分层统计动量因子 IC，验证"制度-因子对应"假设

运行方式：
  python hmm_regime_detection.py

输出：
  - hmm_regime_chart.png       状态时序图（价格 + 颜色标注制度）
  - hmm_factor_ic.png          各制度下动量因子 IC 分布图
  - hmm_return_distribution.png 收益率分布图
  - hmm_results_summary.txt    统计摘要
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

warnings.filterwarnings("ignore")

# ── 1. 数据层 ──────────────────────────────────────────────────────────────────

def fetch_data(start="2015-01-01", end="2025-12-31") -> pd.DataFrame:
    """尝试 baostock；失败则用带结构的模拟数据。"""
    try:
        import baostock as bs
        lg = bs.login()
        if lg.error_code != "0":
            raise RuntimeError(lg.error_msg)
        rs = bs.query_history_k_data_plus(
            "sh.000300", "date,close,turn",
            start_date=start, end_date=end,
            frequency="d", adjustflag="3",
        )
        rows = []
        while rs.error_code == "0" and rs.next():
            rows.append(rs.get_row_data())
        bs.logout()
        df = pd.DataFrame(rows, columns=rs.fields)
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")
        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        df["turn"]  = pd.to_numeric(df["turn"],  errors="coerce")
        df = df.dropna()
        print(f"✅ baostock 数据获取成功，{len(df)} 个交易日")
        return df
    except Exception as e:
        print(f"⚠️  baostock 不可用（{e}），使用结构化模拟数据")
        return _simulate(start, end)


def _simulate(start: str, end: str) -> pd.DataFrame:
    """生成带已知制度标签的模拟沪深300数据，用于验证 HMM 正确性。"""
    rng = pd.date_range(start=start, end=end, freq="B")
    np.random.seed(42)
    n = len(rng)

    # 按A股历史粗略分段
    regimes = np.zeros(n, dtype=int)
    segs = [
        (0,   120, 2),   # 2015 Q1 牛市
        (120, 250, 0),   # 2015 股灾
        (250, 500, 1),   # 2016 震荡
        (500, 700, 0),   # 2018 熊市
        (700, 900, 2),   # 2019 反弹
        (900,1000, 1),   # 2020 疫情
        (1000,1150,2),   # 2020-2021 牛市
        (1150,1400,0),   # 2021-2022 熊市
        (1400, n,  1),   # 2023-2025 震荡
    ]
    for s, e, r in segs:
        regimes[s:min(e, n)] = r

    mu  = {0: -0.0012, 1: 0.0001, 2: 0.0013}
    sig = {0:  0.021,  1: 0.010,  2: 0.016}
    ret = np.array([np.random.normal(mu[r], sig[r]) for r in regimes])
    close = 3500 * np.cumprod(1 + ret)
    turn  = np.array([np.random.lognormal(np.log(0.03 + 0.01 * r), 0.3)
                       for r in regimes])
    df = pd.DataFrame({"close": close, "turn": turn, "_true": regimes}, index=rng)
    print(f"✅ 模拟数据生成，{len(df)} 个交易日（含真实标签供验证）")
    return df


# ── 2. 特征工程 ────────────────────────────────────────────────────────────────

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["log_ret"] = np.log(df["close"] / df["close"].shift(1))
    df["vol_5d"]  = df["log_ret"].rolling(5).std()
    df["vol_20d"] = df["log_ret"].rolling(20).std()
    df["mom_20d"] = df["close"].pct_change(20)
    df["mom_60d"] = df["close"].pct_change(60)
    return df.dropna()


# ── 3. Gaussian HMM（纯 NumPy 实现）──────────────────────────────────────────

class GaussianHMM:
    """
    简洁的 Gaussian HMM，支持多维观测。
    使用对数尺度的前向-后向算法（避免下溢），Viterbi 解码。
    """

    def __init__(self, n_states=3, n_iter=100, tol=1e-4, random_state=42):
        self.K = n_states
        self.n_iter = n_iter
        self.tol = tol
        self.rng = np.random.default_rng(random_state)

    # ── 初始化参数 ──
    def _init_params(self, X):
        N, D = X.shape
        K = self.K
        # 用 K-means 粗初始化均值
        idx = self.rng.choice(N, K, replace=False)
        self.means_ = X[idx].copy().astype(float)
        self.covs_  = np.array([np.cov(X.T) + 1e-6 * np.eye(D)] * K)
        self.pi_    = np.full(K, 1.0 / K)
        self.A_     = self.rng.dirichlet(np.ones(K), size=K)  # 转移矩阵

    # ── 多元正态对数概率密度 ──
    @staticmethod
    def _log_mvn(X, mu, cov):
        D = len(mu)
        diff = X - mu
        try:
            L = np.linalg.cholesky(cov + 1e-8 * np.eye(D))
            sol = np.linalg.solve(L, diff.T)
            maha = np.sum(sol**2, axis=0)
            log_det = 2 * np.sum(np.log(np.diag(L)))
        except np.linalg.LinAlgError:
            cov_reg = cov + 1e-4 * np.eye(D)
            maha = np.einsum("nd,dd,nd->n", diff, np.linalg.inv(cov_reg), diff)
            log_det = np.log(np.linalg.det(cov_reg) + 1e-12)
        return -0.5 * (D * np.log(2 * np.pi) + log_det + maha)

    # ── 计算发射对数概率矩阵 B [N, K] ──
    def _log_emission(self, X):
        N = len(X)
        logB = np.zeros((N, self.K))
        for k in range(self.K):
            logB[:, k] = self._log_mvn(X, self.means_[k], self.covs_[k])
        return logB

    # ── 对数前向算法 ──
    def _forward(self, logB):
        N, K = logB.shape
        logA = np.log(self.A_ + 1e-12)
        alpha = np.full((N, K), -np.inf)
        alpha[0] = np.log(self.pi_ + 1e-12) + logB[0]
        for t in range(1, N):
            for k in range(K):
                alpha[t, k] = np.logaddexp.reduce(alpha[t-1] + logA[:, k]) + logB[t, k]
        return alpha

    # ── 对数后向算法 ──
    def _backward(self, logB):
        N, K = logB.shape
        logA = np.log(self.A_ + 1e-12)
        beta = np.zeros((N, K))          # beta[-1] = log(1) = 0
        for t in range(N-2, -1, -1):
            for k in range(K):
                beta[t, k] = np.logaddexp.reduce(logA[k] + logB[t+1] + beta[t+1])
        return beta

    # ── Baum-Welch EM ──
    def fit(self, X):
        X = np.asarray(X, dtype=float)
        N, D = X.shape
        self._init_params(X)
        log_lik_prev = -np.inf

        for it in range(self.n_iter):
            logB  = self._log_emission(X)
            alpha = self._forward(logB)
            beta  = self._backward(logB)

            # log γ (posterior state)
            log_gamma = alpha + beta
            log_gamma -= np.logaddexp.reduce(log_gamma, axis=1, keepdims=True)
            gamma = np.exp(log_gamma)

            # log ξ (posterior transition)
            logA = np.log(self.A_ + 1e-12)
            log_xi = np.full((N-1, self.K, self.K), -np.inf)
            for t in range(N-1):
                for i in range(self.K):
                    for j in range(self.K):
                        log_xi[t, i, j] = (alpha[t, i] + logA[i, j]
                                            + logB[t+1, j] + beta[t+1, j])
                log_xi[t] -= np.logaddexp.reduce(
                    log_xi[t].reshape(-1)).reshape(1, 1)

            xi = np.exp(log_xi)

            # 更新参数
            self.pi_ = gamma[0] / gamma[0].sum()
            self.A_  = (xi.sum(axis=0) /
                        xi.sum(axis=0).sum(axis=1, keepdims=True) + 1e-12)
            for k in range(self.K):
                w = gamma[:, k]
                wsum = w.sum() + 1e-12
                self.means_[k] = (w[:, None] * X).sum(axis=0) / wsum
                diff = X - self.means_[k]
                self.covs_[k] = (w[:, None, None] *
                                  diff[:, :, None] * diff[:, None, :]).sum(axis=0) / wsum
                self.covs_[k] += 1e-6 * np.eye(D)

            log_lik = np.logaddexp.reduce(alpha[-1])
            if abs(log_lik - log_lik_prev) < self.tol:
                print(f"  收敛于第 {it+1} 轮（log-likelihood={log_lik:.2f}）")
                break
            log_lik_prev = log_lik
        else:
            print(f"  达到最大迭代次数 {self.n_iter}（log-likelihood={log_lik:.2f}）")
        return self

    # ── Viterbi 解码 ──
    def predict(self, X):
        X = np.asarray(X, dtype=float)
        N = len(X)
        logB  = self._log_emission(X)
        logA  = np.log(self.A_ + 1e-12)
        delta = np.full((N, self.K), -np.inf)
        psi   = np.zeros((N, self.K), dtype=int)
        delta[0] = np.log(self.pi_ + 1e-12) + logB[0]
        for t in range(1, N):
            scores = delta[t-1][:, None] + logA
            psi[t] = scores.argmax(axis=0)
            delta[t] = scores.max(axis=0) + logB[t]
        states = np.zeros(N, dtype=int)
        states[-1] = delta[-1].argmax()
        for t in range(N-2, -1, -1):
            states[t] = psi[t+1, states[t+1]]
        return states


# ── 4. 制度分析 ────────────────────────────────────────────────────────────────

REGIME_NAMES  = {0: "熊市", 1: "震荡", 2: "牛市"}
REGIME_COLORS = {0: "#e74c3c", 1: "#f39c12", 2: "#27ae60"}

def remap_states(states: np.ndarray, log_rets: np.ndarray) -> np.ndarray:
    """按各状态均值收益排序：0=最低(熊)，2=最高(牛)。"""
    means = [log_rets[states == s].mean() for s in range(3)]
    order = np.argsort(means)
    remap = {old: new for new, old in enumerate(order)}
    return np.array([remap[s] for s in states])


def regime_statistics(df: pd.DataFrame, states: np.ndarray) -> pd.DataFrame:
    df = df.copy()
    df["state"] = states
    rows = []
    for s in range(3):
        sub = df.loc[df["state"] == s, "log_ret"]
        rows.append({
            "制度":         REGIME_NAMES[s],
            "天数":         len(sub),
            "占比":         f"{len(sub)/len(df):.1%}",
            "日均收益":     f"{sub.mean():.4f}",
            "日波动率":     f"{sub.std():.4f}",
            "年化收益":     f"{sub.mean()*252:.2%}",
            "年化波动":     f"{sub.std()*np.sqrt(252):.2%}",
            "Sharpe":       f"{sub.mean()/sub.std()*np.sqrt(252):.2f}" if sub.std() > 0 else "n/a",
        })
    return pd.DataFrame(rows)


def spearman_r(x, y):
    """手写 Spearman 相关（避免 scipy 依赖）。"""
    def rank(a):
        order = np.argsort(a)
        r = np.empty_like(order, dtype=float)
        r[order] = np.arange(len(a)) + 1
        return r
    rx, ry = rank(x), rank(y)
    n = len(rx)
    rx -= rx.mean(); ry -= ry.mean()
    denom = np.sqrt((rx**2).sum() * (ry**2).sum())
    return float(np.dot(rx, ry) / denom) if denom > 0 else 0.0


def factor_ic_by_regime(df: pd.DataFrame, states: np.ndarray) -> pd.DataFrame:
    df = df.copy()
    df["state"]      = states
    df["fwd_5d"]     = df["log_ret"].shift(-5).rolling(5).sum()
    df["fwd_20d"]    = df["log_ret"].shift(-20).rolling(20).sum()
    rows = []
    for s in range(3):
        mask = (df["state"] == s) & df["fwd_5d"].notna() & df["mom_20d"].notna()
        sub = df.loc[mask]
        if len(sub) < 30:
            continue
        ic5  = spearman_r(sub["mom_20d"].values, sub["fwd_5d"].values)
        ic20 = spearman_r(sub["mom_60d"].values, sub["fwd_20d"].values)
        rows.append({
            "制度":              REGIME_NAMES[s],
            "动量20d→未来5d IC": round(ic5, 3),
            "动量60d→未来20d IC": round(ic20, 3),
            "样本数":            len(sub),
        })
    return pd.DataFrame(rows)


# ── 5. 可视化 ──────────────────────────────────────────────────────────────────

KNOWN_EVENTS = [
    ("2015-06-12", "2015股灾"),
    ("2016-01-04", "熔断"),
    ("2018-01-26", "贸易战"),
    ("2020-02-03", "疫情"),
    ("2020-07-06", "2020牛市"),
    ("2021-02-10", "抱团瓦解"),
    ("2022-10-31", "政策底"),
]

plt.rcParams["font.family"] = ["DejaVu Sans", "sans-serif"]  # 沙箱无中文字体，英文显示


def plot_regime_chart(df, states, path):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 9), sharex=True,
                                    gridspec_kw={"height_ratios": [3, 1]})
    fig.suptitle("CSI300 HMM Regime Detection (2015-2025)", fontsize=15, fontweight="bold")

    dates = df.index
    ax1.plot(dates, df["close"], color="#2c3e50", lw=1.0, label="CSI300")
    ax1.set_ylabel("Index Level (log)", fontsize=11)
    ax1.set_yscale("log")

    # 制度背景色块
    prev_s, prev_d = states[0], dates[0]
    for i in range(1, len(states)):
        if states[i] != prev_s or i == len(states) - 1:
            ax1.axvspan(prev_d, dates[i], alpha=0.22,
                        color=REGIME_COLORS[prev_s], linewidth=0)
            prev_s, prev_d = states[i], dates[i]

    # 事件标线
    for ds, label in KNOWN_EVENTS:
        dt = pd.Timestamp(ds)
        if dates.min() <= dt <= dates.max():
            ax1.axvline(dt, color="navy", ls="--", lw=0.7, alpha=0.55)
            ax1.text(dt, df["close"].max() * 0.93, label,
                     rotation=90, fontsize=7, va="top", color="navy", alpha=0.75)

    patches = [mpatches.Patch(color=REGIME_COLORS[s],
                               label=["Bear", "Range", "Bull"][s], alpha=0.6)
               for s in range(3)]
    ax1.legend(handles=patches + [plt.Line2D([0],[0], color="#2c3e50", label="CSI300")],
               loc="upper left", fontsize=9)

    # 状态散点
    ax2.scatter(dates, states, c=[REGIME_COLORS[s] for s in states], s=2)
    ax2.set_yticks([0, 1, 2])
    ax2.set_yticklabels(["Bear", "Range", "Bull"], fontsize=9)
    ax2.set_xlabel("Date", fontsize=11)

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ 制度图表 → {path}")


def plot_factor_ic(ic_df, path):
    fig, ax = plt.subplots(figsize=(8, 5))
    fig.suptitle("Momentum Factor IC by Regime", fontsize=13, fontweight="bold")
    x = np.arange(len(ic_df))
    w = 0.35
    cols = [REGIME_COLORS[i] for i in range(len(ic_df))]
    b1 = ax.bar(x - w/2, ic_df["动量20d→未来5d IC"],  width=w, color=cols, alpha=0.85, label="Mom20d→5d IC")
    b2 = ax.bar(x + w/2, ic_df["动量60d→未来20d IC"], width=w, color=cols, alpha=0.55, label="Mom60d→20d IC", hatch="//")
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(["Bear", "Range", "Bull"][:len(ic_df)], fontsize=11)
    ax.set_ylabel("Spearman IC", fontsize=11)
    ax.legend(fontsize=9)
    for b in list(b1) + list(b2):
        ax.text(b.get_x() + b.get_width()/2, b.get_height() + 0.003,
                f"{b.get_height():.3f}", ha="center", fontsize=8)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ 因子 IC 图 → {path}")


def plot_distributions(df, states, path):
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.suptitle("Daily Return Distribution by Regime", fontsize=13, fontweight="bold")
    df = df.copy(); df["state"] = states
    for s in range(3):
        sub = df.loc[df["state"] == s, "log_ret"].dropna()
        mu, sig = sub.mean(), sub.std()
        x = np.linspace(sub.min(), sub.max(), 300)
        kde = np.exp(-0.5 * ((x - mu) / sig) ** 2) / (sig * np.sqrt(2 * np.pi))
        lbl = ["Bear", "Range", "Bull"][s]
        ax.plot(x, kde, color=REGIME_COLORS[s], lw=2,
                label=f"{lbl}  (mu={mu:.4f}, sig={sig:.4f})")
        ax.fill_between(x, kde, alpha=0.12, color=REGIME_COLORS[s])
    ax.axvline(0, color="black", lw=0.8, ls="--")
    ax.set_xlabel("Log Return", fontsize=11)
    ax.set_ylabel("Density", fontsize=11)
    ax.legend(fontsize=9)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✅ 收益分布图 → {path}")


# ── 6. 主流程 ──────────────────────────────────────────────────────────────────

def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    print("\n" + "="*60)
    print("  HMM Regime Detection — CSI300  2015-2025")
    print("="*60)

    print("\n[1] 获取数据...")
    df_raw = fetch_data("2015-01-01", "2025-12-31")

    print("[2] 特征工程...")
    df = build_features(df_raw)
    print(f"    有效交易日：{len(df)}（{df.index[0].date()} → {df.index[-1].date()}）")

    print("[3] 拟合 Gaussian HMM（3状态，Baum-Welch）...")
    X = df[["log_ret", "vol_5d", "vol_20d"]].values
    model = GaussianHMM(n_states=3, n_iter=80, tol=1e-3, random_state=42)
    model.fit(X)

    print("[4] Viterbi 解码...")
    raw_states = model.predict(X)
    states = remap_states(raw_states, df["log_ret"].values)
    df["state"] = states

    print("\n[5] 统计汇报")
    stat_df = regime_statistics(df, states)
    print(stat_df.to_string(index=False))

    print("\n[6] 因子 IC 验证")
    ic_df = factor_ic_by_regime(df, states)
    print(ic_df.to_string(index=False))

    # 模拟数据验证
    if "_true" in df_raw.columns:
        true_labels = df_raw["_true"].reindex(df.index).values
        match = (states == true_labels).mean()
        print(f"\n📊 [仅模拟] HMM 与真实标签吻合率：{match:.1%}")

    # 保存摘要
    summary_path = os.path.join(out_dir, "hmm_results_summary.txt")
    with open(summary_path, "w") as f:
        f.write("HMM Regime Detection — Summary\n" + "="*50 + "\n\n")
        f.write("=== Regime Statistics ===\n")
        f.write(stat_df.to_string(index=False))
        f.write("\n\n=== Factor IC by Regime ===\n")
        f.write(ic_df.to_string(index=False))
        f.write("\n\n=== Model Parameters ===\n")
        f.write(f"States: 3  |  Features: log_ret, vol_5d, vol_20d\n")
        for s, name in REGIME_NAMES.items():
            f.write(f"{name}: mean_ret={df.loc[df['state']==s,'log_ret'].mean():.5f}, "
                    f"vol={df.loc[df['state']==s,'log_ret'].std():.5f}\n")
    print(f"\n    文本摘要 → {summary_path}")

    print("\n[7] 生成图表...")
    plot_regime_chart(df, states, os.path.join(out_dir, "hmm_regime_chart.png"))
    plot_factor_ic(ic_df,         os.path.join(out_dir, "hmm_factor_ic.png"))
    plot_distributions(df, states, os.path.join(out_dir, "hmm_return_distribution.png"))

    print("\n" + "="*60)
    print("  ✅ 全部完成！")
    print(f"  输出目录: {out_dir}")
    print("="*60 + "\n")
    return df, model, states, stat_df, ic_df


if __name__ == "__main__":
    main()
