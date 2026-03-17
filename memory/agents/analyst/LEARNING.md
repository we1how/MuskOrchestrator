# LEARNING.md - Quant-Munger 学习记录

## 学习记录索引

### 已学习论文（近7天）
| 日期 | Arxiv ID/标题 | 核心主题 | 状态 |
|------|---------------|----------|------|
| 2026-03-16 | Market Research方法论 | 研究支持决策，非研究表演 | ✅ 技能内化 |
| 2026-03-13 | ML vs Trend分歧交易 | 模型分歧即信号，动态仓位 | ✅ 技能内化 |
| 2026-03-12 | Fractional Kelly仓位管理 | Kelly公式+A股适配+风险管理 | ✅ 技能内化 |
| 2026-03-11 | A股多Agent框架整合 | 信号融合+超跌反弹+策略拥挤度 | ✅ 技能内化 |
| 2026-03-10 | 已有知识深化 | 超跌反弹策略+多Agent融合应用 | ✅ 已学习 |
| 2026-03-09 | ai-hedge-fund量化分析 | 多Agent信号融合，归一化指标 | ✅ 已学习 |
| 2026-03-08 | Multi-Agent LLM Trading System | 多智能体交易系统工程化实践 | ✅ 已学习 |
| 2026-03-06 | 2603.03671 - Is an investor stolen their profits by mimic investors? | 策略拥挤度、Agent-Based模型 | ✅ 已学习 |
| 2026-03-05 | 2603.02898 - Range-Based Volatility Estimators for Monitoring Market Stress | OHLC波动率估计器、市场压力监测 | ✅ 已学习 |

---

### 今日学习（2026-03-10 Monday）

#### 学习内容
- **主题**: 已有知识深化 - 超跌反弹策略 + 多Agent信号融合应用
- **来源**: 内部知识库整合
- **背景**: Arxiv q-fin RSS feed访问格式变更，暂时无法解析，基于已有学习深化

#### 核心洞察
1. **细粒度任务设计是信号有效传递的关键**
   - 论文核心发现：粗粒度指令导致LLM推理中断
   - 细粒度任务（基于预计算的8周期RoC、Bollinger Z-score）显著提升夏普比率
   - **关键公式**: 归一化MACD = (EMA₁₂ - EMA₂₆) / Pₜ

2. **分层决策架构的本质是"职责清晰"**
   - Level 1（分析师层）：专注信号提取，噪声过滤
   - Level 2（调整层）：行业对标、宏观环境校准
   - Level 3（PM层）：权重分配、最终决策
   - **核心洞察**: 即使单Agent系统，分层函数设计也能提升可解释性

3. **超跌反弹策略的量化基础**
   - 理论基础：均值回归（Fama & French, 1988）+ 行为金融学
   - 关键参数：40%跌幅阈值 + 获利比例<10% + 反弹12.5%触发买入
   - **A股应用**: 结合多Agent信号融合，避免价值陷阱

#### A股可应用性
- **策略增强**: 超跌信号 + 基本面过滤 + 宏观择时
- **动态阈值**: 根据VIX替代指标调整（恐慌期30%，平稳期50%）
- **分层过滤**: 超跌信号 → 基本面过滤 → 宏观择时

#### 技能提取
- **细粒度指标预处理**: 归一化指标计算（消除价格偏见）
- **分层决策框架**: 信号提取 → 校准对齐 → 综合决策
- **动态阈值调整**: 根据市场状态动态调整策略参数

#### 待解决问题
- [ ] 修复Arxiv RSS feed解析（格式可能变更，需检查atom/rss结构）
- [ ] 备选方案：直接使用arXiv API (export.arxiv.org/api/query)
- [ ] SSRN作为备选源的可行性验证

---

### 今日学习（2026-03-06 Friday）

#### 学习内容
- **标题**: Is an investor stolen their profits by mimic investors? Investigated by an agent-based model
- **Arxiv ID**: 2603.03671
- **来源**: Arxiv q-fin.CP (Computational Finance)
- **作者**: Takanobu Mizuta, Isao Yagi

#### 核心洞察
1. **策略拥挤度的非对称效应**：策略拥挤对不同策略类型的影响截然相反
   - **基本面策略（AFAs）**：投资者增加 → 市场更稳定 → 收益下降（存在"拥挤惩罚"）
   - **技术分析策略（ATAs）**：投资者增加 → 市场更不稳定 → 收益上升（存在"拥挤红利"）

2. **市场微观结构机制**：
   - 基本面交易者增多会加速价格向基本面回归，减少定价偏差
   - 技术分析交易者增多会强化趋势，增加价格波动性和持续性

3. **策略容量悖论**：传统观点"策略拥挤降低收益"只适用于基本面策略，技术分析策略恰恰相反

4. **Agent-Based模型的优势**：能隔离纯策略效应，排除实际市场中混杂因素的影响

#### 信息差价值
- **高**：直接回答了一个长期争论的问题——为什么有些量化团队分享策略参数后反而表现更好
- **独特发现**：技术分析策略存在"拥挤红利"，参与者越多趋势越强
- **策略启示**：A股技术分析策略（如趋势跟踪、动量）可能因散户众多而更有效

