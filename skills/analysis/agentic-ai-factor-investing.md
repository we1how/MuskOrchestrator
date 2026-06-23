# Agentic AI Factor Investing - Beyond Prompting

> **来源**: arXiv:2603.14288
> **标题**: Beyond Prompting: An Autonomous Framework for Systematic Factor Investing via Agentic AI
> **作者**: Allen Yikuan Huang, Zheqi Fan

---

## 核心概念

Agentic AI因子投资框架——将AI模型从"Prompting工具"转化为"自主决策引擎"，通过闭环系统的严格实证纪律（样本外验证+经济理论约束）实现因子投资的自动化和规模化。

---

## 关键指标

| 指标 | 数值 |
|------|------|
| 年化夏普比率 | **3.11** |
| 年化收益率 | **59.53%** |
| 策略类型 | 多空组合 |
| 信号构建 | 简单线性组合 |

---

## 系统架构

```
Agentic AI因子投资系统
│
├─ 因子假设生成层
│  └─ AI基于市场观察自主提出因子假设
│  └─ 要求: 必须有经济理论支撑
│
├─ 经济理论验证层
│  └─ 验证因子假设的经济学合理性
│  └─ 要求: 理论分数 > 0.7
│
├─ 样本内验证层
│  └─ 历史数据回测验证
│  └─ 统计显著性检验 (t-statistic > 2.0)
│
├─ 样本外验证层 (关键)
│  └─ 完全未参与训练的数据集测试
│  └─ 性能衰减 < 30%
│
└─ 自进化循环
   ├─ 验证通过 → 纳入因子库
   ├─ 验证失败 → 返回重新假设
   └─ 定期淘汰失效因子
```

---

## 核心代码实现

### 1. 主系统类

```python
from typing import List, Dict, Tuple
import pandas as pd
import numpy as np

class AgenticFactorInvestingSystem:
    """
    基于Agentic AI的自主因子投资系统
    """

    def __init__(self, config: Dict):
        self.config = config
        self.factor_library = []  # 已验证因子库
        self.economic_validator = EconomicRationaleValidator()
        self.statistical_validator = StatisticalValidator()

    def self_evolution_cycle(self):
        """自进化循环"""
        # 1. 观察市场状态
        market_state = self.observe_market()

        # 2. 生成新因子假设
        new_hypotheses = self.generate_factor_hypothesis(market_state)

        # 3. 验证新因子
        validated_factors = []
        for hypothesis in new_hypotheses:
            if self.closed_loop_validation(hypothesis, self.data):
                validated_factors.append(hypothesis)

        # 4. 更新因子库
        self.factor_library.extend(validated_factors)

        # 5. 淘汰失效因子
        self.factor_library = self.prune_obsolete_factors(self.factor_library)

        return len(validated_factors)
```

### 2. 经济理论验证器

```python
class EconomicRationaleValidator:
    """验证因子假设的经济理论合理性"""

    VALID_THEORIES = {
        'risk_premium': ['size', 'value', 'momentum', 'quality', 'volatility'],
        'behavioral': ['overreaction', 'underreaction', 'anchoring', 'herding'],
        'microstructure': ['liquidity', 'price_impact', 'information_asymmetry'],
        'information': ['earnings_surprise', 'analyst_coverage', 'insider_trading']
    }

    def validate(self, factor_hypothesis: Dict) -> Tuple[bool, float]:
        """验证经济理论合理性"""
        theory_category = factor_hypothesis.get('theoretical_basis')
        if theory_category not in self.VALID_THEORIES:
            return False, 0.0

        mechanism = factor_hypothesis.get('mechanism_description', '')
        rationale_score = self.evaluate_mechanism(mechanism, theory_category)

        literature = factor_hypothesis.get('supporting_literature', [])
        literature_score = min(len(literature) / 2, 1.0)

        final_score = 0.6 * rationale_score + 0.4 * literature_score
        return final_score > 0.7, final_score
```

### 3. 统计验证框架

```python
class StatisticalValidator:
    """严格样本外验证框架"""

    def __init__(self, in_sample_ratio=0.6):
        self.in_sample_ratio = in_sample_ratio

    def split_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """严格划分样本内/样本外数据"""
        split_point = int(len(data) * self.in_sample_ratio)
        in_sample = data.iloc[:split_point]
        out_sample = data.iloc[split_point:]
        return in_sample, out_sample

    def closed_loop_validation(self, factor: Dict, data: pd.DataFrame) -> bool:
        """闭环验证"""
        in_sample, out_sample = self.split_data(data)

        # 样本内验证
        in_result = self.in_sample_test(factor, in_sample)
        if in_result['t_stat'] < 2.0:
            return False

        # 样本外验证 (关键)
        out_result = self.out_sample_test(factor, out_sample)
        performance_decay = (in_result['sharpe'] - out_result['sharpe']) / in_result['sharpe']

        return performance_decay < 0.3
```

---

## A股适配

### A股特有的经济理论类别

```python
class AShareAgenticFactorSystem(AgenticFactorInvestingSystem):
    """A股适配的Agentic因子投资系统"""

    def __init__(self):
        super().__init__(config={})

        # A股特有的经济理论约束
        self.a_share_theories = {
            'policy_driven': ['policy_cycle', 'regulatory_change', 'state_owned_enterprise'],
            'retail_sentiment': ['retail_herding', 'limit_up_down', 'turnover_sentiment'],
            'liquidity_premium': ['small_cap_premium', 'turnover_illiquidity'],
            'behavioral_a_share': ['earnings_gaming', 'concept_rotation']
        }

        self.economic_validator.VALID_THEORIES.update(self.a_share_theories)
```

---

## 与现有系统的整合

```python
class IntegratedQuantSystem:
    """整合Agentic因子投资与现有系统"""

    def __init__(self):
        # 数据基础设施 (Microsoft Qlib)
        self.data_handler = QlibDataHandler()

        # 多Agent决策 (TradingAgents)
        self.trading_agents = TradingAgentsGraph()

        # Agentic因子生成
        self.factor_system = AShareAgenticFactorSystem()

        # 深度研究 (MiroThinker)
        self.deep_researcher = DeepResearchAgent()

        # 匿名化验证 (BlindTrade)
        self.anonymizer = AShareAnonymizer()
```

---

## 触发条件

- 因子投资研究
- Agentic AI系统设计
- 自动化量化研究
- 策略自进化需求

---

## 关键产出

1. **自主生成的因子假设**
2. **经济理论验证报告**
3. **样本外验证结果**
4. **动态因子库**
5. **多空组合信号**

---

## 参考资源

- **论文**: https://arxiv.org/abs/2603.14288
- **学习记录**: `memory/agents/analyst/LEARNING.md`
- **相关技能**:
  - `skills/analysis/microsoft-qlib-platform.md`
  - `skills/analysis/trading-agents-framework.md`
  - `skills/analysis/blindfolded-llm-trading.md`
  - `skills/analysis/mirothinker-deep-research.md`
