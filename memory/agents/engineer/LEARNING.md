# LEARNING.md - Product Engineer 学习记录

## 学习记录索引

### 已学习项目（近7天）
| 日期 | 项目名称 | 来源 | 核心洞察 |
|------|----------|------|----------|
| 2026-03-27 | Mastra Observational Memory | GitHub Trending TS | 22K+ stars、观测记忆系统、4-10x成本削减、SOTA基准94.87% |
| 2026-03-26 | VoltAgent - TypeScript AI Agent框架 | GitHub Trending TS | 7K+ stars、端到端Agent工程平台、VoltOps可观测性、工作流引擎 |
| 2026-03-25 | Browser Use - AI浏览器自动化 | GitHub Trending Python #1 | 81K+ stars、LLM驱动浏览器控制、结构化输出、Session持久化 |
| 2026-03-23 | Agentic AI Factor Investing | arXiv:2603.14288 | 闭环验证框架、经济理论约束、自进化因子库、Sharpe 3.11 |
| 2026-03-21 | OpenCode - 开源AI编码Agent | Hacker News #1 + GitHub Trending TS #1 | 多模型统一接口、隐私优先架构、LSP自动加载 |
| 2026-03-20 | Open SWE - LangChain异步编码Agent | GitHub Trending Python | 企业级异步Agent、子Agent+中间件架构、精选工具哲学 |
| 2026-03-20 | Microsoft Qlib - AI量化平台 | GitHub Trending | 三层架构、RD-Agent自动因子、A股原生支持 |
| 2026-03-19 | learn-claude-code - Agent Harness | GitHub Trending TS #1 | Harness公式，12阶段架构，Worktree隔离 |
| 2026-03-18 | GitNexus - Zero-Server Code Intelligence | GitHub Trending TS #1 | 客户端知识图谱，Graph RAG Agent，MCP Tools |
| 2026-03-17 | TradingAgents - Multi-Agent Trading | GitHub Trending Python | 多空辩论机制，六层Agent架构，双模型策略 |
| 2026-03-13 | Hindsight - Agent Memory | GitHub Trending | 仿生记忆系统，retain/recall/reflect |
| 2026-03-12 | Promptfoo - RAG评估框架 | GitHub 25k+ stars | RAG质量可量化评估，CI/CD集成 |
| 2026-03-11 | Microsoft MarkItDown | GitHub Trending Python | 文档转Markdown流水线，86k+ stars |
| 2026-03-10 | MiroFish - Swarm Intelligence Engine | GitHub Trending #1 | 群体智能预测范式，去中心化决策 |
| 2026-03-09 | ai-hedge-fund - 多智能体交易系统 | GitHub Trending | 分层Agent架构，信号归一化策略 |
| 2026-03-08 | Ki Editor - AST-based code editor | Hacker News | 基于AST的结构化编辑器，多光标语义操作 |
| 2026-03-05 | Security boundaries in agentic architectures | Vercel Blog | Agent安全的四层架构与隔离策略 |
| 2026-03-05 | Alibaba OpenSandbox | GitHub Trending | AI应用通用沙盒平台，支持多语言SDK |

---

## 2026-03-27 学习记录

### 📚 今日学习
**来源**: GitHub Trending TypeScript + Mastra官方博客
**标题/项目**: Mastra Observational Memory - 观测记忆系统
**链接**: https://github.com/mastra-ai/mastra
**文档**: https://mastra.ai/docs/memory/observational-memory
**学习时长**: 30分钟

---

### 🎯 核心主题
**观测记忆系统：从RAG检索到压缩记忆的范式转变，实现4-10倍成本削减与SOTA性能**

Mastra是一个22K+ stars的TypeScript-first AI框架，由Gatsby团队创建。其Observational Memory（OM）系统代表了Agent记忆架构的重大突破——通过双Agent后台压缩机制，在LongMemEval基准上达到94.87%的SOTA成绩，同时实现4-10倍的token成本削减。

---

### 💡 关键洞察（5点）

**1. 观测记忆 vs RAG：两种记忆范式的本质区别**

| 维度 | 传统RAG | Mastra Observational Memory |
|------|---------|----------------------------|
| 核心机制 | 向量检索 | 文本压缩 |
| 架构依赖 | 向量数据库 | 纯文本，无外部依赖 |
| 检索方式 | 动态相似度搜索 | 静态前缀缓存 |
| Prompt缓存 | 不稳定（动态检索破坏缓存） | 稳定（append-only） |
| 成本影响 | 高（无法利用缓存折扣） | 低（4-10x成本削减） |
| 长程精度 | 80.05% (RAG基准) | **94.87% (SOTA)** |

**核心洞察**：RAG适合知识检索，OM适合对话记忆——两者互补而非替代。

---

**2. 双Agent后台架构：Observer + Reflector**

```
用户对话流
    │
    ▼
┌─────────────────────────────────────────┐
│           上下文窗口 (70K tokens)        │
│  ┌─────────────────────────────────┐   │
│  │  Observation Block (~40K)       │   │
│  │  - 压缩的历史观测 (文本格式)      │   │
│  │  - 🔴🟡🟢 优先级标记             │   │
│  │  - 日期戳 + 结构化摘要           │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  Raw Message Block (~30K)       │   │
│  │  - 原始对话消息                  │   │
│  │  - 触发阈值时压缩为观测           │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐  ┌──────────┐
│Observer│  │Reflector │
│(观察者) │  │(反思者)  │
└────────┘  └──────────┘
```

**Observer Agent**：
- 实时监听对话流
- 将原始消息压缩为带优先级标记的观测（🔴关键/🟡重要/🟢信息）
- 触发条件：原始消息达到30K tokens阈值

**Reflector Agent**：
- 定期"垃圾回收"记忆
- 重组观测、合并相关项、删除过时信息
- 触发条件：观测达到60K tokens阈值

---

**3. 成本削减机制：Prompt缓存的充分利用**

```typescript
// Mastra OM配置示例
const agent = new Agent({
  name: 'my-agent',
  model: 'openai/gpt-5-mini',
  memory: new Memory({
    options: {
      observationalMemory: {
        model: 'google/gemini-2.5-flash',
        observation: {
          messageTokens: 30_000,      // 触发观测压缩阈值
          bufferTokens: 5_000,         // 后台缓冲区间隔
          bufferActivation: 0.7,       // 保留70%后激活
        },
        reflection: {
          observationTokens: 60_000,   // 触发反思阈值
          bufferActivation: 0.5,       // 50%时开始后台反思
        },
      },
    },
  }),
})
```

**成本削减原理**：
1. **Append-only观测**：观测日志只追加不修改，前缀稳定可缓存
2. **异步缓冲**：后台处理不阻塞对话，默认启用
3. **压缩率**：文本3-6x，工具密集型工作负载5-40x
4. **缓存命中率**：稳定前缀使缓存折扣（通常50-90% off）可持续应用

---

**4. SOTA基准性能：LongMemEval 94.87%**

| 系统 | 模型 | LongMemEval分数 |
|------|------|----------------|
| **Mastra OM** | **GPT-5-mini** | **94.87%** ⭐ SOTA |
| **Mastra OM** | **Gemini-3-pro-preview** | **93.27%** |
| Hindsight | Gemini-3-pro-preview | 91.40% |
| **Mastra OM** | **GPT-4o** | **84.23%** |
| Oracle (理想配置) | GPT-4o | 82.40% |
| Supermemory | GPT-4o | 81.60% |
| **Mastra RAG** | GPT-4o | **80.05%** |

**关键发现**：
- OM在GPT-4o上（84.23%）已超越RAG的Oracle理想配置（82.40%）
- 使用轻量级模型（GPT-5-mini）即可达到SOTA，成本效益极高
- 压缩记忆在长程依赖任务上表现优于向量检索

---

**5. Mastra完整框架架构：不只是记忆**

```
Mastra TypeScript AI Framework
│
├─ Agents (智能体)
│  └─ 统一LLM抽象 + 工具访问 + 指令系统
│
├─ Workflows (工作流)
│  └─ 状态机编排 + DAG支持 + 内置状态管理
│
├─ RAG (检索增强)
│  └─ 分块 + 嵌入 + 向量搜索
│
├─ Memory (记忆系统)
│  ├─ 基础记忆：跨对话持久化
│  └─ Observational Memory：压缩观测记忆 ⭐
│
├─ Tools (工具)
│  └─ TypeScript结构化接口 + MCP支持
│
├─ MCP Support
│  └─ Model Context Protocol原生集成
│
└─ Observability (可观测性)
   └─ 内置追踪 + 日志 + 监控
```

**生产用户**：Replit (Agent 3)、Marsh McLennan (75K员工)、SoftBank、PayPal、Sanity

---

### 🔧 技术实现/执行步骤

**1. 快速安装**
```bash
npm install @mastra/core @mastra/memory
```

**2. 基础Agent配置**
```typescript
import { Agent } from '@mastra/core/agent'
import { Memory } from '@mastra/memory'

const agent = new Agent({
  name: 'research-assistant',
  instructions: 'You are a helpful research assistant.',
  model: 'openai/gpt-4o',
  memory: new Memory(),  // 启用基础记忆
})
```

**3. 启用Observational Memory**
```typescript
import { Agent } from '@mastra/core/agent'
import { Memory } from '@mastra/memory'

const agent = new Agent({
  name: 'long-context-agent',
  instructions: 'You maintain context across long conversations.',
  model: 'openai/gpt-4o',
  memory: new Memory({
    options: {
      observationalMemory: {
        model: 'google/gemini-2.5-flash',  // 轻量级模型处理压缩
        observation: {
          messageTokens: 30_000,
          bufferTokens: 5_000,
          bufferActivation: 0.7,
          blockAfter: 1.5,
        },
        reflection: {
          observationTokens: 60_000,
          bufferActivation: 0.5,
          blockAfter: 1.2,
        },
      },
    },
  }),
})
```

**4. 与Stock Platform整合方案**
```typescript
// 量化研究Agent的长程记忆系统
class QuantResearchAgent {
  constructor() {
    this.agent = new Agent({
      name: 'quant-researcher',
      instructions: `你是一个量化研究助手，需要记住：
        - 用户的研究偏好和关注领域
        - 历史因子挖掘的假设和结果
        - 策略回测的参数和结论`,
      model: 'anthropic/claude-3-7-sonnet',
      memory: new Memory({
        options: {
          observationalMemory: {
            model: 'google/gemini-2.5-flash',
            observation: {
              messageTokens: 20_000,
              bufferTokens: 3_000,
            },
            reflection: {
              observationTokens: 40_000,
            },
          },
        },
      }),
    })
  }

  async research(factorIdea: string) {
    // Agent能回忆之前的相关研究
    return await this.agent.generate(
      `研究因子假设: ${factorIdea}\n` +
      `请参考之前关于类似因子的研究结论。`
    )
  }
}
```

**5. 何时使用Observational Memory**

| ✅ 推荐使用 | ❌ 不推荐使用 |
|-----------|-------------|
| 多轮长程对话Agent | 开放式知识发现 |
| 需要维持人设/任务状态 | 合规性要求严格的场景 |
| 工具密集型Agent（浏览器、编码、研究） | 简单搜索引擎式任务 |
| 成本敏感的生产部署 | 仅需情景记忆 |

---

### 📊 信息差价值

| 维度 | 评估 | 说明 |
|------|------|------|
| **国外热度** | ⭐⭐⭐⭐⭐ | 22K+ stars，Gatsby团队背书，Replit/PayPal生产使用 |
| **国内讨论度** | ⭐⭐ | 中文社区几乎无讨论，信息差明显 |
| **技术成熟度** | ⭐⭐⭐⭐⭐ | 生产级框架，SOTA基准验证 |
| **工程可复刻性** | ⭐⭐⭐⭐⭐ | TypeScript开源，npm install即用 |
| **成本影响** | ⭐⭐⭐⭐⭐ | 4-10x成本削减，生产部署关键优势 |

**核心信息差**：
1. **压缩优于检索**：OM证明在长程记忆任务上，压缩记忆优于向量检索
2. **双Agent架构**：Observer+Reflector的后台处理模式是创新设计
3. **成本效益**：通过prompt缓存实现大幅成本削减，这是RAG无法做到的
4. **轻量模型SOTA**：使用GPT-5-mini即可达到94.87%，打破"大模型更好"的迷思

---

### 🎯 可应用性路径

**短期（本周）**:
- [ ] 安装Mastra并测试Observational Memory
- [ ] 对比OM vs RAG在量化研究场景的表现
- [ ] 测试token成本削减效果
- [ ] 评估与现有6-Agent系统的集成方案

**中期（本月）**:
- [ ] 为MuskOrchestrator Agent系统添加OM支持
- [ ] 实现量化研究Agent的长程记忆能力
- [ ] 建立记忆压缩与检索的混合策略
- [ ] 开发记忆可视化工具

