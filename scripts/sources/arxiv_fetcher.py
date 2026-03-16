#!/usr/bin/env python3
"""
ArXiv Fetcher
Fetches papers from arXiv, specifically focusing on quantitative finance (q-fin).
Targets: analyst (quantitative research)
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Optional
from urllib.parse import urlencode

from .base import BaseFetcher, ContentItem


class ArxivFetcher(BaseFetcher):
    """Fetch papers from arXiv."""

    # Categories of interest
    CATEGORIES = {
        'q-fin': 'Quantitative Finance',
        'q-fin.PM': 'Portfolio Management',
        'q-fin.TR': 'Trading and Market Microstructure',
        'q-fin.RM': 'Risk Management',
        'q-fin.ST': 'Statistical Finance',
        'q-fin.MF': 'Mathematical Finance',
        'q-fin.CP': 'Computational Finance',
        'cs.LG': 'Machine Learning',
        'cs.AI': 'Artificial Intelligence',
        'stat.ML': 'Statistics - Machine Learning',
    }

    def __init__(self, cache_dir=None, cache_ttl_hours=12):
        super().__init__(cache_dir, cache_ttl_hours)
        self.api_base = "http://export.arxiv.org/api/query"

    def fetch(self, days: int = 30, limit: int = 20) -> List[ContentItem]:
        """Fetch recent papers from arXiv."""
        # Try cache first
        cached = self.load_from_cache()
        if cached:
            return self.filter_by_date(cached, days)[:limit]

        items = []

        # Fetch from different categories
        for category in ['q-fin', 'cs.LG', 'cs.AI']:
            try:
                cat_items = self._fetch_category(category, limit=limit//3 + 5)
                items.extend(cat_items)
            except Exception as e:
                print(f"Error fetching arXiv category {category}: {e}")

        # Deduplicate and save
        items = self.deduplicate(items)
        self.save_to_cache(items)

        return self.filter_by_date(items, days)[:limit]

    def _fetch_category(self, category: str, limit: int = 10) -> List[ContentItem]:
        """Fetch papers from a specific category."""
        items = []

        # Build query
        query_params = {
            'search_query': f'cat:{category}',
            'start': 0,
            'max_results': limit,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending',
        }

        response = requests.get(
            self.api_base,
            params=query_params,
            timeout=60
        )
        response.raise_for_status()

        # Parse XML
        root = ET.fromstring(response.content)

        # Define namespace
        ns = {
            'atom': 'http://www.w3.org/2005/Atom',
            'arxiv': 'http://arxiv.org/schemas/atom'
        }

        for entry in root.findall('atom:entry', ns):
            try:
                item = self._parse_entry(entry, ns, category)
                if item:
                    items.append(item)
            except Exception as e:
                print(f"Warning: Failed to parse arXiv entry: {e}")
                continue

        return items

    def _parse_entry(self, entry, ns: dict, category: str) -> Optional[ContentItem]:
        """Parse an arXiv entry into ContentItem."""
        # Extract title
        title_elem = entry.find('atom:title', ns)
        if title_elem is None:
            return None
        title = title_elem.text.strip() if title_elem.text else ""

        # Extract ID/URL
        id_elem = entry.find('atom:id', ns)
        url = id_elem.text if id_elem is not None else ""

        # Extract abstract
        summary_elem = entry.find('atom:summary', ns)
        abstract = summary_elem.text.strip() if summary_elem is not None and summary_elem.text else ""

        # Extract authors
        authors = []
        for author in entry.findall('atom:author', ns):
            name_elem = author.find('atom:name', ns)
            if name_elem is not None and name_elem.text:
                authors.append(name_elem.text)

        # Extract published date
        published_elem = entry.find('atom:published', ns)
        published_date = None
        if published_elem is not None and published_elem.text:
            try:
                published_date = datetime.fromisoformat(published_elem.text.replace('Z', '+00:00'))
            except:
                pass

        # Extract categories/tags
        tags = []
        for cat in entry.findall('atom:category', ns):
            term = cat.get('term', '')
            if term:
                tags.append(term)

        # Extract arXiv-specific metadata
        primary_cat = entry.find('arxiv:primary_category', ns)
        if primary_cat is not None:
            primary = primary_cat.get('term', '')
        else:
            primary = category

        # Determine agent target
        agent_target = self._determine_agent_target(primary, title)

        return ContentItem(
            title=title,
            url=url,
            source='arxiv',
            source_type='paper',
            agent_target=agent_target,
            description=abstract[:500] + "..." if len(abstract) > 500 else abstract,
            author=', '.join(authors[:3]) + (" et al." if len(authors) > 3 else ""),
            published_date=published_date,
            tags=tags[:5],
            metrics={
                'category': primary,
                'authors_count': len(authors),
            }
        )

    def _determine_agent_target(self, category: str, title: str) -> str:
        """Determine which agent this content is most relevant for."""
        title_lower = title.lower()

        # Quantitative finance goes to analyst
        if 'q-fin' in category:
            return 'analyst'

        # ML/AI papers go to engineer (for implementation)
        if any(cat in category for cat in ['cs.LG', 'cs.AI', 'stat.ML']):
            # Check if it's finance-related
            if any(kw in title_lower for kw in ['portfolio', 'trading', 'finance', 'stock', 'risk']):
                return 'analyst'
            return 'engineer'

        return 'analyst'
