# 过去30天信息聚合系统 - 设计文档

> **文档版本**: 1.0
> **创建日期**: 2026-03-16
> **状态**: 已实现并测试

---

## 1. 系统概述

### 1.1 目标
替代原有的 `last30days` skill，实现一个自动化的信息聚合系统，能够：
- 从多个高质量信息源自动获取内容
- 根据Agent角色智能分发内容
- 生成结构化的学习材料
- 集成到现有的 Daily Learning 流程

### 1.2 核心特性
- **多源聚合**: 6个信息源，覆盖技术、研究、商业、思维模型
- **智能分发**: 基于内容特征自动路由到对应Agent
- **缓存机制**: 合理的TTL策略，平衡实时性与API限制
- **容错设计**: 单点故障不影响整体系统
- **可扩展**: 模块化架构，易于添加新信息源

---

## 2. 架构设计

### 2.1 系统架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DailyAggregator                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      Data Layer                             │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │   │
│  │  │  GitHub  │  │  HN      │  │  arXiv   │  │ Farnam   │    │   │
│  │  │ Trending │  │  API     │  │  API     │  │ Street   │    │   │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │   │
│  │  ┌──────────┐  ┌──────────┐                                    │   │
│  │  │  Indie   │  │  Reddit  │                                    │   │
│  │  │ Hackers  │  │  API     │                                    │   │
│  │  └────┬─────┘  └────┬─────┘                                    │   │
│  └───────┼─────────────┼─────────────────────────────────────────┘   │
│          │             │                                            │
│          ▼             ▼                                            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                  Processing Layer                           │   │
│  │                                                             │   │
│  │   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐      │   │
│  │   │ Deduplicat. │──▶│   Scoring   │──▶│  Filtering  │      │   │
│  │   └─────────────┘   └─────────────┘   └─────────────┘      │   │
│  │                                                             │   │
│  │   Scoring Factors:                                          │   │
│  │   - Engagement (40%): stars, votes, comments               │   │
│  │   - Recency (30%): newer = higher score                    │   │
│  │   - Authority (20%): source reliability                    │   │
│  │   - Relevance (10%): keyword matching                      │   │
│  │                                                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Distribution Layer                       │   │
│  │                                                             │   │
│  │   planner ◄──┐  engineer ◄──┐  analyst ◄──┐               │   │
│  │              │               │              │               │   │
│  │   mentor  ◄──┘  creator  ◄──┘  reviewer ◄──┘               │   │
│  │                                                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      Output Layer                           │   │
│  │                                                             │   │
│  │   DAILY_FEED.md (per agent)    Raw JSON Data               │   │
│  │   - Markdown formatted         - Full aggregation          │   │
│  │   - Grouped by source          - Historical archive        │   │
│  │   - Ready for review           - Analytics ready           │   │
│  │                                                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  Source │────▶│ Fetcher │────▶│ Content │────▶│  Cache  │
│   API   │     │ Module  │     │  Item   │     │  Store  │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
                                      │
                                      ▼
                              ┌─────────────┐
                              │ Aggregator  │
                              │  (sort &    │
                              │  filter)    │
                              └──────┬──────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
              ┌─────────┐      ┌─────────┐      ┌─────────┐
              │ planner │      │ engineer│      │ analyst │
              │  FEED   │      │  FEED   │      │  FEED   │
              └─────────┘      └─────────┘      └─────────┘
