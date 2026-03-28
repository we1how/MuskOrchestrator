# MASS: Multi-Agent Simulation Scaling for Portfolio Construction

> **来源**: arXiv:2505.10278
> **作者**: Taian Guo et al. (北京大学)
> **GitHub**: https://github.com/gta0804/MASS
> **核心洞察**: 512个Agent的端到端组合构建，A股验证超额收益

---

## 核心概念

### 什么是MASS

MASS (Multi-Agent Simulation Scaling) 是一种基于多智能体模拟的端到端投资组合构建框架。与传统方法不同，MASS：

1. **绕过中间预测步骤**：直接输出投资组合权重，而非先预测个股涨跌
2. **利用规模效应**：Agent数量指数级增长（至512个）时，聚合决策产生更高超额收益
3. **逆向优化**：动态学习异构Agent的最优分布，适应市场变化

### 与传统框架的对比

```
传统多Agent框架:
Agent预测个股 → 信号聚合 → 组合构建 → 权重优化

MASS框架:
多Agent模拟 → 逆向优化 → 直接输出组合权重
```

---

## 核心架构

### 三层架构设计

```
MASS系统架构
│
├─ 异构Agent池层 (Heterogeneous Agent Pool)
│  ├─ 技术面Agent (20%): 动量/均值回归/突破
│  ├─ 基本面Agent (20%): PE/PB/ROE/成长
│  ├─ 情绪面Agent (15%): 新闻/社交/分析师
│  ├─ 宏观Agent (15%): 流动性/政策/周期
│  ├─ 量化Agent (20%): 线性/树模型/神经网络
│  └─ 随机Agent (10%): 提供噪声和多样性
│
├─ 模拟决策层 (Simulation Layer)
│  ├─ 每个Agent独立决策
│  ├─ 记录决策分布
│  └─ 生成决策矩阵 [n_agents × n_stocks]
│
└─ 逆向优化层 (Backward Optimization)
   ├─ 根据组合表现反推
   ├─ 学习最优Agent权重分布
   └─ 动态调整异构性参数
```

### 关键创新：逆向优化

```python
# 伪代码示意
class BackwardOptimizer:
    def optimize(self, agent_decisions, historical_performance):
        # 1. 计算每个Agent的历史贡献
        contributions = calculate_contributions(agent_decisions, historical_performance)

        # 2. 基于贡献度更新权重
        # 表现好的Agent获得更高权重
        new_weights = softmax(contributions)

        # 3. 动态调整Agent类型分布
        if technical_agents_performing_well:
            increase_technical_agent_ratio()

        return new_weights
```

---

## 规模效应：核心发现

### Agent数量与表现的关系

| Agent数量 | 预期效果 | 适用场景 |
|-----------|----------|----------|
| 8-16个 | 基础信号覆盖 | 快速原型验证 |
| 32-64个 | 异构性开始显现 | 小规模实盘 |
| 128-256个 | 规模效应显著 | 生产环境 |
| 512个 | 超额收益最大化 | 机构级应用 |

### 为什么更多Agent更好？

1. **视角多样性**：不同Agent捕捉不同市场模式
2. **误差抵消**：独立Agent的随机误差在聚合时相互抵消
3. **市场适应**：更多Agent意味着更高的概率覆盖当前市场regime
4. **稳健性**：单一Agent失效不会显著影响整体表现

---

## A股适配设计

### A股特色Agent类型

```python
class AShareTechnicalAgent:
    """考虑A股特殊机制的技术面Agent"""

    def decide(self, data):
        signals = {}
        for stock in data['stock_code'].unique():
            stock_data = data[data['stock_code'] == stock]

            # A股特色：涨跌停判断
            limit_up = stock_data['close'].iloc[-1] >= stock_data['pre_close'].iloc[-1] * 1.1
            limit_down = stock_data['close'].iloc[-1] <= stock_data['pre_close'].iloc[-1] * 0.9

            if self.strategy == 'momentum':
                # 避开涨停买入
                if not limit_up:
                    roc = calculate_roc(stock_data, self.lookback)
                    signals[stock] = 1 if roc > 0.05 else 0

            elif self.strategy == 'mean_reversion':
                # 跌停后反弹信号
                signals[stock] = 1 if limit_down else 0

        return signals


class AShareSentimentAgent:
    """基于A股特色情绪指标的Agent"""

    SOURCES = ['eastmoney', 'xueqiu', 'north_flow', 'margin_trading']

    def decide(self, data):
        sentiment = self._get_sentiment(self.source)

        # A股特色：情绪极值反向操作
        if sentiment > 0.8:  # 极度乐观
            return {stock: -1 for stock in data['stock_code'].unique()}
        elif sentiment < 0.2:  # 极度悲观
            return {stock: 1 for stock in data['stock_code'].unique()}

        return {stock: 0 for stock in data['stock_code'].unique()}


class ASharePolicyAgent:
    """A股特色：政策敏感Agent"""

    def decide(self, data):
        # 监控政策信号
        policy_signals = self._detect_policy_changes()

        if 'favorable_policy' in policy_signals:
            # 利好政策：增加相关行业权重
            return self._overweight_affected_sectors(policy_signals)
        elif 'restrictive_policy' in policy_signals:
            # 限制政策：减持相关行业
            return self._underweight_affected_sectors(policy_signals)

        return neutral_weights()
```

### A股实验验证

**实验设计**:
- **市场**: 2023年中国A股市场
- **数据**: 自收集数据集（避免数据泄漏）
- **基准**: 7个最先进的多Agent方法
- **验证**: 回测 + 稳定性分析 + 数据泄漏测试

**关键发现**:
- MASS持续优于所有基准方法
- 规模效应在A股市场同样成立
- 数据泄漏测试验证了结果可信度

---

## 技术实现

