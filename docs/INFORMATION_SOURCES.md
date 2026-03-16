# 信息源完整列表

> MuskOrchestrator 信息聚合系统 - 所有搜索网站与信息源
> 最后更新: 2026-03-16

---

## 快速索引

| Agent | 主要信息源 | 数量 |
|-------|-----------|------|
| @planner | GitHub, Farnam Street | 2 |
| @engineer | GitHub, Hacker News, Indie Hackers, arXiv | 4 |
| @analyst | arXiv, GitHub | 2 |
| @mentor | Farnam Street | 1 |
| @creator | Indie Hackers, Reddit, Hacker News | 3 |
| **总计** | | **6个核心源 + 扩展源** |

---

## 一、技术/工程类信息源

### 1. GitHub Trending ⭐⭐⭐⭐⭐

**用途**: 发现最新技术趋势、开源项目、工具库

**URL**: https://github.com/trending

**获取方式**: Scraping + API

**分类筛选**:
- Python (数据分析、AI/ML)
- TypeScript (前端、工具)
- Go (后端、基础设施)
- Rust (系统编程、WebAssembly)

**评分标准**:
- Stars增长速率
- Fork数量
- 社区活跃度 (issues/PRs)
- 文档完整性

**目标Agent**: @engineer, @planner, @analyst

**使用场景**:
- 发现新的量化库
- 跟踪Agent系统架构演进
- 学习最佳工程实践

---

### 2. Hacker News 🔥

**用途**: 技术讨论、创业资讯、行业趋势

**URL**: https://news.ycombinator.com