```

---

## 3. 信息源配置

### 3.1 Agent-Source 映射

| Agent | 信息源 | 内容类型 | 最大条目 |
|-------|--------|----------|----------|
| @planner | GitHub (架构类), Farnam Street | 架构项目、决策框架 | 10 |
| @engineer | GitHub (工具类), Hacker News | 开发工具、技术讨论 | 12 |
| @analyst | arXiv (q-fin), GitHub (量化) | 量化论文、交易项目 | 10 |
| @mentor | Farnam Street | 思维模型、认知框架 | 8 |
| @creator | Indie Hackers, Reddit | 增长案例、营销策略 | 10 |

### 3.2 信息源详情

#### GitHub Trending
- **URL**: https://github.com/trending
- **方法**: Web scraping (BeautifulSoup)
- **分类逻辑**:
  - 包含 `quant`, `trading`, `finance` → analyst
  - 包含 `microservice`, `distributed`, `architecture` → planner
  - 其他工具类 → engineer
- **TTL**: 6小时

#### Hacker News
- **API**: https://github.com/HackerNews/API
- **方法**: REST API
- **分类逻辑**:
  - 包含 `startup`, `founder`, `business` → creator
  - 其他技术内容 → engineer
- **TTL**: 3小时

#### arXiv
- **API**: http://export.arxiv.org/api/query
- **方法**: Atom feed (XML)
- **分类逻辑**:
  - `q-fin.*` 类别 → analyst
  - `cs.LG`, `cs.AI` + 金融关键词 → analyst
  - 其他 ML/AI → engineer
- **TTL**: 12小时

#### Farnam Street
- **URL**: https://fs.blog/blog/
- **方法**: Web scraping
- **分类逻辑**:
  - 包含 `framework`, `decision`, `strategy` → planner
  - 其他 → mentor
- **TTL**: 12小时

#### Indie Hackers
- **URL**: https://www.indiehackers.com/
- **方法**: Web scraping
- **分类逻辑**:
  - 包含 `growth`, `marketing` → creator
  - 包含 `product`, `development` → engineer
  - 其他 → creator
- **TTL**: 6小时

#### Reddit
- **API**: https://www.reddit.com/r/{subreddit}/hot.json
- **方法**: REST API (需要认证)
- **分类逻辑**:
  - 包含营销关键词 → creator
  - 包含增长关键词 → creator
  - r/ProductManagement → planner
- **TTL**: 3小时
- **注意**: 当前需要OAuth认证，可能需要配置token

---

## 4. 核心模块

### 4.1 BaseFetcher (base.py)

抽象基类，定义所有fetcher的接口：

```python
class BaseFetcher(ABC):
    @abstractmethod
    def fetch(self, days: int, limit: int) -> List[ContentItem]:
        pass
```

提供通用功能：
- 缓存管理 (load_from_cache, save_to_cache)
- 日期过滤 (filter_by_date)
- 去重 (deduplicate)

### 4.2 ContentItem (base.py)

统一的内容数据模型：

```python
@dataclass
class ContentItem:
    title: str
    url: str
    source: str           # 信息源标识
    source_type: str      # 内容类型
    agent_target: str     # 目标Agent
    description: str
    author: str
    published_date: datetime
    tags: List[str]
    metrics: Dict         # 评分指标
    content_hash: str     # 去重标识
```

### 4.3 DailyAggregator (daily_aggregator.py)

主协调器，职责：
1. 初始化所有fetcher
2. 并行/串行获取内容
3. 分发到对应Agent
4. 生成Markdown输出
5. 保存原始数据

---

## 5. 输出格式

### 5.1 DAILY_FEED.md 结构

```markdown
# {AGENT} Daily Feed

> **Focus**: {description}
> **Generated**: {timestamp}
> **Period**: Last 30 days

---

## {Source} ({count} items)

### {Title}
- **URL**: {url}
- **Author**: {author}
- **Tags**: {tags}
- **Metrics**: {metrics}
- **Description**: {description}

---
```

### 5.2 原始数据格式 (JSON)

```json
{
  "timestamp": "2026-03-16T11:51:00",
  "total_items": 21,
  "by_agent": {
    "engineer": [...],
    "planner": [...],
    ...
  },
  "all_items": [...]
}
```

---

## 6. 集成方案

### 6.1 Daily Learning 集成

`daily_learning.py` 在启动时：
1. 检查各Agent的DAILY_FEED.md是否存在且为当日
2. 如需要，调用 `daily_aggregator.py`
3. 显示聚合摘要

```python
def run_aggregator():
    subprocess.run([
        sys.executable,
        "scripts/daily_aggregator.py",
        "--days", "30",
        "--limit", "15"
    ])
