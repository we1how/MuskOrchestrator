# Self-Driving Portfolio: Agentic Architecture for Institutional Asset Management

## Description

基于BlackRock前CIO Andrew Ang团队的论文《The Self Driving Portfolio》，构建机构级多Agent资产管理系统的实现指南。将投资者角色从"分析执行"转变为"监督"，实现资本市场假设生成→组合构建→绩效归因→策略迭代的闭环自动化。

## When to Use

- 设计多Agent量化交易系统架构
- 实现策略自动发现与迭代
- 构建机构级资产管理pipeline
- 优化现有Agent协作流程
- 建立投资政策说明书(IPS)约束的AI治理框架

## Core Architecture

### 5层Agent架构

```
┌─────────────────────────────────────────────────────────────┐
│  Governance Layer: IPS约束层                                  │
│  - 投资政策说明书编码为代理行为边界                             │
│  - 风险控制规则、合规检查、审计日志                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 5: Meta-Agent (元代理) × 1                            │
│  - 对比预测vs实际回报                                         │
│  - 自动重写代理代码和提示词                                    │
│  - 系统级性能优化                                             │
└─────────────────────────────────────────────────────────────┘
                              ↑↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: Researcher Agent (研究员代理) × 1                  │
│  - 提出新的组合构建方法                                       │
│  - 发现未被代表的策略空间                                     │
│  - 创新提案生成                                               │
└─────────────────────────────────────────────────────────────┘
                              ↑↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Evaluation & Voting Agents (评估投票代理) ~10      │
│  - 对候选组合进行同行评审                                     │
│  - 加权投票达成共识                                          │
│  - 风险调整后收益评估                                         │
└─────────────────────────────────────────────────────────────┘
                              ↑↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Portfolio Construction Agents (组合构建代理) ~20     │
│  - 均值-方差优化 (Markowitz)                                 │
│  - Black-Litterman模型                                       │
│  - 风险平价 (Risk Parity)                                    │
│  - 最大分散度 (Maximum Diversification)                      │
│  - 最小方差 (Minimum Variance)                               │
│  - 因子投资 (Factor-based)                                   │
│  - ... (可扩展)                                              │
└─────────────────────────────────────────────────────────────┘
                              ↑↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: CMA Generation Agents (资本市场假设生成代理) ~15     │
│  - 收益预测代理 (@analyst)                                   │
│  - 风险预测代理                                              │
│  - 相关性矩阵预测代理                                        │
│  - 宏观经济情景代理                                          │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Guide

### Phase 1: CMA生成层 (Week 1)

**代理角色映射**：
| 代理 | 角色 | 输出 |
|------|------|------|
| @analyst | 收益预测专家 | 资产类别预期收益 |
| @analyst | 风险预测专家 | 波动率/下行风险估计 |
| @analyst | 相关性专家 | 资产间相关性矩阵 |
| @analyst | 宏观情景专家 | 经济状态概率分布 |

**聚合机制**：
```python
def aggregate_cma(predictions, weights):
    """
    方差加权聚合多个代理的CMA预测
    """
    # 基于历史预测准确度动态调整权重
    weighted_return = sum(p.return * w for p, w in zip(predictions, weights))
    weighted_risk = sqrt(sum(p.risk**2 * w for p, w in zip(predictions, weights)))
    # 相关性矩阵使用平均或中位数聚合
    aggregated_corr = median([p.corr_matrix for p in predictions], axis=0)
    return CMA(weighted_return, weighted_risk, aggregated_corr)
```

### Phase 2: 组合构建层 (Week 2)

**20+方法并行运行**：

```python
PORTFOLIO_METHODS = [
    "mean_variance",
    "black_litterman",
    "risk_parity",
    "max_diversification",
    "min_variance",
    "equal_weight",
    "inverse_volatility",
    "factor_momentum",
    "factor_value",
    "factor_quality",
    "risk_budget",
    "cvar_optimization",
    "robust_optimization",
    "bayesian_shrinkage",
    "hierarchical_risk_parity",
    # ... 研究员代理可动态添加
]

def construct_portfolios(cma, methods):
    """并行构建所有候选组合"""
    portfolios = {}
    for method in methods:
        agent = get_agent(f"portfolio_{method}")
        portfolios[method] = agent.construct(cma)
    return portfolios
```

### Phase 3: 评估投票层 (Week 2-3)

**互评机制**：
```python
def peer_review(portfolios, eval_agents):
    """
    每个评估代理对所有组合进行评分
    """
    scores = defaultdict(dict)
    for eval_agent in eval_agents:
        for method, portfolio in portfolios.items():
            scores[method][eval_agent.name] = eval_agent.evaluate(
                portfolio,
                criteria=["sharpe_ratio", "max_drawdown", "turnover", "diversification"]
            )
    return scores

def consensus_vote(scores, weights):
    """
    加权投票确定最终组合
    """
    final_scores = {}
    for method, agent_scores in scores.items():
        final_scores[method] = sum(
            score * weights.get(agent, 1.0)
            for agent, score in agent_scores.items()
        )
    return max(final_scores, key=final_scores.get)
```

### Phase 4: 研究员代理 (Week 3-4)

**自动策略发现**：
```python
class ResearcherAgent:
    def __init__(self):
        self.known_methods = set(PORTFOLIO_METHODS)
        self.innovation_history = []

    def propose_new_method(self, performance_data):
        """
        基于绩效归因提出新方法
        """
        # 分析现有方法的失效模式
        gaps = self.identify_strategy_gaps(performance_data)

        # 生成新方法提案
        proposal = self.llm.generate(
            prompt=f"""
            现有组合构建方法: {self.known_methods}
            已识别的策略缺口: {gaps}

            请提出一种全新的组合构建方法，要求：
            1. 数学上严谨
            2. 与现有方法差异显著
            3. 有明确的经济学直觉
            4. 可计算实现

            输出格式：方法名称、数学公式、Python伪代码、预期适用场景
            """
        )

        # 验证并添加到候选池
        if self.validate_method(proposal):
            self.known_methods.add(proposal.name)
            self.innovation_history.append(proposal)
            return proposal
        return None
