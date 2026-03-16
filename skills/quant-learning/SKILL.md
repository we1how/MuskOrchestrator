# Quant Learning Skill

## Description

个性化量化学习路径规划与执行系统。基于18个月量化学习路线图，结合用户实际情况，生成可执行的每周学习计划。

## When to Use

- 开始新一周学习时：`/quant-learning week X`
- 查看整体学习路径：`/quant-learning roadmap`
- 生成定制计划：`/quant-learning plan`
- 检查学习进度：`/quant-learning status`

## The 18-Month Quant Roadmap

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         18个月量化学习路线图                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase 1: 基础数学 (5-6个月)                                                  │
│  ═══════════════════════════                                                 │
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   Week 1-4  │ →  │   Week 5-9  │ →  │  Week 10-14 │ →  │  Week 15-20 │  │
│  │  Probability│    │  Statistics │    │ Linear Algebra│   │  Calculus & │  │
│  │  概率论      │    │   统计学     │    │   线性代数    │    │ Optimization│  │
│  │             │    │             │    │             │    │ 微积分与优化 │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│        ↓                  ↓                  ↓                  ↓          │
│   贝叶斯推断            假设检验             PCA降维           凸优化        │
│   条件概率              MLE估计              马科维茨           梯度下降      │
│   期望值                回归分析             特征值分解          泰勒展开      │
│                                                                             │
│  教材: Blitzstein     教材: Wasserman     教材: Strang      教材: Boyd     │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase 2: 金融数学 (6-8个月)                                                  │
│  ═══════════════════════════                                                 │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Week 21-32: Stochastic Calculus                  │   │
│  │                       随机微积分 (最难阶段)                           │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  Week 21-24: Brownian Motion + Geometric Brownian Motion            │   │
│  │  Week 25-28: Itô's Lemma + Deriving Black-Scholes                   │   │
│  │  Week 29-32: Greeks + Risk-Neutral Pricing                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  教材: Shreve《Stochastic Calculus for Finance II》                         │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Phase 3: 实战应用 (4-6个月)                                                  │
│  ═══════════════════════════                                                 │
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │  Week 33-38 │ →  │  Week 39-44 │ →  │  Week 45-50 │ →  │  Week 51+   │  │
│  │    因子投资  │    │   机器学习   │    │   高频交易   │    │   策略实盘   │  │
│  │  Factor     │    │   ML for    │    │   HFT &     │    │  Live       │  │
│  │  Investing  │    │   Trading   │    │   Execution │    │  Trading    │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│        ↓                  ↓                  ↓                  ↓          │
│   Fama-French          XGBoost            Market Making      Risk Mgmt     │
│   Factor Models        LSTM               Almgren-Chriss     Position Sizing│
│   PCA/ICA              Transformers       Latency Opt        Portfolio Opt │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  📚 核心教材清单 (按学习顺序)                                                  │
│  ═══════════════════════════                                                 │
│                                                                             │
│  1. Blitzstein & Hwang - Introduction to Probability (免费PDF)               │
│  2. Wasserman - All of Statistics (Ch 1-13)                                 │
│  3. Strang - Introduction to Linear Algebra + MIT 18.06 视频                │
│  4. Boyd & Vandenberghe - Convex Optimization (免费PDF)                      │
│  5. Shreve - Stochastic Calculus for Finance I & II                         │
│  6. Hull - Options, Futures, and Other Derivatives                          │
│  7. López de Prado - Advances in Financial Machine Learning                 │
│  8. Zuckerman - The Man Who Solved the Market                               │
│                                                                             │
│  🎯 面试准备: Xinfeng Zhou's Green Book (Quant Interview)                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Weekly Plan Library

### Week 1: Bayesian Inference Foundation
```yaml
week: 1
dates: "2026-03-10 to 2026-03-16"
theme: "贝叶斯推断基础"
daily_hours: 2
total_hours: 14
prerequisites: []

learning_goals:
  - 理解条件概率与贝叶斯定理
  - 掌握Beta-Binomial共轭先验
  - 实现贝叶斯因子更新模块

deliverables:
  - BayesianFactorUpdater类
  - 单元测试
  - 学习笔记 LEARNING_BAYES_W1.md

resources:
  videos:
    - "3Blue1Brown: Bayes定理 (15min)"
    - "StatQuest: Bayes定理 (8min)"
  books:
    - "Statistical Inference Casella & Berger, Ch 1.4, 3.3"
  code_refs:
    - "scipy.stats.beta"
    - "scipy.optimize.minimize"

code_integration:
  module: "risk_management/bayesian_factor_updater.py"
  application: "动态更新因子胜率估计"
  stock_platform_integration: true
```

