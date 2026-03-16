#!/usr/bin/env python3
"""
Information Source Fetchers Package
Provides unified interface for fetching content from various sources.
"""

from .github_trending import GitHubTrendingFetcher
from .hacker_news import HackerNewsFetcher
from .arxiv_fetcher import ArxivFetcher
from .farnam_street import FarnamStreetFetcher
from .indie_hackers import IndieHackersFetcher
from .reddit_fetcher import RedditFetcher
from .zhihu_hot import ZhihuHotFetcher
from .product_hunt import ProductHuntFetcher
from .rsshub_fetcher import RSSHubFetcher, RSSHubManager
from .weibo_hot import WeiboHotFetcher

__all__ = [
    'GitHubTrendingFetcher',
    'HackerNewsFetcher',
    'ArxivFetcher',
    'FarnamStreetFetcher',
    'IndieHackersFetcher',
    'RedditFetcher',
    'ZhihuHotFetcher',
    'ProductHuntFetcher',
    'RSSHubFetcher',
    'RSSHubManager',
    'WeiboHotFetcher',
]

# Source registry for dynamic loading
SOURCE_REGISTRY = {
    'github': GitHubTrendingFetcher,
    'hackernews': HackerNewsFetcher,
    'arxiv': ArxivFetcher,
    'farnamstreet': FarnamStreetFetcher,
    'indiehackers': IndieHackersFetcher,
    'reddit': RedditFetcher,
    'zhihu': ZhihuHotFetcher,
    'producthunt': ProductHuntFetcher,
    'rsshub': RSSHubFetcher,
    'weibo': WeiboHotFetcher,
}
