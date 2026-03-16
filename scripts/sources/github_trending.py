#!/usr/bin/env python3
"""
GitHub Trending Fetcher
Fetches trending repositories from GitHub.
Categorizes by: architecture (for planner), tools (for engineer), quant (for analyst)
"""

import requests
from datetime import datetime, timedelta
from typing import List, Optional
from bs4 import BeautifulSoup
import re

from .base import BaseFetcher, ContentItem


class GitHubTrendingFetcher(BaseFetcher):
    """Fetch trending repositories from GitHub."""

    # Language filters for different agent targets
    ARCHITECTURE_LANGUAGES = ['go', 'rust', 'java', 'scala', 'kotlin', 'typescript']
    TOOLS_LANGUAGES = ['python', 'javascript', 'typescript', 'go', 'rust', 'shell']
    QUANT_KEYWORDS = ['quant', 'trading', 'finance', 'stock', 'portfolio', 'backtest', 'algorithmic']

    def __init__(self, cache_dir=None, cache_ttl_hours=6):
        super().__init__(cache_dir, cache_ttl_hours)
        self.base_url = "https://github.com/trending"
        self.api_base = "https://api.github.com"

    def fetch(self, days: int = 30, limit: int = 20) -> List[ContentItem]:
        """Fetch trending repositories."""
        # Try cache first
        cached = self.load_from_cache()
        if cached:
            return self._distribute_to_agents(cached, limit)

        items = []

        # Fetch different categories
        items.extend(self._fetch_trending('daily', 'all', limit=10))
        items.extend(self._fetch_trending('weekly', 'all', limit=10))

        # Fetch language-specific for engineers
        for lang in ['python', 'typescript', 'rust']:
            items.extend(self._fetch_trending('weekly', lang, limit=5))

        # Save to cache
        self.save_to_cache(items)

        return self._distribute_to_agents(items, limit)

    def _fetch_trending(self, since: str = 'daily', language: str = 'all', limit: int = 10) -> List[ContentItem]:
        """Fetch trending repos for a specific time period and language."""
        items = []

        try:
            url = f"{self.base_url}"
            params = {'since': since}
            if language != 'all':
                params['l'] = language

            headers = {
                'Accept': 'text/html',
                'User-Agent': 'Mozilla/5.0 (compatible; InfoAggregator/1.0)'
            }

            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('article', class_='Box-row')

            for article in articles[:limit]:
                try:
                    item = self._parse_repo(article, language, since)
                    if item:
                        items.append(item)
                except Exception as e:
                    print(f"Warning: Failed to parse repo: {e}")
                    continue

        except Exception as e:
            print(f"Error fetching GitHub trending ({since}, {language}): {e}")

        return items

    def _parse_repo(self, article, language: str, since: str) -> Optional[ContentItem]:
        """Parse a repository article into ContentItem."""
        # Extract repo name
        h2 = article.find('h2')
        if not h2:
            return None

        a_tag = h2.find('a')
        if not a_tag:
            return None

        repo_path = a_tag.get('href', '').strip('/')
        if not repo_path:
            return None

        # Extract description
        description = ""
        p_tag = article.find('p', class_=re.compile('col-9'))
        if p_tag:
            description = p_tag.get_text(strip=True)

        # Extract stars
        stars = 0
        stars_link = article.find('a', href=re.compile('stargazers'))
        if stars_link:
            stars_text = stars_link.get_text(strip=True)
            stars = self._parse_count(stars_text)

        # Extract language
        lang = language if language != 'all' else ""
        lang_span = article.find('span', itemprop='programmingLanguage')
        if lang_span:
            lang = lang_span.get_text(strip=True)

        # Determine agent target based on content
        agent_target = self._determine_agent_target(repo_path, description, lang)

        return ContentItem(
            title=repo_path,
            url=f"https://github.com/{repo_path}",
            source='github',
            source_type='trending',
            agent_target=agent_target,
            description=description,
            published_date=datetime.now(),
            tags=[lang, since] if lang else [since],
            metrics={
                'stars': stars,
                'language': lang,
                'period': since,
            }
        )

    def _parse_count(self, text: str) -> int:
        """Parse count like '1.2k' to integer."""
        text = text.replace(',', '').strip()
        if 'k' in text.lower():
            return int(float(text.lower().replace('k', '')) * 1000)
        if 'm' in text.lower():
            return int(float(text.lower().replace('m', '')) * 1000000)
        try:
            return int(text)
        except:
            return 0

    def _determine_agent_target(self, repo_path: str, description: str, language: str) -> str:
        """Determine which agent this content is most relevant for."""
        text = f"{repo_path} {description}".lower()

        # Check for quant/finance keywords
        if any(kw in text for kw in self.QUANT_KEYWORDS):
            return 'analyst'

        # Check for architecture patterns
        if any(kw in text for kw in ['microservice', 'distributed', 'system', 'architecture', 'kubernetes', 'docker']):
            return 'planner'

        # Check for infrastructure/devops
        if any(kw in text for kw in ['cli', 'tool', 'framework', 'library', 'sdk']):
            return 'engineer'

        # Default based on language
        if language.lower() in self.ARCHITECTURE_LANGUAGES:
            return 'planner'

        return 'engineer'

    def _distribute_to_agents(self, items: List[ContentItem], limit: int) -> List[ContentItem]:
        """Distribute items to appropriate agents with limits."""
        # Group by agent target
        by_agent = {}
        for item in items:
            agent = item.agent_target
            if agent not in by_agent:
                by_agent[agent] = []
            by_agent[agent].append(item)

        # Take top items per agent
        result = []
        per_agent_limit = max(3, limit // 3)

        for agent, agent_items in by_agent.items():
            # Sort by stars
            sorted_items = sorted(agent_items, key=lambda x: x.metrics.get('stars', 0), reverse=True)
            result.extend(sorted_items[:per_agent_limit])

        return result[:limit]