**长期（本季度）**:
- [ ] 构建具备长期学习能力的Agent系统
- [ ] 实现跨会话的策略优化记忆
- [ ] 研究Observer/Reflector的自定义实现
- [ ] 探索OM在多空辩论Agent中的应用

---

### 🔖 相关资源

- **GitHub**: https://github.com/mastra-ai/mastra
- **文档**: https://mastra.ai/docs/memory/observational-memory
- **博客**: https://mastra.ai/blog/observational-memory
- **基准**: https://supergok.com/mastra-observational-memory/
- **对比项目**:
  - Hindsight (仿生记忆系统)
  - Supermemory (AI记忆API)
  - Mem0 (AI记忆层)
- **相关学习**:
  - 2026-03-26 VoltAgent (TypeScript Agent框架)
  - 2026-03-13 Hindsight (Agent记忆系统)
  - 2026-03-19 learn-claude-code (Agent Harness)

---

### 📋 技能内化

- **技能文件**: `skills/coding/mastra-observational-memory.md`
- **触发条件**: Agent长程记忆、成本优化、多轮对话系统
- **核心架构**: Observer+Reflector双Agent + 压缩记忆 + Prompt缓存优化
- **关键指标**: LongMemEval 94.87%, 4-10x成本削减

---

### 🧠 与已有知识的整合

**与Hindsight的对比**:
| 维度 | Hindsight | Mastra OM |
|------|-----------|-----------|
| 核心操作 | retain/recall/reflect | observe/reflect |
| 存储格式 | 知识图谱 | 压缩文本 |
| 检索策略 | 多策略融合 | 静态前缀 |
| 最佳场景 | 知识关联 | 对话记忆 |

**与VoltAgent的互补**:
- VoltAgent: 端到端工程平台 + 可观测性
- Mastra: 观测记忆系统 + 成本优化
- **整合价值**: 工程平台 + 高效记忆 = 生产级Agent系统

**与TradingAgents的整合**:
- TradingAgents: 多空辩论决策
- Mastra OM: 辩论历史记忆
- **整合价值**: 辩论Agent能记住历史辩论结论，优化未来决策

---

*Learning Date: 2026-03-27*

---

## 2026-03-26 学习记录

### 📚 今日学习
**来源**: GitHub Trending TypeScript
**标题/项目**: VoltAgent - End-to-End AI Agent Engineering Platform
**链接**: https://github.com/VoltAgent/voltagent
**学习时长**: 30分钟

---

### 🎯 核心主题
**端到端TypeScript AI Agent工程平台：从开发到部署运维的完整闭环**

VoltAgent是一个开源TypeScript AI Agent框架 + VoltOps可观测性控制台的端到端工程平台。7K+ stars，MIT协议，由VoltAgent团队开发。核心亮点：声明式工作流引擎、Supervisor多Agent编排、Zod类型安全工具、内置MCP支持、可恢复流式响应、VoltOps可视化运维。

---

### 💡 关键洞察（5点）

**1. 端到端工程平台架构：框架 + 可观测性控制台**

```
VoltAgent平台架构
│
├─ 开源框架层 (@voltagent/core)
│  ├─ Agent: LLM + Tools + Memory + Instructions
│  ├─ 工作流引擎: 声明式多步骤自动化
│  ├─ 多Agent系统: Supervisor协调子Agent
│  ├─ 工具注册表: Zod类型安全 + MCP支持
│  ├─ 持久化内存: 跨运行上下文保留
│  ├─ RAG检索: Knowledge Base集成
│  └─ 语音能力: TTS/STT支持
│
└─ VoltOps控制台 (Cloud/Self-Hosted)
   ├─ 实时执行追踪: Agent调用链可视化
   ├─ 性能指标: 延迟、token消耗、成功率
   ├─ 日志与追踪: 详细执行日志分析
   ├─ 内存管理: 对话历史检查
   └─ Prompt构建器: 可视化提示词工程
```

**关键学习点**：真正的生产级Agent平台必须包含可观测性，开发→部署→运维是完整闭环。

---

**2. 声明式工作流引擎：暂停/恢复/人工审批**

| 工作流操作 | 说明 | 场景 |
|------------|------|------|
| `andThen` | 顺序执行 | 标准流程 |
| `andAgent` | 委托Agent | 专业任务分发 |
| `andAll` | 并行执行 | 批量处理 |
| `andRace` | 竞速执行 | 最快响应优先 |
| `andWhen` | 条件分支 | 动态决策 |
| **暂停/恢复** | 人机协作 | 等待人工确认 |

**代码示例**:
```typescript
const expenseApprovalWorkflow = new Workflow({
  name: "expense-approval",
})
  .step("extract", async ({ input }) => { /* 解析发票 */ })
  .step("validate", async ({ context }) => { /* 验证金额 */ })
  .step("manager-approval", async () => {
    // 暂停等待人工审批
    return { status: "pending_approval" };
  })
  .step("process", async ({ context }) => { /* 执行报销 */ });
```

**工程启示**：复杂业务流程需要原生支持人机协作，而非简单的自动执行。

---

**3. Zod类型安全 + MCP生态整合**

```typescript
// Zod类型定义工具
const weatherTool = tool({
  name: "get_weather",
  description: "获取指定城市的天气",
  parameters: z.object({
    city: z.string().describe("城市名称"),
    unit: z.enum(["celsius", "fahrenheit"]).default("celsius"),
  }),
  execute: async ({ city, unit }) => {
    // 类型安全的执行
    return await fetchWeather(city, unit);
  },
});

// MCP工具集成
const mcpTools = await mcpClient.tools();
```

**关键洞察**：
- Zod全程类型约束：参数定义→验证→执行→返回，类型安全贯穿始终
- MCP(Model Context Protocol)标准化工具接口，工具生态可插拔
- 对比Python的Pydantic，TypeScript的Zod更适合前端/全栈开发者

---

**4. 多Agent编排：Supervisor模式**

```
Supervisor Agent架构
│
├─ Supervisor (协调者)
│  └─ 任务分解 → Agent选择 → 结果聚合
│
├─ Research Agent (研究)
│  └─ 信息收集、数据分析
│
├─ Code Agent (编码)
│  └─ 代码生成、重构、审查
│
└─ Review Agent (审查)
   └─ 质量检查、合规验证
```

**与单Agent对比**:
| 维度 | 单Agent | 多Agent(Supervisor) |
|------|---------|---------------------|
| 职责 | 全能但浅 | 专业且深 |
| Prompt | 冗长复杂 | 简洁聚焦 |
| 可维护 | 困难 | 模块化 |
| 扩展性 | 有限 | 水平扩展 |

**工程启示**：复杂系统应该分解为专业Agent，而非堆砌Prompt。

---

**5. 可恢复流式响应：客户端断线重连**

**问题场景**：
- 用户关闭浏览器后重新打开
- 移动端App切换到后台再回来
- 网络不稳定导致连接中断

**VoltAgent解决方案**:
```typescript
// 服务端：支持可恢复的流式响应
const stream = await agent.stream(input, {
  resumable: true,
  streamId: "unique-session-id",
});

// 客户端：断线后重新连接
const stream = await agent.resumeStream("unique-session-id");
```

**关键洞察**：生产级Agent必须考虑真实世界的网络状况，优雅处理中断和恢复。

---

### 🔧 技术实现要点

**快速开始**:
```bash
npm create voltagent-app@latest
```

**核心依赖**:
```json
{
  "@voltagent/core": "^0.x",
  "@voltagent/voice": "^0.x",  // 语音能力
  "zod": "^3.x"                // 类型安全
}
```

**部署选项**:
- Cloud: 托管VoltOps控制台
- Self-Hosted: 自有基础设施
- Serverless: Vercel/Netlify适配

---

### 📊 信息差评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 国外热度 | ⭐⭐⭐⭐ | 7K+ stars，TypeScript Agent框架中增长迅速 |
| 国内讨论度 | ⭐⭐⭐ | 中文文档完善，但社区讨论较少 |
| 可复刻性 | ⭐⭐⭐⭐⭐ | MIT协议，完整开源，文档详尽 |
| 生产就绪 | ⭐⭐⭐⭐ | 可观测性内置，但企业案例待验证 |

**对标分析**:
| 特性 | VoltAgent | Mastra | LangChain.js |
|------|-----------|--------|--------------|
| 工作流引擎 | ✅ 声明式 | ✅ 图状态机 | ⚠️ 基础链 |
| 可观测性 | ✅ VoltOps | ⚠️ OpenTelemetry | ❌ 第三方 |
| 类型安全 | ✅ Zod | ✅ Zod | ⚠️ 部分 |
| 语音能力 | ✅ 内置 | ❌ | ❌ |
| MCP支持 | ✅ 原生 | ✅ 原生 | ✅ 社区 |

---

### 🎯 行动建议

**短期（本周）**:
1. 使用`npm create voltagent-app`创建测试项目
2. 实现一个简单的工作流（如：数据提取→分析→报告生成）
3. 体验VoltOps控制台的追踪功能

**中期（本月）**:
1. 将现有MuskOrchestrator的Agent迁移到VoltAgent架构
2. 设计Supervisor多Agent编排（Planner→Engineer→Reviewer）
3. 集成MCP工具生态（如：股票数据MCP Server）

**长期（本季度）**:
1. 构建生产级Agent系统，部署VoltOps自托管版本
2. 开发自定义MCP Server（量化分析、股票数据）
3. 评估与Claude Code的集成可能性

---

### 📝 关联知识

- **相关学习**: 2026-03-21 OpenCode（多模型统一接口）、2026-03-19 learn-claude-code（Agent Harness）
- **技术栈**: TypeScript, Zod, Hono, MCP
- **应用场景**: 自动化工作流、多Agent系统、生产级AI应用

---

## 2026-03-20 学习记录

### 📚 今日学习
**来源**: GitHub Trending Python
**标题/项目**: Microsoft Qlib - AI-oriented Quant Investment Platform
**链接**: https://github.com/microsoft/qlib
**学习时长**: 25分钟

---

### 🎯 核心主题
**微软开源AI量化投资平台：从研究到生产的完整量化基础设施**

Qlib是微软开源的AI驱动量化投资平台，39K+ stars，支持从想法探索到生产部署的全流程。核心亮点：三层松耦合架构、30+ ML/DL模型、RD-Agent自动因子挖掘、强化学习订单执行、原生A股数据支持。

---

### 💡 关键洞察（5点）

**1. 三层松耦合架构设计**

```
Qlib架构
│
├─ 基础设施层 (Infrastructure)
│  ├─ DataServer: 数据存储与访问
│  ├─ Trainer: 模型训练接口
│  └─ Point-in-Time数据库: 避免未来函数
│
├─ 工作流层 (Workflow)
│  ├─ Information Extractor: 特征工程
│  ├─ Forecast Model: 预测模型
│  ├─ Decision Generator: 决策生成
│  └─ Backtester: 回测引擎
│
└─ 接口层 (Interface)
   ├─ 分析报告
   └─ 可视化
```

**关键学习点**：松耦合设计让每个组件可独立使用、替换、测试，这是工程化的核心。

---

**2. 30+ ML模型生态：从基线到前沿**

| 类别 | 模型 | 适用场景 |
|------|------|----------|
| 传统ML | LightGBM, XGBoost | 快速基线验证 |
| 深度学习 | LSTM, GRU, TCN | 时序预测 |
| 注意力机制 | Transformer, Localformer | 长程依赖捕捉 |
| 图神经网络 | GATs | 股票关系建模 |
| 强化学习 | PPO | 订单执行优化 |
| 元学习 | DDG-DA | 市场动态适应 |

**工程启示**：提供完整的模型谱系，从简单基线到复杂模型渐进式迭代。

---

**3. RD-Agent：LLM驱动的自动量化研究（2025新特性）**

- **核心能力**: 自动因子挖掘 + 模型优化
- **技术基础**: Multi-Agent框架
- **论文**: arXiv:2505.15155
- **工作流程**:
  ```
  用户需求 → 因子假设生成 → 数据验证 → 模型训练 → 结果评估 → 迭代优化
  ```

**关键洞察**：RD-Agent代表了量化研究的未来方向——从人工因子挖掘到AI自动发现。

---

**4. A股数据原生支持**

```python
# 下载A股日线数据
python scripts/get_data.py qlib_data \
    --target_dir ~/.qlib/qlib_data/cn_data \
    --region cn

# 下载1分钟高频数据
python scripts/get_data.py qlib_data \
    --target_dir ~/.qlib/qlib_data/cn_data_1min \
    --region cn \
    --interval 1min
```

**数据源**:
- Yahoo Finance (内置爬虫)
- 社区数据源: chenditc/investment_data
- 支持1d和1min粒度
- Arctic Provider后端支持订单簿数据

---

**5. 强化学习框架：订单执行优化**

