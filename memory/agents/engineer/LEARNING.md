# LEARNING.md - Product Engineer 学习记录

## 学习记录索引

### 已学习项目（近7天）
| 日期 | 项目名称 | 来源 | 核心洞察 |
|------|----------|------|----------|
| 2026-03-13 | Hindsight - Agent Memory | GitHub Trending | 仿生记忆系统，retain/recall/reflect |
| 2026-03-12 | Promptfoo - RAG评估框架 | GitHub 25k+ stars | RAG质量可量化评估，CI/CD集成 |
| 2026-03-11 | Microsoft MarkItDown | GitHub Trending Python | 文档转Markdown流水线，86k+ stars |
| 2026-03-10 | MiroFish - Swarm Intelligence Engine | GitHub Trending #1 | 群体智能预测范式，去中心化决策 |
| 2026-03-09 | ai-hedge-fund - 多智能体交易系统 | GitHub Trending | 分层Agent架构，信号归一化策略 |
| 2026-03-08 | Ki Editor - AST-based code editor | Hacker News | 基于AST的结构化编辑器，多光标语义操作 |
| 2026-03-05 | Security boundaries in agentic architectures | Vercel Blog | Agent安全的四层架构与隔离策略 |
| 2026-03-05 | Alibaba OpenSandbox | GitHub Trending | AI应用通用沙盒平台，支持多语言SDK |

---

### 今日学习（2026-03-05）

#### 内容1：Security boundaries in agentic architectures
- **来源**：Vercel Blog (Malte Ubl, Harpreet Arora)
- **核心洞察**：Agentic系统需要四层安全边界——Agent本身、Agent Secrets、生成代码执行、文件系统/环境。当前默认的"零边界"架构使生成的代码能直接访问所有凭据，存在严重的Prompt Injection风险。
- **信息差价值**：高
- **可应用性**：架构

#### 内容2：Alibaba OpenSandbox
- **来源**：GitHub Trending Python
- **核心洞察**：阿里巴巴开源的AI应用通用沙盒平台，提供多语言SDK（Python/Java/JS/C#/Go）、统一沙盒API、Docker/K8s运行时，专门支持Coding Agents、GUI Agents、AI代码执行等场景。
- **信息差价值**：高
- **可应用性**：工具/架构

---

## 2026-03-10 学习记录