#### 可应用性
- **A股策略**：
  - **因子拥挤监控**：基本面因子需要监控拥挤度，及时轮换
  - **技术策略容量**：趋势/动量策略在A股可能有更高容量上限
  - **市场环境判断**：通过观察波动性和趋势持续性来推断主流策略类型

- **具体应用**：
  - 构建因子拥挤度指标（如因子收益率波动、多空拥挤度）
  - 当基本面因子拥挤时，增加技术因子权重
  - 趋势策略可以考虑更大的管理规模

#### 关键发现摘要
```
策略类型      投资者增加      市场影响        收益变化
─────────────────────────────────────────────────
基本面策略    AFAs ↑         价格稳定        收益 ↓
技术分析      ATAs ↑         价格波动        收益 ↑
```

#### 下一步行动
- [ ] 在A股市场验证：检查技术因子拥挤度与因子收益的关系
- [ ] 构建A股因子拥挤度监控面板
- [ ] 设计动态因子权重调整策略（基于拥挤度信号）

---

### 历史学习（2026-03-05 Thursday）

#### 学习内容
- **标题**: Range-Based Volatility Estimators for Monitoring Market Stress: Evidence from Local Food Price Data
- **Arxiv ID**: 2603.02898
- **来源**: Arxiv q-fin.ST
- **作者**: Bo Pieter Johannes Andrée (World Bank)

#### 核心洞察
1. **四种OHLC波动率估计器**：Parkinson、Garman-Klass、Rogers-Satchell、Yang-Zhang，利用日内高低点信息比收盘价波动率更有效
2. **市场压力监测**：波动率能发现RSI等动量指标遗漏的信号，特别是对称冲击或快速反转场景（供需同时受冲击时净价格变化小但日内波动大）
3. **Yang-Zhang最优**：在响应性和降噪之间取得最佳平衡，推荐作为默认估计器

#### 信息差价值
- **高**：A股可直接应用OHLC波动率估计器，Python实现简单（仅需4个价格点）
- **独特发现**：波动率指标能预警RSI/MACD无法识别的市场压力（如震荡市中供需同时变化）
- **计算优势**：轻量级、无需模型重新估计、适合自动化预警系统

#### 可应用性
- **A股策略**：基于Yang-Zhang波动率构建市场压力预警系统，辅助择时决策
- **工具**：已实现Python函数（见skills/volatility_estimators.py）
- **方法**：阈值规则（如滚动95分位数）识别异常波动时期

#### 关键公式摘要
```
Parkinson:     σ² = (ln(H/L))² / (4·ln2)
Garman-Klass:  σ² = 0.5·(ln(H/L))² - (2ln2-1)·(ln(C/O))²  
Rogers-Satchell: σ² = ln(H/C)·ln(H/O) + ln(L/C)·ln(L/O)
Yang-Zhang:    σ² = σ_overnight² + k·σ_open_close² + (1-k)·σ_RS²
```

---

## 学习档案

### 技能列表
- [x] OHLC波动率估计器实现
- [ ] A股数据源接入（Tushare/AkShare）
- [ ] 量化回测框架
- [ ] 因子拥挤度监控指标

### 数据来源
- Arxiv q-fin: 每日检查
- 本文件创建时间: 2026-03-05

---

### 今日学习（2026-03-08 Saturday）

#### 学习内容
- **主题**: 多智能体交易系统的工程化实践 - 从论文到落地
- **来源**: Research Synthesis / Knowledge Base
- **基础论文**: arXiv:2602.23330 - Multi-Agent LLM Trading System

#### 核心洞察
1. **细粒度任务设计的本质**: 把计算工作从LLM转移到确定性代码是提升可靠性的关键。预计算指标（Z-score、RoC、归一化MACD）后再喂给LLM，比让LLM自己算更准确、可解释。

2. **分层架构的真正价值**: 不是"多Agent更准"，而是"分层让每层的职责清晰"。底层专注信号提取（噪声过滤），中层专注校准对齐（语境判断），顶层专注综合决策（权重分配）。

3. **归一化的战略意义**: 任何跨标的策略都必须考虑归一化。普通MACD无法比较不同价格的股票，而归一化MACD（除以收盘价）让所有股票在同一尺度上可比。

4. **语义一致性的工程启示**: 多Agent系统的"黑箱"问题可以通过强制逻辑链条可追溯来解决。即使单Agent系统，也可以要求输出"分析理由"并建立"理由模板"。

5. **A股应用路径**: 当前Stock Platform可以先引入"分层函数"思想（extract_signals → calibrate_signals → make_decision），无需立即做多Agent。

#### 信息差价值
- **国外热点**: 多智能体LLM交易系统是2025-2026量化研究热点，arXiv q-fin相关论文激增
- **国内讨论**: 国内量化圈讨论较少，多数团队仍聚焦传统因子挖掘
- **可应用性**: **高** - 细粒度任务设计和归一化指标可直接应用于现有Stock Platform

