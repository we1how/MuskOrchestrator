# Agent Commons: 多Agent知识共享协议

> **让AI Agent拥有"集体记忆"，避免重复犯错的共享知识基础设施**

---

## 核心概念

Agent Commons是一种多Agent知识共享架构，让独立的AI Agent能够：
- **查询**过往学习：检索其他Agent已验证的解决方案
- **贡献**新知识：将自身学习添加到共享知识库
- **避免重复犯错**：不再每个Agent独立撞墙消耗token

灵感来源：Mozilla AI的[Cq项目](https://github.com/mozilla-ai/cq)（Stack Overflow for Agents）

---

## 为什么需要Agent Commons

### 当前问题：Agent的"集体失忆"

```
Agent A遇到错误X → 学习解决方案 → 解决问题
Agent B遇到错误X → 无法访问A的学习 → 重新学习 → 解决问题
Agent C遇到错误X → 无法访问A/B的学习 → 重新学习 → 解决问题
        ↓
    重复消耗token和计算资源
```

### Agent Commons解决方案

```
Agent A遇到错误X → 学习解决方案 → 贡献到Commons → 解决问题
Agent B遇到错误X → 查询Commons → 获取A的方案 → 解决问题
Agent C遇到错误X → 查询Commons → 获取已验证方案 → 解决问题
        ↓
    集体智慧，避免重复
```

---

## 核心原则

### 1. 多Agent验证 > 单模型猜测

| 维度 | 单Agent | Agent Commons |
|------|---------|---------------|
| 可靠性 | 单Agent最佳猜测 | 多Agent跨代码库确认 |
| 置信度 | 无法验证 | 置信度评分 + 声誉信号 |
| 学习模式 | 孤立学习 | 集体智慧 |

**原则**：被多个Agent在多个代码库中确认的知识，比单个模型的猜测更有权重。

### 2. 知识即基础设施

Agent学习不应是一次性的，而应是可积累的：
- 每次解决问题都是知识资产
- 知识应该被存储、索引、检索
- 知识应该随时间演化（更新、废弃、改进）

### 3. 开放标准，避免锁定

- 不强迫使用单一Agent工具
- 推动Agent间互操作
- 社区驱动的知识共享

---

## 技术架构

### 三层架构

```
┌─────────────────────────────────────────────────────────┐
│                    Agent 插件层                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │Claude Code│ │ OpenCode │ │  Cursor  │ │  Codex   │   │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘   │
└───────┼────────────┼────────────┼────────────┼─────────┘
        │            │            │            │
        └────────────┴──────┬─────┴────────────┘
                            │
┌───────────────────────────┼─────────────────────────────┐
│                      MCP Server                          │
│              (本地知识存储管理)                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │
│  │  Knowledge  │ │   Notes     │ │   Config    │        │
│  │   Store     │ │   (日志)     │ │   (配置)     │        │
│  └─────────────┘ └─────────────┘ └─────────────┘        │
└───────────────────────────┬─────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼───────┐  ┌────────▼────────┐  ┌──────▼──────┐
│   Team API    │  │  Human-in-Loop  │  │  Analytics  │
│  (团队共享)    │  │   (人工审核)     │  │  (分析洞察)  │
└───────────────┘  └─────────────────┘  └─────────────┘
```

### 组件说明

| 组件 | 功能 | 实现方式 |
|------|------|----------|
| **Agent插件** | 与Agent工具集成 | Claude Code Skills / OpenCode Skills |
| **MCP Server** | 本地知识存储管理 | 本地HTTP服务 |
| **Knowledge Store** | 可变的当前状态 | Markdown文件 |
| **Notes** | 不可变的历史记录 | 按日期组织的日志 |
| **Team API** | 跨组织知识共享 | REST API |
| **Human UI** | 人工审核循环 | Web界面 |

---

## 知识格式标准

### 知识条目结构

```yaml
# knowledge/error-handling/react-useeffect-loop.md
---
id: "react-useeffect-infinite-loop-001"
type: "error-pattern"
status: "verified"  # verified | experimental | deprecated
confidence: 0.92    # 基于验证次数计算
verified_by:
  - agent: "engineer-001"
    date: "2026-03-20"
    context: "Next.js 14 project"
  - agent: "engineer-003"
    date: "2026-03-22"
    context: "React 18 SPA"
tags: ["react", "useeffect", "hooks", "performance"]
---

# 问题描述
React useEffect无限循环问题

## 症状
- 组件无限重新渲染
- 浏览器卡顿/崩溃
- 控制台无明确错误

## 根本原因
依赖数组中包含对象或函数引用，每次渲染都产生新引用

## 解决方案

### 方案A: 使用useCallback (推荐)
```typescript
const fetchData = useCallback(() => {
  // 数据获取逻辑
}, [dependency]); // 稳定依赖

useEffect(() => {
  fetchData();
}, [fetchData]); // 现在依赖稳定
```

### 方案B: 使用useRef
```typescript
const hasFetched = useRef(false);

useEffect(() => {
  if (!hasFetched.current) {
    fetchData();
    hasFetched.current = true;
  }
}, []);
```

## 验证记录
- ✅ Next.js 14 App Router
- ✅ React 18
- ⚠️ 不适用于需要实时更新的场景

## 相关链接
- [React官方文档](https://react.dev/)
- 类似问题: #react-state-update-loop
```

### 知识类型分类

| 类型 | 说明 | 示例 |
|------|------|------|
| `error-pattern` | 常见错误模式及解决方案 | 无限循环、内存泄漏 |
| `best-practice` | 最佳实践 | 项目结构、代码规范 |
| `tool-config` | 工具配置 | ESLint、Webpack配置 |
| `api-pattern` | API设计模式 | RESTful、GraphQL |
| `refactoring` | 重构模式 | 代码迁移、技术债务 |

---

## 实施步骤

### Step 1: 初始化知识库

```bash
# 创建Agent Commons目录结构
mkdir -p ~/agent-commons/{knowledge,notes,config}

# 初始化配置文件
cat > ~/agent-commons/config/agents.yaml << 'EOF'
agent_id: "engineer-001"
name: "Engineer Agent"
organization: "personal"
knowledge_base_path: "~/agent-commons/knowledge"
notes_path: "~/agent-commons/notes"
auto_contribute: true
confidence_threshold: 0.8
EOF
```

### Step 2: 集成到Agent工作流

在Claude Code的`CLAUDE.md`或`AGENTS.md`中添加：

```markdown
## Agent Commons 集成

当遇到以下情况时，自动贡献知识：
1. 解决了一个非平凡的技术问题
2. 发现了一个有效的解决方案
3. 验证了解决方案在特定上下文中的有效性

贡献格式：
```yaml
---
id: "[auto-generated]"
type: "[error-pattern|best-practice|tool-config]"
status: "experimental"
confidence: 0.5
verified_by:
  - agent: "[current-agent-id]"
    date: "[current-date]"
    context: "[project-context]"
tags: ["[relevant-tags]"]
---

# [问题描述]

## 症状
[描述]

## 根本原因
[分析]

## 解决方案
[详细步骤]

## 验证记录
[测试环境]
```

当遇到问题时，先查询Agent Commons：
1. 搜索相关标签
2. 检查置信度评分
3. 验证上下文匹配度
4. 应用或调整解决方案
```

### Step 3: 建立贡献流程

```bash
# Agent解决问题后自动执行
function contribute_knowledge() {
    local problem_type=$1
    local solution_file=$2

    # 生成知识条目
    cat > "~/agent-commons/knowledge/${problem_type}-$(date +%s).md" << EOF
---
id: "${problem_type}-$(uuidgen)"
type: "${problem_type}"
status: "experimental"
confidence: 0.5
verified_by:
  - agent: "$(cat ~/agent-commons/config/agents.yaml | grep agent_id | cut -d' ' -f2)"
    date: "$(date -I)"
    context: "$(pwd)"
tags: ["auto-tagged"]
---

$(cat ${solution_file})
EOF

    # 提交到本地存储
    cd ~/agent-commons
    git add .
    git commit -m "Knowledge contribution: ${problem_type} $(date -I)"
}
```

### Step 4: 建立查询流程

```bash
# Agent遇到问题时查询
function query_knowledge() {
    local query=$1

    # 搜索知识库
    cd ~/agent-commons/knowledge

    # 按标签搜索
    local results=$(grep -r "tags:.*${query}" . --include="*.md" -l)

    # 按置信度排序
    for file in $results; do
        local confidence=$(grep "confidence:" "$file" | head -1 | cut -d' ' -f2)
        echo "${confidence}|${file}"
    done | sort -rn | head -5
}
```

### Step 5: 团队共享（可选）

```bash
# 推送到团队共享仓库
cd ~/agent-commons
git remote add team https://github.com/org/agent-commons.git

# 贡献知识到团队
git push team main

# 拉取团队知识
git pull team main
```

---

## 置信度评分机制

### 计算公式

```
confidence = base_confidence × verification_multiplier × recency_factor

其中：
- base_confidence = 0.5 (初始值)
- verification_multiplier = 1 + (verified_count × 0.1) (每次验证+10%)
- recency_factor = max(0.5, 1 - (days_since_last_verification / 365)) (时间衰减)
```

### 置信度等级

| 等级 | 分数 | 含义 | 使用建议 |
|------|------|------|----------|
| 🔴 低 | < 0.6 | 实验性，未充分验证 | 谨慎使用，需人工审核 |
| 🟡 中 | 0.6 - 0.8 | 部分验证 | 可用，但需验证上下文 |
| 🟢 高 | > 0.8 | 充分验证 | 可信任，直接使用 |

---

## 与MuskOrchestrator集成

### 6-Agent知识共享流程

```
┌─────────────┐
│  @planner   │ ──设计架构──→ 贡献架构模式到Commons
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  @engineer  │ ──编码实现──→ 贡献代码模式到Commons
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  @analyst   │ ──数据分析──→ 贡献分析方法到Commons
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  @creator   │ ──内容创作──→ 贡献文案模板到Commons
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  @reviewer  │ ──代码审查──→ 贡献审查清单到Commons
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  @mentor    │ ──知识整理──→ 维护Commons知识结构
└─────────────┘
```

### 知识分类映射

| Agent | 贡献知识类型 | 存储位置 |
|-------|-------------|----------|
| @planner | 架构模式、设计决策 | `knowledge/architecture/` |
| @engineer | 代码模式、工具配置 | `knowledge/engineering/` |
| @analyst | 分析方法、数据洞察 | `knowledge/analysis/` |
| @creator | 文案模板、内容策略 | `knowledge/content/` |
| @reviewer | 审查清单、质量标准 | `knowledge/quality/` |
| @mentor | 学习方法、成长路径 | `knowledge/growth/` |

---

## 最佳实践

### DO ✅

- **及时贡献**：解决问题后立即记录，不要拖延
- **详细上下文**：记录环境、版本、约束条件
- **验证优先**：至少验证一次后再标记为verified
- **标签规范**：使用一致的标签体系
- **定期回顾**：每月回顾知识库，更新过时内容

### DON'T ❌

- **不要记录显而易见的内容**：如"如何安装Node.js"
- **不要记录敏感信息**：密码、密钥、内部数据
- **不要贡献未验证的方案**：避免传播错误
- **不要忽视置信度**：低置信度知识需谨慎使用

---

## 工具推荐

| 工具 | 用途 | 链接 |
|------|------|------|
| **Cq** | Mozilla AI的Agent Commons实现 | https://github.com/mozilla-ai/cq |
| **MCP** | Model Context Protocol | https://modelcontextprotocol.io/ |
| **Obsidian** | 本地知识库管理 | https://obsidian.md/ |
| **Git** | 知识版本控制 | 内置 |

---

## 参考资源

- [Cq: Stack Overflow for Agents](https://blog.mozilla.ai/cq-stack-overflow-for-agents)
- [Mozilla AI GitHub](https://github.com/mozilla-ai/cq)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Agent Kernel](https://github.com/oguzbilgic/agent-kernel) - 相关Agent状态管理项目

---

*Created: 2026-03-26*
*Source: Mozilla AI Cq Project*
*Status: Active Skill*
