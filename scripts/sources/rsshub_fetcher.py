#!/usr/bin/env python3
"""
RSSHub Fetcher
利用本地 RSSHub 服务获取各种网站内容
解决 Reddit、知乎、Product Hunt 等站点的抓取限制
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Optional

from .base import BaseFetcher, ContentItem


class RSSHubFetcher(BaseFetcher):
    """使用 RSSHub 获取各种网站内容"""

    def __init__(self, cache_dir=None, cache_ttl_hours=3):
        super().__init__(cache_dir, cache_ttl_hours)
        self.rsshub_url = "http://localhost:1200"

    def fetch(self, days: int = 1, limit: int = 20) -> list:
        """Base fetch method - not used directly, use specific methods instead"""
        return []

    def _fetch_rss(self, path: str, limit: int = 10) -> List[ContentItem]:
        """从 RSSHub 获取 RSS 内容"""
        items = []

        try:
            response = requests.get(
                f"{self.rsshub_url}{path}",
                timeout=30
            )
            response.raise_for_status()

            # 解析 RSS XML
            root = ET.fromstring(response.text)

            # 处理 RSS 2.0 格式
            channel = root.find('channel')
            if channel is not None:
                for item in channel.findall('item')[:limit]:
                    parsed = self._parse_rss_item(item)
                    if parsed:
                        items.append(parsed)

        except Exception as e:
            print(f"Error fetching RSSHub {path}: {e}")

        return items

    def _parse_rss_item(self, item) -> Optional[ContentItem]:
        """解析 RSS item"""
        try:
            title = item.findtext('title', '')
            link = item.findtext('link', '')
            description = item.findtext('description', '')
            pub_date = item.findtext('pubDate', '')
            author = item.findtext('author', '')

            if not title:
                return None

            # 解析日期
            published_date = datetime.now()
            if pub_date:
                try:
                    from email.utils import parsedate_to_datetime
                    published_date = parsedate_to_datetime(pub_date)
                except:
                    pass

            return ContentItem(
                title=title,
                url=link,
                source='rsshub',
                source_type='rss',
                agent_target='creator',  # 默认给 creator
                description=description[:300] + "..." if len(description) > 300 else description,
                author=author,
                published_date=published_date,
                tags=['rsshub'],
                metrics={}
            )
        except Exception as e:
            print(f"Warning: Failed to parse RSS item: {e}")
            return None

    def fetch_reddit(self, subreddit: str, limit: int = 10) -> List[ContentItem]:
        """通过 RSSHub 获取 Reddit 内容"""
        items = self._fetch_rss(f"/reddit/{subreddit}", limit)
        for item in items:
            item.source = 'reddit'
            item.agent_target = 'creator'
            item.tags = ['reddit', subreddit, 'discussion']
        return items

    def fetch_zhihu_hot(self, limit: int = 20) -> List[ContentItem]:
        """通过 RSSHub 获取知乎热榜"""
        items = self._fetch_rss("/zhihu/hotlist", limit)
        for item in items:
            item.source = 'zhihu'
            item.agent_target = 'creator'
            item.tags = ['zhihu', 'hot-topic', 'chinese']
        return items

    def fetch_producthunt(self, limit: int = 15) -> List[ContentItem]:
        """通过 RSSHub 获取 Product Hunt"""
        items = self._fetch_rss("/producthunt/today", limit)
        for item in items:
            item.source = 'producthunt'
            item.agent_target = 'creator'
            item.tags = ['producthunt', 'product-launch']
        return items

    def fetch_github_trending(self, lang: str = 'daily', limit: int = 10) -> List[ContentItem]:
        """通过 RSSHub 获取 GitHub Trending"""
        items = self._fetch_rss(f"/github/trending/{lang}", limit)
        for item in items:
            item.source = 'github'
            item.agent_target = 'engineer'
            item.tags = ['github', 'trending']
        return items

    def fetch_hackernews(self, limit: int = 15) -> List[ContentItem]:
        """通过 RSSHub 获取 Hacker News"""
        items = self._fetch_rss("/hackernews", limit)
        for item in items:
            item.source = 'hackernews'
            item.agent_target = 'engineer'
            item.tags = ['hackernews', 'tech-news']
        return items

    def check_health(self) -> bool:
        """检查 RSSHub 服务是否可用"""
        try:
            response = requests.get(self.rsshub_url, timeout=5)
            return response.status_code == 200
        except:
            return False


class RSSHubManager:
    """RSSHub 管理器，兼容 stock-platform 项目"""

    def __init__(self):
        self.rsshub_url = "http://localhost:1200"

    def is_running(self) -> bool:
        """检查 RSSHub 是否运行"""
        try:
            response = requests.get(self.rsshub_url, timeout=3)
            return response.status_code == 200
        except:
            return False

    def get_status(self) -> dict:
        """获取 RSSHub 状态"""
        running = self.is_running()
        return {
            'running': running,
            'url': self.rsshub_url,
            'message': 'RSSHub 运行中' if running else 'RSSHub 未启动'
        }
