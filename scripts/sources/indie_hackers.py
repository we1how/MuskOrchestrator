#!/usr/bin/env python3
"""
Indie Hackers Fetcher - Fixed Version
Fetches posts and case studies from Indie Hackers.
Targets: creator (growth cases, marketing strategies)
"""

import re
import requests
from datetime import datetime
from typing import List, Optional
from bs4 import BeautifulSoup

from .base import BaseFetcher, ContentItem


class IndieHackersFetcher(BaseFetcher):
    """Fetch posts from Indie Hackers."""

    # Revenue milestones
    REVENUE_PATTERNS = [
        r'\$[\d,]+(?:k|K)?\s*(?:MRR|ARR|revenue|monthly)',
        r'\d{1,2},?\d{3}\s*(?:MRR|ARR)',
        r'(?:making|earning)\s+\$[\d,]+',
    ]

    GROWTH_KEYWORDS = [
        'growth', 'marketing', 'launch', 'acquisition', 'seo', 'content marketing',
        'twitter', 'reddit', 'product hunt', 'newsletter', 'email marketing'
    ]

    def __init__(self, cache_dir=None, cache_ttl_hours=6):
        super().__init__(cache_dir, cache_ttl_hours)
        self.base_url = "https://www.indiehackers.com"

    def fetch(self, days: int = 30, limit: int = 15) -> List[ContentItem]:
        """Fetch recent posts from Indie Hackers."""
        # Try cache first
        cached = self.load_from_cache()
        if cached:
            return self.filter_by_date(cached, days)[:limit]

        items = []

        try:
            # Fetch posts from homepage
            items.extend(self._fetch_posts(limit=limit))

        except Exception as e:
            print(f"Error fetching Indie Hackers: {e}")

        # Deduplicate and save
        items = self.deduplicate(items)
        self.save_to_cache(items)

        return self.filter_by_date(items, days)[:limit]

    def _fetch_posts(self, limit: int = 15) -> List[ContentItem]:
        """Fetch posts from Indie Hackers homepage."""
        items = []

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }

        response = requests.get(
            self.base_url,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all post links
        links = soup.find_all('a', href=True)

        # Filter for post/product links
        post_links = []
        seen_urls = set()

        for link in links:
            href = link.get('href', '')
            if '/post/' in href or '/product/' in href:
                # Get the main URL (without query params for deduplication)
                main_url = href.split('?')[0]
                if main_url not in seen_urls:
                    seen_urls.add(main_url)
                    post_links.append(link)

        # Limit unique posts
        post_links = post_links[:limit]

        for link in post_links:
            try:
                item = self._parse_post(link)
                if item:
                    items.append(item)
            except Exception as e:
                print(f"Warning: Failed to parse IH post: {e}")
                continue

        return items

    def _parse_post(self, link) -> Optional[ContentItem]:
        """Parse a post link into ContentItem."""
        href = link.get('href', '')
        if not href:
            return None

        # Build full URL
        if href.startswith('/'):
            url = f"{self.base_url}{href}"
        else:
            url = href

        # Get title from link text
        title = link.get_text(strip=True)

        # Skip if no title or if it's a comment count
        if not title or re.match(r'^\d+comments$', title):
            # Try to find title in parent element
            parent = link.find_parent()
            if parent:
                # Look for title in parent or siblings
                title_elem = parent.find(['h1', 'h2', 'h3', 'h4'])
                if title_elem:
                    title = title_elem.get_text(strip=True)

        # Skip if still no valid title
        if not title or title.lower() in ['comments', '']:
            return None

        # Determine if it's a product or post
        is_product = '/product/' in href
        source_type = 'product-launch' if is_product else 'post'

        # Determine agent target
        agent_target = self._determine_agent_target(title)

        # Extract tags
        tags = ['indie-hackers', 'startup']
        if is_product:
            tags.append('product-launch')
        if any(kw in title.lower() for kw in self.GROWTH_KEYWORDS):
            tags.append('growth')

        return ContentItem(
            title=title,
            url=url,
            source='indiehackers',
            source_type=source_type,
            agent_target=agent_target,
            description="",  # Would need to fetch individual page for description
            published_date=datetime.now(),
            tags=tags,
            metrics={}
        )

    def _determine_agent_target(self, title: str) -> str:
        """Determine which agent this content is most relevant for."""
        text = title.lower()

        # Check for growth/marketing content
        if any(kw in text for kw in self.GROWTH_KEYWORDS):
            return 'creator'

        # Check for product/development content
        if any(kw in text for kw in ['product', 'development', 'tech', 'code']):
            return 'engineer'

        # Default to creator for IH content
        return 'creator'
