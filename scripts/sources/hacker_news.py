#!/usr/bin/env python3
"""
Hacker News Fetcher
Fetches top stories and discussions from Hacker News.
Targets: engineer (technical discussions)
"""

import requests
from datetime import datetime
from typing import List, Optional

from .base import BaseFetcher, ContentItem


class HackerNewsFetcher(BaseFetcher):
    """Fetch top stories from Hacker News."""

    # Keywords for categorization
    TECH_KEYWORDS = [
        'programming', 'software', 'code', 'development', 'api', 'database',
        'cloud', 'devops', 'architecture', 'performance', 'security',
        'python', 'javascript', 'rust', 'go', 'typescript'
    ]

    STARTUP_KEYWORDS = [
        'startup', 'founder', 'entrepreneur', 'business', 'product',
        'marketing', 'growth', 'revenue', 'funding', 'saas'
    ]

    def __init__(self, cache_dir=None, cache_ttl_hours=3):
        super().__init__(cache_dir, cache_ttl_hours)
        self.api_base = "https://hacker-news.firebaseio.com/v0"

    def fetch(self, days: int = 30, limit: int = 20) -> List[ContentItem]:
        """Fetch top stories from HN."""
        # Try cache first
        cached = self.load_from_cache()
        if cached:
            return cached[:limit]

        items = []

        try:
            # Fetch top stories
            top_ids = self._fetch_top_stories(limit * 2)

            for story_id in top_ids:
                try:
                    item = self._fetch_story(story_id)
                    if item:
                        items.append(item)
                except Exception as e:
                    print(f"Warning: Failed to fetch story {story_id}: {e}")
                    continue

                if len(items) >= limit:
                    break

        except Exception as e:
            print(f"Error fetching Hacker News: {e}")

        # Save to cache
        self.save_to_cache(items)

        return items[:limit]

    def _fetch_top_stories(self, limit: int = 50) -> List[int]:
        """Fetch list of top story IDs."""
        response = requests.get(
            f"{self.api_base}/topstories.json",
            timeout=30
        )
        response.raise_for_status()
        return response.json()[:limit]

    def _fetch_story(self, story_id: int) -> Optional[ContentItem]:
        """Fetch a single story by ID."""
        response = requests.get(
            f"{self.api_base}/item/{story_id}.json",
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        if not data or data.get('deleted') or data.get('dead'):
            return None

        # Skip job postings and polls
        if data.get('type') != 'story':
            return None

        title = data.get('title', '')
        url = data.get('url', '')
        score = data.get('score', 0)
        descendants = data.get('descendants', 0)
        author = data.get('by', '')
        timestamp = data.get('time', 0)

        # Use HN discussion URL if no external URL
        if not url:
            url = f"https://news.ycombinator.com/item?id={story_id}"

        # Determine agent target
        agent_target = self._determine_agent_target(title)

        # Parse timestamp
        published_date = datetime.fromtimestamp(timestamp) if timestamp else datetime.now()

        return ContentItem(
            title=title,
            url=url,
            source='hackernews',
            source_type='discussion',
            agent_target=agent_target,
            description=f"HN Discussion with {descendants} comments",
            author=author,
            published_date=published_date,
            tags=['hackernews', 'tech-news'],
            metrics={
                'score': score,
                'comments': descendants,
            }
        )

    def _determine_agent_target(self, title: str) -> str:
        """Determine which agent this content is most relevant for."""
        title_lower = title.lower()

        # Check for startup/business content
        if any(kw in title_lower for kw in self.STARTUP_KEYWORDS):
            return 'creator'

        # Default to engineer for tech content
        return 'engineer'