- **发布**: 2022年11月
- **应用**: 连续决策建模
- **算法**: PPO等
- **价值**: 优化大单执行，降低市场冲击成本

**独特价值**：大多数量化框架忽略订单执行优化，Qlib将其作为一等公民。

---

### 🔧 技术实现/执行步骤

**1. 快速安装**
```bash
# 创建环境
conda create -n qlib python=3.12
pip install pyqlib

# 或源码安装
git clone https://github.com/microsoft/qlib
cd qlib
python setup.py install
```

**2. 运行首个工作流**
```bash
cd examples
qrun benchmarks/LightGBM/workflow_config_lightgbm_Alpha158.yaml
```

**3. A股自定义数据接入**
```python
from qlib.data import D
from qlib.config import REG_CN

# 配置A股
qlib.init(provider_uri='~/.qlib/qlib_data/cn_data', region=REG_CN)

# 获取数据
instruments = D.instruments(market='csi300')
df = D.features(instruments, ['$close', '$volume'], start_time='2020-01-01', end_time='2024-12-31')
```

**4. 自定义模型训练**
```python
from qlib.model.trainer import Trainer
from qlib.workflow import R
from qlib.contrib.model.pytorch_alstm import ALSTM

# 定义模型
model = ALSTM(d_feat=158, hidden_size=64, num_layers=2)

# 训练
with R.start(experiment_name='alstm_test'):
    trainer = Trainer(model=model, dataset=dataset)
    trainer.fit()
```

**5. 与TradingAgents/MiroThinker整合思路**
```python
# Qlib作为数据+回测基础设施
# TradingAgents作为多Agent决策层
# MiroThinker作为深度研究模块

class AShareQuantSystem:
    def __init__(self):
        # Qlib基础设施
        self.data_handler = QlibDataHandler(region='cn')
        self.backtester = QlibBacktester()

        # TradingAgents决策层
        self.analysts = [TechnicalAnalyst(), FundamentalAnalyst()]
        self.trader = TradingAgent()

        # MiroThinker深度研究
        self.deep_researcher = DeepResearchAgent()

    def run_strategy(self, strategy_config):
        # 1. Qlib数据准备
        dataset = self.data_handler.load(strategy_config.symbols)

        # 2. 多Agent决策
        signals = [a.analyze(dataset) for a in self.analysts]
        decision = self.trader.decide(signals)

        # 3. Qlib回测
        results = self.backtester.run(decision)

        return results
```

---

### 📊 信息差价值

| 维度 | 评估 | 说明 |
|------|------|------|
| **国外热度** | ⭐⭐⭐⭐⭐ | 39K+ stars，微软官方维护 |
| **国内应用** | ⭐⭐⭐⭐ | 有中文教程（扫地僧系列），但深度应用较少 |
| **技术成熟度** | ⭐⭐⭐⭐⭐ | 生产级平台，支持在线服务 |
| **A股适用性** | ⭐⭐⭐⭐⭐ | 原生支持A股数据 |
| **与项目契合度** | ⭐⭐⭐⭐⭐ | 完美契合Stock Platform需求 |

**核心信息差**:
1. **RD-Agent自动因子挖掘**: 2025年新特性，国内讨论极少
2. **强化学习订单执行**: 大多数量化框架忽略订单执行优化
3. **Point-in-Time数据库**: 避免未来函数的数据库设计

---

### 🎯 可应用性路径

**短期（本周）**:
- [ ] 安装Qlib并下载A股数据
- [ ] 运行LightGBM基线模型
- [ ] 研究RD-Agent自动因子挖掘机制

**中期（本月）**:
- [ ] 将Qlib作为Stock Platform的数据基础设施
- [ ] 实现自定义因子库
- [ ] 集成TradingAgents决策层到Qlib工作流

**长期（本季度）**:
- [ ] 基于Qlib构建完整A股量化平台
- [ ] 实现RD-Agent风格的自动因子发现
- [ ] 强化学习订单执行优化

---

### 🔖 相关资源

- **项目**: https://github.com/microsoft/qlib
- **文档**: https://qlib.readthedocs.io
- **RD-Agent论文**: arXiv:2505.15155
- **中文教程**: 扫地僧系列 (Python 3.12新版)
- **技能文件**: `skills/analysis/microsoft-qlib-platform.md`

---

### 📋 技能内化

- **技能文件**: `skills/analysis/microsoft-qlib-platform.md`
- **触发条件**: A股量化研究/模型训练/回测需求
- **核心架构**: 三层松耦合设计
- **关键模型**: LightGBM基线 → 深度学习 → 强化学习
- **2025重点**: RD-Agent自动因子挖掘

---

### 🧠 与已有知识的整合

**与TradingAgents的互补**:
- TradingAgents: 多Agent决策架构
- Qlib: 数据基础设施 + 回测引擎
- **整合价值**: 决策层 + 执行层的完整闭环

**与MiroThinker的互补**:
- MiroThinker: 深度研究能力
- Qlib: 标准化量化流程
- **整合价值**: 研究洞察 → 量化验证的快速通道

**与ai-hedge-fund的互补**:
- ai-hedge-fund: 分层Agent架构理念
- Qlib: 工程化实现框架
- **整合价值**: 理念 → 落地的工程路径

---

*Learning Date: 2026-03-21*

---

## 2026-03-23 学习记录

### 📚 今日学习
**来源**: arXiv:2603.14288 (ICLR 2026 FinAI Workshop相关)
**标题/项目**: Agentic AI Factor Investing - Beyond Prompting
**链接**: https://arxiv.org/abs/2603.14288
**作者**: Allen Yikuan Huang, Zheqi Fan
**学习时长**: 20分钟

---

### 🎯 核心主题
**Agentic AI因子投资框架：从Prompting工具到自主决策引擎的范式转变**

Agentic AI Factor Investing是一个突破性的量化研究框架，通过闭环验证系统（样本外验证+经济理论约束）实现因子投资的自动化。核心创新在于将AI从"被动执行提示词的工具"转化为"主动提出假设并验证的自主引擎"。

---

### 💡 关键洞察（5点）

**1. 闭环验证框架：四层严格实证纪律**

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

**关键学习点**：样本外验证是防止过拟合的关键，性能衰减<30%是硬性门槛。

---

**2. 经济理论约束：防止数据挖掘的防火墙**

| 理论类别 | 包含因子 | 验证权重 |
|----------|----------|----------|
| risk_premium | size, value, momentum, quality, volatility | 60% |
| behavioral | overreaction, underreaction, anchoring, herding | 60% |
| microstructure | liquidity, price_impact, information_asymmetry | 60% |
| information | earnings_surprise, analyst_coverage, insider_trading | 60% |

**A股特有理论类别**：
```python
self.a_share_theories = {
    'policy_driven': ['policy_cycle', 'regulatory_change', 'state_owned_enterprise'],
    'retail_sentiment': ['retail_herding', 'limit_up_down', 'turnover_sentiment'],
    'liquidity_premium': ['small_cap_premium', 'turnover_illiquidity'],
    'behavioral_a_share': ['earnings_gaming', 'concept_rotation']
}
```

**工程启示**：任何因子假设必须有经济理论支撑，纯数据挖掘的因子会被过滤。

---

**3. 自进化因子库：动态适应市场变化**

```python
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

**关键机制**：
- 新因子必须经过完整验证流程才能入库
- 定期回测库中因子，淘汰失效者
- 因子库动态适应市场状态变化

---

**4. 严格的样本外验证框架**

```python
class StatisticalValidator:
    """严格样本外验证框架"""

    def __init__(self, in_sample_ratio=0.6):
        self.in_sample_ratio = in_sample_ratio

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

        return performance_decay < 0.3  # 性能衰减必须<30%
```

**验证标准**：
- t-statistic > 2.0（统计显著性）
- 样本外性能衰减 < 30%（防止过拟合）
- 经济理论分数 > 0.7（理论合理性）

---

**5. 卓越的性能表现：Sharpe 3.11**

| 指标 | 数值 | 说明 |
|------|------|------|
| 年化夏普比率 | **3.11** | 多空组合，风险调整后收益极高 |
| 年化收益率 | **59.53%** | 简单线性组合信号 |
| 策略类型 | 多空组合 | 市场中性 |
| 信号构建 | 简单线性组合 | 非复杂黑盒模型 |

**关键洞察**：简单线性组合+严格验证 > 复杂模型+松散验证

---

### 🔧 技术实现/执行步骤

**1. 经济理论验证器实现**

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

**2. 与现有系统的整合方案**

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

**3. A股适配方案**

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

**4. 可立即应用的SOP**

| 步骤 | 行动 | 产出 |
|------|------|------|
| 1 | 实现经济理论验证器 | 因子假设过滤机制 |
| 2 | 建立样本外验证框架 | 过拟合防护系统 |
| 3 | 构建自进化因子库 | 动态适应市场的因子集合 |
| 4 | 集成到TradingAgents | 多Agent决策+自主因子生成 |
| 5 | 添加A股特有理论类别 | 本土化因子验证 |

---

### 📊 信息差价值

| 维度 | 评估 | 说明 |
|------|------|------|
| **国外热度** | ⭐⭐⭐⭐⭐ | arXiv论文，ICLR 2026 FinAI Workshop |
| **国内讨论度** | ⭐⭐ | 中文社区几乎无讨论，信息差明显 |
| **技术成熟度** | ⭐⭐⭐⭐⭐ | 论文提供完整实现框架 |
| **工程可复刻性** | ⭐⭐⭐⭐⭐ | Python伪代码清晰，可直接实现 |
| **与项目契合度** | ⭐⭐⭐⭐⭐ | 完美契合Stock Platform的因子研究需求 |

**核心信息差**:
1. **闭环验证框架**：样本外验证+经济理论约束的双重防护
2. **自进化机制**：因子库动态适应市场变化
3. **A股本土化**：政策驱动、散户情绪等A股特有理论类别
4. **简单优于复杂**：线性组合+严格验证 > 复杂黑盒模型

---

### 🎯 可应用性路径

**短期（本周）**:
- [ ] 实现EconomicRationaleValidator类
- [ ] 建立样本内/样本外数据划分机制
- [ ] 设计因子假设生成Prompt模板
- [ ] 研究A股特有经济理论类别

**中期（本月）**:
- [ ] 构建自进化因子库系统
- [ ] 集成到TradingAgents框架
- [ ] 实现因子失效检测机制
- [ ] 建立因子性能监控仪表盘

**长期（本季度）**:
- [ ] 实现完整的Agentic因子投资系统
- [ ] 与Qlib数据基础设施深度整合
- [ ] 开发可视化因子研究工作台
- [ ] 探索多因子组合优化策略

---

### 🔖 相关资源

- **论文**: https://arxiv.org/abs/2603.14288
- **技能文件**: `skills/analysis/agentic-ai-factor-investing.md`
- **相关学习**:
  - 2026-03-21 Microsoft Qlib（数据基础设施）
  - 2026-03-17 TradingAgents（多Agent决策）
  - 2026-03-20 BlindTrade（匿名化验证）

---

### 📋 技能内化

- **技能文件**: `skills/analysis/agentic-ai-factor-investing.md`
- **触发条件**: 因子投资研究、自动化量化研究、策略自进化需求
- **核心架构**: 四层闭环验证 + 经济理论约束 + 自进化因子库
- **关键指标**: Sharpe 3.11, 样本外性能衰减<30%, 理论分数>0.7

---

### 🧠 与已有知识的整合

**与Microsoft Qlib的互补**:
- Qlib: 数据基础设施 + 回测引擎
- Agentic AI: 自主因子生成 + 验证框架
- **整合价值**: 数据+算法+验证的完整量化研究闭环

**与TradingAgents的互补**:
- TradingAgents: 多Agent分层决策
- Agentic AI: 自主因子发现与验证
- **整合价值**: 决策层+研究层的双轮驱动

**与BlindTrade的互补**:
- BlindTrade: 匿名化验证信号真实性
- Agentic AI: 经济理论约束防止数据挖掘
- **整合价值**: 双重验证机制确保因子质量

---

*Learning Date: 2026-03-23*

---

## 2026-03-21 学习记录

### 📚 今日学习
**来源**: Hacker News #1 (230 pts / 102 comments) + GitHub Trending TypeScript #1
**标题/项目**: OpenCode - The Open Source AI Coding Agent
**链接**: https://github.com/anomalyco/opencode
**官网**: https://opencode.ai/
**学习时长**: 25分钟

---

### 🎯 核心主题
**开源AI编码Agent的新范式：多模型统一接口 + 隐私优先架构 + LSP智能加载**

OpenCode是一个全新的开源AI编码Agent，今日同时登顶Hacker News和GitHub Trending TypeScript榜单。与Claude Code不同，OpenCode主打"模型自由"——支持75+ LLM提供商（包括本地模型），同时提供GitHub Copilot和ChatGPT Plus/Pro账号集成。核心创新在于"LSP自动加载"机制，Agent能自动识别项目语言并加载对应LSP，为LLM提供精准的代码上下文。

---

### 💡 关键洞察（5点）

**1. 多模型统一接口：打破单一模型锁定**

| 特性 | OpenCode | Claude Code |
|------|----------|-------------|
| 模型选择 | 75+ 提供商任意切换 | 固定Anthropic模型 |
| 本地模型 | 完全支持 | 不支持 |
| Copilot集成 | 可直接使用GitHub Copilot账号 | 无 |
| ChatGPT集成 | 支持Plus/Pro账号 | 无 |
| 成本策略 | 免费模型 + 自有API key | 固定成本 |

**核心机制**：
```
用户请求 → 模型路由层 → 选择最优模型 → 执行 → 结果返回
                ↓
        ┌───────┴───────┐
        ↓               ↓
   本地模型(Ollama)   云端API
   Claude/GPT/Gemini  Models.dev聚合