#### 下一步行动
- [ ] 本周: 在Stock Platform中实现归一化MACD和Bollinger Z-score计算模块
- [ ] 下周: 重构策略函数为分层结构（信号提取→校准→决策）
- [ ] 本月: 设计"理由模板"，强制策略输出包含关键术语的分析理由

---

## 2026-03-09 学习记录

### 📚 今日学习
**主题**: Arxiv q-fin访问问题解决 + ai-hedge-fund项目深度分析
**来源**: GitHub + 已有知识整合
**学习时长**: 15分钟

---

### 🎯 学习状态

**Arxiv访问情况**: ⚠️ 需配置API Key
- 当前Arxiv RSS访问需要API认证
- 已记录待办：配置Arxiv API访问
- 备选方案：使用已下载的论文库+GitHub Trending补充

---

### 💡 今日核心洞察

**1. ai-hedge-fund项目量化维度分析**

从量化分析师视角拆解该项目的创新点：

**多Agent信号融合模型**:
```
最终信号 = Σ(Agent_i信号 × Agent_i权重 × 置信度_i)

其中:
- Agent_i信号 ∈ {-1, 0, 1} (做空/观望/做多)
- Agent_i权重 = f(历史准确率, 当前市场环境)
- 置信度_i = Agent对自身判断的确信程度
```

**2. 分层架构的量化意义**

| 层级 | 量化功能 | 数学表达 |
|------|----------|----------|
| 信号提取 | 技术指标计算 | Z-score, RoC, nMACD |
| 校准对齐 | 语境自适应 | 权重调整函数 w(t) |
| 决策综合 | 信号聚合 | 加权平均/投票机制 |
| 风险管理 | 仓位控制 | Kelly公式变种 |

**3. 归一化指标的战略价值**

**问题**: 传统MACD无法比较不同价格股票
- A股: 茅台(1500元) MACD = 5
- A股: 某小票(10元) MACD = 0.5
- 无法直接比较动量强弱

**解决方案**: 归一化MACD = MACD / Close
- 茅台: nMACD = 5/1500 = 0.0033 (0.33%)
- 小票: nMACD = 0.5/10 = 0.05 (5%)
- 小票动量实际更强

**A股应用场景**:
- 全市场动量排序（跨价格可比）
- 板块内相对强度比较
- 配对交易中价差标准化

---

### 📊 信息差价值评估

**GitHub项目信息**:
- **国外热度**: ⭐⭐⭐⭐⭐ 极高（11K+ stars）
- **国内讨论度**: ⭐⭐⭐ 低（国内量化圈较少讨论多Agent架构）
- **可复刻性**: ⭐⭐⭐⭐⭐ 极高（开源Python代码）
- **A股适用性**: ⭐⭐⭐⭐ 高（架构通用，需适配A股数据）

**技术栈信息**:
- **LangGraph**: 状态机工作流编排（新兴框架）
- **Financial Datasets API**: 美股数据API（可对标Tushare/AkShare）

---

### 🎯 A股应用路径

**立即可行**:
1. 实现归一化技术指标函数
   ```python
   def normalized_macd(close, fast=12, slow=26, signal=9):
       macd_line, signal_line, _ = talib.MACD(close, fast, slow, signal)
       return macd_line / close  # 归一化
   ```

2. 设计多因子加权框架
   ```python
   def weighted_signal(signals, weights, confidences):
       """多信号加权融合"""
       return np.average(signals, weights=weights*confidences)
   ```

**需进一步研究**:
- [ ] A股数据接入（Tushare Pro API）
- [ ] 回测框架选择（Backtrader vs. Zipline vs. 自研）
- [ ] 多Agent辩论机制设计

---

### 🔖 相关资源
- GitHub: https://github.com/virattt/ai-hedge-fund
- 论文: arXiv:2602.23330 - Multi-Agent LLM Trading System
- 工具: LangGraph文档、Tushare Pro API

---

### 📋 待办事项
- [ ] 配置Arxiv API Key恢复每日论文追踪
- [ ] 实现归一化MACD/Bollinger Z-score模块
- [ ] 设计A股多Agent信号融合原型

---

---

## 2026-03-11 学习记录

### 📚 今日学习
**主题**: A股多Agent量化交易框架整合
**来源**: 现有知识深化（Arxiv知识库整合）
**基础**: arXiv:2602.23330 + arXiv:2603.03671 + 均值回归理论
**学习时长**: 20分钟

---

### 🎯 核心主题
**三大策略融合：多Agent信号融合 + 超跌反弹 + 策略拥挤度监控**

基于前几日的学习，今天整合三个独立策略，构建完整的A股量化交易框架。

---

### 💡 关键洞察

**1. 多Agent信号融合回顾**

```
最终信号 = Σ(Agent_i信号 × Agent_i权重 × 置信度_i)

分层架构:
- Level 1: 信号提取（技术指标计算）
- Level 2: 校准对齐（市场语境适配）
- Level 3: 决策综合（权重分配）
```

