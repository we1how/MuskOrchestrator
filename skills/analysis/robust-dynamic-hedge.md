# 鲁棒动态对冲策略 (Robust Dynamic Hedge)

> **来源**: arXiv:2604.02126 - Hedging Market Risk and Uncertainty via a Robust Portfolio Approach
> **作者**: Ravagnani et al. (University of Siena, Politecnico di Milano)
> **日期**: 2026-04-03

---

## 核心思想

传统动态对冲假设波动率预测是精确的，但现实中预测误差普遍存在。本策略通过**Box不确定性鲁棒优化**，显式纳入预测误差，构建对估计噪声不敏感的对冲比率。

---

## 数学框架

### 1. 鲁棒对冲比率

```
h_t^* = σ_SF,t+τ / (σ_F,t+τ^2 + Θ_F,τ)
```

| 符号 | 含义 |
|------|------|
| `σ_SF,t+τ` | 现货-期货协方差预测 |
| `σ_F,t+τ^2` | 期货方差预测 |
| `Θ_F,τ` | 不确定性区间（核心创新）|

### 2. 与传统对冲对比

| 方法 | 公式 | 问题 |
|------|------|------|
| **静态OLS** | h = Cov(S,F) / Var(F) | 忽略时变性 |
| **动态对冲** | h_t = σ_SF,t / σ_F,t^2 | 对预测误差敏感 |
| **鲁棒对冲** | h_t = σ_SF,t / (σ_F,t^2 + Θ) | 惩罚不确定性 |

---

## 实现步骤

### Step 1: 高频数据准备

```python
import numpy as np
import pandas as pd

# 计算5分钟实现方差
def realized_variance(minute_returns):
    """
    计算日内实现方差
    minute_returns: 5分钟收益率序列 ( shape: (n_intraday,) )
    """
    return np.sum(minute_returns ** 2)

# 计算实现协方差
def realized_covariance(returns_x, returns_y):
    """
    计算两个资产的实现协方差
    """
    return np.sum(returns_x * returns_y)

# 构建RV序列
def build_rv_series(price_df, freq_minutes=5):
    """
    从分钟数据构建日RV序列
    price_df: DataFrame with ['datetime', 'close'] columns
    """
    price_df['datetime'] = pd.to_datetime(price_df['datetime'])
    price_df['date'] = price_df['datetime'].dt.date
    price_df['time'] = price_df['datetime'].dt.time

    rv_list = []
    for date, group in price_df.groupby('date'):
        # 计算5分钟收益率
        returns = group['close'].pct_change().dropna()
        rv = realized_variance(returns)
        rv_list.append({'date': date, 'RV': rv})

    return pd.DataFrame(rv_list).set_index('date')
```

### Step 2: HAR-RV模型

```python
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

class HARRVModel:
    """
    Heterogeneous Autoregressive Realized Volatility Model
    Corsi (2009)
    """

    def __init__(self):
        self.model = LinearRegression()
        self.is_fitted = False

    def prepare_features(self, rv_series):
        """
        准备HAR特征
        """
        df = pd.DataFrame({'RV': rv_series})

        # 日成分 (昨天)
        df['daily'] = df['RV'].shift(1)

        # 周成分 (上周平均)
        df['weekly'] = df['RV'].shift(1).rolling(window=5).mean()

        # 月成分 (上月平均)
        df['monthly'] = df['RV'].shift(1).rolling(window=22).mean()

        return df[['daily', 'weekly', 'monthly']]

    def fit(self, rv_series):
        """
        训练HAR-RV模型
        """
        X = self.prepare_features(rv_series)
        y = rv_series.loc[X.index]

        # 删除缺失值
        valid_idx = X.dropna().index
        X = X.loc[valid_idx]
        y = y.loc[valid_idx]

        self.model.fit(X, y)
        self.is_fitted = True

        # 计算R^2
        y_pred = self.model.predict(X)
        r2 = r2_score(y, y_pred)

        print(f"HAR-RV Model Fitted. R^2 = {r2:.4f}")
        print(f"Coefficients: daily={self.model.coef_[0]:.4f}, "
              f"weekly={self.model.coef_[1]:.4f}, monthly={self.model.coef_[2]:.4f}")

        return self

    def predict(self, rv_series, horizon=1):
        """
        预测未来horizon期的RV
        """
        if not self.is_fitted:
            raise ValueError("Model not fitted. Call fit() first.")

        X_latest = self.prepare_features(rv_series).iloc[-1:]
        return self.model.predict(X_latest)[0]
```

