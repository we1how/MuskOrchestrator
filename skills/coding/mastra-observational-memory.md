# Mastra Observational Memory - 观测记忆系统

> **核心洞察**: 从RAG检索到压缩记忆的范式转变，实现4-10倍成本削减与SOTA性能

---

## 概述

Mastra Observational Memory (OM) 是TypeScript-first AI框架Mastra的旗舰记忆创新，通过双Agent后台压缩机制，在LongMemEval基准上达到**94.87%的SOTA成绩**，同时实现**4-10倍的token成本削减**。

---

## 核心架构

### 双Agent后台系统

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

**Observer Agent**:
- 实时监听对话流
- 将原始消息压缩为带优先级标记的观测
- 标记: 🔴关键 / 🟡重要 / 🟢信息
- 触发: 原始消息达到30K tokens

**Reflector Agent**:
- 定期"垃圾回收"记忆
- 重组观测、合并相关项、删除过时信息
- 触发: 观测达到60K tokens

---

## OM vs RAG 对比

| 维度 | 传统RAG | Mastra OM |
|------|---------|-----------|
| 核心机制 | 向量检索 | 文本压缩 |
| 架构依赖 | 向量数据库 | 纯文本，无外部依赖 |
| 检索方式 | 动态相似度搜索 | 静态前缀缓存 |
| Prompt缓存 | 不稳定 | 稳定（append-only） |
| 成本削减 | 无 | 4-10x |
| LongMemEval | 80.05% | **94.87% (SOTA)** |

---

## 快速开始

### 安装
```bash
npm install @mastra/core @mastra/memory
```

### 基础配置
```typescript
import { Agent } from '@mastra/core/agent'
import { Memory } from '@mastra/memory'

const agent = new Agent({
  name: 'research-assistant',
  instructions: 'You are a helpful assistant.',
  model: 'openai/gpt-4o',
  memory: new Memory(),  // 启用基础记忆
})
```

### 启用Observational Memory
```typescript
const agent = new Agent({
  name: 'long-context-agent',
  instructions: 'You maintain context across long conversations.',
  model: 'openai/gpt-4o',
  memory: new Memory({
    options: {
      observationalMemory: {
        model: 'google/gemini-2.5-flash',  // 轻量级模型处理压缩
        observation: {
          messageTokens: 30_000,      // 触发观测压缩阈值
          bufferTokens: 5_000,         // 后台缓冲区间隔
          bufferActivation: 0.7,       // 保留70%后激活
          blockAfter: 1.5,             // 1.5倍阈值时强制同步
        },
        reflection: {
          observationTokens: 60_000,   // 触发反思阈值
          bufferActivation: 0.5,       // 50%时开始后台反思
          blockAfter: 1.2,
        },
      },
    },
  }),
})
```

---

## 配置参数详解

### Observation配置
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `messageTokens` | 原始消息块大小 | 30,000 |
| `bufferTokens` | 后台缓冲区间隔 | 5,000 |
| `bufferActivation` | 缓冲激活比例 | 0.7 |
| `blockAfter` | 强制同步倍数 | 1.5 |

### Reflection配置
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `observationTokens` | 观测块大小 | 60,000 |
| `bufferActivation` | 反思启动比例 | 0.5 |
| `blockAfter` | 强制同步倍数 | 1.2 |

---

## 应用场景

### ✅ 推荐使用
- 多轮长程对话Agent
- 需要维持人设/任务状态
- 工具密集型Agent（浏览器、编码、研究）
- 成本敏感的生产部署

### ❌ 不推荐使用
- 开放式知识发现
- 合规性要求严格的场景
- 简单搜索引擎式任务
- 仅需情景记忆

---

## 成本削减原理

1. **Append-only观测**: 观测日志只追加不修改，前缀稳定可缓存
2. **异步缓冲**: 后台处理不阻塞对话
3. **压缩率**: 文本3-6x，工具密集型5-40x
4. **缓存折扣**: 稳定前缀使50-90% token成本折扣可持续应用

---

## 基准性能

| 系统 | 模型 | LongMemEval分数 |
|------|------|----------------|
| **Mastra OM** | **GPT-5-mini** | **94.87%** ⭐ SOTA |
| **Mastra OM** | **Gemini-3-pro-preview** | **93.27%** |
| Hindsight | Gemini-3-pro-preview | 91.40% |
| **Mastra OM** | **GPT-4o** | **84.23%** |
| Oracle (理想配置) | GPT-4o | 82.40% |
| Supermemory | GPT-4o | 81.60% |
| **Mastra RAG** | GPT-4o | **80.05%** |

---

## 与MuskOrchestrator整合

### 量化研究Agent示例
```typescript
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
    return await this.agent.generate(
      `研究因子假设: ${factorIdea}\n` +
      `请参考之前关于类似因子的研究结论。`
    )
  }
}
```

---

## 相关资源

- **GitHub**: https://github.com/mastra-ai/mastra
- **文档**: https://mastra.ai/docs/memory/observational-memory
- **博客**: https://mastra.ai/blog/observational-memory
- **基准**: https://supergok.com/mastra-observational-memory/

---

## 信息差评估

| 维度 | 评分 | 说明 |
|------|------|------|
| 国外热度 | ⭐⭐⭐⭐⭐ | 22K+ stars，Replit/PayPal生产使用 |
| 国内讨论度 | ⭐⭐ | 中文社区几乎无讨论 |
| 技术成熟度 | ⭐⭐⭐⭐⭐ | 生产级框架，SOTA基准验证 |
| 工程可复刻性 | ⭐⭐⭐⭐⭐ | TypeScript开源，npm install即用 |
| 成本影响 | ⭐⭐⭐⭐⭐ | 4-10x成本削减 |

---

*技能内化日期: 2026-03-27*
*来源: GitHub Trending TypeScript + Mastra官方博客*
