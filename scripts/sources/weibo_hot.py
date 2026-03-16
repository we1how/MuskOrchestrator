#!/usr/bin/env python3
"""
Weibo Hot Search Fetcher
获取微博热搜榜
Targets: creator (中文社交趋势，热点话题)
"""

import requests
from datetime import datetime
from typing import List, Optional

from .base import BaseFetcher, ContentItem


class WeiboHotFetcher(BaseFetcher):
    """Fetch hot topics from Weibo."""

    def __init__(self, cache_dir=None, cache_ttl_hours=2):
        super().__init__(cache_dir, cache_ttl_hours)
        # Weibo 热搜榜 API
        self.api_url = "https://weibo.com/ajax/side/hotSearch"

    def fetch(self, days: int = 1, limit: int = 50) -> List[ContentItem]:
        """Fetch hot search from Weibo."""
        # Try cache first
        cached = self.load_from_cache()
        if cached:
            return cached[:limit]

        items = []

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Referer': 'https://weibo.com/hot/search',
            }

            response = requests.get(
                self.api_url,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()

            if 'data' in data and 'realtime' in data['data']:
                for i, item_data in enumerate(data['data']['realtime'][:limit]):
                    item = self._parse_item(item_data)
                    if item:
                        items.append(item)

        except Exception as e:
            print(f"Error fetching Weibo hot search: {e}")

        # Save to cache
        self.save_to_cache(items)

        return items[:limit]

    def _parse_item(self, data: dict) -> Optional[ContentItem]:
        """Parse a Weibo hot item into ContentItem."""
        try:
            # 热搜词
            title = data.get('word', '')
            if not title:
                return None

            # 链接
            url = f"https://s.weibo.com/weibo?q=%23{title}%23"

            # 热度值
            raw_hot = data.get('raw_hot', 0)
            category = data.get('category', '')

            # 是否爆/热/新
            flag = data.get('flag', '')

            # 描述
            description = data.get('note', '') or data.get('word_scheme', '')

            # 确定目标 Agent
            agent_target = self._determine_agent_target(title, category)

            metrics = {
                'heat': raw_hot,
                'rank': data.get('rank', 0),
                'flag': flag
            }

            return ContentItem(
                title=title,
                url=url,
                source='weibo',
                source_type='trending',
                agent_target=agent_target,
                description=description[:200] if description else title,
                published_date=datetime.now(),
                tags=['weibo', 'hot-search', 'chinese'],
                metrics=metrics
            )

        except Exception as e:
            print(f"Warning: Failed to parse Weibo item: {e}")
            return None

    def _determine_agent_target(self, title: str, category: str) -> str:
        """Determine which agent this content is most relevant for."""
        text = f"{title} {category}".lower()

        business_keywords = ['财经', '商业', '创业', '投资', '品牌', '营销', '公司']
        tech_keywords = ['科技', 'AI', '人工智能', '编程', '互联网', '程序员']

        if any(kw in text for kw in business_keywords):
            return 'creator'
        if any(kw in text for kw in tech_keywords):
            return 'engineer'

        return 'creator'