```

**关键学习点**：多模型策略不仅降低成本，更重要的是不同任务可用不同模型——简单任务用轻量模型，复杂任务用强模型。

---

**2. LSP自动加载：为LLM提供精准上下文**

传统编码Agent的问题：
- 无法准确理解代码符号关系
- 跨文件引用解析困难
- 类型信息缺失导致错误建议

**OpenCode解决方案**：
```
项目检测 → 识别语言栈 → 自动启动LSP → 实时符号索引
    ↓
Python项目 → pyright/pylsp → 类型推断
TypeScript → tsserver → 类型定义追踪
Rust → rust-analyzer → 模块解析
```

**技术价值**：
- LSP提供结构化代码理解（而非纯文本）
- 实时类型信息辅助LLM生成正确代码
- 跨文件符号跳转支持重构建议

---

**3. 隐私优先架构：代码不上云**

| 数据类型 | OpenCode | 传统云端Agent |
|----------|----------|---------------|
| 源代码 | 本地处理 | 上传云端 |
| 上下文 | 本地存储 | 云端存储 |
| 对话历史 | 本地加密 | 服务端存储 |
| 遥测数据 | 可选关闭 | 通常强制 |

**架构设计**：
```
┌─────────────────────────────────────┐
│           用户设备                   │
│  ┌─────────┐    ┌───────────────┐  │
│  │ OpenCode │ ←→ │ 本地LSP服务器  │  │
│  │  Agent   │    │ (类型/符号)   │  │
│  └────┬────┘    └───────────────┘  │
│       │                             │
│       ↓ (仅API调用，无代码上传)      │
│  ┌─────────┐                       │
│  │ LLM API │ (Claude/GPT/本地)     │
│  └─────────┘                       │
└─────────────────────────────────────┘
```

**关键洞察**：企业级应用必须考虑代码隐私，本地化处理是重要差异化优势。

---

**4. 多会话并行：真正的多任务处理**

OpenCode支持"Start multiple agents in parallel on the same project"：

```
项目根目录
    ├── Agent A: 重构用户模块
    ├── Agent B: 编写测试用例
    ├── Agent C: 优化数据库查询
    └── Agent D: 更新API文档
```

**与Open SWE的对比**：
- Open SWE: 异步执行 + 消息队列（单Agent多任务）
- OpenCode: 多会话并行（多Agent同时工作）

**应用场景**：
- 大型项目多模块并行开发
- 代码审查与功能开发同时进行
- 技术债务修复与功能迭代并行

---

**5. Zen服务：模型质量筛选层**

OpenCode提供"Zen"服务—— curated validated models：

```
Model Marketplace (Models.dev)
    ├── 未经筛选的模型 (质量参差不齐)
    │
    └── Zen筛选层
        ├── 性能测试通过
        ├── 代码生成质量验证
        ├── 上下文窗口稳定性测试
        └── 推荐模型列表
```

**价值主张**：
- 节省用户模型选择成本
- 避免"模型抽奖"问题
- 确保生产环境稳定性

---

### 🔧 技术实现/执行步骤

**1. 快速安装**
```bash
# 官方安装脚本
curl -fsSL https://opencode.ai/install | bash

# 或选择包管理器
npm install -g opencode
bun install -g opencode
brew install opencode
```

**2. 多模型配置**
```yaml
# ~/.opencode/config.yaml
models:
  default: claude-3-7-sonnet

  providers:
    anthropic:
      api_key: ${ANTHROPIC_API_KEY}
      models:
        - claude-3-7-sonnet
        - claude-3-5-haiku

    openai:
      api_key: ${OPENAI_API_KEY}
      models:
        - gpt-4o
        - gpt-4o-mini

    ollama:
      base_url: http://localhost:11434
      models:
        - codellama:13b
        - deepseek-coder:33b

    github_copilot:
      enabled: true
      # 使用GitHub账号登录
```

**3. LSP自动检测配置**
```json
{
  "lsp": {
    "auto_detect": true,
    "servers": {
      "python": ["pyright", "pylsp"],
      "typescript": ["typescript-language-server"],
      "rust": ["rust-analyzer"],
      "go": ["gopls"]
    },
    "indexing": {
      "on_startup": true,
      "watch_files": true
    }
  }
}
```

**4. 多会话启动模式**
```bash
# 会话1: 重构任务
opencode --session refactor --task "重构用户认证模块"

# 会话2: 测试任务（并行）
opencode --session testing --task "为订单模块编写单元测试"

# 查看所有会话
opencode sessions list

# 合并会话结果
opencode sessions merge refactor testing
```

**5. 隐私模式配置**
```yaml
privacy:
  mode: strict  # strict | balanced | relaxed

  strict_mode:
    cloud_upload: false      # 禁止代码上传
    local_only: true         # 仅本地处理
    telemetry: false         # 关闭遥测

  balanced_mode:
    cloud_upload: selective  # 仅上传必要上下文
    anonymization: true      # 匿名化处理
```

---

### 📊 信息差价值

| 维度 | 评估 | 说明 |
|------|------|------|
| **国外热度** | ⭐⭐⭐⭐⭐ | Hacker News #1 (230 pts) + GitHub TS #1 (825 stars今日) |
| **国内讨论度** | ⭐⭐ | 中文社区几乎无讨论，信息差明显 |
| **技术成熟度** | ⭐⭐⭐⭐ | 已有Desktop App，但刚发布需观察 |
| **工程可复刻性** | ⭐⭐⭐⭐⭐ | 开源TypeScript，架构清晰 |
| **与项目契合度** | ⭐⭐⭐⭐⭐ | 编码Agent架构设计直接相关 |

**核心信息差**:
1. **LSP自动加载机制**：国内讨论Agent时很少涉及LSP集成，这是代码理解的关键
2. **多模型路由策略**：不同于单一模型，OpenCode展示如何优雅支持多提供商
3. **隐私优先架构**：企业级部署必须考虑的架构设计
4. **Zen筛选服务**：模型质量管控的创新思路

---

### 🎯 可应用性路径

**短期（本周）**:
- [ ] 研究OpenCode源码，理解LSP集成实现
- [ ] 分析多模型路由层设计
- [ ] 评估隐私优先架构对MuskOrchestrator的启示
- [ ] 对比OpenCode与Claude Code的架构差异

**中期（本月）**:
- [ ] 为6-Agent系统设计LSP集成能力
- [ ] 实现多模型 fallback 机制
- [ ] 设计Agent会话隔离机制
- [ ] 评估本地模型（Ollama）与云端模型混合策略

**长期（本季度）**:
- [ ] 构建模型质量评估体系（类似Zen服务）
- [ ] 实现多Agent并行工作流
- [ ] 设计企业级隐私保护方案
- [ ] 开发模型路由智能调度算法

---

### 🔖 相关资源

- **GitHub**: https://github.com/anomalyco/opencode
- **官网**: https://opencode.ai/
- **Models.dev**: https://models.dev/ (75+模型聚合)
- **对比项目**:
  - Claude Code (Anthropic闭源)
  - Open SWE (LangChain异步Agent)
  - learn-claude-code (教育性质Agent Harness)

---

### 📋 技能内化

- **技能文件**: `skills/coding/opencode-multi-model-agent.md`
- **触发条件**: 编码Agent架构设计、多模型策略、LSP集成
- **核心架构**: 多模型路由 + LSP自动加载 + 隐私优先
- **关键创新**: Zen服务模型筛选、多会话并行

---

### 🧠 与已有知识的整合

**与Open SWE的互补**:
- Open SWE: 异步执行 + 子Agent + 中间件（企业级工作流）
- OpenCode: 多模型 + LSP + 多会话（开发体验优化）
- **整合价值**: 异步工作流 + 多模型策略 + LSP上下文

**与learn-claude-code的互补**:
- learn-claude-code: Agent Harness教育（从零构建）
- OpenCode: 生产级开源实现（直接使用）
- **整合价值**: 理论+实践，学习+应用

**与GitNexus的互补**:
- GitNexus: 知识图谱 + Graph RAG（代码理解）
- OpenCode: LSP + 多模型（代码生成）
- **整合价值**: 代码理解 + 代码生成的完整闭环

---

*Learning Date: 2026-03-21*

---

## 2026-03-20 学习记录 #2

### 📚 今日学习
**来源**: GitHub Trending Python
**标题/项目**: Open SWE - Open-Source Asynchronous Coding Agent
**链接**: https://github.com/langchain-ai/open-swe
**学习时长**: 25分钟

---

### 🎯 核心主题
**企业级异步编码Agent框架：LangChain官方开源的内部编码Agent解决方案**

Open SWE是LangChain官方开源的异步编码Agent框架，旨在帮助企业构建类似Stripe、Ramp、Coinbase内部使用的编码Agent。955+ stars今日增长，核心创新是"异步+子Agent+中间件"架构，以及"精选工具而非堆砌"的哲学。

---

### 💡 关键洞察（5点）

**1. 异步Agent架构：从同步到异步的范式转变**

| 传统Agent | Open SWE异步Agent |
|-----------|-------------------|
| 即时响应 | 收到消息后👀确认，后台执行 |
| 单次交互 | 支持执行中跟进消息 |
| 同步阻塞 | 异步非阻塞，长时任务友好 |
| 无状态 | 线程级持久化沙箱 |

**核心机制**：
```python
# 中间件实现运行中消息注入
check_message_queue_before_model  # 每次模型调用前检查消息队列
```

**关键学习点**：异步架构让Agent能处理耗时任务（大型重构、复杂分析），同时保持用户交互能力。

---

**2. 子Agent + 中间件架构（Subagents + Middleware）**

```
Open SWE架构
│
├─ Deep Agent (主Agent)
│  ├─ 工具调用
│  ├─ 子Agent派生 (并行子任务)
│  └─ 中间件链
│     ├─ ToolErrorMiddleware (工具错误处理)
│     ├─ check_message_queue_before_model (消息注入)
│     └─ SafetyNetMiddleware (安全网)
│
└─ Sandbox (隔离云环境)
   ├─ Modal
   ├─ Daytona
   ├─ Runloop
   └─ LangSmith
```

**子Agent使用场景**：
- 并行分析多个文件
- 独立执行子任务（测试、lint、文档生成）
- 复杂任务的分解与委派

---

**3. 精选工具哲学（Curated, Not Accumulated）**

Open SWE只精选约15个工具，而非堆砌大量工具：

| 工具类别 | 工具示例 | 用途 |
|----------|----------|------|
| 代码操作 | read, edit, bash | 文件读写、命令执行 |
| 协作沟通 | linear_comment, slack_thread_reply | 进度更新 |
| 版本控制 | commit_and_open_pr | 自动提交PR |
| 网络请求 | http_request, fetch_url | 外部API调用 |

**设计原则**：
- 每个工具必须有明确用途
- 工具之间职责不重叠
- 通过组合而非数量解决问题

**与MCP对比**：
- MCP: 标准化工具暴露协议
- Open SWE: 精选工具集 + 深度集成

---

**4. 多平台触发机制（Multi-Platform Invocation）**

```
用户触发
    ├── Slack @openswe "重构用户模块"
    ├── Linear issue 分配给 @openswe
    └── GitHub PR comment @openswe
                ↓
        Open SWE Agent
                ↓
    ┌───────────┼───────────┐
    ↓           ↓           ↓
 即时确认    后台执行    自动PR
 (👀表情)   (沙箱运行)   (草稿PR)
```

**上下文来源**：
- `AGENTS.md` - 项目级Agent配置
- Linear issue - 任务描述
- Slack thread - 讨论上下文
- GitHub PR - 代码上下文

---

**5. 基于Deep Agents的组合架构**

Open SWE不是从零构建，而是基于Deep Agents组合：

```python
from langgraph_deep_agents import create_deep_agent

