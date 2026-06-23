# Agent Kernel: 无框架的AI Agent状态管理

> **用3个Markdown文件实现AI Agent的长期记忆和状态持久化**
>
> 来源: [GitHub - oguzbilgic/agent-kernel](https://github.com/oguzbilgic/agent-kernel) | HN Show HN #1 (March 25, 2026)

---

## 核心概念

Agent Kernel是一种**极简主义**的AI Agent状态管理方案——无需复杂框架（LangChain/LangGraph）、无需向量数据库、无需部署基础设施，仅用**3个Markdown文件 + git**即可实现Agent的长期记忆。

### 为什么重要

| 传统方案 | Agent Kernel |
|----------|--------------|
| LangChain/LangGraph学习曲线陡峭 | 零学习成本，即插即用 |
| 需要向量数据库和复杂部署 | 仅需文件系统和git |
| 框架锁定，难以迁移 | 任何AI编码工具都支持 |
| 过度工程化 | 极简设计，聚焦核心问题 |

---

## 文件结构

```
my-agent/
├── AGENTS.md           # 内核协议（通用，不编辑）
├── IDENTITY.md         # Agent身份定义（Agent自维护）
├── KNOWLEDGE.md        # 知识文件索引（Agent自维护）
├── knowledge/          # 可变状态（当前事实）
│   ├── preferences.md
│   ├── config.md
│   └── domain-specific.md
└── notes/              # 仅追加叙事（历史记录）
    ├── 2026-03-25.md
    ├── 2026-03-26.md
    └── ...
```

### 双模式记忆架构

| 类型 | 位置 | 特性 | 类比人类记忆 |
|------|------|------|-------------|
| **State** | `knowledge/` | 可变（Mutable） | 工作记忆 |
| **Narrative** | `notes/` | 仅追加（Append-only） | 情节记忆 |

---

## 快速开始

### 1. 初始化Agent

```bash
# 克隆内核模板
git clone https://github.com/oguzbilgic/agent-kernel.git my-agent
cd my-agent

# 初始化新仓库
rm -rf .git
git init
git add .
git commit -m "Initial agent kernel"
```

### 2. 启动Agent

```bash
# Claude Code
claude

# OpenCode
opencode

# Cursor（打开项目文件夹）
cursor .

# 其他支持AGENTS.md的工具...
```

### 3. Agent自主维护

Agent会自动：
1. **定义身份** —— 首次启动时询问"你是谁"
2. **维护索引** —— 更新`KNOWLEDGE.md`记录知识文件位置
3. **记录会话** —— 在`notes/`下创建每日日志
4. **更新状态** —— 在`knowledge/`下维护可变事实

---

## 核心协议（AGENTS.md）

```markdown
# Agent Kernel Protocol

## 身份定义
- 首次启动时，询问用户定义你的身份
- 将身份写入`IDENTITY.md`
- 后续会话读取`IDENTITY.md`恢复上下文

## 记忆管理

### 知识文件（knowledge/）
- 存储可变状态：配置、偏好、当前事实
- 格式：Markdown，每个主题一个文件
- 更新时：直接编辑，保持最新状态

### 会话日志（notes/）
- 存储不可变历史：每日做了什么、学了什么
- 格式：`YYYY-MM-DD.md`
- 规则：仅追加，永不修改历史记录

## 启动流程
1. 读取`IDENTITY.md`恢复身份
2. 读取`KNOWLEDGE.md`了解知识结构
3. 读取相关`knowledge/`文件恢复状态
4. 询问用户今日任务
5. 会话结束时更新相关文件并提交git
```

---

## 多Agent架构

### 目录结构

```
~/agents/
├── stock-analyst/          # 股票分析Agent
│   ├── AGENTS.md
│   ├── IDENTITY.md         # "我是股票分析专家..."
│   ├── KNOWLEDGE.md
│   ├── knowledge/
│   │   ├── watchlist.md    # 自选股列表
│   │   ├── strategies.md   # 交易策略
│   │   └── market-data.md  # 市场数据缓存
│   └── notes/
│       ├── 2026-03-25.md   # 今日分析记录
│       └── ...
├── content-creator/        # 内容创作Agent
├── code-reviewer/          # 代码审查Agent
└── health-coach/           # 健康教练Agent
```

### Agent间协作

**模式1: 知识传递**
```bash
# Analyst发现投资机会
# 写入: stock-analyst/knowledge/opportunities.md

# Creator读取并生成内容
# 读取: stock-analyst/knowledge/opportunities.md
# 写入: content-creator/knowledge/ideas.md
```

**模式2: 任务委托**
```markdown
<!-- notes/2026-03-25.md -->
## 今日任务
- [x] 分析A股市场趋势
- [ ] 委托@creator生成分析报告
  - 参考: `~/agents/stock-analyst/knowledge/analysis.md`
  - 要求: 适合小红书的格式
```

**模式3: 共同知识库**
```
~/agents/
├── shared-knowledge/       # 共享知识库
│   ├── common-sense.md
│   ├── user-preferences.md
│   └── project-goals.md
├── stock-analyst/
└── content-creator/
```

---

## 最佳实践

### 1. Git工作流

```bash
# 每次会话后提交
git add .
git commit -m "Session $(date +%Y-%m-%d): [简要描述]"

# 定期推送远程（多设备同步）
git push origin main

# 重要决策打标签
git tag -a v1.0 -m "Agent身份定义完成"
```

### 2. 知识文件组织

```markdown
<!-- knowledge/preferences.md -->
# 用户偏好

## 沟通风格
- 喜欢直接、简洁的回答
- 重视可执行的建议
- 欣赏结构化的输出

## 关注领域
- 投资：A股、量化交易
- 编程：Python、AI Agent
- 阅读：投资经典、技术书籍

## 目标
- 2026年股票盈利至十万
- 上线1个有价值的产品
- 阅读50本书
```

### 3. 会话日志格式

```markdown
<!-- notes/2026-03-25.md -->
# 2026-03-25 会话记录

## 今日任务
1. 学习Agent Kernel项目
2. 设计多Agent架构

## 关键洞察
- Agent Kernel代表"无框架化"趋势
- 双模式记忆（State+Narrative）设计精妙
- 多Agent架构可用git仓库隔离

## 行动项
- [ ] 为6个Agent创建Kernel仓库
- [ ] 撰写学习记录
- [ ] 创建技能文件

## 相关资源
- https://github.com/oguzbilgic/agent-kernel
- HN Show HN #1 (March 25, 2026)
```

### 4. 与现有工具集成

**Claude Code**
```bash
# 在Agent目录下启动
claude ~/agents/stock-analyst
# 自动读取AGENTS.md
```

**Cursor**
```bash
# 打开Agent项目
cursor ~/agents/content-creator
# 读取.cursorrules + AGENTS.md
```

**OpenCode**
```bash
cd ~/agents/code-reviewer
opencode
# 读取AGENTS.md
```

---

## 应用场景

### 场景1: 个人AI助手
- 长期记忆用户偏好和习惯
- 跨会话保持上下文
- 多设备同步（通过git）

### 场景2: 专业化Agent团队
- 股票分析Agent
- 内容创作Agent
- 代码审查Agent
- 每个Agent独立进化

### 场景3: 项目专用Agent
- 每个项目一个Agent仓库
- 项目知识随Agent持久化
- 团队成员共享Agent上下文

### 场景4: 学习记录Agent
- 记录每日学习内容
- 自动关联相关知识
- 构建个人知识图谱

---

## 进阶技巧

### 1. 模板化创建

```bash
#!/bin/bash
# create-agent.sh

AGENT_NAME=$1
TEMPLATE_REPO="https://github.com/oguzbilgic/agent-kernel.git"

git clone $TEMPLATE_REPO ~/agents/$AGENT_NAME
cd ~/agents/$AGENT_NAME
rm -rf .git
git init

# 自定义AGENTS.md
cat > AGENTS.md << EOF
# $AGENT_NAME Agent

## 身份
[启动时定义]

## 专长
- [待定义]

## 工作流
1. 读取历史上下文
2. 执行用户任务
3. 更新知识文件
4. 提交git
EOF

git add .
git commit -m "Initialize $AGENT_NAME agent"

echo "Agent $AGENT_NAME created at ~/agents/$AGENT_NAME"
```

### 2. 自动化提交

```bash
#!/bin/bash
# auto-commit.sh

AGENT_DIR=$1
cd $AGENT_DIR

git add .
if [ -n "$(git status --porcelain)" ]; then
    git commit -m "Auto-commit: $(date '+%Y-%m-%d %H:%M')"
    echo "Committed changes"
fi
```

### 3. Agent健康检查

```bash
#!/bin/bash
# agent-health.sh

for agent in ~/agents/*/; do
    echo "Checking $(basename $agent)..."
    cd $agent

    # 检查是否有未提交更改
    if [ -n "$(git status --porcelain)" ]; then
        echo "  ⚠️  Uncommitted changes"
    fi

    # 检查最近提交时间
    LAST_COMMIT=$(git log -1 --format=%ct)
    NOW=$(date +%s)
    DAYS_SINCE=$(( (NOW - LAST_COMMIT) / 86400 ))

    if [ $DAYS_SINCE -gt 7 ]; then
        echo "  ⚠️  Last commit $DAYS_SINCE days ago"
    fi

    # 检查文件结构
    if [ ! -f "AGENTS.md" ]; then
        echo "  ❌ Missing AGENTS.md"
    fi
    if [ ! -f "IDENTITY.md" ]; then
        echo "  ⚠️  Missing IDENTITY.md (not initialized)"
    fi
done
```

---

## 与其他方案对比

| 方案 | 复杂度 | 依赖 | 学习曲线 | 适用场景 |
|------|--------|------|----------|----------|
| **Agent Kernel** | 极简 | 无 | 零 | 个人Agent、快速原型 |
| LangGraph | 高 | Python库 | 陡峭 | 复杂工作流编排 |
| LangChain | 中 | Python/JS库 | 中等 | 通用Agent开发 |
| CrewAI | 中 | Python库 | 中等 | 多Agent协作 |
| AutoGPT | 高 | 多依赖 | 陡峭 | 自主任务执行 |

---

## 相关资源

- **原文**: https://github.com/oguzbilgic/agent-kernel
- **HN讨论**: https://news.ycombinator.com/item?id=[Show HN]
- **类似项目**:
  - [Wave Orchestration](https://mcpmarket.com/tools/skills/wave-orchestration) - Claude Code并行Agent
  - [LangGraph](https://github.com/langchain-ai/langgraph) - 复杂状态管理
- **相关概念**: Stateful AI Agents, Memory Architecture, Agent Protocols

---

## 触发条件

- 设计AI Agent系统
- 需要Agent长期记忆
- 构建多Agent架构
- 避免框架锁定
- 快速原型验证

## 核心输出

- Agent Kernel仓库模板
- 多Agent协作协议
- 个性化Agent配置
- 可复用的记忆系统

---

*技能内化日期: 2026-03-25*
*来源: HN Show HN #1 + GitHub开源项目*
