#!/usr/bin/env python3
"""
Farnam Street Fetcher
Fetches articles from Farnam Street (fs.blog) - focused on mental models and decision making.
Targets: planner (decision frameworks), mentor (mental models)
"""

import re
import requests
from datetime import datetime
from typing import List, Optional
from bs4 import BeautifulSoup

from .base import BaseFetcher, ContentItem


class FarnamStreetFetcher(BaseFetcher):
    """Fetch articles from Farnam Street blog."""

    # Mental model categories
    MENTAL_MODELS = [
        'inversion', 'second-order thinking', 'occam\'s razor', 'hanlon\'s razor',
        'thought experiment', 'probabilistic thinking', 'bayesian thinking',
        'systems thinking', 'feedback loops', 'margin of safety'
    ]

    DECISION_KEYWORDS = [
        'decision', 'framework', 'mental model', 'cognitive bias',
        'thinking', 'judgment', 'choice', 'strategy'
    ]

    def __init__(self, cache_dir=None, cache_ttl_hours=12):
        super().__init__(cache_dir, cache_ttl_hours)
        self.base_url = "https://fs.blog"
        self.blog_url = "https://fs.blog/blog/"

    def fetch(self, days: int = 30, limit: int = 15) -> List[ContentItem]:
        """Fetch recent articles from Farnam Street."""
        # Try cache first
        cached = self.load_from_cache()
        if cached:
            return self.filter_by_date(cached, days)[:limit]

        items = []

        try:
            # Fetch blog page
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; InfoAggregator/1.0)'
            }
            response = requests.get(self.blog_url, headers=headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find article cards
            articles = soup.find_all('article') or soup.find_all('div', class_=re.compile('post|entry|article'))

            for article in articles[:limit * 2]:
                try:
                    item = self._parse_article(article)
                    if item:
                        items.append(item)
                except Exception as e:
                    print(f"Warning: Failed to parse FS article: {e}")
                    continue

        except Exception as e:
            print(f"Error fetching Farnam Street: {e}")

        # Deduplicate and save
        items = self.deduplicate(items)
        self.save_to_cache(items)

        return self.filter_by_date(items, days)[:limit]

    def _parse_article(self, article) -> Optional[ContentItem]:
        """Parse an article element into ContentItem."""
        # Find title and link
        title_elem = article.find(['h2', 'h3', 'h1']) or article.find('a', class_=re.compile('title|entry'))
        if not title_elem:
            return None

        a_tag = title_elem.find('a') if title_elem.name != 'a' else title_elem
        if not a_tag:
            return None

        title = a_tag.get_text(strip=True)
        url = a_tag.get('href', '')

        if not url.startswith('http'):
            url = self.base_url + url

        # Find description/excerpt
        description = ""
        desc_elem = article.find(['p', 'div'], class_=re.compile('excerpt|summary|description'))
        if desc_elem:
            description = desc_elem.get_text(strip=True)

        # Find date
        published_date = None
        date_elem = article.find('time') or article.find(['span', 'div'], class_=re.compile('date|time'))
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            published_date = self._parse_date(date_text)

        # Determine agent target
        agent_target = self._determine_agent_target(title, description)

        # Extract tags
        tags = ['mental-models', 'decision-making']
        if any(mm in title.lower() for mm in self.MENTAL_MODELS):
            tags.append('mental-model')

        return ContentItem(
            title=title,
            url=url,
            source='farnamstreet',
            source_type='article',
            agent_target=agent_target,
            description=description[:400] + "..." if len(description) > 400 else description,
            author='Farnam Street',
            published_date=published_date or datetime.now(),
            tags=tags,
            metrics={}
        )

    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse date from various formats."""
        # Try common formats
        formats = [
            '%B %d, %Y',
            '%b %d, %Y',
            '%Y-%m-%d',
            '%d %B %Y',
        ]

        # Clean up the text
        date_text = re.sub(r'\s+', ' ', date_text.strip())

        for fmt in formats:
            try:
                return datetime.strptime(date_text, fmt)
            except:
                continue

        return None

    def _determine_agent_target(self, title: str, description: str) -> str:
        """Determine which agent this content is most relevant for."""
        text = f"{title} {description}".lower()

        # Check for decision frameworks
        if any(kw in text for kw in ['framework', 'decision', 'strategy', 'planning']):
            return 'planner'

        # Default to mentor for mental models
        return 'mentor'