create_deep_agent(
    model="anthropic:claude-opus-4-6",
    system_prompt=construct_system_prompt(repo_dir, ...),
    tools=[http_request, fetch_url, commit_and_open_pr, ...],
    backend=sandbox_backend,  # Modal/Daytona/Runloop/LangSmith
    middleware=[
        ToolErrorMiddleware(),
        check_message_queue_before_model,
        ...
    ],
)
```

**架构优势**：
- 复用Deep Agents的成熟能力
- 专注业务逻辑而非基础设施
- 易于扩展和定制

---

### 🔧 技术实现/执行步骤

**1. 快速启动**
```bash
# 克隆项目
git clone https://github.com/langchain-ai/open-swe
cd open-swe

# 安装依赖
pip install -e ".[dev]"

# 配置环境变量
cp .env.example .env
# 编辑 .env 添加 API keys
```

**2. 配置多平台集成**
```yaml
# config.yaml
integrations:
  slack:
    bot_token: ${SLACK_BOT_TOKEN}
    signing_secret: ${SLACK_SIGNING_SECRET}

  linear:
    api_key: ${LINEAR_API_KEY}
    webhook_secret: ${LINEAR_WEBHOOK_SECRET}

  github:
    app_id: ${GITHUB_APP_ID}
    private_key: ${GITHUB_PRIVATE_KEY}

sandbox:
  provider: modal  # 或 daytona, runloop, langsmith
  image: python:3.11-slim
```

**3. 自定义工具实现模板**
```python
from open_swe.tools import Tool

class CustomAnalysisTool(Tool):
    """自定义代码分析工具"""

    name = "analyze_code_complexity"
    description = "分析代码复杂度并返回报告"

    async def run(self, file_path: str) -> dict:
        # 1. 读取文件
        content = await self.read_file(file_path)

        # 2. 分析复杂度
        complexity = self._calculate_complexity(content)

        # 3. 返回结构化结果
        return {
            "file": file_path,
            "complexity_score": complexity.score,
            "recommendations": complexity.suggestions
        }
```

**4. 子Agent派生模式**
```python
async def parallel_analysis(self, files: list[str]) -> list[AnalysisResult]:
    """并行分析多个文件"""

    # 为每个文件派生子Agent
    subagents = [
        self.spawn_subagent(
            task=f"分析文件: {file}",
            context={"file": file, "analysis_type": "complexity"}
        )
        for file in files
    ]

    # 并行执行
    results = await asyncio.gather(*[
        subagent.run() for subagent in subagents
    ])

    return results
```

**5. 中间件实现模板**
```python
from open_swe.middleware import Middleware

class SafetyNetMiddleware(Middleware):
    """安全网中间件：防止危险操作"""

    DANGEROUS_PATTERNS = [
        r"rm\s+-rf\s+/",
        r"DROP\s+DATABASE",
        # ...
    ]

    async def before_tool_call(self, tool_name: str, params: dict) -> dict:
        # 检查危险模式
        if tool_name == "bash":
            command = params.get("command", "")
            for pattern in self.DANGEROUS_PATTERNS:
                if re.search(pattern, command, re.IGNORECASE):
                    raise SecurityError(f"危险命令被拦截: {command}")

        return params

    async def after_tool_call(self, tool_name: str, result: dict) -> dict:
        # 检查结果是否包含敏感信息泄露
        if self._contains_secrets(result):
            result = self._redact_secrets(result)

        return result
```

---

### 📊 信息差价值

| 维度 | 评估 | 说明 |
|------|------|------|
| **国外热度** | ⭐⭐⭐⭐⭐ | LangChain官方项目，今日955+ stars增长 |
| **国内讨论度** | ⭐⭐ | 中文社区几乎无讨论，信息差明显 |
| **技术成熟度** | ⭐⭐⭐⭐⭐ | 对标Stripe/Ramp/Coinbase内部Agent |
| **工程可复刻性** | ⭐⭐⭐⭐⭐ | Python开源，架构清晰 |
| **与项目契合度** | ⭐⭐⭐⭐⭐ | 直接相关6-Agent系统架构 |

**核心信息差**:
1. **异步Agent设计模式**：国内讨论集中在同步Agent，异步架构认知不足
2. **子Agent+中间件架构**：比单Agent复杂任务处理能力更强
3. **精选工具哲学**：与"堆砌工具"相反的设计思路
4. **多平台触发机制**：Slack/Linear/GitHub统一集成方案

---

### 🎯 可应用性路径

**短期（本周）**:
- [ ] 研究Open SWE源码，理解异步Agent架构
- [ ] 提取子Agent派生和中间件实现模式
- [ ] 设计MuskOrchestrator的异步任务执行机制
- [ ] 评估与现有6-Agent系统的集成方案

**中期（本月）**:
- [ ] 实现子Agent+中间件架构的Agent Harness
- [ ] 建立精选工具集（15-20个核心工具）
- [ ] 集成异步消息队列机制
- [ ] 为Stock Platform实现异步分析Agent

**长期（本季度）**:
- [ ] 构建多平台触发能力（Slack/Discord/GitHub）
- [ ] 实现线程级持久化沙箱
- [ ] 建立Agent间协作协议
- [ ] 开发可视化Agent工作流监控

---

### 🔖 相关资源

- **项目**: https://github.com/langchain-ai/open-swe
- **Deep Agents**: https://github.com/langchain-ai/deep-agents
- **LangGraph**: https://langchain-ai.github.io/langgraph/
- **对比项目**:
  - learn-claude-code (教育性质，渐进式教程)
  - GitNexus (知识图谱+Graph RAG)
  - TradingAgents (多Agent辩论)

---

### 📋 技能内化

- **技能文件**: `skills/coding/open-swe-async-agent.md`
- **触发条件**: 企业级Agent开发、异步任务处理、多Agent协作
- **核心架构**: 子Agent+中间件 + 异步消息队列 + 精选工具集
- **关键模型**: Deep Agents + LangGraph

---

### 🧠 与已有知识的整合

**与learn-claude-code的互补**:
- learn-claude-code: 教育性质，从零构建Agent Harness
- Open SWE: 生产级，企业级异步Agent框架
- **整合价值**: 理论+实践，教育+生产

**与TradingAgents的互补**:
- TradingAgents: 多Agent分层决策（金融场景）
- Open SWE: 子Agent+中间件架构（编码场景）
- **整合价值**: 不同场景的Agent架构设计模式

**与GitNexus的互补**:
- GitNexus: 知识图谱+Graph RAG（代码理解）
- Open SWE: 异步编码Agent（代码生成）
- **整合价值**: 代码理解+代码生成的完整闭环

---

*Learning Date: 2026-03-20*

---

## 历史学习记录

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

---

## 2026-03-16 学习记录

### 📚 今日学习
**来源**: Everything Claude Code (ECC) Skill Library
**技能**: TDD Workflow - 测试驱动开发完整工作流
**学习时长**: 20分钟

---

### 🎯 核心主题
**测试驱动开发 (TDD) 的标准化工作流：红-绿-重构循环**

TDD不是可选项，而是生产级代码的必要条件。80%+覆盖率是底线，不是目标。

---

### 💡 关键洞察

**1. TDD七步工作流**

```
写用户故事 → 生成测试用例 → 运行测试(红) → 实现代码 → 运行测试(绿) → 重构 → 验证覆盖率
```

| 步骤 | 关键动作 | 时间分配 |
|------|----------|----------|
| 1. 用户故事 | As a [role], I want to [action], so that [benefit] | 2分钟 |
| 2. 生成测试 | 覆盖正常路径+边界条件+错误场景 | 5分钟 |
| 3. 运行测试 | 必须失败，验证测试有效 | 1分钟 |
| 4. 实现代码 | 最小代码使测试通过 | 10分钟 |
| 5. 再次测试 | 必须全部通过 | 1分钟 |
| 6. 重构 | 消除重复，优化命名 | 5分钟 |
| 7. 验证覆盖率 | 确保80%+ | 1分钟 |

**2. 三层测试金字塔**

```
    /\
   /  \  E2E Tests (Playwright) - 关键用户流程
  /____\
 /      \ Integration Tests - API端点、数据库操作
/________\
          Unit Tests - 函数、组件、工具函数 (最多)
```

**覆盖率要求**:
- 单元测试: 覆盖所有函数和边界条件
- 集成测试: 覆盖所有API端点和外部调用
- E2E测试: 覆盖关键用户流程

**3. 测试文件组织规范**

```
src/
├── components/
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx          # 同目录单元测试
│   │   └── Button.stories.tsx
├── app/api/markets/
│   ├── route.ts
│   └── route.test.ts                # API集成测试
└── e2e/
    ├── markets.spec.ts              # E2E测试
    └── auth.spec.ts
```

**4. 常见测试错误**

| 错误类型 | 错误示例 | 正确做法 |
|----------|----------|----------|
| 测试实现细节 | `expect(component.state.count).toBe(5)` | 测试用户可见行为 |
| 脆弱选择器 | `await page.click('.css-class-xyz')` | 使用语义选择器 `[data-testid="submit-button"]` |
| 测试依赖 | test2依赖test1创建的数据 | 每个测试独立设置数据 |

---

### 🔧 可应用代码模式

**API集成测试模板**:
```typescript
import { NextRequest } from 'next/server'
import { GET } from './route'

describe('GET /api/markets', () => {
  it('returns markets successfully', async () => {
    const request = new NextRequest('http://localhost/api/markets')
    const response = await GET(request)
    const data = await response.json()

    expect(response.status).toBe(200)
    expect(data.success).toBe(true)
    expect(Array.isArray(data.data)).toBe(true)
  })

  it('validates query parameters', async () => {
    const request = new NextRequest('http://localhost/api/markets?limit=invalid')
    const response = await GET(request)
    expect(response.status).toBe(400)
  })
})
```

**Mock外部依赖**:
```typescript
jest.mock('@/lib/supabase', () => ({
  supabase: {
    from: jest.fn(() => ({
      select: jest.fn(() => ({
        eq: jest.fn(() => Promise.resolve({ data: [], error: null }))
      }))
    }))
  }
}))
```

---

### 📊 信息差价值评估
- **来源质量**: ⭐⭐⭐⭐⭐ 极高 (ECC生产级技能库)
- **可应用性**: ⭐⭐⭐⭐⭐ 极高 (直接应用于Stock Platform开发)
- **工程价值**: ⭐⭐⭐⭐⭐ 极高 (TDD是代码质量的保险)

---

### 🎯 立即行动
1. **为Stock Platform建立测试框架** - Jest + React Testing Library + Playwright
2. **设定覆盖率门槛** - 80%以下不允许提交
3. **建立CI/CD测试门禁** - GitHub Actions自动运行测试
4. **编写第一个TDD功能** - 从简单功能开始实践红-绿-重构

---

### 🔖 技能文件
`skills/everything-claude-code/.agents/skills/tdd-workflow/SKILL.md`

---

### 📋 技能内化
- **技能文件**: TDD Workflow
- **触发条件**: 任何新功能开发、Bug修复、代码重构
- **核心输出**: 红-绿-重构七步工作流

---

---

## 2026-03-17 学习记录

### 📚 今日学习
**来源**: GitHub Trending Python
**标题/项目**: TradingAgents - Multi-Agents LLM Financial Trading Framework
**链接**: https://github.com/TauricResearch/TradingAgents
**学习时长**: 25分钟

---

### 🎯 核心主题
**多Agent协作交易框架：模拟真实对冲基金的分层决策与多空辩论机制**

TradingAgents是一个32K+ stars的开源项目，通过部署专业化的LLM驱动Agent团队，模拟真实交易公司的决策流程。核心创新在于"多空辩论机制"——通过Bullish/Bearish Researchers的结构化辩论来平衡潜在收益与固有风险。

---

### 💡 关键洞察（5点）

**1. 六层Agent架构设计（Six-Layer Agent Architecture）**

```
┌─────────────────────────────────────────────┐
│  Portfolio Manager Agent                    │
│  - 最终交易决策：批准/拒绝/调整仓位          │
└──────────────┬──────────────────────────────┘
               │ 风险调整后的交易提案
┌──────────────▼──────────────────────────────┐
│  Risk Management Agent                      │
│  - 评估市场波动率、流动性风险               │
│  - 计算VaR、最大回撤等风险指标              │
└──────────────┬──────────────────────────────┘
               │ 风险评估报告
┌──────────────▼──────────────────────────────┐
│  Trader Agent                               │
│  - 综合所有分析报告                         │
│  - 确定交易时机和仓位规模                   │
└──────────────┬──────────────────────────────┘
               │ 多空平衡的研究报告
┌──────────────▼──────────────────────────────┐
│  Researcher Team (Bullish vs Bearish)       │
│  - 结构化辩论：批判性评估分析师洞察          │
│  - 平衡潜在收益 vs 固有风险                 │
└──────────────┬──────────────────────────────┘
               │ 多维度市场分析
