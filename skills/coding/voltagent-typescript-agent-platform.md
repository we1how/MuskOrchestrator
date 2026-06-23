# Skill: VoltAgent TypeScript Agent Platform

## 触发条件
- 构建生产级TypeScript AI Agent系统
- 设计多Agent编排架构
- 实现可观测的Agent工作流
- 开发人机协作(Human-in-the-loop)流程
- 需要类型安全的Agent工具系统

---

## 核心概念

### 端到端Agent工程平台

```
VoltAgent = 开源框架 + VoltOps控制台

框架: 开发Agent、工作流、多Agent系统
控制台: 观测、调试、优化、部署
```

**关键洞察**: 生产级Agent不仅是代码，更需要完整的开发→部署→运维闭环。

---

## 架构组件

### 1. Agent核心模型

```typescript
interface AgentConfig {
  name: string;
  instructions: string;
  model: LanguageModel;  // OpenAI, Anthropic, Gemini等
  tools: Tool[];         // Zod类型安全工具
  memory?: Memory;       // 持久化上下文
}

const agent = new Agent({
  name: "my-agent",
  instructions: "A helpful assistant...",
  model: openai("gpt-4o-mini"),
  tools: [weatherTool, searchTool],
  memory: new Memory(),
});
```

### 2. 声明式工作流引擎

| 操作 | 方法 | 用途 |
|------|------|------|
| 顺序 | `.andThen()` | 标准流程 |
| 委托 | `.andAgent()` | 专业Agent分发 |
| 并行 | `.andAll()` | 批量处理 |
| 竞速 | `.andRace()` | 最快响应 |
| 条件 | `.andWhen()` | 动态分支 |
| 暂停 | `.pause()` | 人工审批点 |

**工作流示例**:
```typescript
const workflow = new Workflow({ name: "expense-approval" })
  .step("extract", async ({ input }) => {
    // 解析发票数据
    return { amount: input.amount, category: input.category };
  })
  .step("validate", async ({ context }) => {
    // 验证金额合理性
    if (context.amount > 10000) {
      return { status: "needs_approval" };
    }
    return { status: "auto_approved" };
  })
  .step("manager-approval", async ({ context }) => {
    // 暂停等待人工审批
    if (context.status === "needs_approval") {
      await workflow.pause({ reason: "awaiting_manager_approval" });
    }
  })
  .step("process", async ({ context }) => {
    // 执行报销流程
    await processExpense(context);
  });
```

### 3. Supervisor多Agent编排

```
Supervisor Agent架构
│
├─ Supervisor (协调者)
│  └─ 任务分解 → Agent路由 → 结果聚合
│
├─ Research Agent    → 信息收集、数据分析
├─ Code Agent        → 代码生成、重构
├─ Review Agent      → 质量检查、合规
└─ Test Agent        → 测试用例生成、执行
```

**实现模式**:
```typescript
const supervisor = new Agent({
  name: "supervisor",
  instructions: "协调专业Agent完成任务...",
  tools: [
    delegateToAgent("research", researchAgent),
    delegateToAgent("code", codeAgent),
    delegateToAgent("review", reviewAgent),
  ],
});

const team = new VoltAgent({
  agents: {
    supervisor,
    research: researchAgent,
    code: codeAgent,
    review: reviewAgent,
  },
});
```

### 4. Zod类型安全工具

```typescript
import { z } from "zod";
import { tool } from "@voltagent/core";

// 定义类型安全的工具
const stockTool = tool({
  name: "get_stock_price",
  description: "获取股票实时价格",
  parameters: z.object({
    symbol: z.string().describe("股票代码，如AAPL"),
    market: z.enum(["US", "CN", "HK"]).default("US"),
  }),
  execute: async ({ symbol, market }) => {
    // 类型安全：symbol是string，market是enum
    const price = await fetchStockPrice(symbol, market);
    return { symbol, price, currency: market === "CN" ? "CNY" : "USD" };
  },
});

// Agent使用工具
const agent = new Agent({
  name: "stock-analyst",
  tools: [stockTool],
});
```

### 5. MCP(Model Context Protocol)集成

```typescript
import { MCPClient } from "@voltagent/mcp";

// 连接MCP Server
const mcpClient = new MCPClient({
  serverUrl: "https://mcp-server.example.com",
});

// 获取MCP工具
const mcpTools = await mcpClient.tools();

// 在Agent中使用
const agent = new Agent({
  name: "mcp-agent",
  tools: [...mcpTools, customTool],
});
```

### 6. 持久化内存系统

```typescript
import { Memory, PostgresMemoryAdapter } from "@voltagent/core";

// 配置持久化内存
const memory = new Memory({
  adapter: new PostgresMemoryAdapter({
    connectionString: process.env.DATABASE_URL,
  }),
  maxMessages: 100,  // 保留最近100条消息
  ttl: 86400 * 7,    // 7天过期
});

// Agent自动使用内存
const agent = new Agent({
  name: "memory-agent",
  memory,
});

// 跨会话保持上下文
const session1 = await agent.run("我叫张三", { sessionId: "user-123" });
const session2 = await agent.run("我叫什么名字？", { sessionId: "user-123" });
// Agent会回答："你叫张三"
```

---

## 可观测性(VoltOps)

### 1. 实时执行追踪

```typescript
// 自动追踪所有Agent调用
new VoltAgent({
  agents: { myAgent },
  voltOps: {
    enabled: true,
    apiKey: process.env.VOLTOPS_API_KEY,
  },
});
```