### 📚 今日精选
**来源**: GitHub Trending Python
**项目**: [MiroFish](https://github.com/666ghj/MiroFish)
**作者**: 666ghj
**热度**: GitHub Trending #1, +2,222 stars (单日)
**主题**: Swarm Intelligence Engine - 群体智能预测引擎

---

### 🎯 核心主题
**Swarm Intelligence（群体智能）正在成为AI预测的新范式**

通过模拟自然界群体行为（鱼群、鸟群）来解决复杂预测问题。与单一LLM Agent不同，Swarm Intelligence强调多Agent协作、去中心化决策，每个Agent只有局部信息但能涌现全局智能。

---

### 💡 关键洞察

1. **群体智能 vs 多Agent角色分工**
   - ai-hedge-fund: 角色分工（分析师/风险管理员/PM）
   - MiroFish: 去中心化群体决策（类似鱼群、鸟群的行为模式）
   - **本质区别**: 前者是层级架构，后者是涌现架构

2. **"Predicting Anything"的野心**
   - 项目定位极具野心，覆盖股票预测、天气、趋势分析等多个领域
   - 同作者的BettaFish（多Agent舆情分析）也在trending，显示多Agent系统正在形成生态

3. **与ai-hedge-fund的互补性**
   - ai-hedge-fund: 金融领域的分层决策
   - MiroFish: 通用预测引擎的群体智能范式
   - **Stock Platform应用**: 可将两者结合，分层决策+群体预测

---

### 🔧 技术亮点

| 特性 | 说明 |
|------|------|
| Swarm协调机制 | 粒子群优化（PSO）或类似算法 |
| 去中心化 | 每个Agent独立决策，无中心控制器 |
| 局部信息 | Agent只基于局部信息行动，全局智能涌现 |

---

### 🧠 可应用技术

**Swarm Prediction Engine（群体预测引擎）**
- **触发**: 多维度预测任务
- **步骤**: 定义目标 → 创建Specialized Agents → 独立预测 → Swarm聚合 → 输出结果
- **应用**: Stock Platform预测模块、多因子信号融合

---

### 📊 信息差价值评估
- **国外热度**: ⭐⭐⭐⭐⭐ 极高（GitHub #1，单日+2K星）
- **国内讨论度**: ⭐⭐ 低（刚出现，中文社区尚未大规模讨论）
- **工程可复刻性**: ⭐⭐⭐⭐⭐ 极高（开源Python）
- **创新价值**: ⭐⭐⭐⭐ 高（群体智能范式不同于传统多Agent）

---

### 🔖 相关资源
- GitHub: https://github.com/666ghj/MiroFish
- 对比项目: https://github.com/virattt/ai-hedge-fund

---

### 备选发现（值得关注）
| 项目 | 链接 | 描述 | 价值点 |
|------|------|------|--------|
| Terminal Use | - | Vercel for filesystem-based agents | 文件系统Agent托管 |
| claude-skills | - | 169 production-ready skills | 技能设计模式参考 |
| hermes-agent | - | The agent that grows with you | NousResearch出品，自我成长机制 |

---

## 2026-03-08 学习记录

### 内容：Ki Editor - 基于AST的结构化代码编辑器

**Source**: https://ki-editor.org/ (Hacker News Top, 347 points)
**Focus**: Editor / Developer Experience

**核心洞察**：
1. **范式突破**：Ki Editor直接操作AST（抽象语法树）而非纯文本，将代码编辑从"字符操作"升级为"语义操作"
2. **多光标+选择模式**：通过"Selection Modes"统一词/行/语法节点级别的导航，支持并行操作多个语法节点
3. **重构安全性**：AST级别的操作天然保证语法有效性，避免传统文本重构引入的语法错误
4. **意图驱动**：减少"键盘/鼠标体操"，让开发者直接表达操作意图（如"提取函数"而非"剪切粘贴"）

**信息差分析**：
- **国外热度**：高（Hacker News Top，347 points）
- **国内使用情况**：几乎无人知晓，属于前沿概念
- **工程价值**：对代码重构、IDE插件开发、AI代码生成有启发意义

**可应用性评估**：
- **短期**：研究其Selection Modes设计，优化我们的代码编辑体验
- **中期**：借鉴AST操作理念，改进AI代码生成后的自动重构能力
- **长期**：探索将结构化编辑集成到Agent代码生成工作流中

---

## 关键学习要点

### Agent安全架构最佳实践

**四 Actor 模型**：
1. **Agent Harness**: 可信任的标准SDLC组件
2. **Agent Secrets**: API Token、数据库凭据等，需严格保护
3. **Generated Code Execution**: 不可信的wildcard，需要隔离
4. **Filesystem/Environment**: 运行环境

**三层安全架构演进**：
1. **零边界（当前默认）**：所有组件共享安全上下文，风险最高
2. **Secret Injection Proxy**: 代理层注入凭据，防止泄露但无法阻止运行时滥用
3. **独立计算分离**: Agent Harness与生成代码在独立VM/沙盒中运行，最优安全

### Alibaba OpenSandbox 特性
- 多语言SDK支持
- Docker + Kubernetes高性能运行时
- 内置命令执行、文件系统、代码解释器
- Ingress Gateway + Egress Controls网络策略
- 适用场景：Coding Agents、GUI Agents、Agent Evaluation、RL Training

---

## 可应用技术

### 立即可以应用：
- [ ] 评估OpenSandbox作为我们的Agent执行环境
- [ ] 设计Agent Secrets管理机制，避免直接暴露给Agent
- [ ] 研究Secret Injection Proxy模式

### 需要进一步研究：
- [ ] OpenSandbox与现有K8s基础设施集成方案
- [ ] 与Claude Code/Cursor沙盒模式的对比
- [ ] Ki Editor的Selection Modes设计原理及实现
- [ ] AST操作在AI代码生成后的自动重构应用

---

## 2026-03-09 学习记录

### 📚 今日精选
**来源**: GitHub Trending
**项目**: [ai-hedge-fund](https://github.com/virattt/ai-hedge-fund)
**作者**: virattt
**趋势**: 11,000+ stars, 持续高热
**学习时长**: 20分钟

---

### 🎯 核心主题
**多智能体AI对冲基金系统：从概念到开源落地**

这是一个由多个AI Agent组成的交易决策系统，模拟真实对冲基金的工作流程。每个Agent代表不同的投资流派（本杰明·格雷厄姆、巴菲特、比尔·阿克曼等），最终由风险管理和投资组合管理Agent整合决策。

---

### 💡 关键洞察

**1. 分层Agent架构 (Layered Agent Architecture)**

```
┌─────────────────────────────────────────┐
│  Portfolio Management Agent             │
│  - 最终投资决策                         │
└──────────────┬──────────────────────────┘
               │ 综合各Agent信号
┌──────────────▼──────────────────────────┐
│  Risk Management Agent                  │
│  - 风险评估、仓位控制                   │
└──────────────┬──────────────────────────┘
               │ 风险过滤
┌──────────────▼──────────────────────────┐
│  多Agent信号生成层                      │
│  - 价值投资者Agent (Graham/Buffett)     │
│  - 激进投资者Agent (Ackman)             │
│  - 量化策略Agent                        │
└─────────────────────────────────────────┘
```

**2. 每个Agent的细粒度任务设计**

- **信号提取Agent**: 负责技术指标预计算（Z-score、RoC、归一化MACD）
- **校准对齐Agent**: 基于市场语境调整信号权重
- **决策综合Agent**: 多源信号加权融合

**关键学习点**：把计算工作从LLM转移到确定性代码是提升可靠性的关键。

**3. 信号归一化的战略意义**

- 普通MACD无法跨标的比较（不同价格基数）
- 归一化MACD（除以收盘价）让所有股票在同一尺度可比
- 这是跨标的量化策略必须考虑的设计

---

### 🔧 技术栈分析

| 组件 | 技术选择 | 启示 |
|------|----------|------|
| LLM | GPT-4/Claude | 不需要自研模型，善用API |
| 数据 | Yahoo Finance + Financial Datasets API | 免费+付费数据源结合 |
| 工作流 | LangGraph (State Machine) | 复杂Agent编排需要状态管理 |
| 输出 | JSON结构化决策 | 便于程序化执行和回溯 |

---

### 🧠 可应用技术

**1. 分层函数设计**
```python
# 分层架构模式
def extract_signals(market_data):      # 信号提取
    return normalized_indicators

def calibrate_signals(signals, context):  # 校准对齐
    return adjusted_weights

def make_decision(calibrated_signals):    # 决策综合
    return final_action
```

**2. 归一化指标实现**
- 归一化MACD = MACD / Close_Price
- Bollinger Z-score = (Price - MA) / Std
- 所有指标在同一尺度上可比

**3. 理由模板强制输出**
每个Agent必须输出包含以下要素的分析理由：
- 信号类型（趋势/均值回归/动量）
- 置信度评分（0-100）
- 关键数据支撑
- 风险因素

---

### 📊 信息差价值评估
- **国外热度**: ⭐⭐⭐⭐⭐ 极高（11K+ stars，持续上趋势榜）
- **国内讨论度**: ⭐⭐⭐ 低（类似开源项目在国内少见讨论）
- **工程可复刻性**: ⭐⭐⭐⭐⭐ 极高（Python代码清晰，依赖明确）
- **创新价值**: ⭐⭐⭐⭐ 高（将多Agent架构应用于量化交易，思路可迁移）

---

### 🎯 可应用性路径

**短期（本周）**:
- [ ] 研究项目代码结构，理解LangGraph状态机设计
- [ ] 提取归一化MACD和Bollinger Z-score实现
- [ ] 设计"理由模板"格式，强制策略输出结构化理由

**中期（本月）**:
- [ ] 在Stock Platform中实现分层策略函数
- [ ] 测试多Agent信号融合效果
- [ ] 建立策略回测框架

**长期（本季度）**:
- [ ] 探索自定义Agent角色（A股特色因子）
- [ ] 实现Agent间的辩论机制（多空对抗）
- [ ] 研究如何将此架构扩展到其他决策场景

---

### 🔖 相关资源
- GitHub: https://github.com/virattt/ai-hedge-fund
- LangGraph文档: https://langchain-ai.github.io/langgraph/
- 论文: arXiv:2602.23330 - Multi-Agent LLM Trading System

---

---

## 2026-03-11 学习记录

### 📚 今日精选
**来源**: GitHub Trending Python
**项目**: [Microsoft MarkItDown](https://github.com/microsoft/markitdown)
**作者**: Microsoft
**热度**: 86,000+ stars, Python分类趋势第一
**学习时长**: 15分钟

---

### 🎯 核心主题
**文档智能预处理：非结构化文档到结构化Markdown的流水线**

MarkItDown是微软开源的文档转换工具，支持PDF、Word、Excel、PowerPoint、图片、音频、HTML等多种格式转换为Markdown。特别适用于RAG（检索增强生成）系统的文档预处理流程。

---

### 💡 关键洞察

**1. RAG流程中的文档预处理痛点**

传统RAG系统面临的挑战：
- PDF/Word等非结构化文档难以直接切片
- 文档结构（标题、表格、列表）丢失
- 图片中的文字信息无法提取
- 格式混乱影响检索质量

**MarkItDown解决方案**:
- 保留文档结构层次（转换为Markdown标题）
- 表格转为Markdown表格格式
- OCR提取图片文字（可选）
- 统一输出格式便于后续处理

**2. 多格式支持能力**

| 格式 | 用途场景 |
|------|----------|
| PDF | 报告、论文、电子书 |
| Word/Excel/PPT | 办公文档 |
| 图片 | 截图、扫描件（需OCR） |
| 音频 | 会议录音转文字 |
| HTML | 网页存档 |

**3. 工程集成友好**

```python
# Python API使用
from markitdown import MarkItDown
md = MarkItDown()
result = md.convert("document.pdf")
print(result.text_content)

# 批量处理流水线
def batch_convert(input_dir, output_dir):
    # 批量转换 + 分块 + 元数据提取
    pass
```

---

### 🔧 技术特性

| 特性 | 说明 |
|------|------|
| 多格式支持 | PDF/DOCX/XLSX/PPTX/HTML/PNG/JPG/MP3等 |
| OCR集成 | 可选OCR提取图片文字 |
| 结构保留 | 标题、列表、表格转换为Markdown格式 |
| CLI支持 | 命令行直接转换 |

---

### 🧠 可应用技术

**1. RAG文档预处理流水线**
```python
# 文档 → Markdown → 分块 → 向量存储
def rag_pipeline(file_path):
    # 1. MarkItDown转换
    # 2. 文本分块（按标题/段落）
    # 3. 元数据提取
    # 4. 向量存储
    pass
```

**2. 知识库构建**
- 批量处理企业文档
- 统一格式便于检索
- 支持图片文字提取

---

### 📊 信息差价值评估
- **国外热度**: ⭐⭐⭐⭐⭐ 极高（微软官方，86K+ stars）
- **国内讨论度**: ⭐⭐⭐ 中（技术圈开始讨论）
- **工程可复刻性**: ⭐⭐⭐⭐⭐ 极高（pip install即可用）
- **创新价值**: ⭐⭐⭐⭐ 高（文档预处理的标准化方案）

---

### 🎯 可应用性路径

**短期（本周）**:
- [ ] 安装测试MarkItDown
- [ ] 测试PDF/Word转换效果
- [ ] 评估OCR功能准确性

**中期（本月）**:
- [ ] 集成到Stock Platform文档处理流程
- [ ] 批量处理研报/财报PDF
- [ ] 构建知识库RAG pipeline

---

### 🔖 相关资源
- GitHub: https://github.com/microsoft/markitdown
- 技能文件: `skills/coding/markitdown-document-pipeline.md`

---

### 📋 技能内化
- **技能文件**: `skills/coding/markitdown-document-pipeline.md`
- **触发条件**: RAG文档预处理、批量文档转换
- **核心代码**: Python API + 批量处理函数

---

---

## 2026-03-12 学习记录

### 📚 今日学习
**来源**: GitHub Trending (Promptfoo)
**项目**: [Promptfoo](https://github.com/promptfoo/promptfoo)
**主题**: RAG评估与LLM测试框架
**学习时长**: 20分钟

---

### 🎯 核心主题
**RAG系统可量化评估：从主观感受走向数据驱动**

Promptfoo是开源LLM测试框架，提供RAG专项测试套件，支持CI/CD集成。25k+ stars，被127家财富500强企业采用。

---

### 💡 关键洞察

**1. RAG评估三大支柱**
| 维度 | 指标 | 阈值 |
|------|------|------|
| Context Faithfulness | 事实一致性 | >0.85 |
| Answer Relevance | 答案相关性 | >0.80 |
| Retrieval Quality | 检索质量 | >0.75 |

**2. YAML配置驱动**
```yaml
prompts:
  - "基于以下上下文：{{context}}\n问题：{{question}}"
providers:
  - openai:gpt-4
tests:
  - vars:
      question: "苹果Q4营收？"
    assert:
      - type: context-faithfulness
        threshold: 0.9
```

**3. CI/CD集成**
GitHub Actions自动化评估，设置阈值门禁。

**4. 自定义指标**
支持金融领域精确数字匹配等自定义scorer。

---

### 🔧 技术栈
- Node.js CLI + Python SDK
- 支持OpenAI/Anthropic/Azure等多provider
- 可视化报告输出

---

### 📊 信息差价值
- **国外热度**: ⭐⭐⭐⭐⭐ (25k+ stars)
- **国内讨论度**: ⭐⭐⭐ (技术圈开始关注)
- **工程价值**: ⭐⭐⭐⭐⭐ (RAG质量标准化)

---

### 🎯 可应用性
**短期**: 在Stock Platform研报生成模块集成RAG评估
**中期**: 构建自动化质量监控体系

---

### 🔖 技能文件
`skills/coding/rag-evaluation-pipeline.md`

---

---

## 2026-03-13 学习记录

### 📚 今日学习
**来源**: GitHub Trending
**项目**: [Hindsight](https://github.com/vectorize-io/hindsight)
**主题**: Agent Memory系统 - 让Agent真正学习而非仅记忆
**学习时长**: 20分钟

---

### 🎯 核心主题
**仿生记忆架构：retain/recall/reflect三核心操作**

Hindsight是Agent记忆系统的突破，不是简单存储对话历史，而是让Agent具备真正的学习能力——通过反思生成洞察、建立记忆间的连接。

---

### 💡 关键洞察

**1. 三大核心操作**
| 操作 | 功能 | 实现 |
|------|------|------|
| **retain** | 存储并提取实体/关系/时序 | 存储时处理，建立索引 |
| **recall** | 4种策略并行检索 | 语义+关键词+图谱+时序 |
| **reflect** | 生成洞察，建立新连接 | LLM分析模式生成洞察 |

**2. 4种检索策略融合**
- 语义检索 (向量相似度)
- 关键词检索 (BM25)
- 图谱检索 (实体关联)
- 时序检索 (最近+重要性)

使用Reciprocal Rank Fusion合并，cross-encoder重排序。

**3. 记忆vs学习的区别**
| 传统记忆 | Hindsight记忆 |
|----------|---------------|
| 对话历史 | 结构化知识 |
| 相似度匹配 | 多策略融合 |
| 无学习 | 反思生成洞察 |
| 孤立记录 | 知识图谱关联 |

---

### 🔧 技术实现

```python
class AgentMemory:
    def retain(self, content):  # 存储+索引
    def recall(self, query):    # 多策略检索
    def reflect(self, query):   # 生成洞察
```

**与Stock Platform集成**: QuantAgentMemory专门存储交易信号，recall相似市场条件，reflect优化策略。

---

### 📊 信息差价值
- **国外热度**: ⭐⭐⭐⭐⭐ (GitHub快速上升)
- **国内讨论度**: ⭐⭐ (国内几乎无讨论)
- **可复刻性**: ⭐⭐⭐⭐⭐ (开源Python)

---

### 🔖 技能文件
`skills/coding/agent-memory-system.md`

---

*Learning Date: 2026-03-13*

*Learning Date: 2026-03-12*

*Learning Date: 2026-03-11*

*Learning Date: 2026-03-09*
