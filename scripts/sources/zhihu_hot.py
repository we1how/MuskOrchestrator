#!/usr/bin/env python3
"""
Zhihu Hot List Fetcher
Fetches trending topics from Zhihu (知乎热榜).
Targets: creator (中文内容趋势，话题洞察)
Alternative to WeChat Index for Chinese market trends.
"""

import requests
from datetime import datetime
from typing import List, Optional

from .base import BaseFetcher, ContentItem


class ZhihuHotFetcher(BaseFetcher):
    """Fetch trending topics from Zhihu Hot List."""

    # Categories for filtering
    BUSINESS_KEYWORDS = [
        '创业', '商业', '赚钱', '投资', '公司', '品牌', '营销', '产品',
        '互联网', '科技', 'AI', '人工智能', ' startup', '商业模式'
    ]

    TECH_KEYWORDS = [
        '编程', '代码', '开发', '程序员', 'Python', 'JavaScript',
        '技术', '算法', '数据库', '开源', 'GitHub', 'AI', '大模型'
    ]

    def __init__(self, cache_dir=None, cache_ttl_hours=3):
        super().__init__(cache_dir, cache_ttl_hours)
        self.api_url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"

    def fetch(self, days: int = 1, limit: int = 20) -> List[ContentItem]:
        """Fetch hot topics from Zhihu."""
        # Try cache first
        cached = self.load_from_cache()
        if cached:
            return cached[:limit]

        items = []

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Referer': 'https://www.zhihu.com/hot',
                'Cookie': '_zap=; d_c0=',  # Minimal cookie to pass basic check
            }

            # Zhihu now uses a different endpoint for public access
            # Fallback to scraping the hot list page
            response = requests.get(
                'https://www.zhihu.com/hot',
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            if 'data' in data:
                for item_data in data['data'][:limit]:
                    item = self._parse_item(item_data)
                    if item:
                        items.append(item)

        except Exception as e:
            print(f"Error fetching Zhihu hot list: {e}")

        # Save to cache
        self.save_to_cache(items)

        return items[:limit]

    def _parse_item(self, data: dict) -> Optional[ContentItem]:
        """Parse a Zhihu hot item into ContentItem."""
        try:
            card = data.get('target', {})

            title = card.get('title', '') or card.get('question', {}).get('title', '')
            if not title:
                return None

            url = card.get('url', '')
            if url and not url.startswith('http'):
                url = f"https://www.zhihu.com{url}"

            # Get detail text if available
            detail_text = card.get('excerpt', '') or card.get('detail_text', '')

            # Get metrics
            metrics = {}
            if 'metrics_area' in data:
                for metric in data['metrics_area']:
                    text = metric.get('text', '')
                    if '万' in text or '热度' in text:
                        metrics['heat'] = text

            # Get answer count if it's a question
            answer_count = card.get('answer_count', 0)
            if answer_count:
                metrics['answers'] = answer_count

            # Determine agent target
            agent_target = self._determine_agent_target(title, detail_text)

            return ContentItem(
                title=title,
                url=url,
                source='zhihu',
                source_type='trending',
                agent_target=agent_target,
                description=detail_text[:300] + "..." if len(detail_text) > 300 else detail_text,
                published_date=datetime.now(),
                tags=['zhihu', 'hot-topic', 'chinese'],
                metrics=metrics
            )

        except Exception as e:
            print(f"Warning: Failed to parse Zhihu item: {e}")
            return None

    def _determine_agent_target(self, title: str, detail: str) -> str:
        """Determine which agent this content is most relevant for."""
        text = f"{title} {detail}".lower()

        # Check for business/startup content
        if any(kw in text for kw in self.BUSINESS_KEYWORDS):
            return 'creator'

        # Check for tech content
        if any(kw in text for kw in self.TECH_KEYWORDS):
            return 'engineer'

        # Default to creator (for general trends)
        return 'creator'
