#!/usr/bin/env python3
"""
Base fetcher class for all information sources.
Defines the interface that all fetchers must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import hashlib


@dataclass
class ContentItem:
    """Represents a single piece of content from any source."""
    title: str
    url: str
    source: str  # e.g., 'github', 'hackernews', 'arxiv'
    source_type: str  # e.g., 'trending', 'paper', 'discussion'
    agent_target: str  # e.g., 'engineer', 'analyst', 'planner'

    # Optional fields
    description: str = ""
    author: str = ""
    published_date: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)  # stars, votes, etc.
    summary: str = ""
    content_hash: str = ""

    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = self._generate_hash()

    def _generate_hash(self) -> str:
        """Generate unique hash for deduplication."""
        content = f"{self.title}{self.url}{self.source}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'title': self.title,
            'url': self.url,
            'source': self.source,
            'source_type': self.source_type,
            'agent_target': self.agent_target,
            'description': self.description,
            'author': self.author,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'tags': self.tags,
            'metrics': self.metrics,
            'summary': self.summary,
            'content_hash': self.content_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentItem':
        """Create from dictionary."""
        if data.get('published_date'):
            data['published_date'] = datetime.fromisoformat(data['published_date'])
        return cls(**data)


class BaseFetcher(ABC):
    """Base class for all content fetchers."""

    def __init__(self, cache_dir: Optional[Path] = None, cache_ttl_hours: int = 6):
        """
        Initialize fetcher.

        Args:
            cache_dir: Directory to cache fetched content
            cache_ttl_hours: How long to keep cache before refresh
        """
        self.cache_dir = cache_dir
        self.cache_ttl_hours = cache_ttl_hours
        self.name = self.__class__.__name__.replace('Fetcher', '').lower()

        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def fetch(self, days: int = 30, limit: int = 20) -> List[ContentItem]:
        """
        Fetch content from the source.

        Args:
            days: How many days back to fetch
            limit: Maximum number of items to return

        Returns:
            List of ContentItem objects
        """
        pass

    def get_cache_path(self, suffix: str = "") -> Optional[Path]:
        """Get cache file path for this fetcher."""
        if not self.cache_dir:
            return None
        filename = f"{self.name}{suffix}.json"
        return self.cache_dir / filename

    def load_from_cache(self, suffix: str = "") -> Optional[List[ContentItem]]:
        """Load content from cache if valid."""
        cache_path = self.get_cache_path(suffix)
        if not cache_path or not cache_path.exists():
            return None

        # Check TTL
        mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        age_hours = (datetime.now() - mtime).total_seconds() / 3600

        if age_hours > self.cache_ttl_hours:
            return None

        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [ContentItem.from_dict(item) for item in data]
        except Exception:
            return None

    def save_to_cache(self, items: List[ContentItem], suffix: str = ""):
        """Save content to cache."""
        cache_path = self.get_cache_path(suffix)
        if not cache_path:
            return

        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump([item.to_dict() for item in items], f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save cache for {self.name}: {e}")

    def filter_by_date(self, items: List[ContentItem], days: int) -> List[ContentItem]:
        """Filter items to only include those within the date range."""
        if not days:
            return items

        from datetime import timezone
        cutoff = datetime.now(timezone.utc) - __import__('datetime').timedelta(days=days)

        result = []
        for item in items:
            if item.published_date:
                # Ensure both dates are timezone-aware for comparison
                item_date = item.published_date
                if item_date.tzinfo is None:
                    item_date = item_date.replace(tzinfo=timezone.utc)
                if cutoff.tzinfo is None:
                    cutoff = cutoff.replace(tzinfo=timezone.utc)
                if item_date >= cutoff:
                    result.append(item)
        return result

    def deduplicate(self, items: List[ContentItem]) -> List[ContentItem]:
        """Remove duplicate items based on content hash."""
        seen = set()
        unique = []
        for item in items:
            if item.content_hash not in seen:
                seen.add(item.content_hash)
                unique.append(item)
        return unique