┌──────────────▼──────────────────────────────┐
│  Analyst Team                               │
│  - Fundamentals Analyst (财务指标)          │
│  - Sentiment Analyst (情绪分析)             │
│  - News Analyst (新闻宏观)                  │
│  - Technical Analyst (技术指标)             │
└─────────────────────────────────────────────┘
```

**关键学习点**：风险管理不是后置步骤，而是嵌入决策流程的独立Agent层级。

---

**2. 多空辩论机制（Bullish vs Bearish Debate）**

这是项目最核心的创新点：

| 传统多Agent系统 | TradingAgents辩论机制 |
|----------------|----------------------|
| 各Agent独立输出信号 | 多空双方强制对抗性辩论 |
| 简单加权平均融合 | 结构化批判性评估 |
| 无冲突解决机制 | 多轮辩论（configurable rounds） |
| 容易确认偏误 | 强制考虑对立观点 |

**辩论流程**：
1. Bullish Researcher提出看多理由
2. Bearish Researcher提出看空反驳
3. 双方针对对方论点进行批判
4. 经过`max_debate_rounds`轮后形成平衡报告
5. Trader Agent基于辩论结果制定策略

**Stock Platform应用**：可为每个交易信号引入"魔鬼代言人"角色，强制挑战策略假设。

---

**3. 双模型策略（Dual-Model Strategy）**

```python
config = {
    "deep_think_llm": "gpt-5.2",      # 复杂推理：辩论、风险管理
    "quick_think_llm": "gpt-5-mini",  # 快速任务：数据提取、格式化
}
```

| 任务类型 | 使用模型 | 原因 |
|---------|---------|------|
| 多空辩论 | Deep Think | 需要复杂推理和批判性思维 |
| 风险管理评估 | Deep Think | 涉及多维度风险评估 |
| 技术指标计算 | Quick Think | 确定性计算，无需复杂推理 |
| 报告格式化 | Quick Think | 结构化输出任务 |

**成本优化**：通过任务分级可节省60%+的API成本，同时保证关键决策质量。

---

**4. LangGraph状态机设计（State Machine Architecture）**

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 初始化图
ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())

# 执行决策流程
_, decision = ta.propagate(ticker="NVDA", date="2026-01-15")
```

**状态流转**：
```
[Start] → [Data Collection] → [Analyst Team] → [Researcher Debate]
                                            ↓
[Execution] ← [Portfolio Manager] ← [Risk Management] ← [Trader Decision]
```

**关键优势**：
- 每个节点可独立测试和替换
- 状态持久化支持断点恢复
- 可视化调试（LangGraph Studio）

---

**5. 多LLM提供商支持（Multi-Provider Flexibility）**

| 提供商 | 配置值 | 适用场景 |
|--------|--------|---------|
| OpenAI | "openai" | 通用推理 |
| Anthropic | "anthropic" | 长文本分析 |
| Google | "google" | 成本敏感任务 |
| xAI | "xai" | 实时数据推理 |
| OpenRouter | "openrouter" | 模型聚合 |
| Ollama | "ollama" | 本地部署 |

**策略**：可为不同Agent分配不同提供商，实现成本-质量平衡。

---

### 🔧 技术实现/执行步骤

**1. 辩论机制实现模板**

```python
class DebateSystem:
    """多空辩论系统"""

    def __init__(self, max_rounds: int = 2):
        self.max_rounds = max_rounds
        self.bullish_agent = BullishResearcher()
        self.bearish_agent = BearishResearcher()

    def debate(self, market_analysis: dict) -> DebateResult:
        """执行多空辩论"""
        context = market_analysis

        for round_num in range(self.max_rounds):
            # 多方论证
            bullish_case = self.bullish_agent.argue(context)

            # 空方反驳
            bearish_rebuttal = self.bearish_agent.rebut(bullish_case, context)

            # 多方回应
            bullish_response = self.bullish_agent.respond(bearish_rebuttal)

            # 更新上下文
            context = self._update_context(context, bullish_case, bearish_rebuttal)

        return self._synthesize(context)
```

**2. 风险管理Agent集成**

```python
class RiskManagementAgent:
    """风险管理Agent - 独立评估风险"""

    def evaluate(self, trade_proposal: dict, portfolio: dict) -> RiskAssessment:
        """评估交易提案风险"""
        risks = {
            'market_risk': self._calculate_market_risk(trade_proposal),
            'liquidity_risk': self._assess_liquidity(trade_proposal),
            'concentration_risk': self._check_concentration(trade_proposal, portfolio),
            'var_95': self._calculate_var(trade_proposal, confidence=0.95)
        }

        # 风险阈值检查
        if risks['var_95'] > portfolio['max_var_threshold']:
            return RiskAssessment(
                approved=False,
                reason=f"VaR {risks['var_95']:.2%} exceeds threshold",
                adjusted_position=self._suggest_adjustment(trade_proposal, risks)
            )

        return RiskAssessment(approved=True, risks=risks)
```

**3. 双模型配置模式**

```python
# config/trading_agents.yaml
llm_config:
  providers:
    openai:
      api_key: ${OPENAI_API_KEY}

  # 任务-模型映射
  task_models:
    debate:
      provider: openai
      model: gpt-4o  # 复杂推理
    risk_assessment:
      provider: openai
      model: gpt-4o  # 复杂推理
    technical_analysis:
      provider: openai
      model: gpt-4o-mini  # 快速任务
    report_formatting:
      provider: openai
      model: gpt-4o-mini  # 快速任务
```

**4. 可立即应用的SOP**

| 步骤 | 行动 | 产出 |
|------|------|------|
| 1 | 为每个策略添加"魔鬼代言人" | 多空对比报告 |
| 2 | 分离风险管理层 | 独立风险评估Agent |
| 3 | 实施双模型策略 | 成本降低60%+ |
| 4 | 使用LangGraph重构工作流 | 可视化、可测试 |
| 5 | 配置多LLM提供商 | 降低单点依赖 |

---

### 📊 信息差价值

| 维度 | 评分 | 说明 |
|------|------|------|
| **国外热度** | ⭐⭐⭐⭐⭐ | 32K+ stars，GitHub Trending持续上榜 |
| **国内讨论度** | ⭐⭐⭐ | 中文社区讨论较少，信息差明显 |
| **可复刻性** | ⭐⭐⭐⭐⭐ | Python开源，架构清晰，文档完善 |
| **对项目价值** | **极高** | 与Stock Platform直接相关，可立即应用 |

**独特价值点**：
- 多空辩论机制是其他开源量化项目（如ai-hedge-fund）所没有的
- 分层架构比MiroFish的群体智能更适合作坊式金融决策
- LangGraph状态机设计提供了工程可落地的实现路径

---

### 🎯 可应用性路径

**短期（本周）**:
- [ ] 研究TradingAgents源码，提取辩论机制实现
- [ ] 设计Stock Platform的"多空辩论"模块
- [ ] 实现简单的Bullish/Bearish Agent原型
- [ ] 配置双模型策略（gpt-4o vs gpt-4o-mini）

**中期（本月）**:
- [ ] 集成LangGraph重构现有Agent工作流
- [ ] 实现独立RiskManagementAgent
- [ ] 建立六层Agent架构的Stock Platform版本
- [ ] 测试多空辩论对策略收益的改进效果

**长期（本季度）**:
- [ ] 实现多LLM提供商支持（降低OpenAI依赖）
- [ ] 可视化Agent决策流程（LangGraph Studio）
- [ ] 建立可配置的辩论轮数机制
- [ ] 探索辩论历史的学习机制（优化辩论策略）

---

### 🔖 相关资源

- **原文**: https://github.com/TauricResearch/TradingAgents
- **LangGraph文档**: https://langchain-ai.github.io/langgraph/
- **对比项目**: https://github.com/virattt/ai-hedge-fund（无辩论机制）
- **相关学习**: 2026-03-09 ai-hedge-fund学习记录（分层架构）

---

### 📋 技能内化

- **技能文件**: `skills/coding/multi-agent-debate-system.md`
- **触发条件**: 量化策略设计、多Agent决策系统、风险管理
- **核心输出**: 六层Agent架构 + 多空辩论机制 + 双模型策略

---

---

## 2026-03-18 学习记录

### 📚 今日学习
**来源**: GitHub Trending TypeScript
**标题/项目**: GitNexus - Zero-Server Code Intelligence Engine
**链接**: https://github.com/abhigyanpatwari/GitNexus
**学习时长**: 20分钟

---

### 🎯 核心主题
**客户端知识图谱 + Graph RAG Agent：零服务器架构的代码智能引擎**

GitNexus是一个革命性的代码智能工具，完全在浏览器端构建知识图谱，通过7个MCP工具为AI Agent提供预计算的关系智能。16K+ stars，核心创新是"Precomputed Relational Intelligence"——在索引时计算结构，使Agent能一次调用获得完整上下文。

---

### 💡 关键洞察（5点）

**1. 六阶段索引流水线（Six-Phase Indexing Pipeline）**

```
Structure → Parsing → Resolution → Clustering → Processes → Search
```

| 阶段 | 功能 | 技术 |
|------|------|------|
| Structure | 文件树遍历 | 文件/文件夹关系映射 |
| Parsing | AST提取 | Tree-sitter WASM |
| Resolution | 跨文件解析 | Import追踪、调用链、继承关系 |
| Clustering | 功能分组 | Leiden社区检测算法 |
| Processes | 执行流追踪 | 从入口点追踪调用链 |
| Search | 混合索引 | BM25 + 语义 + RRF |

**关键学习点**：知识图谱构建是离线计算密集型任务，查询时只需检索预计算结果。

---

**2. Graph RAG Agent架构：7个MCP工具**

GitNexus通过MCP协议暴露7个图能力工具，这是与Claude Code集成的核心：

```python
# MCP Tools暴露的图能力
tools = [
    "list_repos",      # 发现已索引仓库
    "query",           # 混合搜索（BM25+语义+RRF）
    "context",         # 360度符号视图（分类引用）
    "impact",          # 影响范围分析（深度分组+置信度评分）
    "detect_changes",  # Git diff影响映射
    "rename",          # 多文件协调重命名
    "cypher"           # 原始Cypher图查询
]
```

**Precomputed Relational Intelligence**:
- 传统RAG：Agent需要多次查询探索图结构
- GitNexus：工具返回"8个调用者，3个集群，全部90%+置信度"的预结构化响应

---

**3. 零服务器架构（Zero-Server Architecture）**

| 组件 | 技术选择 | 运行环境 |
|------|----------|----------|
| 数据库 | LadybugDB WASM | 浏览器内存 |
| 解析 | Tree-sitter WASM | 浏览器 |
| 嵌入 | 浏览器内计算（可选） | 浏览器 |
| 存储 | `.gitnexus/`目录 | 本地文件系统 |

**核心优势**："No server, no install — your code never leaves the browser"

---

**4. Claude Code深度集成：4个Agent Skills**

GitNexus为Claude Code提供"Full"支持级别——最深度的编辑器集成：

**MCP + Skills + Hooks**:
- `claude mcp add gitnexus -- npx -y gitnexus@latest mcp`
- **PreToolUse hooks**: "用图上下文丰富搜索"
- **PostToolUse hooks**: "提交后自动重新索引"

**4个自动安装的Agent Skills**（到`.claude/skills/`）:
| Skill | 用途 |
|-------|------|
| Exploring | 用知识图谱导航陌生代码 |
| Debugging | 通过调用链追踪Bug |
| Impact Analysis | 变更前分析影响范围 |
| Refactoring | 用依赖映射规划安全重构 |

**Repo-specific Skills**: `--skills`标志通过Leiden社区检测识别功能区域，生成描述"模块关键文件、入口点、执行流、跨区域连接"的SKILL.md文件。

---

**5. 多仓库架构与连接池**

```
Global Registry (~/.gitnexus/registry.json)
    ├── Repo A (.gitnexus/)
    ├── Repo B (.gitnexus/)
    └── Repo C (.gitnexus/)
```

- 一个MCP服务器可服务多个已索引仓库
- 懒连接池（最大5个并发，5分钟驱逐）
- 每个仓库独立的`.gitnexus/`目录存储索引

---

### 🔧 技术实现/执行步骤

**1. 客户端知识图谱构建模板**

```typescript
// 六阶段索引流水线
class KnowledgeGraphBuilder {
    async build(repoPath: string): Promise<Graph> {
        // Phase 1: Structure - 文件树遍历
        const fileTree = await this.walkFileTree(repoPath);

        // Phase 2: Parsing - AST提取
        const astNodes = await Promise.all(
            fileTree.map(f => this.parseAST(f))
        );

        // Phase 3: Resolution - 跨文件解析
        const resolved = this.resolveCrossReferences(astNodes);

        // Phase 4: Clustering - Leiden社区检测
        const clusters = this.leidenClustering(resolved);

        // Phase 5: Processes - 执行流追踪
        const processes = this.traceExecutionFlows(clusters);

        // Phase 6: Search - 混合索引
        return this.buildSearchIndex(processes);
    }

    private async parseAST(file: File): Promise<ASTNode> {
        // Tree-sitter WASM解析
        const parser = await this.getParser(file.language);
        return parser.parse(file.content);
    }
}
```