### Week 2: Statistical Inference
```yaml
week: 2
dates: "2026-03-17 to 2026-03-23"
theme: "假设检验与统计推断"
daily_hours: 2
total_hours: 14
prerequisites: [week1]

learning_goals:
  - 掌握假设检验与p值
  - 理解多重比较校正
  - 学会Bootstrap方法
  - 实现策略质量门禁

deliverables:
  - StrategySignificanceTester类
  - MultipleComparisonCorrection类
  - StrategyGateKeeper门禁系统
  - 学习笔记 LEARNING_STATS_W2.md

resources:
  videos:
    - "StatQuest: Hypothesis Testing (7min)"
    - "StatQuest: p-values (7min)"
    - "StatQuest: Multiple Comparisons (8min)"
    - "StatQuest: Bootstrap (12min)"
  books:
    - "All of Statistics Wasserman, Ch 10-12"

code_integration:
  module: "risk_management/statistical_tests/"
  application: "策略显著性检验与质量门禁"
  stock_platform_integration: true
```

### Week 3-4: Advanced Statistics & MLE
```yaml
week: 3-4
theme: "高级统计与最大似然估计"
daily_hours: 2
total_hours: 28
prerequisites: [week2]

learning_goals:
  - 深入理解MLE原理
  - 掌握分布拟合与检验
  - 理解信息准则(AIC/BIC)
  - 实现参数估计模块

deliverables:
  - MLE分布拟合模块
  - AIC/BIC模型选择
  - 收益率分布分析

resources:
  books:
    - "All of Statistics Wasserman, Ch 7-9"
  code_refs:
    - "scipy.optimize"
    - "scipy.stats"
```

### Week 5-8: Linear Algebra for Finance
```yaml
week: 5-8
theme: "金融线性代数"
daily_hours: 2
total_hours: 56
prerequisites: [week4]

learning_goals:
  - 矩阵运算与性质
  - 特征值与特征向量
  - PCA因子降维
  - 马科维茨组合优化

deliverables:
  - 协方差矩阵估计模块
  - PCA分解工具
  - 马科维茨优化器
  - 有效前沿计算

resources:
  videos:
    - "MIT 18.06 Linear Algebra (全集)"
  books:
    - "Strang: Introduction to Linear Algebra"
  code_refs:
    - "numpy.linalg"
    - "cvxpy"
    - "sklearn.decomposition.PCA"
```

### Week 9-12: Optimization
```yaml
week: 9-12
theme: "凸优化与数值方法"
daily_hours: 2
total_hours: 56
prerequisites: [week8]

learning_goals:
  - 凸优化理论
  - 约束优化问题
  - 梯度下降与牛顿法
  - 投资组合优化

deliverables:
  - 凸优化求解器封装
  - 带约束的组合优化
  - 交易成本模型
  - 滑点优化

resources:
  books:
    - "Boyd & Vandenberghe: Convex Optimization (免费PDF)"
  code_refs:
    - "cvxpy"
    - "scipy.optimize"
```

### Week 13-20: Stochastic Calculus
```yaml
week: 13-20
theme: "随机微积分 (最难阶段)"
daily_hours: 2
total_hours: 112
prerequisites: [week12]

learning_goals:
  - 布朗运动与维纳过程
  - 伊藤引理
  - Black-Scholes推导
  - 希腊字母与风险管理

deliverables:
  - BS期权定价实现
  - 希腊字母计算模块
  - 隐含波动率曲面
  - 蒙特卡洛模拟器

resources:
  books:
    - "Shreve: Stochastic Calculus for Finance II"
    - "Hull: Options, Futures, and Other Derivatives"
  code_refs:
    - "QuantLib"
```

## How to Use This Skill

### 1. 查看整体路线图
```
/quant-learning roadmap
```
显示完整的18个月学习路径和当前位置。

### 2. 获取本周学习计划
```
/quant-learning week 1
/quant-learning week 2
```
生成具体的每日学习安排、资源链接、代码框架。

### 3. 生成定制计划
```
/quant-learning plan
```
基于当前进度和可用时间，生成定制化学习计划。

### 4. 检查学习状态
```
/quant-learning status
```
显示已完成内容、当前进度、下一步建议。

## Success Criteria

### Week Completion Criteria
每周末自查：
- [ ] 能否用费曼技巧解释本周核心概念？
- [ ] 代码是否能运行并通过测试？
- [ ] 是否能应用到Stock Platform？
- [ ] 学习笔记是否完整？

### Phase Completion Criteria
每阶段结束：
- [ ] 完成该阶段所有教材阅读
- [ ] 实现核心算法模块
- [ ] 通过综合项目验证
- [ ] 能用该阶段知识解释一个实际金融问题

## Risk Management

### If You Fall Behind
- **落后1周**: 正常推进，利用周末补上
- **落后2周**: 暂停新内容，先补完遗漏
- **落后3周+**: 重新评估目标，调整计划节奏

### Quality Gates
- 每周产出必须通过代码审查
- 概念理解必须通过费曼检验
- 应用到项目必须通过功能测试

## Integration with Stock Platform

```
学习计划 ──→ 知识获取 ──→ 代码实现 ──→ 策略验证 ──→ 实盘应用
    ↑                                                      │
    └────────────── 回测结果反馈优化学习重点 ────────────────┘
```

所有学习产出必须：
1. 可直接集成到Stock Platform
2. 有单元测试验证
3. 有文档说明
4. 有实际策略应用案例

---

**Skill Version**: 1.0
**Last Updated**: 2026-03-16
**Based on**: 18-Month Quant Roadmap + User Progress