**2. 超跌反弹策略要点**

- **理论基础**: 均值回归（Fama & French, 1988）+ 行为金融学
- **触发条件**: 40%跌幅 + 获利比例<10% + 反弹12.5%
- **A股适用**: 散户众多的市场环境，超跌反弹效应更明显

**3. 策略拥挤度洞察**

| 策略类型 | 拥挤时表现 | A股应用 |
|----------|------------|---------|
| 基本面策略 | 收益下降 | 需监控PE/PB因子拥挤度 |
| 技术策略 | 收益上升 | A股散户多，趋势策略容量更大 |

**4. 归一化指标战略价值**

解决跨价格比较问题：
```python
# 归一化MACD = MACD / Close
茅台: nMACD = 5/1500 = 0.0033
小票: nMACD = 0.5/10 = 0.05
# 小票动量实际更强
```

---

### 🔧 整合框架结构

```
A股多Agent量化框架
│
├─ 信号层
│  ├─ 技术Agent: 归一化MACD, Bollinger Z-score
│  ├─ 基本面Agent: PE/PB/ROE分析
│  ├─ 宏观Agent: VIX, 市场情绪
│  └─ 超跌Agent: 回撤检测, 反弹信号
│
├─ 校准层
│  ├─ 策略拥挤度调整
│  ├─ 市场环境适配（趋势/震荡）
│  └─ 权重动态调整
│
└─ 决策层
   ├─ 信号融合
   ├─ 仓位控制
   └─ 风险管理
```

---

### 🧠 A股特殊考虑

1. **散户效应**: 情绪驱动明显，技术策略更有效
2. **涨跌停限制**: 需考虑流动性突变
3. **T+1制度**: 不能日内回转，持仓隔夜风险
4. **动态阈值**: 根据市场状态（恐慌/正常/贪婪）调整参数

---

### 📊 信息差价值评估
- **论文来源**: Arxiv q-fin (国际前沿)
- **国内应用**: ⭐⭐⭐⭐ 高（A股特色适配）
- **可复刻性**: ⭐⭐⭐⭐⭐ 极高（Python代码已整理）
- **信息差**: 多策略融合框架在国内量化圈较少公开讨论

---

### 🎯 可应用性路径

**短期（本周）**:
- [ ] 实现归一化MACD/Bollinger Z-score函数
- [ ] 编写多Agent信号融合代码
- [ ] 测试超跌反弹检测逻辑

**中期（本月）**:
- [ ] 接入Tushare/AkShare数据
- [ ] 构建完整回测框架
- [ ] 策略拥挤度监控面板

---

### 🔖 相关资源
- 论文: arXiv:2602.23330, arXiv:2603.03671
- 技能文件: `skills/analysis/a-share-multi-agent-framework.md`

---

### 📋 技能内化
- **技能文件**: `skills/analysis/a-share-multi-agent-framework.md`
- **核心公式**: 归一化MACD, Bollinger Z-score, 多信号融合
- **代码实现**: Python函数完整可运行

---

---

## 2026-03-12 学习记录

### 📚 今日学习
**主题**: Fractional Kelly仓位管理
**来源**: 量化金融研究 (Kelly Criterion + A股适配)
**链接**: https://mcginniscommawill.com/posts/2026-01-16-fractional-kelly/
**学习时长**: 20分钟

---

### 🎯 核心主题
**Kelly公式与Fractional Kelly仓位管理策略**

最优仓位公式: f* = (bp - q) / b
专业实践使用10-25%的Kelly比例控制风险。

---

### 💡 关键洞察

**1. Kelly公式核心**
```
f* = (bp - q) / b

f* = 最优仓位比例
b = 平均盈利/平均亏损 (赔率)
p = 胜率
q = 败率 = 1-p
```

**2. Fractional Kelly实践**
| 比例 | 风格 | 适用场景 |
|------|------|----------|
| 10% | 保守 | 严格回撤控制 |
| 25% | 平衡 | 标准专业做法 |
| 50% | 激进 | 高风险承受 |

**3. A股特殊适配**
- T+1限制惩罚系数: 0.95
- 涨跌停惩罚系数: 0.90
- 市场环境调整: 牛市1.2x / 正常1.0x / 熊市0.7x

**4. 连续分布Kelly**
公式: f* = (μ - r) / σ²
适用于连续收益分布场景。

---

### 🔧 代码实现

```python
class FractionalKellySizer:
    def calculate_kelly(self, win_rate, avg_win, avg_loss):
        b = avg_win / avg_loss
        kelly = (b * win_rate - (1 - win_rate)) / b
        return kelly * self.fraction  # 0.25
```

---

### 📊 信息差价值
- **专业标准**: 量化投资核心技能
- **A股适用**: ⭐⭐⭐⭐ 高（已适配T+1/涨跌停）
- **可复刻性**: ⭐⭐⭐⭐⭐ 极高（Python完整实现）

---

### 🎯 可应用性路径

**短期（本周）**:
- [ ] 实现Fractional Kelly计算模块
- [ ] 接入Stock Platform仓位管理

