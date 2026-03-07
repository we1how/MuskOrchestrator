# 项目目录清单 (PROJECT_INVENTORY.md)

> **维护原则**：每次增加、修改、删除文件/文件夹时，必须同步更新本清单
> **自动更新**：定时任务执行后自动更新
> **手动更新**：其他变更需用户确认后更新
> **最后更新**：2026-03-08
> **版本**：v1.0

---

## 📁 根目录文件

| 文件路径 | 一句话描述 | 最后修改 |
|----------|-----------|----------|
| `CLAUDE.md` | 主人格定义（冷酷CEO+可反驳模式） | 2026-03-08 |
| `AGENTS.md` | Agent团队协作规范 | 2026-03-08 |
| `HEARTBEAT.md` | 自我成长系统配置（v2.3） | 2026-03-08 |
| `USER.md` | 用户画像（从OpenClaw迁移） | 2026-03-08 |
| `MEMORY.md` | 长期记忆（从OpenClaw迁移） | 2026-03-08 |
| `MIGRATION_PLAN.md` | 迁移方案文档 | 2026-03-08 |
| `PROJECT_INVENTORY.md` | 本文件（项目清单） | 2026-03-08 |

---

## 📁 Agent系统

### /subagents/ - Agent定义

| 路径 | 描述 | 修改时间 |
|------|------|----------|
| `subagents/planner/CLAUDE.md` | 规划专家人格定义 | 2026-03-08 |
| `subagents/planner/AGENT.md` | 规划专家系统提示 | 2026-03-08 |
| `subagents/engineer/CLAUDE.md` | 产品工程师人格定义 | 2026-03-08 |
| `subagents/engineer/AGENT.md` | 产品工程师系统提示 | 2026-03-08 |
| `subagents/analyst/CLAUDE.md` | 量化分析师人格定义 | 2026-03-08 |
| `subagents/analyst/AGENT.md` | 量化分析师系统提示 | 2026-03-08 |
| `subagents/mentor/CLAUDE.md` | 成长导师人格定义 | 2026-03-08 |
| `subagents/mentor/AGENT.md` | 成长导师系统提示 | 2026-03-08 |
| `subagents/creator/CLAUDE.md` | 内容创作者人格定义 | 2026-03-08 |
| `subagents/creator/AGENT.md` | 内容创作者系统提示 | 2026-03-08 |
| `subagents/reviewer/CLAUDE.md` | 审查员人格定义 | 2026-03-08 |
| `subagents/reviewer/AGENT.md` | 审查员系统提示 | 2026-03-08 |

---

## 📁 记忆系统

### /memory/ - Agent学习记录

| 路径 | 描述 | 修改时间 |
|------|------|----------|
| `memory/agents/engineer/LEARNING.md` | 产品工程师学习记录（迁移） | 2026-03-08 |
| `memory/agents/analyst/LEARNING.md` | 量化分析师学习记录（迁移） | 2026-03-08 |
| `memory/agents/mentor/LEARNING.md` | 成长导师学习记录（迁移） | 2026-03-08 |
| `memory/agents/creator/LEARNING.md` | 内容创作者学习记录（迁移） | 2026-03-08 |
| `memory/reports/weekly/` | 周报存档目录 | 2026-03-08 |
| `memory/reports/daily/` | 日报存档目录 | 2026-03-08 |

---

## 📁 知识库

### /knowledge/ - 知识存储

| 路径 | 描述 | 修改时间 |
|------|------|----------|
| `knowledge/books/` | 读书笔记存档（从OpenClaw迁移） | 2026-03-08 |
| `knowledge/research/` | 研究报告存档（从OpenClaw迁移） | 2026-03-08 |
| `knowledge/insights/` | 洞察提取目录 | 2026-03-08 |

---

## 📁 产品项目

### /projects/ - 实际项目

| 路径 | 描述 | 修改时间 |
|------|------|----------|
| `projects/stock-platform/` | 股票量化平台（从OpenClaw迁移） | 2026-03-08 |

---

## 📁 自动化系统

### /scripts/ - 脚本工具

| 路径 | 描述 | 修改时间 |
|------|------|----------|
| `scripts/launchd/` | macOS launchd定时任务配置 | 2026-03-08 |
| `scripts/launchd/*.plist` | 定时任务plist文件 | 2026-03-08 |
| `scripts/launchd/*.sh` | 定时任务执行脚本 | 2026-03-08 |

