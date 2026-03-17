# Agent Daily Learning - 去重检查机制

> 防止Agent每日学习重复内容，确保每次学习都有新价值

---

## 🔍 问题诊断

**重复学习发生的原因**:
1. 信息源列表固定，Agent随机选择时可能重复
2. 没有检查历史学习记录
3. 同一来源不同URL可能指向相似内容
4. 没有记录已学习的文章/项目唯一标识

**重复学习的成本**:
- 浪费时间（15分钟/次）
- 错失学习新知识的机会
- 降低学习系统的可信度

---

## ✅ 解决方案：三层去重机制

### Layer 1: 来源级去重（Source-level）

**机制**: 记录每个Agent已学习的来源URL，学习前检查

```yaml
# memory/agents/{agent}/learning-history.yaml
analyst:
  sources:
    arxiv:
      last_visited: "2026-03-17"
      learned_urls:
        - "https://arxiv.org/abs/2501.12345"
        - "https://arxiv.org/abs/2502.67890"
    github_trending:
      last_visited: "2026-03-17"
      learned_projects:
        - "tradingagents-ai/trading-agents"

mentor:
  sources:
    farnam_street:
      last_visited: "2026-03-17"
      learned_urls:
        - "https://fs.blog/ride-wave/"      # 2026-03-05 首次
        - "https://fs.blog/ride-wave/"      # 2026-03-10 深化
        - "https://fs.blog/ride-wave/"      # 2026-03-17 ❌ 重复
        - "https://fs.blog/circle-of-competence/"  # 2026-03-17 修正后
```

### Layer 2: 内容级去重（Content-level）

**机制**: 提取内容指纹，相似度>80%视为重复

```python
def content_fingerprint(title: str, summary: str) -> str:
    """生成内容指纹用于去重"""
    # 提取关键词
    keywords = extract_keywords(title + " " + summary)
    # 排序并连接
    return "|".join(sorted(keywords))

# 示例
ride_the_wave_fp = "competitive|destruction|kodak|munger|surfing|technology|wave"
circle_of_competence_fp = "buffett|competence|circle|expertise|knowledge|munger|rose"
```

### Layer 3: 主题级去重（Topic-level）

**机制**: 记录已学习的核心概念，避免同一概念短期重复

```yaml
# 已学习的核心概念（30天滑动窗口）
learned_concepts:
  "冲浪模型": "2026-03-05"  # 30天内不再学习
  "能力圈": "2026-03-17"
  "OODA循环": "2026-03-11"   # 已过期，可重新学习
  "72小时法则": "2026-03-10"
```

---

## 📝 执行流程（更新版）

### Step 1: 学习前检查

```
1. 读取 learning-history.yaml
2. 检查今天是否已学习
3. 从候选列表中排除已学习的URL
4. 如果全部已学习，标记为"需寻找新的信息源"
```

### Step 2: 内容获取后检查

```
1. 获取候选内容标题和摘要
2. 生成内容指纹
3. 与历史指纹比对
4. 相似度>80% → 放弃，选择下一个候选
```

### Step 3: 学习后记录

```
1. 更新 learning-history.yaml
2. 添加URL到 learned_urls
3. 提取核心概念，更新 learned_concepts
4. 记录学习日期
```

---

## 🛠️ 技术实现

### 文件结构

```
memory/agents/{agent}/
├── LEARNING.md              # 学习记录（原有）
├── learning-history.yaml    # 去重检查数据库（新增）
└── concepts/               # 概念提取存储（可选）
    └── 2026-03/
        └── ride-the-wave.md
```

### learning-history.yaml 模板

```yaml
# memory/agents/mentor/learning-history.yaml
agent: mentor
last_updated: "2026-03-17T14:30:00Z"

sources:
  farnam_street:
    base_url: "https://fs.blog"
    learned_articles:
      - url: "https://fs.blog/ride-wave/"
        title: "Ride the Wave"
        date: "2026-03-05"
        concepts: ["冲浪模型", "竞争毁灭", "先行者优势"]
        fingerprint: "competitive|destruction|kodak|munger|surfing"

      - url: "https://fs.blog/ride-wave/"
        title: "Ride the Wave - 深化学习"
        date: "2026-03-10"
        concepts: ["72小时决策法则", "浪潮识别框架"]
        fingerprint: "competitive|destruction|72hours|wave|switching"
        notes: "深化版本，增加了可执行框架"

      - url: "https://fs.blog/circle-of-competence/"
        title: "Circle of Competence"
        date: "2026-03-17"
        concepts: ["能力圈", "earned knowledge", "边界识别"]
        fingerprint: "buffett|competence|circle|expertise|knowledge|munger"

  wait_but_why:
    base_url: "https://waitbutwhy.com"
    learned_articles: []

  lesswrong:
    base_url: "https://lesswrong.com"
    learned_articles: []

# 概念去重追踪（30天滑动窗口）
concept_window_days: 30
learned_concepts:
  "冲浪模型": "2026-03-05"
  "72小时决策法则": "2026-03-10"
  "能力圈": "2026-03-17"
  "OODA循环": "2026-03-11"
  "Chesterton's Fence": "2026-03-12"
  "Winner's Edge": "2026-03-13"
  "持续学习系统": "2026-03-16"

# 统计数据
total_learned: 8
unique_sources: 3
repeated_attempts: 1  # 记录重复尝试次数
```

---

## 📋 去重检查清单

### 每日学习前必须执行

```markdown
## Agent: {agent_name} 学习前检查

### 1. 来源检查
- [ ] 读取 learning-history.yaml
- [ ] 获取候选来源列表
- [ ] 排除已学习的URL
- [ ] 剩余候选数量: ___

### 2. 内容检查
- [ ] 获取候选内容标题+摘要
- [ ] 生成内容指纹
- [ ] 与历史指纹比对
- [ ] 相似度最高: ___% (阈值: 80%)

### 3. 概念检查
- [ ] 提取候选内容核心概念
- [ ] 检查是否在30天内已学习
- [ ] 冲突概念: ___

### 4. 决策
- [ ] 通过 → 开始学习
- [ ] 不通过 → 选择下一个候选
- [ ] 全部不通过 → 寻找新的信息源
```

---

## 🚨 重复学习应急处理

### 发现重复时

1. **立即停止** - 不再继续学习重复内容
2. **记录日志** - 在 learning-history.yaml 中标记 `repeated_attempts += 1`
3. **寻找替代** - 从备选列表中选择新内容
4. **更新机制** - 如果重复频繁，考虑更换信息源

### 当所有来源都已学习时

```
策略选项:
1. 切换到备选信息源
2. 降低学习频率（每周而非每天）
3. 深化已有内容（新角度、新应用）
4. 等待新内容产生（设置监控）
```

---

## 📊 监控指标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 重复率 | <5% | 重复学习次数/总学习次数 |
| 来源覆盖率 | >80% | 已学习来源/总来源数 |
| 概念新鲜度 | >90% | 新概念/总学习概念 |
| 每日成功率 | 100% | 每天成功学习新内容 |

---

## 💡 冷酷法则

> **重复学习 = 浪费时间 = 犯罪**
>
> 每次重复都意味着：
> - 你失去了学习新知识的机会
> - 你的学习系统存在漏洞
> - 你的Agent没有尽到责任
>
> **零容忍政策**：发现重复立即修复，不留到第二天。

---

**Created**: 2026-03-17
**Status**: 🟡 待实施（需要集成到daily-learning skill）
