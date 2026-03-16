#!/usr/bin/env python3
"""
Daily Information Aggregator
Aggregates high-quality content from multiple sources for all agents.
Replaces the last30days skill functionality.

Usage:
    python daily_aggregator.py [--days 30] [--limit 20] [--agent all]
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from sources.base import ContentItem
from sources.github_trending import GitHubTrendingFetcher
from sources.hacker_news import HackerNewsFetcher
from sources.arxiv_fetcher import ArxivFetcher
from sources.farnam_street import FarnamStreetFetcher
from sources.indie_hackers import IndieHackersFetcher
from sources.reddit_fetcher import RedditFetcher
from sources.zhihu_hot import ZhihuHotFetcher
from sources.product_hunt import ProductHuntFetcher
from sources.rsshub_fetcher import RSSHubFetcher, RSSHubManager
from sources.weibo_hot import WeiboHotFetcher


# Configuration
BASE_DIR = Path("/Users/linweihao/project/MuskOrchestrator")
DATA_DIR = BASE_DIR / "data" / "aggregator"
MEMORY_DIR = BASE_DIR / "memory" / "agents"
CACHE_DIR = DATA_DIR / "cache"

# Agent to source mapping
# Priority: International sources first, Chinese sources optional
AGENT_SOURCES = {
    'planner': {
        'sources': ['github', 'farnamstreet'],
        'description': 'Architecture projects and decision frameworks',
        'max_items': 12,
    },
    'engineer': {
        'sources': ['github', 'hackernews', 'arxiv'],
        'description': 'Developer tools and technical discussions',
        'max_items': 15,
    },
    'analyst': {
        'sources': ['arxiv', 'github'],
        'description': 'Quantitative research and trading projects',
        'max_items': 12,
    },
    'mentor': {
        'sources': ['farnamstreet'],
        'description': 'Mental models and thinking frameworks',
        'max_items': 10,
    },
    'creator': {
        'sources': ['indiehackers', 'hackernews'],
        'description': 'Growth cases and marketing strategies',
        'max_items': 12,
    },
}


class DailyAggregator:
    """Main aggregator that orchestrates all fetchers."""

    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Initialize fetchers
        # Check RSSHub availability
        rsshub_manager = RSSHubManager()
        self.rsshub_available = rsshub_manager.is_running()

        self.fetchers = {
            'github': GitHubTrendingFetcher(cache_dir=cache_dir / 'github'),
            'hackernews': HackerNewsFetcher(cache_dir=cache_dir / 'hackernews'),
            'arxiv': ArxivFetcher(cache_dir=cache_dir / 'arxiv'),
            'farnamstreet': FarnamStreetFetcher(cache_dir=cache_dir / 'farnamstreet'),
            'indiehackers': IndieHackersFetcher(cache_dir=cache_dir / 'indiehackers'),
            'reddit': RedditFetcher(cache_dir=cache_dir / 'reddit'),
            'zhihu': ZhihuHotFetcher(cache_dir=cache_dir / 'zhihu'),
            'producthunt': ProductHuntFetcher(cache_dir=cache_dir / 'producthunt'),
            'weibo': WeiboHotFetcher(cache_dir=cache_dir / 'weibo'),
        }

        # Add RSSHub fetcher if available
        if self.rsshub_available:
            self.rsshub = RSSHubFetcher(cache_dir=cache_dir / 'rsshub')

        # Results storage
        self.all_items: List[ContentItem] = []
        self.agent_items: Dict[str, List[ContentItem]] = defaultdict(list)

    def fetch_all(self, days: int = 30, limit_per_source: int = 20) -> List[ContentItem]:
        """Fetch content from all sources."""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Starting aggregation...")
        print(f"Fetching last {days} days of content from {len(self.fetchers)} sources\n")

        all_items = []

        for name, fetcher in self.fetchers.items():
            try:
                print(f"  Fetching from {name}...", end=" ")
                items = fetcher.fetch(days=days, limit=limit_per_source)
                print(f"✓ {len(items)} items")
                all_items.extend(items)
            except Exception as e:
                print(f"✗ Error: {e}")
                continue

        # Fetch from RSSHub if available
        if self.rsshub_available:
            print("\n  Fetching from RSSHub (enhanced sources)...")
            try:
                # Reddit via RSSHub
                print("    Reddit (via RSSHub)...", end=" ")
                reddit_items = self.rsshub.fetch_reddit('startups', limit=8)
                reddit_items += self.rsshub.fetch_reddit('entrepreneur', limit=5)
                reddit_items += self.rsshub.fetch_reddit('marketing', limit=5)
                print(f"✓ {len(reddit_items)} items")
                all_items.extend(reddit_items)
            except Exception as e:
                print(f"✗ Error: {e}")

            try:
                # Zhihu via RSSHub
                print("    Zhihu (via RSSHub)...", end=" ")
                zhihu_items = self.rsshub.fetch_zhihu_hot(limit=15)
                print(f"✓ {len(zhihu_items)} items")
                all_items.extend(zhihu_items)
            except Exception as e:
                print(f"✗ Error: {e}")

            try:
                # Product Hunt via RSSHub
                print("    Product Hunt (via RSSHub)...", end=" ")
                ph_items = self.rsshub.fetch_producthunt(limit=10)
                print(f"✓ {len(ph_items)} items")
                all_items.extend(ph_items)
            except Exception as e:
                print(f"✗ Error: {e}")

        self.all_items = all_items
        print(f"\nTotal items fetched: {len(all_items)}")

        return all_items

    def distribute_to_agents(self) -> Dict[str, List[ContentItem]]:
        """Distribute content to appropriate agents."""
        print("\nDistributing content to agents...")

        # Group by agent target
        for item in self.all_items:
            agent = item.agent_target
            if agent in AGENT_SOURCES:
                self.agent_items[agent].append(item)

        # Sort and limit per agent
        for agent, items in self.agent_items.items():
            max_items = AGENT_SOURCES[agent]['max_items']

            # Sort by relevance (can be customized)
            items.sort(key=lambda x: self._score_item(x), reverse=True)

            # Limit
            self.agent_items[agent] = items[:max_items]
            print(f"  {agent}: {len(self.agent_items[agent])} items")

        return dict(self.agent_items)

    def _score_item(self, item: ContentItem) -> float:
        """Score an item for relevance sorting."""
        score = 0.0

        # Base score from metrics
        if 'stars' in item.metrics:
            score += min(item.metrics['stars'] / 1000, 10)
        if 'score' in item.metrics:
            score += min(item.metrics['score'] / 100, 10)
        if 'comments' in item.metrics:
            score += min(item.metrics['comments'] / 50, 5)

        # Boost for recent content
        if item.published_date:
            from datetime import timezone
            now = datetime.now(timezone.utc)
            item_date = item.published_date
            if item_date.tzinfo is None:
                item_date = item_date.replace(tzinfo=timezone.utc)
            days_old = (now - item_date).days
            if days_old <= 1:
                score += 5
            elif days_old <= 7:
                score += 3
            elif days_old <= 30:
                score += 1

        return score

    def generate_agent_feed(self, agent: str) -> str:
        """Generate markdown feed for a specific agent."""
        if agent not in self.agent_items:
            return ""

        items = self.agent_items[agent]
        config = AGENT_SOURCES[agent]

        lines = [
            f"# {agent.upper()} Daily Feed",
            "",
            f"> **Focus**: {config['description']}",
            f"> **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"> **Period**: Last 30 days",
            "",
            "---",
            "",
        ]

        # Group by source
        by_source = defaultdict(list)
        for item in items:
            by_source[item.source].append(item)

        for source, source_items in by_source.items():
            lines.append(f"## {source.title()} ({len(source_items)} items)")
            lines.append("")

            for item in source_items:
                lines.append(f"### {item.title}")
                lines.append(f"- **URL**: {item.url}")

                if item.author:
                    lines.append(f"- **Author**: {item.author}")

                if item.tags:
                    lines.append(f"- **Tags**: {', '.join(item.tags[:5])}")

                if item.metrics:
                    metrics_str = ', '.join([f"{k}: {v}" for k, v in item.metrics.items() if v])
                    if metrics_str:
                        lines.append(f"- **Metrics**: {metrics_str}")

                if item.description:
                    lines.append(f"- **Description**: {item.description}")

                lines.append("")

            lines.append("---")
            lines.append("")

        return '\n'.join(lines)

    def save_feeds(self):
        """Save agent feeds to disk."""
        print("\nSaving feeds to disk...")

        for agent in AGENT_SOURCES.keys():
            feed_content = self.generate_agent_feed(agent)

            if feed_content:
                agent_dir = MEMORY_DIR / agent
                agent_dir.mkdir(parents=True, exist_ok=True)

                feed_file = agent_dir / "DAILY_FEED.md"
                feed_file.write_text(feed_content, encoding='utf-8')
                print(f"  ✓ Saved {agent} feed ({len(self.agent_items.get(agent, []))} items)")

    def save_raw_data(self):
        """Save raw aggregated data for analysis."""
        data_file = DATA_DIR / f"aggregation_{datetime.now().strftime('%Y%m%d')}.json"
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        data = {
            'timestamp': datetime.now().isoformat(),
            'total_items': len(self.all_items),
            'by_agent': {
                agent: [item.to_dict() for item in items]
                for agent, items in self.agent_items.items()
            },
            'all_items': [item.to_dict() for item in self.all_items],
        }

        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"  ✓ Saved raw data to {data_file}")

    def generate_summary(self) -> str:
        """Generate a summary of the aggregation."""
        lines = [
            "## Aggregation Summary",
            "",
            f"- **Total Items**: {len(self.all_items)}",
            f"- **Sources**: {len(self.fetchers)}",
            f"- **Agents**: {len(AGENT_SOURCES)}",
            "",
            "### By Agent:",
        ]

        for agent, items in self.agent_items.items():
            lines.append(f"- **{agent}**: {len(items)} items")

        lines.append("")
        lines.append("### By Source:")

        by_source = defaultdict(int)
        for item in self.all_items:
            by_source[item.source] += 1

        for source, count in sorted(by_source.items(), key=lambda x: -x[1]):
            lines.append(f"- **{source}**: {count} items")

        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Daily Information Aggregator')
    parser.add_argument('--days', type=int, default=30, help='Number of days to fetch')
    parser.add_argument('--limit', type=int, default=20, help='Items per source')
    parser.add_argument('--agent', type=str, default='all', help='Specific agent to update')
    parser.add_argument('--no-save', action='store_true', help='Do not save to disk')
    parser.add_argument('--summary-only', action='store_true', help='Only show summary')

    args = parser.parse_args()

    # Create aggregator
    aggregator = DailyAggregator()

    # Fetch content
    aggregator.fetch_all(days=args.days, limit_per_source=args.limit)

    # Distribute to agents
    aggregator.distribute_to_agents()

    # Print summary
    print("\n" + "="*60)
    print(aggregator.generate_summary())
    print("="*60)

    if args.summary_only:
        return

    # Save feeds
    if not args.no_save:
        aggregator.save_feeds()
        aggregator.save_raw_data()

    # Print sample feed if specific agent requested
    if args.agent != 'all' and args.agent in AGENT_SOURCES:
        print(f"\n--- {args.agent.upper()} FEED SAMPLE ---")
        feed = aggregator.generate_agent_feed(args.agent)
        print(feed[:2000] + "..." if len(feed) > 2000 else feed)

    print("\n✓ Aggregation complete!")


if __name__ == "__main__":
    main()