**获取方式**: Official API (https://github.com/HackerNews/API)

**关键端点**:
- `topstories.json` - 热门帖子
- `newstories.json` - 最新帖子
- `showstories.json` - Show HN
- `askstories.json` - Ask HN

**评分标准**:
- 投票数 (score)
- 评论深度
- 作者声望
- 话题相关性

**目标Agent**: @engineer, @creator

**使用场景**:
- 发现技术趋势
- 了解独立开发者案例
- 学习产品发布策略

---

### 3. arXiv (Computer Science / Quantitative Finance) 📄

**用途**: 学术研究、量化策略、AI前沿

**URL**: https://arxiv.org

**获取方式**: RSS Feed + API (export.arxiv.org/api)

**关注分类**:
- `cs.AI` - 人工智能
- `cs.SE` - 软件工程
- `cs.LG` - 机器学习
- `q-fin.ST` - 统计金融
- `q-fin.CP` - 计算金融
- `q-fin.TR` - 交易与做市

**评分标准**:
- 引用数 (Crossref)
- GitHub实现stars
- 作者权威性
- 可复现性

**目标Agent**: @analyst, @engineer

**使用场景**:
- 发现新量化策略
- 跟踪AI交易研究
- 学习最新算法

---

## 二、商业/增长类信息源

### 4. Indie Hackers 🚀

**用途**: 独立开发者案例、增长策略、商业模式

**URL**: https://www.indiehackers.com

**获取方式**: Scraping

**关注板块**:
- Product Launch - 产品发布案例
- Growth - 增长策略
- Revenue - 收入分享
- Milestones - 里程碑

**评分标准**:
- 收入数据 ($MRR)
- 用户增长曲线
- 策略可复制性
- 讨论参与度

**目标Agent**: @creator, @engineer

**使用场景**:
- 学习冷启动策略
- 了解定价模式
- 发现增长渠道

---

### 5. Reddit 📝

**用途**: 社区讨论、用户反馈、营销洞察

**URL**: https://www.reddit.com

**获取方式**: Reddit API (需OAuth认证)

**关注Subreddits**:

| Subreddit | 主题 | 目标Agent |
|-----------|------|-----------|
| r/entrepreneur | 创业 | @creator |
| r/indiehackers | 独立开发 | @creator |
| r/marketing | 营销 | @creator |
| r/SaaS | SaaS业务 | @creator |
| r/startups | 创业 | @creator |
| r/growthhacking | 增长黑客 | @creator |
| r/programming | 编程 | @engineer |
| r/webdev | Web开发 | @engineer |
| r/Python | Python | @engineer |
| r/algotrading | 算法交易 | @analyst |

**评分标准**:
- Upvotes数量
- 评论深度
- 用户意图 (问题/分享/讨论)
- 时效性

**目标Agent**: @creator (主要), @engineer, @analyst

**使用场景**:
- 发现用户痛点
- 验证产品想法
- 学习社区营销

---

## 三、思维/决策类信息源

### 6. Farnam Street 🧠

**用途**: 思维模型、决策框架、长期学习

**URL**: https://fs.blog

**获取方式**: Scraping (RSS格式不稳定)

**关注类别**:
- Mental Models - 思维模型
- Decision Making - 决策制定
- Learning - 学习方法
- Reading - 阅读建议

**评分标准**:
- 信息密度
- 可应用性
- 来源权威性
- 与Agent角色的相关性

**目标Agent**: @planner, @mentor

**使用场景**:
- 学习决策框架 (OODA, Chesterton's Fence)
- 构建思维模型库
- 提升认知能力

---

## 四、扩展信息源 (待集成)

### 7. Product Hunt 🎯

**用途**: 产品发布、市场验证、竞品分析

**URL**: https://www.producthunt.com

**获取方式**: GraphQL API

**关注分类**:
- Developer Tools - 开发工具
- Productivity - 效率工具
- AI - 人工智能
- Finance - 金融

**目标Agent**: @creator

---

### 8. Lobsters 🦞

**用途**: 技术讨论 (高质量社区)

**URL**: https://lobste.rs

**获取方式**: RSS Feed

**特点**: 邀请制社区，讨论质量高

**目标Agent**: @engineer

---

### 9. Dev.to 👩‍💻

**用途**: 技术文章、教程、最佳实践

**URL**: https://dev.to

**获取方式**: API (https://developers.forem.com/api)

**目标Agent**: @engineer

---

### 10. Medium 📰

**用途**: 深度文章、行业分析

**URL**: https://medium.com

**获取方式**: RSS Feed

**关注标签**:
- artificial-intelligence
- programming
- startups
- investing

**目标Agent**: @mentor, @creator

---

### 11. Twitter/X API 🐦

**用途**: 实时趋势、专家观点

**URL**: https://twitter.com

**获取方式**: X API (付费)

**关注列表**:
- AI/ML专家
- 量化交易员
- 独立开发者
- 投资人

**目标Agent**: @creator, @analyst

---

### 12. 播客/YouTube 📺

**用途**: 深度访谈、案例学习

**推荐频道**:
- Y Combinator (创业)
- Farnam Street (思维模型)
- Lex Fridman (AI)
- Patrick Boyle (量化金融)

**目标Agent**: @mentor, @planner

---

## 五、信息源覆盖矩阵

| 信息源 | @planner | @engineer | @analyst | @mentor | @creator |
|--------|:--------:|:---------:|:--------:|:-------:|:--------:|
| GitHub Trending | ⭐ | ⭐⭐⭐ | ⭐⭐ | - | - |
| Hacker News | ⭐ | ⭐⭐⭐ | - | - | ⭐⭐ |
| arXiv | - | ⭐⭐ | ⭐⭐⭐ | - | - |
| Indie Hackers | - | ⭐⭐ | - | - | ⭐⭐⭐ |
| Reddit | - | ⭐ | ⭐ | - | ⭐⭐⭐ |
| Farnam Street | ⭐⭐⭐ | - | - | ⭐⭐⭐ | - |
| Product Hunt | - | - | - | - | ⭐⭐ |
| Lobsters | - | ⭐⭐ | - | - | - |
| Dev.to | - | ⭐⭐ | - | - | - |
| Medium | ⭐ | ⭐ | - | ⭐⭐ | ⭐⭐ |

---

## 六、API限制与配置

### GitHub API
- **未认证**: 60 requests/hour
- **认证**: 5,000 requests/hour
- **配置**: `config/github_config.json`

### Reddit API
- **未认证**: 10 requests/minute
- **OAuth**: 60 requests/minute
- **配置**: `config/reddit_config.json`

### arXiv API
- **限制**: 合理频率，建议1秒/请求
- **格式**: export.arxiv.org/api/query
- **配置**: 内置，无需认证

### Hacker News API
- **限制**: 无明确限制
- **格式**: 官方REST API
- **配置**: 内置，无需认证

---

## 七、质量评估框架

每个信息源的内容都经过以下评分：

```
总分 = relevance × 0.4 + authority × 0.3 + engagement × 0.2 + recency × 0.1

- relevance: 与Agent角色的相关性 (0-1)
- authority: 来源权威性 (0-1)
- engagement: 社区互动度 (0-1)
- recency: 时效性 (0-1)
```

**过滤阈值**: 总分 < 0.5 的内容自动丢弃

---

## 八、使用建议

### 每日流程
1. **06:30** - `info-aggregator` 运行，抓取所有源
2. **07:00** - `daily-learning` 运行，基于DAILY_FEED学习
3. **手动** - 随时运行 `daily_aggregator.py --agent {agent}` 刷新特定Agent

### 手动探索
```bash
# 查看所有可用源
python -c "from scripts.sources import SOURCE_REGISTRY; print(list(SOURCE_REGISTRY.keys()))"

# 测试单个源
python scripts/sources/github_trending.py

# 获取特定主题
python scripts/daily_aggregator.py --agent creator --days 3
```

---

## 九、新增信息源流程

想要添加新信息源？遵循以下步骤：

1. **在 `scripts/sources/` 创建新模块**
   ```python
   # scripts/sources/new_source.py
   from .base import BaseSource

   class NewSource(BaseSource):
       def fetch(self, **kwargs):
           # 实现抓取逻辑
           pass
   ```

2. **注册到 `scripts/sources/__init__.py`**
   ```python
   from .new_source import NewSource
   SOURCE_REGISTRY['new_source'] = NewSource
   ```

3. **更新本文档**
   - 添加到相应分类
   - 更新覆盖矩阵
   - 记录API限制

4. **测试**
   ```bash
   python scripts/daily_aggregator.py --agent planner --source new_source
   ```

---

*信息源列表动态更新，欢迎建议新增高质量来源*
