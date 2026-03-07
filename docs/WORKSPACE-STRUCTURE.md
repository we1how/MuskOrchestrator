# 📁 MuskOrchestrator 工作空间目录结构

> 最后更新：2026-03-08 (迁移自 OpenClaw)

```
/Users/linweihao/project/MuskOrchestrator/
│
├── 📋 核心配置文件 (根目录)
│   ├── CLAUDE.md             # 🚀 CEO人格定义（MuskOrchestrator）
│   ├── AGENTS.md             # Agent系统规范
│   ├── USER.md               # 👤 用户档案
│   ├── MEMORY.md             # 💾 长期记忆
│   ├── HEARTBEAT.md          # 💓 Agent成长系统配置
│   ├── PROJECT_INVENTORY.md  # 📊 项目清单（自动更新）
│   └── README.md             # 项目说明
│
├── 📚 docs/                  # 文档目录
│   ├── templates/
│   │   └── FUSION-TEMPLATE.md    # 🤖 融合工作流模板
│   ├── reports/
│   │   └── team-skill-upgrade-report.md
│   ├── guides/               # 使用指南
│   ├── research/             # 研究报告
│   └── WORKSPACE-STRUCTURE.md    # 📁 本文件
│
├── 🤖 subagents/             # 6个子Agent定义
│   ├── planner/              # 📋 规划专家
│   │   └── AGENT.md
│   ├── engineer/             # ⚡ 产品工程师
│   │   └── AGENT.md
│   ├── analyst/              # 📊 量化分析师
│   │   └── AGENT.md
│   ├── mentor/               # 🎯 成长导师
│   │   └── AGENT.md
│   ├── creator/              # 🚀 内容创作者
│   │   └── AGENT.md
│   └── reviewer/             # 🔍 审查员
│       └── AGENT.md
│
├── 💾 memory/                # 记忆文件夹
│   ├── agents/               # 各Agent记忆
│   │   ├── planner/
│   │   ├── engineer/
│   │   │   └── LEARNING.md
│   │   ├── analyst/
│   │   │   └── LEARNING.md
│   │   ├── mentor/
│   │   │   └── LEARNING.md
│   │   ├── creator/
│   │   │   └── LEARNING.md
│   │   └── reviewer/
│   ├── learning-plans/       # 学习计划
│   └── reports/              # 报告存档
│       ├── archive/          # 归档报告
│       ├── event-driven/     # 事件驱动报告
│       └── weekly/           # 周报
│
├── 📚 knowledge/             # 知识库
│   ├── research/             # 研究报告
│   ├── insights/             # 洞察总结
│   └── books/                # 读书笔记
│
├── 🔧 scripts/               # 脚本库
│   ├── cron/
│   │   └── jobs.json         # 定时任务配置
│   ├── launchd/              # macOS定时任务
│   ├── archive_agent_outputs.py    # Agent输出归档
│   ├── sync_agent_report.py        # 报告同步
│   ├── trigger_archive.py          # 归档触发器
│   ├── daily_learning.py           # 每日学习脚本
│   ├── weekly_review.py            # 每周回顾脚本
│   └── git_auto_commit.sh          # Git自动提交
│
├── 🛠️ skills/                # 技能库 (20+)
│   ├── daily-learning/
│   ├── weekly-review/
│   ├── knowledge-archive/
│   ├── social-media-crawler/
│   ├── stock-local-db-init/
│   ├── stock-local-db-daily-update/
│   ├── tavily-search/
│   └── ... (其他技能)
│
├── 📂 projects/              # 项目目录
│   └── stock-platform/       # 量化平台项目
│
└── 📊 data/                  # 数据存储
    ├── agent-intelligence/
    └── stock/
```

---

## 🚀 快速导航

### 我是谁？
→ 读 `CLAUDE.md`

### 我的团队？
→ 读 `AGENTS.md`

### Agent 成长系统？
→ 读 `HEARTBEAT.md`

### 书籍笔记放哪里？
→ `knowledge/books/`

### Agent 学习日志？
→ `memory/agents/{agent-name}/LEARNING.md`

### 归档脚本？
→ `scripts/archive_agent_outputs.py`

---

## 📊 统计数据

| 类别 | 数量 |
|-----|------|
| 子 Agent | 6 个 |
| 学习记录 | 4 份 |
| 归档脚本 | 8 个 |
| 定时任务 | 7 个 |
| Skills | 20+ |
| 项目 | 1 个 (stock-platform) |
| 知识文档 | 40+ |

---

## 🔄 迁移记录

| 时间 | 操作 | 状态 |
|-----|------|------|
| 2026-03-08 | 从 OpenClaw 迁移核心文档 | ✅ 完成 |
| 2026-03-08 | 迁移 Agent LEARNING.md | ✅ 完成 |
| 2026-03-08 | 迁移归档脚本并更新路径 | ✅ 完成 |
| 2026-03-08 | 迁移 skills/ (20+ 技能) | ✅ 完成 |
| 2026-03-08 | 迁移 stock-platform 项目 | ✅ 完成 |
| 2026-03-08 | 清理旧 OpenClaw 路径引用 (14个文件) | ✅ 完成 |
| 2026-03-08 | 整理根目录文档到 docs/ | ✅ 完成 |
| 2026-03-08 | 更新本目录结构文档 | ✅ 完成 |

---

_第一性原理，永不懈怠，冷酷无情，改变世界_ 🚀