**2. MCP Tool实现模式**

```typescript
// 预计算关系智能的核心
class GraphRAGTools {
    async context(symbol: string): Promise<ContextResult> {
        // 不是返回原始边，而是返回预计算的360度视图
        const callers = this.getCallers(symbol, maxDepth=3);
        const callees = this.getCallees(symbol, maxDepth=3);
        const clusters = this.getRelatedClusters(symbol);

        return {
            symbol,
            callers: { count: callers.length, confidence: 0.95 },
            callees: { count: callees.length, confidence: 0.92 },
            clusters: clusters.map(c => ({
                name: c.name,
                files: c.files,
                relevance: c.relevanceScore
            }))
        };
    }

    async impact(symbol: string, depth: number): Promise<ImpactResult> {
        // 影响范围分析：深度分组 + 置信度评分
        const blastRadius = this.calculateBlastRadius(symbol, depth);
        return {
            affectedFiles: blastRadius.files,
            affectedClusters: blastRadius.clusters,
            confidence: blastRadius.confidence,
            riskLevel: this.assessRisk(blastRadius)
        };
    }
}
```

**3. 技能自动生成机制**

```typescript
// 基于Leiden社区检测生成repo-specific skills
class SkillGenerator {
    generateSkills(graph: KnowledgeGraph): Skill[] {
        // 1. 运行Leiden算法识别功能社区
        const communities = this.leiden.detect(graph);

        // 2. 为每个社区生成SKILL.md
        return communities.map(community => ({
            name: community.name,
            description: this.generateDescription(community),
            keyFiles: community.entryPoints,
            executionFlows: this.traceFlows(community),
            crossAreaConnections: this.findConnections(community, graph)
        }));
    }
}
```

**4. 可立即应用的SOP**

| 步骤 | 行动 | 产出 |
|------|------|------|
| 1 | 研究Tree-sitter WASM集成 | AST解析能力 |
| 2 | 实现Leiden社区检测 | 代码功能分组 |
| 3 | 设计Precomputed Relational Intelligence | 快速查询响应 |
| 4 | 构建MCP Tool接口 | Agent集成能力 |
| 5 | 实现Skill自动生成 | 上下文感知Agent |

---

### 📊 信息差价值

| 维度 | 评分 | 说明 |
|------|------|------|
| **国外热度** | ⭐⭐⭐⭐⭐ | 16K+ stars，GitHub Trending TypeScript #1 |
| **国内讨论度** | ⭐⭐ | 中文社区几乎无讨论，信息差明显 |
| **可复刻性** | ⭐⭐⭐⭐⭐ | TypeScript开源，架构清晰 |
| **对Agent系统价值** | **极高** | 知识图谱+Graph RAG是下一代Agent基础设施 |
| **对Stock Platform价值** | ⭐⭐⭐⭐ | 代码库分析、策略回测代码理解 |

**独特价值点**：
- 零服务器架构：完全客户端运行，隐私保护
- Precomputed Relational Intelligence：查询性能革命
- 自动生成Skills：Agent上下文感知的新范式
- MCP深度集成：与Claude Code无缝协作

---

### 🎯 可应用性路径

**短期（本周）**:
- [ ] 研究GitNexus源码，理解六阶段索引流水线
- [ ] 测试Tree-sitter WASM在浏览器端的解析能力
- [ ] 设计Agent成长系统的知识图谱存储方案
- [ ] 评估LadybugDB WASM的适用性

**中期（本月）**:
- [ ] 实现技能文件的自动生成机制
- [ ] 构建Precomputed Relational Intelligence查询层
- [ ] 集成MCP Tools到Agent工作流
- [ ] 为Stock Platform代码库建立知识图谱

**长期（本季度）**:
- [ ] 实现零服务器架构的Agent记忆系统
- [ ] 构建跨项目的知识图谱关联
- [ ] 开发可视化知识图谱浏览器
- [ ] 研究Leiden算法在策略分组中的应用

---

### 🔖 相关资源

- **原文**: https://github.com/abhigyanpatwari/GitNexus
- **Tree-sitter**: https://tree-sitter.github.io/tree-sitter/
- **Leiden算法**: https://arxiv.org/abs/1810.08473
- **对比项目**: Sourcegraph（服务器架构）、GitHub Copilot（闭源）
- **相关学习**: 2026-03-13 Hindsight记忆系统、2026-03-09 ai-hedge-fund分层架构

---

### 📋 技能内化

- **技能文件**: `skills/coding/client-side-knowledge-graph.md`
- **触发条件**: 代码库分析、Agent记忆系统、技能自动生成
- **核心输出**: 六阶段索引流水线 + Precomputed Relational Intelligence + MCP Tools

---

---

## 2026-03-19 学习记录

### 📚 今日学习
**来源**: GitHub Trending TypeScript
**标题/项目**: learn-claude-code - Zero-to-One Agent Harness Engineering
**链接**: https://github.com/shareAI-lab/learn-claude-code
**学习时长**: 25分钟

---

### 🎯 核心主题
**Agent Harness工程：从零构建Claude Code-like Agent的完整教程**

learn-claude-code是一个革命性的开源项目（33K+ stars），通过12个渐进式Session教授如何从零构建一个完整的Agent Harness。核心哲学是"Bash is all you need"和"the model is the agent"——模型本身就是Agent，代码只提供环境。

---

### 💡 关键洞察（5点）

**1. Harness Formula（Harness公式）**

```
Harness = Tools + Knowledge + Observation + Action Interfaces + Permissions
```

这是Agent工程的第一性原理。与复杂框架不同，Harness只提供：
- **Tools**: Agent可调用的能力
- **Knowledge**: 技能文件的按需加载
- **Observation**: 环境状态的读取能力
- **Action Interfaces**: 执行动作的统一接口
- **Permissions**: 安全边界控制

**关键学习点**：Agent不是框架，不是提示链，而是"模型+环境"。

---

**2. 十二阶段渐进式架构（12-Session Architecture）**

| Session | 机制 | 核心洞察 |
|---------|------|----------|
| s01 | Agent Loop | "One loop & Bash is all you need" |
| s02 | Tool Use | Dispatch map: name→handler 模式 |
| s03 | TodoWrite | Planning with nag reminders（催促提醒） |
| s04 | Subagents | 独立messages[]实现真正的上下文隔离 |
| s05 | Skills | 按需加载，而非塞入system prompt |
| s06 | Context Compact | 三层压缩策略 |
| s07 | Tasks | 文件CRUD + 依赖图 |
| s08 | Background Tasks | Daemon threads + notify queue |
| s09 | Agent Teams | Teammates + JSONL mailboxes |
| s10 | Team Protocols | Request-response FSM |
| s11 | Autonomous Agents | Idle cycle + auto-claim |
| s12 | Worktree Isolation | Task-directory绑定 |

**渐进式学习价值**：每个Session都是可运行的独立单元，从简单循环到复杂多Agent系统。

---

**3. 最小Agent循环（The Minimal Agent Loop）**

```python
def agent_loop(messages):
    while True:
        response = client.messages.create(
            model=MODEL,
            system=SYSTEM,
            messages=messages,
            tools=TOOLS,
        )
        messages.append({
            "role": "assistant",
            "content": response.content
        })

        if response.stop_reason != "tool_use":
            return  # 完成，返回结果

        # 执行工具，追加结果，继续循环
        tool_results = execute_tools(response.content)
        messages.append({
            "role": "user",
            "content": tool_results
        })
```

**核心洞察**：整个Agent系统可以简化为一个循环——接收消息、调用模型、执行工具、追加结果。

---

**4. 三层上下文压缩策略（Three-Layer Context Compression）**

```
Layer 1: System Prompt (固定)
Layer 2: Conversation History (动态，需压缩)
Layer 3: Tool Results (临时，可摘要)
```

**压缩策略**：
- **Summarization**: 长对话历史摘要
- **Truncation**: 保留最近N轮，丢弃早期
- **Hierarchical**: 重要消息标记，优先保留

**与Hindsight记忆系统的对比**：
- Hindsight: retain/recall/reflect三操作
- learn-claude-code: 压缩+按需加载技能

---

**5. Worktree隔离模式（Worktree Isolation Pattern）**

```
main-repo/
├── .git/
├── src/              # 主分支代码
└── .worktrees/
    ├── task-001/     # 独立worktree
    ├── task-002/     # 独立worktree
    └── task-003/     # 独立worktree
```

**优势**：
- 每个任务在独立目录执行
- Git worktree天然支持并行
- 任务失败不影响主分支
- 自动清理机制

**对比Docker隔离**：
- Worktree: 轻量级，文件系统级
- Docker: 重量级，进程+网络隔离

---

### 🔧 技术实现/执行步骤

**1. 工具注册模式（Dispatch Map Pattern）**

```python
# 可扩展的工具注册系统
class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name: str, handler: Callable):
        """注册工具"""
        self._tools[name] = handler

    def execute(self, name: str, params: dict) -> dict:
        """执行工具"""
        if name not in self._tools:
            return {"error": f"Unknown tool: {name}"}
        return self._tools[name](**params)

# 使用示例
registry = ToolRegistry()
registry.register("bash", bash_handler)
registry.register("read", read_handler)
registry.register("TodoWrite", todo_handler)

# Agent循环中调用
tool_result = registry.execute(tool_name, tool_params)
```

**2. 技能按需加载（Lazy Skill Loading）**

```python
# 错误做法：塞入system prompt
SYSTEM_PROMPT = """
You are a coding agent.
Here are 100 skills: [...]  # 太长！
"""

# 正确做法：通过工具按需加载
SKILLS_LIBRARY = {
    "tdd": "skills/tdd-workflow.md",
    "refactor": "skills/refactoring-patterns.md",
    "api-design": "skills/api-design.md",
}

def load_skill(skill_name: str) -> str:
    """Agent通过工具调用加载技能"""
    if skill_name in SKILLS_LIBRARY:
        with open(SKILLS_LIBRARY[skill_name]) as f:
            return f.read()
    return f"Skill '{skill_name}' not found"

# Agent决定何时加载
# Agent: "我需要应用TDD，先加载tdd技能"
# -> 调用 load_skill("tdd")
```

**3. 子Agent上下文隔离**

```python
class SubagentManager:
    """管理子Agent的独立上下文"""

    def spawn(self, task: str, parent_messages: list) -> str:
        """创建子Agent，继承父上下文但独立演化"""
        # 子Agent获得父消息的副本，而非引用
        child_messages = parent_messages.copy()

        # 添加任务描述
        child_messages.append({
            "role": "user",
            "content": f"New task: {task}"
        })

        # 在独立线程/进程中运行
        result = self._run_isolated(child_messages)
        return result

    def _run_isolated(self, messages: list) -> str:
        """隔离执行，不影响父Agent"""
        # 独立的agent_loop实例
        return agent_loop(messages)
```

**4. 文件任务系统（File-based Task CRUD）**

```python
# 任务存储在文件系统，支持依赖图
TASKS_DIR = ".tasks/"

def create_task(name: str, description: str, depends_on: list = None):
    """创建新任务"""
    task = {
        "id": generate_id(),
        "name": name,
        "description": description,
        "status": "pending",  # pending | in_progress | completed | failed
        "depends_on": depends_on or [],
        "created_at": now(),
        "updated_at": now(),
    }
    save_task(task)
    return task

def get_ready_tasks() -> list:
    """获取所有依赖已满足的任务"""
    all_tasks = load_all_tasks()
    completed = {t["id"] for t in all_tasks if t["status"] == "completed"}
    return [
        t for t in all_tasks
        if t["status"] == "pending"
        and all(dep in completed for dep in t["depends_on"])
    ]
```

**5. 可立即应用的SOP**

| 步骤 | 行动 | 产出 |
|------|------|------|
| 1 | 实现最小Agent循环 | 可运行的bash agent |
| 2 | 建立工具注册系统 | 可扩展的工具生态 |
| 3 | 迁移技能到按需加载 | 减少token消耗50%+ |
| 4 | 实现worktree隔离 | 并行任务执行能力 |
| 5 | 添加任务依赖图 | 复杂工作流编排 |

---

### 📊 信息差价值

| 维度 | 评分 | 说明 |
|------|------|------|
| **国外热度** | ⭐⭐⭐⭐⭐ | 33K+ stars，GitHub Trending TypeScript #1 |
| **国内讨论度** | ⭐⭐ | 中文社区讨论极少，信息差明显 |
| **可复刻性** | ⭐⭐⭐⭐⭐ | 渐进式教程，每Session可独立运行 |
| **对Agent系统价值** | **极高** | 从零构建Agent Harness的完整路径 |
| **对Stock Platform价值** | ⭐⭐⭐⭐ | 量化任务编排、并行回测执行 |

