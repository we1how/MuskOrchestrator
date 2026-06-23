# Skill: Agent Harness Engineering

## 触发条件
- 设计Agent系统架构
- 开发Agent工具
- 任务编排与工作流设计
- 多Agent协作系统

---

## 核心概念

### Harness Formula
```
Harness = Tools + Knowledge + Observation + Action Interfaces + Permissions
```

Agent不是框架，不是提示链，而是"模型+环境"。

---

## 12阶段渐进式架构

| Session | 机制 | 核心洞察 |
|---------|------|----------|
| s01 | Agent Loop | "One loop & Bash is all you need" |
| s02 | Tool Use | Dispatch map: name→handler |
| s03 | TodoWrite | Planning with nag reminders |
| s04 | Subagents | 独立messages[]实现上下文隔离 |
| s05 | Skills | 按需加载，而非塞入system prompt |
| s06 | Context Compact | 三层压缩策略 |
| s07 | Tasks | 文件CRUD + 依赖图 |
| s08 | Background Tasks | Daemon threads + notify queue |
| s09 | Agent Teams | Teammates + JSONL mailboxes |
| s10 | Team Protocols | Request-response FSM |
| s11 | Autonomous Agents | Idle cycle + auto-claim |
| s12 | Worktree Isolation | Task-directory绑定 |

---

## 代码模式

### 1. 最小Agent循环
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
            return

        tool_results = execute_tools(response.content)
        messages.append({
            "role": "user",
            "content": tool_results
        })
```

### 2. 工具注册模式
```python
class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name: str, handler: Callable):
        self._tools[name] = handler

    def execute(self, name: str, params: dict) -> dict:
        if name not in self._tools:
            return {"error": f"Unknown tool: {name}"}
        return self._tools[name](**params)
```

### 3. 技能按需加载
```python
SKILLS_LIBRARY = {
    "tdd": "skills/tdd-workflow.md",
    "refactor": "skills/refactoring-patterns.md",
}

def load_skill(skill_name: str) -> str:
    if skill_name in SKILLS_LIBRARY:
        with open(SKILLS_LIBRARY[skill_name]) as f:
            return f.read()
    return f"Skill '{skill_name}' not found"
```

### 4. Worktree隔离
```
main-repo/
├── .git/
├── src/
└── .worktrees/
    ├── task-001/
    ├── task-002/
    └── task-003/
```

### 5. 任务依赖图
```python
def get_ready_tasks() -> list:
    all_tasks = load_all_tasks()
    completed = {t["id"] for t in all_tasks if t["status"] == "completed"}
    return [
        t for t in all_tasks
        if t["status"] == "pending"
        and all(dep in completed for dep in t["depends_on"])
    ]
```

---

## 三层上下文压缩

```
Layer 1: System Prompt (固定)
Layer 2: Conversation History (动态，需压缩)
Layer 3: Tool Results (临时，可摘要)
```

压缩策略：
- Summarization: 长对话历史摘要
- Truncation: 保留最近N轮
- Hierarchical: 重要消息优先保留

---

## 来源
- https://github.com/shareAI-lab/learn-claude-code
- 学习日期: 2026-03-19