### Step 3: 不确定性区间估计

```python
def estimate_uncertainty_interval(rv_series, model, n_bootstrap=100, confidence=0.95):
    """
    使用Bootstrap方法估计预测不确定性

    Parameters:
    -----------
    rv_series : pd.Series
        历史RV序列
    model : HARRVModel
        已训练的HAR模型
    n_bootstrap : int
        Bootstrap样本数
    confidence : float
        置信水平

    Returns:
    --------
    theta : float
        不确定性区间宽度
    """
    errors = []

    # 使用滚动窗口计算历史预测误差
    window = 252  # 1年
    for i in range(window, len(rv_series) - 1):
        train_data = rv_series.iloc[i-window:i]
        actual = rv_series.iloc[i+1]

        # 在当前窗口训练模型
        temp_model = HARRVModel()
        temp_model.fit(train_data)
        pred = temp_model.predict(train_data)

        errors.append(abs(actual - pred))

    errors = np.array(errors)

    # 基于误差分布计算不确定性
    theta = np.percentile(errors, confidence * 100)

    return theta
```

### Step 4: 鲁棒对冲比率计算

```python
class RobustDynamicHedge:
    """
    鲁棒动态对冲策略实现
    """

    def __init__(self, uncertainty_factor=1.0):
        """
        Parameters:
        -----------
        uncertainty_factor : float
            不确定性调节因子 (默认1.0，可根据风险偏好调整)
        """
        self.uncertainty_factor = uncertainty_factor
        self.var_model = HARRVModel()
        self.cov_model = HARRVModel()

    def fit(self, spot_rv, future_rv, cov_series):
        """
        训练模型

        Parameters:
        -----------
        spot_rv : pd.Series
            现货RV序列
        future_rv : pd.Series
            期货RV序列
        cov_series : pd.Series
            实现协方差序列
        """
        self.var_model.fit(future_rv)
        self.cov_model.fit(cov_series)

        # 估计不确定性
        self.theta_var = estimate_uncertainty_interval(future_rv, self.var_model)
        self.theta_cov = estimate_uncertainty_interval(cov_series, self.cov_model)

        print(f"Uncertainty intervals: var={self.theta_var:.6f}, cov={self.theta_cov:.6f}")

        return self

    def calculate_hedge_ratio(self, spot_rv, future_rv, cov_series):
        """
        计算当前鲁棒对冲比率
        """
        # 预测下一期方差和协方差
        var_pred = self.var_model.predict(future_rv)
        cov_pred = self.cov_model.predict(cov_series)

        # 鲁棒对冲比率
        adjusted_var = var_pred + self.uncertainty_factor * self.theta_var
        hedge_ratio = cov_pred / adjusted_var

        return hedge_ratio

    def calculate_standard_hedge(self, spot_rv, future_rv, cov_series):
        """
        计算标准动态对冲比率（用于对比）
        """
        var_pred = self.var_model.predict(future_rv)
        cov_pred = self.cov_model.predict(cov_series)
        return cov_pred / var_pred
```

### Step 5: A股完整实现

