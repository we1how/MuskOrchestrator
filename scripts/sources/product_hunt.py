#!/usr/bin/env python3
"""
Product Hunt Fetcher
Fetches trending products and launches from Product Hunt.
Targets: creator (product launches, growth strategies)
"""

import requests
from datetime import datetime, timedelta
from typing import List, Optional

from .base import BaseFetcher, ContentItem


class ProductHuntFetcher(BaseFetcher):
    """Fetch trending products from Product Hunt."""

    # Categories of interest
    RELEVANT_TOPICS = [
        'developer-tools', 'productivity', 'artificial-intelligence',
        ' SaaS', 'marketing', 'analytics', 'api'
    ]

    GROWTH_KEYWORDS = [
        'launch', 'growth', 'marketing', 'acquisition', 'revenue',
        'MRR', 'ARR', 'startup', 'bootstrapped'
    ]

    def __init__(self, cache_dir=None, cache_ttl_hours=6):
        super().__init__(cache_dir, cache_ttl_hours)
        self.api_url = "https://www.producthunt.com/feed"
        # Note: Product Hunt has an official GraphQL API that requires authentication
        # This fetcher uses the public RSS feed

    def fetch(self, days: int = 7, limit: int = 15) -> List[ContentItem]:
        """Fetch trending products from Product Hunt."""
        # Try cache first
        cached = self.load_from_cache()
        if cached:
            return self.filter_by_date(cached, days)[:limit]

        items = []

        try:
            # Product Hunt RSS feed
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; InfoAggregator/1.0)'
            }

            # Fetch today's featured products
            response = requests.get(
                self.api_url,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            # Parse RSS-like content (actually returns JSON)
            import xml.etree.ElementTree as ET

            root = ET.fromstring(response.text)

            # RSS namespace
            ns = {'content': 'http://purl.org/rss/1.0/modules/content/'}

            for item in root.findall('.//item', ns)[:limit]:
                parsed = self._parse_item(item)
                if parsed:
                    items.append(parsed)

        except Exception as e:
            print(f"Error fetching Product Hunt: {e}")
            # Fallback: return empty list
            pass

        # Save to cache
        self.save_to_cache(items)

        return self.filter_by_date(items, days)[:limit]

    def _parse_item(self, item) -> Optional[ContentItem]:
        """Parse a Product Hunt item into ContentItem."""
        try:
            import xml.etree.ElementTree as ET

            title_elem = item.find('title')
            link_elem = item.find('link')
            desc_elem = item.find('description')
            pub_date_elem = item.find('pubDate')

            if title_elem is None:
                return None

            title = title_elem.text or ''
            url = link_elem.text if link_elem is not None else ''
            description = desc_elem.text if desc_elem is not None else ''

            # Parse date
            published_date = datetime.now()
            if pub_date_elem is not None and pub_date_elem.text:
                try:
                    # Product Hunt uses RFC 2822 format
                    from email.utils import parsedate_to_datetime
                    published_date = parsedate_to_datetime(pub_date_elem.text)
                except:
                    pass

            # Determine agent target
            agent_target = self._determine_agent_target(title, description)

            return ContentItem(
                title=title,
                url=url,
                source='producthunt',
                source_type='product-launch',
                agent_target=agent_target,
                description=description[:400] + "..." if len(description) > 400 else description,
                published_date=published_date,
                tags=['producthunt', 'product-launch'],
                metrics={}
            )

        except Exception as e:
            print(f"Warning: Failed to parse Product Hunt item: {e}")
            return None

    def _determine_agent_target(self, title: str, description: str) -> str:
        """Determine which agent this content is most relevant for."""
        text = f"{title} {description}".lower()

        # Check for growth/business content
        if any(kw in text for kw in self.GROWTH_KEYWORDS):
            return 'creator'

        # Check for dev tools
        if any(kw in text for kw in ['developer', 'api', 'sdk', 'code', 'github']):
            return 'engineer'

        # Default to creator (Product Hunt is primarily for product launches)
        return 'creator'