```

### Phase 5: 元代理 (Week 4+)

**自我进化机制**：
```python
class MetaAgent:
    def __init__(self):
        self.performance_history = []
        self.agent_versions = {}

    def track_performance(self, predictions, realized_returns):
        """
        追踪预测vs实际回报
        """
        attribution = self.attribution_analysis(predictions, realized_returns)
        self.performance_history.append(attribution)
        return attribution

    def optimize_agents(self):
        """
        基于归因结果自动优化代理
        """
        for agent_name, errors in self.identify_systematic_errors():
            # 生成优化后的提示词
            new_prompt = self.generate_improved_prompt(agent_name, errors)

            # 或生成优化后的代码
            if errors.code_related:
                new_code = self.generate_improved_code(agent_name, errors)
                self.deploy_code_update(agent_name, new_code)

            # 记录版本
            self.agent_versions[agent_name].append({
                "timestamp": now(),
                "prompt": new_prompt,
                "performance_delta": self.estimate_improvement(errors)
            })

    def attribution_analysis(self, predictions, realized):
        """
        绩效归因：识别误差来源
        """
        return {
            "cma_error": self.cma_prediction_error(predictions.cma, realized),
            "construction_error": self.construction_method_error(predictions.weights, realized),
            "timing_error": self.market_timing_error(predictions.signals, realized),
            "model_risk": self.model_uncertainty_contribution(predictions, realized)
        }
```

## IPS Governance Framework

### 约束编码
```python
class IPSGovernance:
    def __init__(self, ips_document):
        self.constraints = self.parse_ips(ips_document)

    def check_constraints(self, portfolio_action):
        """
        检查组合操作是否符合IPS
        """
        checks = [
            self.check_asset_allocation_limits(portfolio_action),
            self.check_risk_budget(portfolio_action),
            self.check_turnover_limits(portfolio_action),
            self.check_esg_constraints(portfolio_action),
            self.check_liquidity_requirements(portfolio_action),
        ]
        return all(checks)

    def parse_ips(self, doc):
        """
        使用LLM将自然语言IPS转换为可执行约束
        """
        return self.llm.extract(
            doc,
            schema={
                "asset_classes": ["stocks", "bonds", "alternatives"],
                "allocation_ranges": {"min": float, "max": float},
                "risk_metrics": {"var_limit": float, "max_drawdown": float},
                "turnover": {"annual_max": float},
            }
        )
```

## Integration with Current System

### 现有Agent映射

| 现有Agent | 论文架构角色 | 增强方向 |
|-----------|-------------|----------|
| @planner | CMA生成 + 组合构建协调 | 增加多方法并行能力 |
| @engineer | 组合构建实现 | 增加20+方法库 |
| @analyst | CMA生成核心 | 增加宏观情景分析 |
| @reviewer | 评估投票代理 | 增加互评机制 |
| @creator | 研究员代理 | 增加策略发现能力 |
| (新增) | 元代理 | 自我进化系统 |

### 演进路径

**Week 1**: 静态多方法并行
- 实现20种组合构建方法
- 简单平均或投票聚合

**Week 2**: 动态权重调整
- 基于历史表现动态调整方法权重
- 引入风险平价作为基准

**Week 3**: 研究员代理
- 实现自动策略发现
- A/B测试新vs旧方法

**Week 4**: 元代理闭环
- 实现提示词自动优化
- 建立性能归因系统

**Week 5+**: IPS治理
- 将投资约束编码
- 实现合规自动检查

## Key Metrics

### 系统级指标
- **预测准确度**: CMA预测vs实现的RMSE
- **组合夏普比率**: 风险调整后收益
- **方法多样性**: 有效方法数量（权重>5%）
- **创新速率**: 每周新策略提案数
- **进化速度**: 代理版本迭代频率

### 代理级指标
- **个体准确度**: 各CMA代理的预测误差
- **投票影响力**: 各评估代理的投票权重变化
- **创新质量**: 研究员代理提案的回测表现
- **优化效果**: 元代理优化的性能提升

## Risk Management

### 模型风险
- **过度拟合**: 20+方法并行增加过拟合风险 → 交叉验证 + 正则化
- **代理一致性**: 代理间高相关性降低多样性 → 强制 decorrelation
- **反馈循环**: 元代理优化可能引发不稳定 → 渐进式更新 + 回滚机制

### 操作风险
- **代码错误**: 自动生成的代码可能有bug → 单元测试 + 沙盒验证
- **提示词漂移**: LLM提示词优化可能偏离目标 → 人工审核关键变更
- **数据质量**: CMA依赖数据输入 → 数据验证层

## References

- **原文**: Ang, A., Azimbayev, N., & Kim, A. (2026). The Self Driving Portfolio: Agentic Architecture for Institutional Asset Management. arXiv:2604.02279.
- **关联论文**:
  - 2603.14288: Beyond Prompting: Agentic AI Factor Investing
  - 2603.17692: Blindfolded LLMs Trading
  - 2603.20965: Zero-Shot LLM Agent Aggregation

---

*Skill Version: 1.0*
*Created: 2026-04-08*
*Based on: arXiv:2604.02279*