**追踪数据**:
- Agent调用链可视化
- 工具执行时间
- LLM token消耗
- 错误率和延迟

### 2. 性能指标监控

| 指标 | 说明 | 告警阈值 |
|------|------|----------|
| latency_p99 | 99分位延迟 | > 5s |
| token_usage | Token消耗 | > 10K/请求 |
| error_rate | 错误率 | > 1% |
| tool_success | 工具成功率 | < 95% |

### 3. 日志与调试

```typescript
// 结构化日志
import { logger } from "@voltagent/core";

logger.info("Agent started", {
  agent: "stock-analyst",
  sessionId: "sess-123",
  input: "分析AAPL走势",
});

// 调试模式
const agent = new Agent({
  name: "debug-agent",
  debug: true,  // 输出详细执行日志
});
```

---

## 高级模式

### 1. 可恢复流式响应

**场景**: 用户断网、页面刷新、App后台切换

```typescript
// 服务端：启用可恢复流式
const stream = await agent.stream(input, {
  resumable: true,
  streamId: "unique-session-id",
  timeout: 300000,  // 5分钟保留
});

// 客户端：断线后恢复
const stream = await agent.resumeStream("unique-session-id");

// 监听恢复事件
stream.on("resumed", ({ progress }) => {
  console.log(`从 ${progress}% 恢复`);
});
```

### 2. 语音能力集成

```typescript
import { Voice } from "@voltagent/voice";

const voice = new Voice({
  tts: openaiTTS(),      // 文本转语音
  stt: whisperSTT(),     // 语音转文本
});

const agent = new Agent({
  name: "voice-agent",
  voice,
});

// 语音对话
const response = await agent.voice.chat(audioStream);
```

### 3. Guardrails安全策略

```typescript
import { Guardrails } from "@voltagent/core";

const guardrails = new Guardrails({
  // 输入过滤
  input: [
    blockPII(),           // 阻止个人敏感信息
    blockPromptInjection(), // 阻止提示注入
  ],
  // 输出过滤
  output: [
    blockHarmfulContent(), // 阻止有害内容
    validateJSON(),        // 验证JSON格式
  ],
  // 工具调用限制
  tools: {
    maxCallsPerRequest: 10,
    timeout: 30000,
  },
});

const agent = new Agent({
  name: "safe-agent",
  guardrails,
});
```

---

## 部署策略

### 1. Cloud托管

```bash
# 使用VoltAgent Cloud
volt deploy --env production
```

**特点**:
- 自动扩缩容
- 内置VoltOps
- 全球CDN

### 2. Self-Hosted自托管

```typescript
// 自建VoltOps控制台
import { VoltOpsServer } from "@voltagent/voltops";

const server = new VoltOpsServer({
  port: 3000,
  database: {
    type: "postgres",
    url: process.env.DATABASE_URL,
  },
});

server.start();
```

### 3. Serverless部署

```typescript
// Vercel适配
import { handle } from "@voltagent/vercel";

export const POST = handle(agent);

// Netlify适配
import { handler } from "@voltagent/netlify";

export { handler };
```

---

## 最佳实践

### 1. Agent设计原则

| 原则 | 说明 | 示例 |
|------|------|------|
| 单一职责 | 每个Agent只做一件事 | Research Agent只收集信息 |
| 明确边界 | 定义清晰的输入输出 | Zod schema约束 |
| 可观测 | 所有操作可追踪 | 集成VoltOps |
| 可恢复 | 支持失败重试 | 幂等设计 |

### 2. 工作流设计模式

```typescript
// 模式1: 审批工作流
const approvalWorkflow = new Workflow()
  .step("submit")
  .step("validate")
  .step("approve")      // 人工审批点
  .step("execute");

// 模式2: 并行处理
const parallelWorkflow = new Workflow()
  .step("split")
  .andAll([
    step("process-a"),
    step("process-b"),
    step("process-c"),
  ])
  .step("merge");

// 模式3: 错误处理
const resilientWorkflow = new Workflow()
  .step("attempt", { retries: 3 })
  .step("fallback", { onError: "continue" })
  .step("notify");
```

### 3. 类型安全最佳实践

```typescript
// 1. 定义共享schema
const schemas = {
  stock: z.object({
    symbol: z.string(),
    price: z.number(),
    change: z.number(),
  }),
};

// 2. 工具使用共享schema
const stockTool = tool({
  name: "get_stock",
  parameters: schemas.stock.omit({ price: true, change: true }),
  returns: schemas.stock,
  execute: async ({ symbol }) => {
    return await fetchStock(symbol);
  },
});

// 3. Agent输出类型约束
const agent = new Agent<typeof schemas.stock>({
  name: "typed-agent",
  outputSchema: schemas.stock,
});
```

---

## 快速开始

```bash
# 1. 创建项目
npm create voltagent-app@latest my-agent

# 2. 安装依赖
cd my-agent
npm install

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 添加 OPENAI_API_KEY

# 4. 启动开发
npm run dev

# 5. 访问 VoltOps 控制台
open http://localhost:3000/voltops
```

---

## 资源

- **GitHub**: https://github.com/VoltAgent/voltagent
- **文档**: https://voltagent.dev
- **Discord**: https://discord.gg/voltagent
- **示例**: https://github.com/VoltAgent/examples

---

## 关联技能

- [Agent Harness Engineering](./agent-harness-engineering.md) - Agent架构设计
- [Agent Memory System](./agent-memory-system.md) - 记忆系统设计
- [OpenCode Multi-Model Agent](./opencode-multi-model-agent.md) - 多模型统一接口