```python
class ASHAREHedgeSystem:
    """
    A股市场鲁棒对冲系统
    支持ETF-股指期货对冲
    """

    def __init__(self, spot_etf='510300.SH', future='IF'):
        """
        Parameters:
        -----------
        spot_etf : str
            现货ETF代码 (默认510300.SH 沪深300ETF)
        future : str
            期货品种 (默认IF 沪深300股指期货)
        """
        self.spot_etf = spot_etf
        self.future = future
        self.hedge_engine = RobustDynamicHedge()

    def fetch_intraday_data(self, start_date, end_date):
        """
        获取1分钟高频数据
        数据源: 需要接入Qlib/JoinQuant/Tushare
        """
        # 伪代码 - 需要根据实际数据源实现
        """
        from qlib.data import D

        spot_data = D.features(
            [self.spot_etf],
            fields=['$close'],
            start_time=start_date,
            end_time=end_date,
            freq='1min'
        )

        future_data = D.features(
            [self.future],
            fields=['$close'],
            start_time=start_date,
            end_time=end_date,
            freq='1min'
        )
        """
        pass

    def calculate_daily_rv(self, intraday_df):
        """
        从日内数据计算日实现方差
        """
        intraday_df['date'] = pd.to_datetime(intraday_df['datetime']).dt.date

        daily_rv = []
        for date, group in intraday_df.groupby('date'):
            # 计算对数收益率
            log_prices = np.log(group['close'])
            log_returns = log_prices.diff().dropna()

            # 计算实现方差 (年化)
            rv = np.sum(log_returns ** 2) * 252  # 年化
            daily_rv.append({'date': date, 'RV': rv})

        return pd.DataFrame(daily_rv).set_index('date')['RV']

    def adjust_for_ashare_features(self, hedge_ratio, spot_price, future_price):
        """
        A股特殊调整:
        1. 涨跌停限制
        2. T+1交易
        3. 合约乘数调整
        """
        # 涨跌停检查
        # 如果标的接近涨跌停，调整对冲比例

        # 合约乘数
        # IF: 每点300元
        # ETF: 每份1元

        multiplier_ratio = 300  # 期货合约乘数 / ETF面值
        adjusted_ratio = hedge_ratio * multiplier_ratio

        return adjusted_ratio

    def run_backtest(self, start_date, end_date):
        """
        运行回测
        """
        # 1. 获取数据
        # 2. 计算RV序列
        # 3. 滚动训练模型
        # 4. 计算对冲比率
        # 5. 评估对冲效果
        pass
```

---

## 参数配置

### 推荐参数

| 参数 | 默认值 | 说明 | 调优建议 |
|------|--------|------|----------|
| `HAR窗口` | 252日 | 模型训练窗口 | 波动率制度变化快时可缩短 |
| `不确定性因子` | 1.0 | Θ的乘数 | 风险偏好低时增大 |
| `置信水平` | 0.95 | Bootstrap分位数 | 极端风险厌恶时用0.99 |
| `调仓阈值` | 0.05 | 对冲比率变化触发调仓 | 降低阈值减少换手 |

### A股特殊参数

| 参数 | 设置 | 原因 |
|------|------|------|
| `合约乘数` | 300 (IF) | 股指期货每点300元 |
| `交易时间` | 9:30-11:30, 13:00-15:00 | A股交易时段 |
| `涨跌停` | ±10% (ST±5%) | 限制价格变动 |
| `保证金` | 12% | 股指期货保证金比例 |

---

## 性能评估

### 核心指标

```python
def evaluate_hedge_performance(hedged_returns, unhedged_returns):
    """
    评估对冲效果
    """
    results = {}

    # 方差削减率
    results['variance_reduction'] = 1 - np.var(hedged_returns) / np.var(unhedged_returns)

    # 夏普比率
    results['sharpe'] = np.mean(hedged_returns) / np.std(hedged_returns) * np.sqrt(252)

    # 最大回撤
    cumulative = (1 + hedged_returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    results['max_drawdown'] = drawdown.min()

    # 换手率
    results['turnover'] = np.sum(np.abs(np.diff(hedge_ratios))) / len(hedge_ratios)

    return results
```

### 预期表现

基于论文实证结果（2016-2024年ETF数据）：

| 指标 | 鲁棒对冲 | 标准动态对冲 | 改善 |
|------|----------|--------------|------|
| 方差削减 | 99% | 98.5% | 相当 |
| 年化换手 | 12次 | 24次 | -50% |
| 夏普比率 | 1.2 | 0.9 | +33% |
| 最大回撤 | -8% | -12% | -33% |

---

## 风险提示

1. **模型风险**: HAR-RV假设波动率长记忆性，在制度突变时可能失效
2. **数据质量**: 高频数据需要清洗（剔除异常值、非交易时段）
3. **流动性风险**: 极端行情下期货升贴水扩大，对冲成本增加
4. **基差风险**: 现货与期货价格偏离导致对冲不完美

---

## 相关资源

- **论文**: [arXiv:2604.02126](https://arxiv.org/abs/2604.02126)
- **HAR-RV**: Corsi (2009) "A Simple Approximate Long-Memory Model of Realized Volatility"
- **Qlib数据**: [Microsoft Qlib](https://github.com/microsoft/qlib)

---

## 更新日志

- **2026-04-05**: 初始版本，基于arXiv:2604.02126
