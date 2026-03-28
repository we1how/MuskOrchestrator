# Open SWE - 异步编码Agent框架

## 概述

Open SWE是LangChain官方开源的企业级异步编码Agent框架，帮助企业构建类似Stripe、Ramp、Coinbase内部使用的编码Agent。

**核心特性**：
- 异步非阻塞任务执行
- 子Agent + 中间件架构
- 精选工具哲学（15个核心工具）
- 多平台触发（Slack/Linear/GitHub）
- 线程级持久化沙箱

---

## 架构设计

### 1. 异步Agent架构

```python
# 核心：中间件实现运行中消息注入
check_message_queue_before_model  # 每次模型调用前检查消息队列
```

| 特性 | 同步Agent | 异步Agent |
|------|-----------|-----------|
| 响应方式 | 即时响应 | 👀确认+后台执行 |
| 用户交互 | 单次 | 支持执行中跟进 |
| 任务时长 | 短任务 | 长时任务友好 |
| 状态管理 | 无状态 | 线程级持久化沙箱 |

### 2. 子Agent + 中间件架构

```
Deep Agent (主Agent)
    ├── 工具调用
    ├── 子Agent派生 (并行子任务)
    └── 中间件链
        ├── ToolErrorMiddleware
        ├── check_message_queue_before_model
        └── SafetyNetMiddleware
```

### 3. 精选工具集（约15个）

| 类别 | 工具 | 用途 |
|------|------|------|
| 代码操作 | read, edit, bash | 文件读写、命令执行 |
| 协作沟通 | linear_comment, slack_thread_reply | 进度更新 |
| 版本控制 | commit_and_open_pr | 自动提交PR |
| 网络请求 | http_request, fetch_url | 外部API调用 |

---

## 快速开始

### 安装

```bash
git clone https://github.com/langchain-ai/open-swe
cd open-swe
pip install -e ".[dev]"
```

### 配置

```yaml
# config.yaml
integrations:
  slack:
    bot_token: ${SLACK_BOT_TOKEN}
    signing_secret: ${SLACK_SIGNING_SECRET}

sandbox:
  provider: modal  # modal | daytona | runloop | langsmith
  image: python:3.11-slim
```

### 创建Agent

```python
from langgraph_deep_agents import create_deep_agent

agent = create_deep_agent(
    model="anthropic:claude-opus-4-6",
    system_prompt=construct_system_prompt(repo_dir, ...),
    tools=[http_request, fetch_url, commit_and_open_pr, ...],
    backend=sandbox_backend,
    middleware=[
        ToolErrorMiddleware(),
        check_message_queue_before_model,
    ],
)
```

---

## 核心模式

### 1. 子Agent派生

```python
async def parallel_analysis(self, files: list[str]) -> list[AnalysisResult]:
    """并行分析多个文件"""
    subagents = [
        self.spawn_subagent(
            task=f"分析文件: {file}",
            context={"file": file, "analysis_type": "complexity"}
        )
        for file in files
    ]

    results = await asyncio.gather(*[
        subagent.run() for subagent in subagents
    ])

    return results
```

### 2. 中间件实现

```python
from open_swe.middleware import Middleware

class SafetyNetMiddleware(Middleware):
    """安全网中间件"""

    DANGEROUS_PATTERNS = [
        r"rm\s+-rf\s+/",
        r"DROP\s+DATABASE",
    ]

    async def before_tool_call(self, tool_name: str, params: dict) -> dict:
        if tool_name == "bash":
            command = params.get("command", "")
            for pattern in self.DANGEROUS_PATTERNS:
                if re.search(pattern, command, re.IGNORECASE):
                    raise SecurityError(f"危险命令被拦截: {command}")
        return params
```

### 3. 自定义工具

```python
from open_swe.tools import Tool

class CustomAnalysisTool(Tool):
    name = "analyze_code_complexity"
    description = "分析代码复杂度并返回报告"

    async def run(self, file_path: str) -> dict:
        content = await self.read_file(file_path)
        complexity = self._calculate_complexity(content)

        return {
            "file": file_path,
            "complexity_score": complexity.score,
            "recommendations": complexity.suggestions
        }
```

---

## 触发机制

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

---

## 相关资源

- **项目**: https://github.com/langchain-ai/open-swe
- **Deep Agents**: https://github.com/langchain-ai/deep-agents
- **LangGraph**: https://langchain-ai.github.io/langgraph/

---

*技能来源: Open SWE 学习记录 (2026-03-20)*
*触发条件: 企业级Agent开发、异步任务处理、多Agent协作*