**中期（本月）**:
- [ ] 多策略仓位优化
- [ ] 回测验证效果

---

### 🔖 相关资源
- 技能文件: `skills/analysis/fractional-kelly-position-sizing.md`

---

### 📋 技能内化
- **技能文件**: `skills/analysis/fractional-kelly-position-sizing.md`
- **触发条件**: 计算最优仓位/设计资金管理策略
- **核心公式**: Kelly公式 + Fractional系数 + A股调整

---

---

## 2026-03-13 学习记录

### 📚 今日学习
**来源**: Quantpedia + ACM
**主题**: ML vs Trend分歧交易 + 危机对冲整合
**链接**: https://quantpedia.com/can-we-profit-from-disagreements-between-machine-learning-and-trend-following-models/
**学习时长**: 20分钟

---

### 🎯 核心主题
**模型分歧即信号：分歧越大，交易机会越大**

当深度学习预测与传统趋势指标出现分歧时，分歧程度本身就是可交易的alpha源。

---

### 💡 关键洞察

**1. 分歧公式**
```
Signal_Strength = |ML_Prediction - Trend_Prediction|
Position_Size = Base_Size × (1 + Signal_Strength × k)
```

**2. 危机对冲稀缺性**
- Quantpedia数据库中仅12%策略是真正的危机对冲
- 最佳危机对冲：时间序列动量效应
- 危机期间表现：质量因子+2.1%，动量因子+1.6%

**3. 央行公告前漂移**
| 央行 | 入场时机 | 夏普比率 |
|------|----------|----------|
| FOMC | D-1 | >1.0 |
| ECB | D-1 | >1.0 |
| BoE | D-2 | >1.0 |

**4. 多Agent协作奖励**
```
R_i = α × Individual_Profit + (1-α) × Portfolio_Profit
最优α = 0.8 (个体为主，组合为辅)
```

---

### 🔧 可应用技术

**1. 分歧加权仓位**
- 高分歧：最小仓位
- 低分歧：满仓
- 中等分歧：动态调整

**2. 危机对冲整合**
```python
if VIX > threshold:
    Allocate_to_Crisis_Hedges = 20%
    Preferred_Hedges = [Time_Series_Momentum, Quality_Factor]
```

---

### 📊 信息差价值
- **来源**: Quantpedia (顶级量化策略库)
- **A股适用**: ⭐⭐⭐⭐ 高（模型分歧策略直接可用）
- **时效性**: ⭐⭐⭐⭐⭐ 极高（2025最新研究）

---

### 🔖 技能文件
`skills/analysis/disagreement-position-sizing.md`

---

---

## 2026-03-16 学习记录

### 📚 今日学习
**来源**: ECC Market Research Skill
**主题**: 市场研究方法论 - 研究支持决策，非研究表演
**学习时长**: 15分钟

---

### 🎯 核心主题
**生产支持决策的研究，而非研究表演 (Research Theater)**

---

### 💡 关键洞察

**1. 研究的核心原则**

| 原则 | 说明 |
|------|------|
| 每个重要声明都需要来源 | 无来源的数据不可信 |
| 优先近期数据，标注过时数据 | 时间敏感性 |
| 包含反面证据和下行案例 | 避免确认偏误 |
| 将发现转化为决策 | 而非仅总结 |
| 明确区分事实、推断和建议 | 逻辑清晰 |

**2. 常见研究模式**

**投资者/基金尽职调查**:
- 基金规模、阶段、典型投资金额
- 相关投资组合公司
- 公开投资理念和近期活动
- 匹配度评估

**竞争分析**:
- 产品现实（非营销文案）
- 融资历史（如公开）
- traction指标（如公开）
- 分销和定价线索
- 优势、劣势和定位差距

**市场规模估算**:
- 自上而下：报告或公开数据集
- 自下而上：客户获取假设的现实检验
- 明确标注每个逻辑跳跃的假设

**3. 输出格式标准**

```
1. 执行摘要
2. 关键发现
3. 影响分析
4. 风险和注意事项
5. 建议
6. 来源
```

**4. 质量门禁检查清单**

交付前确认：
- [ ] 所有数字都有来源或标注为估算
- [ ] 旧数据已标注
- [ ] 建议基于证据
- [ ] 包含风险和反方观点
- [ ] 输出使决策更容易

---

### 🧠 可应用思维模型

**1. 研究-决策链 (Research-Decision Chain)**
```
问题定义 → 信息收集 → 分析处理 → 洞察提取 → 决策建议
    ↑                                                  ↓
    └──────────────── 反馈验证 ────────────────────────┘
```

**2. 来源可信度评估矩阵**
| 来源类型 | 可信度 | 使用场景 |
|----------|--------|----------|
| 一手数据 | 最高 | 核心决策依据 |
| 权威机构 | 高 | 市场规模、行业趋势 |
| 行业报告 | 中 | 竞争格局、技术趋势 |
| 媒体文章 | 中低 | 初步了解、线索收集 |
| 社交媒体 | 低 | 情绪感知、趋势发现 |