```

### 6.2 定时任务配置

建议添加到现有的launchd/cron配置：

```bash
# 每天 06:30 执行（早于Daily Learning 07:00）
30 6 * * * python /Users/linweihao/project/MuskOrchestrator/scripts/daily_aggregator.py
```

---

## 7. 扩展指南

### 7.1 添加新信息源

1. 创建 `scripts/sources/new_source.py`
2. 继承 `BaseFetcher`
3. 实现 `fetch()` 方法
4. 在 `daily_aggregator.py` 中注册
5. 更新 `SKILL.md` 文档

### 7.2 添加新Agent

1. 在 `AGENT_SOURCES` 中添加配置
2. 在各fetcher中实现 `_determine_agent_target()`
3. 创建模板 `memory/agents/{agent}/DAILY_FEED.md`

---

## 8. 性能与限制

### 8.1 性能指标

| 指标 | 数值 |
|------|------|
| 总执行时间 | ~30-60秒 |
| 单源超时 | 30-60秒 |
| 缓存命中率 | ~80% (6小时内) |
| 平均内容条目 | 20-40条 |

### 8.2 已知限制

1. **Reddit**: 需要OAuth认证才能稳定访问
2. **GitHub**: 可能有速率限制（未认证60 req/hour）
3. **Farnam Street/Indie Hackers**: 依赖页面结构，可能因网站改版失效

### 8.3 改进建议

- [ ] 添加代理支持以应对IP限制
- [ ] 实现指数退避重试机制
- [ ] 添加内容摘要AI生成
- [ ] 实现基于embedding的去重
- [ ] 添加Agent反馈循环优化推荐

---

## 9. 文件清单

### 核心脚本
- `/Users/linweihao/project/MuskOrchestrator/scripts/daily_aggregator.py` - 主聚合脚本
- `/Users/linweihao/project/MuskOrchestrator/scripts/sources/__init__.py` - 包初始化
- `/Users/linweihao/project/MuskOrchestrator/scripts/sources/base.py` - 基类定义

### 信息源模块
- `/Users/linweihao/project/MuskOrchestrator/scripts/sources/github_trending.py`
- `/Users/linweihao/project/MuskOrchestrator/scripts/sources/hacker_news.py`
- `/Users/linweihao/project/MuskOrchestrator/scripts/sources/arxiv_fetcher.py`
- `/Users/linweihao/project/MuskOrchestrator/scripts/sources/farnam_street.py`
- `/Users/linweihao/project/MuskOrchestrator/scripts/sources/indie_hackers.py`
- `/Users/linweihao/project/MuskOrchestrator/scripts/sources/reddit_fetcher.py`

### 输出文件
- `/Users/linweihao/project/MuskOrchestrator/memory/agents/planner/DAILY_FEED.md`
- `/Users/linweihao/project/MuskOrchestrator/memory/agents/engineer/DAILY_FEED.md`
- `/Users/linweihao/project/MuskOrchestrator/memory/agents/analyst/DAILY_FEED.md`
- `/Users/linweihao/project/MuskOrchestrator/memory/agents/mentor/DAILY_FEED.md`
- `/Users/linweihao/project/MuskOrchestrator/memory/agents/creator/DAILY_FEED.md`

### 文档
- `/Users/linweihao/project/MuskOrchestrator/skills/last30days/SKILL.md` - 技能定义
- `/Users/linweihao/project/MuskOrchestrator/docs/INFO_AGGREGATION_SYSTEM.md` - 本设计文档

---

## 10. 使用示例

### 手动执行

```bash
# 完整聚合
python scripts/daily_aggregator.py

# 仅查看摘要（不保存）
python scripts/daily_aggregator.py --summary-only --no-save

# 指定时间范围和条目数
python scripts/daily_aggregator.py --days 7 --limit 10

# 仅生成特定Agent的feed
python scripts/daily_aggregator.py --agent analyst
```

### 作为模块使用

```python
from scripts.daily_aggregator import DailyAggregator

aggregator = DailyAggregator()
aggregator.fetch_all(days=30, limit_per_source=20)
aggregator.distribute_to_agents()
aggregator.save_feeds()
```

---

**冷酷法则**: 信息就是力量，但过载就是噪音。这个系统确保每个Agent只收到最相关、最高质量的内容。