---

## 📁 Skills系统

### /skills/ - 可复用工具

| 路径 | 描述 | 修改时间 |
|------|------|----------|
| `skills/daily-learning/` | 每日微学习Skill | 2026-03-08 |
| `skills/project-tracker/` | 项目跟踪Skill | 2026-03-08 |
| `skills/knowledge-archive/` | 知识归档Skill | 2026-03-08 |

---

## 📁 其他目录

| 路径 | 描述 | 修改时间 |
|------|------|----------|
| `docs/` | 文档存档 | 2026-03-08 |
| `docs/archive/` | 原始文档存档 | 2026-03-08 |
| `data/` | 数据存储 | 2026-03-08 |
| `data/agent-intelligence/` | Agent情报数据 | 2026-03-08 |
| `logs/` | 日志文件 | 2026-03-08 |

---

## 🔧 维护指南

### 何时更新本清单

**自动更新**（定时任务）：
- ✅ 每日学习记录更新
- ✅ 周报生成
- ✅ 归档任务执行

**需确认更新**（其他变更）：
- ✅ 新增文件/文件夹
- ✅ 修改文件/文件夹名称
- ✅ 移动文件/文件夹位置
- ✅ 删除文件/文件夹
- ✅ 文件功能发生重大变化

### 如何更新

1. **新增条目**：在对应目录下按字母顺序插入新行
2. **修改条目**：更新描述和修改时间
3. **删除条目**：标记为 `~~已删除~~` 或直接从清单移除
4. **移动条目**：在原位置标记 `→ 已移动至新路径`，在新位置添加条目

### 更新格式

```markdown
| `路径/文件名` | 一句话描述功能 | YYYY-MM-DD |
```

---

## 📊 统计信息

| 类别 | 数量 |
|------|------|
| 根目录文件 | 7 |
| Agent定义 | 12 (6个Agent × 2文件) |
| 一级目录 | 9 |
| 已迁移项目 | 1 (stock-platform) |

---

## 📋 当前待办清单 (TODO)

> **最后更新**：2026-03-08
> **状态**：动态更新，完成即归档到「已完成」

### 🔴 进行中 (In Progress)

| 优先级 | 项目 | 任务 | 预计完成 | 状态 |
|--------|------|------|----------|------|
| **P0** | **Migration** | 完成OpenClaw到Claude Code迁移 | 2026-03-08 | 🔄 进行中 |

### ⏸️ 待启动 (Backlog)

| 优先级 | 项目 | 任务 | 预计完成 | 阻塞原因 |
|--------|------|------|----------|----------|
| **P1** | **Launchd** | 配置并启动launchd定时任务 | 2026-03-08 | 需用户确认 |
| **P1** | **Testing** | 测试Agent调用和工作流 | 2026-03-08 | 等待迁移完成 |
| **P2** | **Skills** | 创建/daily-learning等Skill | 2026-03-09 | 前置依赖 |

### ✅ 已完成 (Completed)

| 日期 | 项目 | 任务 | 成果 |
|------|------|------|------|
| 2026-03-08 | **Infrastructure** | 创建完整目录结构 | 9个一级目录 |
| 2026-03-08 | **Agents** | 创建6个Agent人格定义 | 12个定义文件 |
| 2026-03-08 | **Migration** | 迁移学习记录和知识库 | books/ research/ |
| 2026-03-08 | **Migration** | 迁移stock-platform项目 | projects/ |
| 2026-03-08 | **Automation** | 创建launchd定时任务配置 | 3个plist + 3个sh |

---

## 🚀 下一步行动

1. **配置launchd定时任务**
   ```bash
   cd /Users/linweihao/project/MuskOrchestrator/scripts/launchd
   ./install.sh
   ```

2. **测试Agent调用**
   - 打开Claude Code
   - 测试每个Agent的调用

3. **创建Skills**
   - /daily-learning
   - /project-tracker
   - /knowledge-archive

4. **首次Git提交**
   ```bash
   git add -A
   git commit -m "Migration complete: OpenClaw → Claude Code v1.0"
   ```

---

_维护本清单是项目管理的必要工作，是冷酷法则的延伸_ 🚀

**版本**: v1.0
**创建**: 2026-03-08
**迁移源**: /Users/linweihao/.openclaw/