---

### 📊 信息差价值评估
- **可应用性**: ⭐⭐⭐⭐⭐ 极高 (适用于所有研究任务)
- **时效性**: ⭐⭐⭐⭐⭐ 极高 (研究质量直接影响决策)
- **决策质量提升**: ⭐⭐⭐⭐⭐ 极高 (从"信息收集"到"决策支持")

---

### 🎯 立即行动
1. **建立研究模板** - 为常见研究类型创建标准化格式
2. **来源管理系统** - 追踪关键数据的来源和时效性
3. **质量门禁检查** - 每次研究输出前通过检查清单

---

### 🔖 相关资源
- 技能文件: `skills/everything-claude-code/.agents/skills/market-research/SKILL.md`

---

### 📋 技能内化
- **技能文件**: `skills/everything-claude-code/.agents/skills/market-research/SKILL.md`
- **触发条件**: 市场研究、竞争分析、投资决策、技术评估
- **核心输出**: 决策导向的研究报告

---

*Learning Date: 2026-03-16*

*Learning Date: 2026-03-13*

*Learning Date: 2026-03-12*

*Learning Date: 2026-03-11*

---

## 2026-03-17 学习记录

### 📚 今日学习
**来源**: GitHub
**标题/项目**: TradingAgents: Multi-Agents LLM Financial Trading Framework
**链接**: https://github.com/TauricResearch/TradingAgents
**学习时长**: 25分钟

---

### 🎯 核心主题
**多智能体LLM金融交易框架：模拟真实交易公司组织架构的AI交易系统**

---

### 💡 关键洞察（5点）

**1. 真实交易公司架构的AI映射**
该项目将真实交易公司的组织架构完整映射到AI系统：
- **分析师团队**：基本面/情绪/新闻/技术四位分析师并行工作
- **研究团队**：看涨与看跌研究员通过结构化辩论平衡风险收益
- **交易员智能体**：综合报告决定交易时机与规模
- **风控与组合经理**：评估波动率、流动性等风险因素，最终审批交易

**核心价值**：不是简单的多Agent投票，而是模拟真实金融机构的决策流程和制衡机制。

**2. LangGraph驱动的状态机工作流**
- **底层框架**: LangGraph构建，确保灵活性与模块化
- **配置区分**: "deep_think_llm"用于复杂推理，"quick_think_llm"用于快速任务
- **多模型支持**: OpenAI (GPT-5.x)、Google (Gemini 3.x)、Anthropic (Claude 4.x)、xAI (Grok 4.x)、OpenRouter、Ollama本地模型

**关键洞察**：通过区分"深度思考"和"快速思考"模型，在成本和性能之间取得平衡。

**3. 细粒度任务设计原则**
- 粗粒度指令导致LLM推理中断
- 细粒度任务（基于预计算的8周期RoC、Bollinger Z-score）显著提升夏普比率
- **关键公式**: 归一化MACD = (EMA₁₂ - EMA₂₆) / Pₜ

**工程启示**：把计算工作从LLM转移到确定性代码是提升可靠性的关键。

**4. 32.4K Stars的社区验证**
- 极高社区认可度（32.4k stars）
- 活跃Discord与GitHub社区
- 持续更新：v0.2.1 (2026-03)支持GPT-5.4、Gemini 3.1、Claude 4.6
- 配套论文：arXiv:2412.20138

**信息差价值**：国外量化圈热点，国内讨论较少，存在明显信息差。

**5. 与Stock Platform的战略契合**
该项目架构与我们的"Agent成长系统"和"Stock Platform"战略高度契合：
- 分层决策架构可直接借鉴
- 多Agent信号融合机制已验证有效
- 归一化指标设计可直接复用

---

### 🔧 技术实现/执行步骤