### 核心类实现

```python
import numpy as np
import pandas as pd
from typing import List, Dict


class MASSPortfolioConstructor:
    """
    MASS: Multi-Agent Simulation Scaling for Portfolio Construction
    """

    def __init__(self, n_agents: int = 512, learning_rate: float = 0.01):
        self.n_agents = n_agents
        self.lr = learning_rate
        self.agent_pool = self._initialize_agents()
        self.agent_weights = np.ones(n_agents) / n_agents
        self.performance_history = []

    def _initialize_agents(self) -> List:
        """初始化异构Agent群体"""
        agents = []
        distribution = {
            'technical': 0.20,
            'fundamental': 0.20,
            'sentiment': 0.15,
            'macro': 0.15,
            'quant': 0.20,
            'random': 0.10
        }

        for agent_type, ratio in distribution.items():
            n = int(self.n_agents * ratio)
            agents.extend(self._create_agents(agent_type, n))

        return agents

    def construct_portfolio(self, market_data: pd.DataFrame) -> Dict[str, float]:
        """端到端组合构建"""
        # 1. 所有Agent独立决策
        decisions = []
        for agent in self.agent_pool:
            decision = agent.decide(market_data)
            decisions.append(decision)

        # 2. 逆向优化权重
        if len(self.performance_history) > 0:
            self.agent_weights = self._optimize_weights(decisions)

        # 3. 加权聚合
        portfolio = self._aggregate_decisions(decisions, self.agent_weights)

        return portfolio

    def _optimize_weights(self, decisions: List[Dict]) -> np.ndarray:
        """逆向优化Agent权重"""
        contributions = self._calculate_contributions(decisions)

        # 基于贡献度更新权重
        new_weights = self.agent_weights * np.exp(self.lr * contributions)
        return new_weights / new_weights.sum()

    def _aggregate_decisions(self, decisions: List[Dict], weights: np.ndarray) -> Dict:
        """加权聚合Agent决策"""
        stocks = list(decisions[0].keys())
        portfolio = {}

        for stock in stocks:
            weighted_sum = sum(
                d.get(stock, 0) * w for d, w in zip(decisions, weights)
            )
            portfolio[stock] = weighted_sum

        # 归一化为权重
        total = sum(abs(v) for v in portfolio.values())
        if total > 0:
            portfolio = {k: v/total for k, v in portfolio.items()}

        return portfolio

    def update_performance(self, returns: float):
        """更新历史表现（用于逆向优化）"""
        self.performance_history.append(returns)
        if len(self.performance_history) > 252:  # 保留1年数据
            self.performance_history.pop(0)
```

### 与现有系统整合

```python
class IntegratedMASSSystem:
    """MASS与现有量化系统整合"""

    def __init__(self):
        # 数据层
        self.data_handler = QlibDataHandler(region='cn')

        # MASS组合构建
        self.mass = MASSPortfolioConstructor(n_agents=512)

        # 风险管理
        self.sizer = FractionalKellySizer(fraction=0.25)

    def run(self, date: str) -> Dict:
        """完整策略流程"""
        # 1. 获取数据
        data = self.data_handler.get_data(date)

        # 2. MASS组合构建
        weights = self.mass.construct_portfolio(data)

        # 3. 仓位管理
        positions = self.sizer.calculate_positions(weights)

        return positions

    def backtest(self, start_date: str, end_date: str) -> pd.DataFrame:
        """回测验证"""
        results = []

        for date in pd.date_range(start_date, end_date):
            positions = self.run(date)
            returns = self._calculate_returns(positions, date)

            self.mass.update_performance(returns)
            results.append({
                'date': date,
                'returns': returns,
                'positions': positions
            })

        return pd.DataFrame(results)
```

---

## 性能指标

### 实验结果

| 指标 | 数值 | 说明 |
|------|------|------|
| 基准对比 | 优于7个SOTA方法 | 持续超额收益 |
| 规模效应 | 512 Agent最优 | 数量与收益正相关 |
| 市场适应 | 动态调整 | 适应A股regime变化 |
| 稳健性 | 数据泄漏测试通过 | 结果可信 |

### 关键优势

1. **端到端优化**：直接最大化组合收益
2. **规模递增**：更多Agent = 更好表现（与传统直觉相反）
3. **动态适应**：逆向优化自动调整Agent权重
4. **A股验证**：专门针对中国市场验证

---

## 使用场景

### 适用场景

- **组合构建**：需要动态权重调整的投资组合
- **多策略融合**：整合多种异构策略信号
- **A股投资**：专门针对A股市场的量化策略
- **机构级应用**：大规模Agent并行计算环境

### 触发条件

```
何时使用MASS:
✓ 需要端到端组合优化（非信号生成）
✓ 有大量计算资源（支持512+ Agent并行）
✓ 投资A股市场（已验证有效）
✓ 追求稳健超额收益（非高风险高回报）

何时不使用MASS:
✗ 计算资源有限（Agent数量不足32个）
✗ 需要高频交易（MASS适合日/周频）
✗ 单一策略足够（不需要异构Agent）
```

---

## 相关资源

- **论文**: [MASS: Multi-Agent Simulation Scaling for Portfolio Construction](https://arxiv.org/abs/2505.10278)
- **代码**: https://github.com/gta0804/MASS
- **相关技能**:
  - `trading-agents-framework.md` - 多Agent交易架构
  - `blindfolded-llm-trading.md` - 匿名化验证
  - `agentic-ai-factor-investing.md` - Agentic因子投资
  - `microsoft-qlib-platform.md` - 数据基础设施

---

## 版本历史

- **v1.0** (2026-03-25): 初始技能文件创建

---

*技能文件: mass-multi-agent-scaling.md*
*创建日期: 2026-03-25*
*更新日期: 2026-03-25*
