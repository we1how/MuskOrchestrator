# BlindTrade: 匿名化LLM交易框架

> **核心洞察**: LLM交易Agent必须通过匿名化验证，证明其基于市场动态而非预训练记忆做决策。

## 概述

BlindTrade是ICLR 2026 FinAI Workshop接收的研究，通过匿名化所有股票标识符，验证LLM是否真正理解市场动态。实验显示匿名化后仍能达到Sharpe 1.40，证明LLM具备真实的交易能力。

## 核心问题：LLM交易的虚假性能来源

### 1. 记忆偏差 (Memorization Bias)
- LLM在预训练中记住特定ticker的历史表现
- 回测时利用这些记忆产生虚高表现
- 实盘时记忆失效，策略崩溃

### 2. 幸存者偏差 (Survivorship Bias)
- 回测只考虑存活股票，忽略退市/破产案例
- 高估策略稳健性
- 实盘遇到退市风险时损失惨重

## 系统架构

```
BlindTrade系统
│
├─ 输入层: 匿名化数据 (股票代码 → ID_XXX)
├─ 分析层: 4个LLM Agent并行分析
├─ 聚合层: GNN图神经网络提取跨Agent信号
└─ 决策层: PPO-DSR强化学习执行交易
```

## 实验结果

| 指标 | 数值 | 说明 |
|------|------|------|
| Sharpe Ratio | 1.40 ± 0.22 | 2025 YTD，20个种子平均 |
| 匿名化性能损失 | <15% | 证明非记忆驱动 |
| 最佳市场环境 | 高波动震荡市 | Alpha最高 |
| 最差市场环境 | 趋势牛市 | Alpha下降 |

## A股应用价值

### 为什么A股更需要匿名化验证？

| A股特性 | 记忆偏差风险 | BlindTrade应对 |
|---------|--------------|----------------|
| 散户众多，情绪驱动 | LLM可能记住"妖股"历史 | 匿名化强制基于动态分析 |
| 政策影响大 | 可能记住政策相关股票 | 匿名化后基于政策信号而非标签 |
| 概念股轮动快 | 历史标签关联失效快 | 匿名化迫使关注实时信号 |

## 实现代码

### 1. A股数据匿名化

```python
import hashlib
import pandas as pd

class AShareAnonymizer:
    """A股数据匿名化处理"""

    def __init__(self, salt="blindtrade_a_share_2026"):
        self.salt = salt
        self.mapping = {}

    def anonymize_ticker(self, ticker: str) -> str:
        if ticker not in self.mapping:
            hash_val = hashlib.md5(f"{ticker}{self.salt}".encode()).hexdigest()[:6]
            self.mapping[ticker] = f"ID_{hash_val}"
        return self.mapping[ticker]

    def anonymize_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df_anon = df.copy()
        df_anon['ticker'] = df_anon['ticker'].apply(self.anonymize_ticker)
        # 移除公司名称相关列
        cols_to_drop = ['name', 'company_name', 'industry_name']
        df_anon = df_anon.drop(columns=[c for c in cols_to_drop if c in df_anon.columns])
        return df_anon
```

### 2. 多Agent分析系统

```python
class BlindTradeAgent:
    """BlindTrade风格的多Agent分析"""

    def __init__(self, model="gpt-4o"):
        self.model = model
        self.agents = [
            {"name": "technical", "prompt": self._technical_prompt()},
            {"name": "fundamental", "prompt": self._fundamental_prompt()},
            {"name": "sentiment", "prompt": self._sentiment_prompt()},
            {"name": "macro", "prompt": self._macro_prompt()},
        ]

    def analyze(self, stock_data: Dict) -> List[Dict]:
        """并行调用4个Agent进行分析"""
        results = []
        for agent in self.agents:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": agent["prompt"]},
                    {"role": "user", "content": f"分析数据: {stock_data}"}
                ],
                temperature=0.3
            )
            results.append({
                "agent": agent["name"],
                "output": response.choices[0].message.content
            })
        return results
```

### 3. 市场状态检测

```python
class MarketRegimeDetector:
    """检测当前市场状态，动态调整策略权重"""

    def detect_regime(self, market_data: pd.DataFrame) -> str:
        """检测市场状态：volatile, trending_bull, trending_bear"""
        returns = market_data['close'].pct_change().dropna()
        volatility = returns.rolling(60).std().iloc[-1] * np.sqrt(252)
        trend = returns.rolling(60).mean().iloc[-1] * 252

        if volatility > 0.25:
            return "volatile"
        elif trend > 0.15:
            return "trending_bull"
        elif trend < -0.15:
            return "trending_bear"
        else:
            return "neutral"

    def adjust_weights(self, regime: str) -> Dict[str, float]:
        weights = {
            "volatile": {"technical": 0.4, "sentiment": 0.3, "fundamental": 0.2, "macro": 0.1},
            "trending_bull": {"technical": 0.2, "sentiment": 0.2, "fundamental": 0.4, "macro": 0.2},
            "trending_bear": {"technical": 0.3, "sentiment": 0.3, "fundamental": 0.2, "macro": 0.2},
            "neutral": {"technical": 0.25, "sentiment": 0.25, "fundamental": 0.25, "macro": 0.25},
        }
        return weights.get(regime, weights["neutral"])
```

### 4. 负面对照实验

```python
def negative_control_test(data: pd.DataFrame, strategy) -> bool:
    """
    负面对照实验：验证信号合法性
    如果随机打乱标签后性能大幅下降，说明信号真实
    """
    # 打乱标签
    shuffled_data = data.copy()
    shuffled_data['ticker'] = np.random.permutation(shuffled_data['ticker'])

    # 对比性能
    normal_result = run_backtest(data, strategy)
    shuffled_result = run_backtest(shuffled_data, strategy)

    # 如果打乱后性能下降>50%，说明信号真实
    performance_drop = (normal_result['sharpe'] - shuffled_result['sharpe']) / normal_result['sharpe']

    return performance_drop > 0.5
```

## 与现有系统的整合

### 与TradingAgents整合
```
TradingAgents架构 + BlindTrade验证层
= 更可信的多Agent交易系统
```

### 与Qlib整合
```
Qlib数据基础设施 + BlindTrade LLM验证方法
= 标准化量化流程 + LLM信号验证
```

## 关键指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| Sharpe Ratio | >1.0 | 匿名化后的风险调整后收益 |
| Negative Control通过率 | >80% | 信号真实性验证 |
| 匿名化性能损失 | <20% | 证明非记忆驱动 |

## 参考资源

- **论文**: arXiv:2603.17692
- **会议**: ICLR 2026 FinAI Workshop
- **学习记录**: `memory/agents/analyst/LEARNING.md`

## 触发条件

- LLM交易系统设计
- 回测验证
- 信号真实性检验
- A股多Agent交易策略开发