**1. 快速体验**
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())
_, decision = ta.propagate("NVDA", "2026-01-15")
```

**2. A股适配路径**
```python
# 分层架构映射
A股TradingAgents适配
│
├─ 分析师团队
│  ├─ 基本面分析师: PE/PB/ROE分析 (AkShare数据源)
│  ├─ 情绪分析师: 东方财富情绪指数 + 雪球热股
│  ├─ 新闻分析师: 财联社/华尔街见闻新闻情感分析
│  └─ 技术分析师: 归一化MACD + Bollinger Z-score
│
├─ 研究团队
│  ├─ 看涨研究员: 多头逻辑论证
│  └─ 看跌研究员: 空头逻辑论证
│
├─ 交易员智能体: 信号综合 + 时机选择
│
└─ 风控经理: 波动率检查 + 仓位控制 + 最终审批
```

**3. 模型配置策略**
```python
# deep_think_llm用于复杂推理
# quick_think_llm用于快速任务
CONFIG = {
    "deep_think_llm": "gpt-5.4",  # 研究员辩论、风控评估
    "quick_think_llm": "gpt-4o-mini",  # 信号提取、数据预处理
}
```

---

### 📊 信息差价值
- **国外热度**: ⭐⭐⭐⭐⭐ (32.4k stars，社区极活跃)
- **国内讨论度**: ⭐⭐ (国内量化圈讨论较少)
- **可复刻性**: ⭐⭐⭐⭐⭐ (开源Python代码，架构清晰)
- **对项目价值**: **极高** (直接契合Stock Platform + Agent成长系统战略)

---

### 🎯 可应用性路径

**短期（本周）**:
- [ ] 克隆TradingAgents仓库，深度研究架构实现
- [ ] 提取核心模块设计，适配A股数据源(AkShare/Tushare)
- [ ] 设计"deep_think_llm"和"quick_think_llm"的配置策略

**中期（本月）**:
- [ ] 实现A股版多Agent交易系统原型
- [ ] 集成归一化技术指标(MACD/Bollinger Z-score)
- [ ] 设计研究员辩论机制(看涨vs看跌)

**长期（本季度）**:
- [ ] 完整Stock Platform多Agent模块上线
- [ ] 实现风控经理自动审批流程
- [ ] 策略回测与实盘模拟

---

### 🔖 相关资源
- 项目: https://github.com/TauricResearch/TradingAgents
- 论文: arXiv:2412.20138
- 技能文件: `skills/analysis/trading-agents-framework.md`

---

### 📋 技能内化
- **技能文件**: `skills/analysis/trading-agents-framework.md`
- **触发条件**: 多Agent交易系统设计/量化策略开发
- **核心架构**: 分析师团队 → 研究团队 → 交易员 → 风控经理

---

---

## 2026-03-18 学习记录

### 📚 今日学习
**来源**: GitHub
**标题/项目**: MiroThinker - Deep Research Agent for Complex Research and Prediction
**链接**: https://github.com/MiroMindAI/MiroThinker
**学习时长**: 20分钟

---

### 🎯 核心主题
**深度研究Agent框架：针对复杂研究和预测任务的AI系统，v1.5版本专门针对金融预测优化**

---

### 💡 关键洞察（5点）

**1. 金融预测专项优化（v1.5版本）**
MiroThinker-v1.5明确针对金融预测场景进行了优化：
- 在BrowseComp-ZH基准上超越Kimi-K2-Thinking，成本更低
- 性能指标：39.2% HLE-Text, 69.8% BrowseComp, 71.5% BrowseComp-ZH, 80.8% GAIA-Val-165
- **关键发现**: 金融预测需要"长视野推理"（long-horizon reasoning）和深度多步分析

**工程启示**: 金融预测Agent需要专门优化，而非通用LLM直接应用。

**2. 交互式扩展机制（Interactive Scaling）**
- 训练Agent处理更深、更频繁的Agent-环境交互
- 支持每任务最多300次工具调用（v1.0支持600次）
- 256K上下文窗口，支持长文档和时序数据分析

**与TradingAgents对比**:
| 特性 | MiroThinker | TradingAgents |
|------|-------------|---------------|
| 定位 | 深度研究Agent | 多Agent交易框架 |
| 工具调用 | 300次/任务 | 分层架构限制 |
| 上下文 | 256K tokens | 依赖模型本身 |
| 金融优化 | v1.5专项优化 | 原生交易架构 |

**3. FutureX基准：预测未知未来**
MiroThinker团队设计了专门的**FutureX基准**，用于评估模型预测未知未来事件的能力：
- 这与金融预测的核心挑战高度契合
- 传统NLP基准测试的是知识检索，FutureX测试的是推理和预测能力
- **关键洞察**: 金融预测不是知识问答，而是基于有限信息的概率推断

**4. 工具增强推理（Tool-Augmented Reasoning）**
- 与外部工具和API的无缝集成
- 核心库`miroflow-tools`提供标准化工具接口
- Trace Collection功能：完整的Agent交互日志，包含耗时和预估完成时间

**对Stock Platform的价值**:
```python
# 可借鉴的架构模式
class FinancialResearchAgent:
    def __init__(self):
        self.tools = [MarketDataAPI, NewsAPI, FinancialReportParser]
        self.max_tool_calls = 300  # 深度研究需要更多工具调用
        self.context_window = 256000

    def predict(self, query, historical_data):
        # 1. 多源数据收集（工具调用）
        # 2. 长文档分析（财报、研报）
        # 3. 时序模式识别
        # 4. 概率预测输出
        pass
```

**5. 训练方法：SFT + DPO**
- **SFT（监督微调）**: 基础能力训练
- **DPO（直接偏好优化）**: 对齐人类偏好，提升输出质量
- 基础模型：Qwen3系列（8B/30B/235B参数）

**关键洞察**: 金融预测Agent的训练需要结合领域数据（SFT）和人类专家反馈（DPO）。

---

### 🔧 技术实现/执行步骤

**1. 快速体验**
```python
# MiroThinker架构可借鉴的模式
from miroflow_tools import ToolRegistry, TraceCollector

# 注册金融分析工具
registry = ToolRegistry()
registry.register("market_data", MarketDataTool())
registry.register("news_sentiment", NewsSentimentTool())
registry.register("financial_report", ReportParserTool())

