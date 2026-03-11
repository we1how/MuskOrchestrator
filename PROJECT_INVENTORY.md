# 项目目录清单 (PROJECT_INVENTORY.md)

> **维护原则**：每次增加、修改、删除文件/文件夹时，必须同步更新本清单
> **自动更新**：定时任务执行后自动更新
> **手动更新**：其他变更需用户确认后更新
> **最后更新**：2026-03-11
> **版本**：v2.0 (迁移完成)

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
| `memory/agents/engineer/LEARNING.md` | 产品工程师学习记录（每日更新） | 2026-03-11 |
| `memory/agents/analyst/LEARNING.md` | 量化分析师学习记录（每日更新） | 2026-03-11 |
| `memory/agents/mentor/LEARNING.md` | 成长导师学习记录（每日更新） | 2026-03-11 |
| `memory/agents/creator/LEARNING.md` | 内容创作者学习记录（每日更新） | 2026-03-11 |
| `memory/conversations/` | 每日学习执行记录存档 | 2026-03-11 |
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
| `scripts/cron/jobs.json` | 定时任务配置（Claude Code格式） | 2026-03-08 |
| `scripts/daily_learning.py` | 每日微学习执行脚本 | 2026-03-08 |
| `scripts/weekly_review.py` | 每周回顾执行脚本 | 2026-03-08 |
| `scripts/monthly_evolution.py` | 月度人格进化脚本 | 2026-03-08 |
| `scripts/git_auto_commit.sh` | Git自动提交脚本 | 2026-03-08 |
| `scripts/archive_agent_outputs.py` | Agent输出归档脚本（路径已适配） | 2026-03-08 |

---

## 📁 Skills系统

### /skills/ - 可复用工具

| 路径 | 描述 | 修改时间 |
|------|------|----------|
| `skills/daily-learning/SKILL.md` | 每日微学习Skill（Claude Code格式） | 2026-03-08 |
| `skills/weekly-review/SKILL.md` | 每周深度回顾Skill | 2026-03-08 |
| `skills/monthly-evolution/SKILL.md` | 月度人格进化Skill | 2026-03-08 |
| `skills/knowledge-archive/SKILL.md` | 知识归档Skill | 2026-03-08 |
| `skills/everything-claude-code/` | 完整技能库（673个文件，从OpenClaw迁移） | 2026-03-08 |
| `skills/social-media-crawler/` | 社交媒体爬虫技能 | 2026-03-08 |
| `skills/stock-local-db-init/` | 股票数据库初始化技能 | 2026-03-08 |
| `skills/stock-local-db-daily-update/` | 股票数据库日更技能 | 2026-03-08 |
| `skills/tavily-search/` | Tavily搜索技能 | 2026-03-08 |
| `skills/coding/markitdown-document-pipeline.md` | MarkItDown文档预处理技能 | 2026-03-11 |
| `skills/analysis/a-share-multi-agent-framework.md` | A股多Agent量化框架技能 | 2026-03-11 |
| `skills/planning/ooda-decision-framework.md` | OODA快速决策框架技能 | 2026-03-11 |
| `skills/communication/reddit-precision-marketing.md` | Reddit精准获客技能 | 2026-03-11 |

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
| Skills | 25 (673个文件) |
| 定时任务 | 8 (7启用, 1禁用) |
| 脚本工具 | 9 |
| 知识文档 | 40+ |

---

## 📋 当前待办清单 (TODO)

> **最后更新**：2026-03-08
> **状态**：动态更新，完成即归档到「已完成」

### 🔴 进行中 (In Progress)

| 优先级 | 项目 | 任务 | 预计完成 | 状态 |
|--------|------|------|----------|------|
| 无 | - | - | - | - |

### ⏸️ 待启动 (Backlog)

| 优先级 | 项目 | 任务 | 预计完成 | 阻塞原因 |
|--------|------|------|----------|----------|
| **P1** | **Launchd** | 配置并启动launchd定时任务 | 2026-03-09 | 需用户确认 |
| **P2** | **Testing** | 测试Agent调用和工作流 | 2026-03-09 | - |

### ✅ 已完成 (Completed)

| 日期 | 项目 | 任务 | 成果 |
|------|------|------|------|
| 2026-03-08 | **Infrastructure** | 创建完整目录结构 | 9个一级目录 |
| 2026-03-08 | **Agents** | 创建6个Agent人格定义 | 12个定义文件 |
| 2026-03-08 | **Migration** | P0: 迁移定时任务+技能库+量化平台 | cron/, skills/, stock-platform/ |
| 2026-03-08 | **Migration** | P1: 迁移知识库+学习记录+报告 | knowledge/, memory/, reports/ |
| 2026-03-08 | **Migration** | P2: 迁移脚本+配置+Agent工作区 | scripts/, FUSION-WORKFLOW/ |
| 2026-03-08 | **Adaptation** | 格式适配: OpenClaw → Claude Code | SKILL.md, jobs.json, Python脚本 |
| 2026-03-08 | **Automation** | 创建launchd定时任务配置 | 3个plist + 3个sh |

---

## 🚀 下一步行动

1. **配置launchd定时任务**（高优先级）
   ```bash
   cd /Users/linweihao/project/MuskOrchestrator/scripts/launchd
   ./install.sh
   ```

2. **测试定时任务脚本**（高优先级）
   ```bash
   python scripts/daily_learning.py
   python scripts/weekly_review.py
   ./scripts/git_auto_commit.sh
   ```

3. **测试Agent调用**（中优先级）
   - 在Claude Code中测试 `@planner`, `@engineer` 等Agent

4. **Git提交迁移成果**
   ```bash
   git add -A
   git commit -m "Migration complete v2.0: OpenClaw → Claude Code with adaptations"
   git push origin main
   ```

---

_维护本清单是项目管理的必要工作，是冷酷法则的延伸_ 🚀

**版本**: v1.0
**创建**: 2026-03-08
**迁移源**: /Users/linweihao/.openclaw/
