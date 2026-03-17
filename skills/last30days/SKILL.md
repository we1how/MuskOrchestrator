# Last30Days Information Aggregation Skill

> **Skill ID**: `last30days`
> **Version**: 1.0
> **Type**: Background Service

## Description

Automatically aggregates high-quality information from multiple sources over the past 30 days and distributes personalized content feeds to each agent.

Replaces the manual `last30days` skill with an automated, intelligent aggregation system.

## Information Sources

| Source | Content Type | Target Agents | Update Frequency |
|--------|-------------|---------------|------------------|
| GitHub Trending | Repositories, Tools | engineer, planner, analyst | Daily |
| Hacker News | Technical Discussions | engineer, creator | 3 hours |
| arXiv q-fin | Quantitative Research | analyst | 12 hours |
| Farnam Street | Mental Models, Frameworks | mentor, planner | 12 hours |
| Indie Hackers | Growth Cases, Startups | creator | 6 hours |
| Reddit | Marketing Discussions | creator | 3 hours |

## Agent Content Mapping

### @planner
- **Focus**: Architecture decisions, system design, decision frameworks
- **Sources**: GitHub (architecture repos), Farnam Street (frameworks)
- **Max Items**: 10

### @engineer
- **Focus**: Developer tools, technical discussions, implementation patterns
- **Sources**: GitHub (tools), Hacker News (tech discussions)
- **Max Items**: 12

### @analyst
- **Focus**: Quantitative research, trading algorithms, financial models
- **Sources**: arXiv (q-fin papers), GitHub (quant projects)
- **Max Items**: 10

### @mentor
- **Focus**: Mental models, thinking frameworks, personal growth
- **Sources**: Farnam Street (articles)
- **Max Items**: 8

### @creator
- **Focus**: Growth strategies, marketing tactics, launch cases
- **Sources**: Indie Hackers (case studies), Reddit (discussions)
- **Max Items**: 10

## Usage

### Manual Execution

```bash
# Fetch and aggregate all content
python scripts/daily_aggregator.py

# Fetch specific time range
python scripts/daily_aggregator.py --days 7 --limit 15

# Generate feed for specific agent only
python scripts/daily_aggregator.py --agent analyst

# Preview without saving
python scripts/daily_aggregator.py --no-save --summary-only
```

### Integration with Daily Learning

The aggregator is automatically called by `daily_learning.py` during the daily micro-learning routine.

## Output Files

### Agent Feeds
- `memory/agents/planner/DAILY_FEED.md`
- `memory/agents/engineer/DAILY_FEED.md`
- `memory/agents/analyst/DAILY_FEED.md`
- `memory/agents/mentor/DAILY_FEED.md`
- `memory/agents/creator/DAILY_FEED.md`

### Raw Data
- `data/aggregator/aggregation_YYYYMMDD.json` - Full aggregation data
- `data/aggregator/cache/` - Cached source data

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DailyAggregator                          │
├─────────────────────────────────────────────────────────────┤
│  Data Layer          Processing Layer        Output Layer   │
│  ┌──────────┐       ┌──────────────┐       ┌──────────┐    │
│  │ GitHub   │──────▶│              │       │ Agent    │    │
│  │ Trending │       │   Content    │──────▶│ Feeds    │    │
│  ├──────────┤       │   Scoring    │       │ (MD)     │    │
│  │ HN       │──────▶│              │       ├──────────┤    │
│  ├──────────┤       │  Deduplicat. │       │ Raw JSON │    │
│  │ arXiv    │──────▶│  Filtering   │       │ Data     │    │
│  ├──────────┤       └──────────────┘       └──────────┘    │
│  │ Farnam   │──────▶│                                      │
│  ├──────────┤       │  Agent Distribution                  │
│  │ Indie    │──────▶│  - planner                           │
│  ├──────────┤       │  - engineer                          │
│  │ Reddit   │──────▶│  - analyst                           │
│  └──────────┘       │  - mentor                            │
│                     │  - creator                           │
│                     └──────────────────────────────────────┘
└─────────────────────────────────────────────────────────────┘
```

## Scoring Algorithm

Items are scored based on:
1. **Engagement Metrics** (40%): Stars, votes, comments
2. **Recency** (30%): Newer content gets higher scores
3. **Source Authority** (20%): Weighted by source reliability
4. **Content Relevance** (10%): Keyword matching for agent targets

## Caching Strategy

| Source | TTL | Rationale |
|--------|-----|-----------|
| GitHub | 6h | Trending changes frequently |
| HN | 3h | Fast-moving discussions |
| arXiv | 12h | Academic papers update daily |
| Farnam Street | 12h | Blog updates infrequently |
| Indie Hackers | 6h | Community content |
| Reddit | 3h | Very fast-moving |

## Error Handling

- Failed sources are logged but don't block other sources
- Cache is used as fallback when APIs are unavailable
- Rate limiting is respected with exponential backoff

## Future Enhancements

- [ ] AI-powered content summarization
- [ ] Cross-source deduplication using embeddings
- [ ] Personalized ranking based on agent feedback
- [ ] Trend detection and alerting
- [ ] Integration with Tavily for web search

## Dependencies

```
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
```

## Maintenance

- Monitor API rate limits and adjust fetch frequency
- Review agent feedback to tune content relevance
- Update source URLs if websites change structure
- Add new sources based on agent needs