**独特价值点**：
- 与复杂框架（LangChain/LlamaIndex）相反，强调"简单即美"
- 12个Session构成完整学习路径，从入门到生产
- Worktree隔离模式是并行执行的创新方案
- "模型即Agent"的哲学与我们的6-Agent系统设计一致

---

### 🎯 可应用性路径

**短期（本周）**:
- [ ] 研究learn-claude-code源码，提取最小Agent循环实现
- [ ] 设计工具注册系统，统一Agent工具调用接口
- [ ] 迁移现有技能文件到按需加载模式
- [ ] 实现简单的worktree隔离原型

**中期（本月）**:
- [ ] 重构6-Agent系统，采用Harness公式架构
- [ ] 实现任务依赖图，支持复杂工作流编排
- [ ] 集成worktree隔离到Stock Platform回测系统
- [ ] 建立技能库懒加载机制

**长期（本季度）**:
- [ ] 实现Agent Teams多Agent协作
- [ ] 开发自主Agent（idle cycle + auto-claim）
- [ ] 构建可视化Agent工作流编辑器
- [ ] 研究上下文压缩策略优化token成本

---

### 🔖 相关资源

- **原文**: https://github.com/shareAI-lab/learn-claude-code
- **文档**: https://github.com/shareAI-lab/learn-claude-code/tree/main/docs
- **对比项目**: Claude Code（闭源）、Open SWE（LangChain生态）
- **相关学习**:
  - 2026-03-18 GitNexus（知识图谱+Graph RAG）
  - 2026-03-17 TradingAgents（多空辩论机制）
  - 2026-03-13 Hindsight（Agent记忆系统）

---

### 📋 技能内化

- **技能文件**: `skills/coding/agent-harness-engineering.md`
- **触发条件**: Agent系统架构设计、工具开发、任务编排
- **核心输出**: Harness公式 + 12阶段架构 + Worktree隔离模式

---

*Learning Date: 2026-03-25*

---

## 2026-03-25 学习记录

### 📚 今日学习
**来源**: GitHub Trending Python #1
**标题/项目**: Browser Use - Make websites accessible for AI agents
**链接**: https://github.com/browser-use/browser-use
**文档**: https://docs.browser-use.com
**学习时长**: 25分钟

---

### 🎯 核心主题
**让AI Agent像人类一样使用浏览器：开源浏览器自动化框架的新标准**

Browser Use是一个81K+ stars的Python库，使AI Agent能够控制浏览器完成复杂网页任务。它是Manus AI等通用Agent的核心基础设施，支持结构化输出、Session持久化、多LLM提供商，并提供Cloud托管服务。核心创新是"自然语言描述目标，结构化数据返回"的极简API设计。

---

### 💡 关键洞察（5点）

**1. 极简API设计：自然语言到结构化输出**

```python
from browser_use import Agent, ChatBrowserUse

agent = Agent(
    task="Find the top 3 trending repos on GitHub",
    llm=ChatBrowserUse(),
)
result = await agent.run()  # 返回结构化数据
```

**核心设计哲学**：
- 用户用自然语言描述目标
- Agent自主规划执行步骤
- 返回结构化数据（而非原始HTML）

**对比传统爬虫**：
| 传统爬虫 | Browser Use |
|---------|-------------|
| 编写XPath/Selector | 自然语言描述目标 |
| 处理反爬、验证码 | 内置stealth和CAPTCHA解决 |
| 返回原始HTML | 返回结构化提取数据 |
|  brittle（易失效） | 自适应页面变化 |

---

**2. 双模式架构：开源+云端灵活部署**

```
┌─────────────────────────────────────────────┐
│           Browser Use Architecture          │
├─────────────────────┬───────────────────────┤
│   Open Source       │   Cloud (Managed)     │
│   (Self-hosted)     │   (SDK/API)           │
├─────────────────────┼───────────────────────┤
│ • 本地Playwright    │ • 隐身浏览器          │
│ • 自带LLM API Key   │ • 代理轮换            │
│ • 免费开源          │ • CAPTCHA自动解决     │
│ • Python ≥3.11      │ • 持久化Session       │
│ • 社区驱动          │ • 按量付费            │
└─────────────────────┴───────────────────────┘
```

**Cloud定价**（每1M token）：
- 输入: $0.20
- 缓存输入: $0.02
- 输出: $2.00

---

**3. Session与Profile：状态持久化的关键设计**

```python
# Session：多步骤工作流保持登录状态
client = AsyncBrowserUse()
session = await client.sessions.create(proxy_country_code="us")

# 第一步：登录
result1 = await client.run(
    "Log into example.com",
    session_id=str(session.id),
    keep_alive=True  # 保持Session活跃
)

# 第二步：基于已登录状态操作
result2 = await client.run(
    "Now click settings",
    session_id=str(session.id)
)

await client.sessions.stop(str(session.id))
```

**Profile：跨Session持久化登录状态**
```bash
# 同步本地浏览器cookies到云端
curl -fsSL https://browser-use.com/profile.sh | sh
```

```python
# 使用已保存的Profile（免重新登录）
result = await client.run(
    "Go to dashboard",
    profile_id="your-profile-uuid"
)
```

---

**4. 结构化输出：Pydantic/Zod Schema驱动**

```python
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: float
    rating: float
    reviews: int

# Agent自动提取并验证结构化数据
result = await client.run(
    "Extract product info from amazon.com/dp/B08N5WRWNW",
    output_schema=Product
)

print(result.output)
# Product(name="Kindle Paperwhite", price=139.99, rating=4.7, reviews=15234)
```

**TypeScript版本**：
```typescript
import { z } from "zod";

const Product = z.object({
    name: z.string(),
    price: z.number(),
});

const result = await client.run(
    "Get product info",
    { schema: Product }
);
```

---

**5. Workspace与文件操作：Agent的持久化存储**

```python
# 创建Workspace
workspace = await client.workspaces.create(name="research-workspace")

# Agent在Workspace中创建文件
result = await client.run(
    "Research Tesla stock and create report.md",
    workspace_id=str(workspace.id)
)

# 获取文件列表
files = await client.workspaces.files(
    str(workspace.id),
    include_urls=True
)

# 下载文件
for file in files:
    print(f"{file.name}: {file.download_url}")
```

**文件上传场景**：
```python
from browser_use_sdk.v3 import FileUploadItem

# 上传CSV让Agent分析
upload_resp = await client.sessions.upload_files(
    str(session.id),
    files=[FileUploadItem(name="data.csv", content_type="text/csv")],
)

# 上传后Agent可直接读取
result = await client.run(
    "Read data.csv and create summary report",
    session_id=str(session.id)
)
```

---

### 🔧 技术实现/执行步骤

**1. 快速开始（Open Source）**

```bash
# 安装
pip install browser-use

# 设置LLM API Key
export OPENAI_API_KEY=sk-...
# 或
export ANTHROPIC_API_KEY=sk-...
```

```python
# 基础用法
from browser_use import Agent, ChatBrowserUse
import asyncio

async def main():
    agent = Agent(
        task="Find the number of stars of browser-use repo",
        llm=ChatBrowserUse(),  # 优化模型，比其他模型快3-5倍
    )
    result = await agent.run()
    print(result)

asyncio.run(main())
```

**2. Cloud SDK使用**

```bash
pip install browser-use-sdk
export BROWSER_USE_API_KEY=your_key
```

```python
from browser_use_sdk.v3 import AsyncBrowserUse

client = AsyncBrowserUse()

# 基础任务
result = await client.run("Find top 3 Hacker News posts")
print(result.output)

# 结构化输出
from pydantic import BaseModel

class NewsItem(BaseModel):
    title: str
    points: int
    comments: int

class NewsList(BaseModel):
    items: list[NewsItem]

result = await client.run(
    "Get top 3 Hacker News posts",
    output_schema=NewsList
)
```

**3. 多LLM提供商支持**

```python
from browser_use import Agent
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# OpenAI
agent = Agent(
    task="...",
    llm=ChatOpenAI(model="gpt-4o"),
)

# Anthropic
agent = Agent(
    task="...",
    llm=ChatAnthropic(model="claude-3-5-sonnet-20241022"),
)

# 本地模型 (Ollama)
from langchain_ollama import ChatOllama
agent = Agent(
    task="...",
    llm=ChatOllama(model="qwen2.5:14b"),
)
```

**4. 自定义工具扩展**

```python
from browser_use import Tools

tools = Tools()

@tools.action(description='Send notification to Slack')
def notify_slack(message: str, channel: str = "#alerts") -> str:
    """Send a notification to Slack channel"""
    # 实现Slack通知逻辑
    return f"Sent to {channel}: {message}"

@tools.action(description='Query internal API')
def query_internal_api(endpoint: str) -> dict:
    """Query company internal API"""
    # 实现API查询逻辑
    return {"data": "..."}

agent = Agent(
    task="Check stock price and notify team",
    llm=ChatBrowserUse(),
    tools=tools,  # 注入自定义工具
)
```

**5. 与Stock Platform整合方案**

```python
class StockDataCollector:
    """基于Browser Use的A股数据收集器"""

    def __init__(self):
        self.client = AsyncBrowserUse()

    async def collect_financial_reports(self, stock_code: str):
        """收集个股财报数据"""
        from pydantic import BaseModel

        class FinancialData(BaseModel):
            revenue: float
            net_profit: float
            eps: float
            roe: float

        result = await self.client.run(
            f"Go to eastmoney.com, search {stock_code}, "
            "extract latest quarterly financial data",
            output_schema=FinancialData,
            proxy_country_code="cn"
        )

        return result.output

    async def monitor_news(self, stock_code: str):
        """监控个股新闻"""
        class NewsItem(BaseModel):
            title: str
            source: str
            time: str
            sentiment: str  # positive/negative/neutral

        result = await self.client.run(
            f"Search {stock_code} latest news on 10jqka.com.cn, "
            "extract top 5 news with sentiment analysis",
            output_schema=list[NewsItem]
        )

        return result.output
```

---

### 📊 信息差价值

| 维度 | 评估 | 说明 |
|------|------|------|
| **国外热度** | ⭐⭐⭐⭐⭐ | 81K+ stars，GitHub Python Trending #1 |
| **国内讨论度** | ⭐⭐⭐ | 中文社区讨论较少，信息差明显 |
| **技术成熟度** | ⭐⭐⭐⭐⭐ | 生产级，Manus AI等产品的核心基础设施 |
| **工程可复刻性** | ⭐⭐⭐⭐⭐ | Python开源，API设计简洁 |
| **与项目契合度** | ⭐⭐⭐⭐⭐ | 完美契合Stock Platform数据采集需求 |

**核心信息差**：
1. **结构化输出能力**：不仅是浏览器控制，更是数据提取框架
2. **Session持久化**：多步骤工作流的状态管理设计
3. **Cloud+开源双模式**：灵活部署选项
4. **与Manus AI的关系**：开源基础设施 vs 终端产品

---

### 🎯 可应用性路径

**短期（本周）**:
- [ ] 安装browser-use并运行第一个Agent任务
- [ ] 测试A股数据网站（东方财富、同花顺）的访问
- [ ] 设计财报数据提取的Pydantic Schema
- [ ] 评估Cloud vs 开源模式的成本

**中期（本月）**:
- [ ] 构建基于Browser Use的A股数据收集Pipeline
- [ ] 实现财报、新闻、公告的自动化采集
- [ ] 集成到Stock Platform数据层
- [ ] 建立Session管理和错误重试机制

**长期（本季度）**:
- [ ] 开发可视化Agent任务编排界面
- [ ] 实现多Agent并行数据采集
- [ ] 构建数据质量验证和清洗流程
- [ ] 探索与TradingAgents的整合（数据→决策闭环）

---

### 🔖 相关资源

- **GitHub**: https://github.com/browser-use/browser-use
- **文档**: https://docs.browser-use.com
- **Cloud**: https://cloud.browser-use.com
- **对比项目**:
  - Playwright MCP (Microsoft)
  - Stagehand (Browserbase)
  - Skyvern (Vision-based)
- **相关学习**:
  - 2026-03-17 TradingAgents（多Agent决策）
  - 2026-03-20 Microsoft Qlib（数据基础设施）

---

### 📋 技能内化

- **技能文件**: `skills/coding/browser-use-ai-automation.md`
- **触发条件**: 网页数据采集、自动化测试、AI Agent浏览器控制
- **核心架构**: Agent + Browser + LLM 三组件模式
- **关键设计**: Session持久化、结构化输出、Workspace存储

---

*Learning Date: 2026-03-25*

---

*Learning Date: 2026-03-20*

*Learning Date: 2026-03-19*

*Learning Date: 2026-03-18*

*Learning Date: 2026-03-17*