# 启用Trace收集（用于审计和优化）
tracer = TraceCollector()
```

**2. A股研究Agent适配路径**
```python
# 基于MiroThinker思想的A股深度研究Agent
class AShareResearchAgent:
    """
    专门针对A股市场的深度研究Agent
    借鉴MiroThinker的交互式扩展和长上下文能力
    """

    def __init__(self):
        self.max_iterations = 50  # 限制研究深度，避免过度拟合
        self.tools = {
            "akshare": AkShareDataTool(),      # A股数据
            "tushare": TushareProTool(),       # 财务数据
            "eastmoney": EastMoneyTool(),      # 情绪数据
            "news": FinancialNewsTool(),       # 财联社/华尔街见闻
        }

    def deep_research(self, stock_code, research_question):
        """
        深度研究流程：
        1. 收集基础数据（价格、财务、新闻）
        2. 识别关键驱动因素
        3. 多维度交叉验证
        4. 概率化预测输出
        """
        context = {"stock": stock_code, "question": research_question}

        # Phase 1: 数据收集（多工具并行调用）
        market_data = self.tools["akshare"].get_price_data(stock_code)
        financial_data = self.tools["tushare"].get_financials(stock_code)
        sentiment = self.tools["eastmoney"].get_sentiment(stock_code)

        # Phase 2: 深度分析（迭代推理）
        for iteration in range(self.max_iterations):
            analysis = self._analyze(context)
            if analysis["confidence"] > 0.85 or iteration >= self.max_iterations - 1:
                break
            context = self._refine_context(context, analysis)

        return self._generate_prediction(context)
```

**3. 与TradingAgents的整合思路**
```python
# 将MiroThinker作为TradingAgents的"研究团队"增强
class EnhancedTradingSystem:
    """
    整合两个框架的优势：
    - TradingAgents: 成熟的多Agent交易架构
    - MiroThinker: 深度研究能力
    """

    def __init__(self):
        # TradingAgents核心架构
        self.analysts = [FundamentalAnalyst(), TechnicalAnalyst(), SentimentAnalyst()]
        self.traders = TradingAgent()
        self.risk_manager = RiskManager()

        # MiroThinker增强：深度研究模块
        self.deep_researcher = AShareResearchAgent(max_iterations=30)

    def make_decision(self, stock_code):
        # 1. 快速信号（TradingAgents模式）
        signals = [a.analyze(stock_code) for a in self.analysts]

        # 2. 深度研究（MiroThinker模式）- 用于高置信度场景
        if self._needs_deep_research(signals):
            deep_insight = self.deep_researcher.deep_research(
                stock_code,
                research_question="未来7天价格走势预测"
            )
            signals.append(deep_insight)

        # 3. 综合决策
        return self.traders.decide(signals)
```

---

### 📊 信息差价值

**GitHub项目信息**:
| 维度 | 评估 | 说明 |
|------|------|------|
| 国外热度 | ⭐⭐⭐⭐ | 新兴项目，增长迅速 |
| 国内讨论度 | ⭐⭐ | 国内量化圈尚未关注 |
| 可复刻性 | ⭐⭐⭐⭐ | 开源架构，需自研金融模块 |
| A股适用性 | ⭐⭐⭐⭐ | 架构通用，需适配A股数据源 |
| 技术深度 | ⭐⭐⭐⭐⭐ | 交互式扩展机制先进 |

**核心信息差**:
1. **交互式扩展**: 大多数Agent系统固定推理深度，MiroThinker支持动态扩展
2. **FutureX基准**: 专门针对预测任务设计的评估体系
3. **金融优化v1.5**: 明确针对金融场景的模型优化路径

---

### 🎯 可应用性路径

**短期（本周）**:
- [ ] 研究MiroThinker的交互式扩展机制实现
- [ ] 设计A股研究Agent的工具调用接口
- [ ] 实现基础的Trace Collection功能

**中期（本月）**:
- [ ] 构建A股深度研究Agent原型（30次工具调用限制）
- [ ] 设计FutureX风格的金融预测评估基准
- [ ] 整合MiroThinker思想到TradingAgents架构

**长期（本季度）**:
- [ ] 实现完整的深度研究+交易决策闭环
- [ ] 构建A股专用的预测评估基准
- [ ] 训练/微调专门的金融预测模型

---

### 🔖 相关资源
- 项目: https://github.com/MiroMindAI/MiroThinker
- 核心洞察: 交互式扩展 + 长上下文 + 工具增强推理
- 技能文件: `skills/analysis/mirothinker-deep-research.md`

---

### 📋 技能内化
- **技能文件**: `skills/analysis/mirothinker-deep-research.md`
- **触发条件**: 深度研究任务/复杂预测场景
- **核心架构**: 交互式扩展 + 多工具调用 + 长上下文推理
- **关键参数**: max_iterations=30-50, context_window=256K

---

*Learning Date: 2026-03-18*

*Learning Date: 2026-03-17*

*Learning Date: 2026-03-09*
