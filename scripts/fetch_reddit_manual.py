#!/usr/bin/env python3
"""
Reddit 数据获取 - 手动配置版本
用户授权自动配置，提供账号：linyoujia0886@gmail.com / 13580lwh
"""

import json
import time
import requests
from pathlib import Path
from datetime import datetime


class RedditManualFetcher:
    """Reddit 数据获取器 - 支持手动配置和测试"""

    def __init__(self):
        self.config_path = Path("/Users/linweihao/project/MuskOrchestrator/config/reddit_config.json")
        self.config = self._load_config()
        self.access_token = None

    def _load_config(self):
        """加载配置"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        return {}

    def _get_access_token(self):
        """使用 client_credentials 流程获取访问令牌"""
        if not self.config.get("client_id") or self.config["client_id"] == "YOUR_CLIENT_ID":
            print("❌ 未配置 Reddit API 凭证")
            return None

        auth = requests.auth.HTTPBasicAuth(
            self.config["client_id"],
            self.config["client_secret"]
        )

        data = {
            'grant_type': 'client_credentials',
        }

        headers = {
            'User-Agent': self.config.get("user_agent", "MuskOrchestrator/1.0")
        }

        try:
            response = requests.post(
                'https://www.reddit.com/api/v1/access_token',
                auth=auth,
                data=data,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data.get('access_token')
            return self.access_token

        except Exception as e:
            print(f"❌ 获取访问令牌失败: {e}")
            return None

    def fetch_subreddit(self, subreddit: str, limit: int = 10, sort: str = 'hot'):
        """获取 subreddit 帖子"""
        if not self.access_token:
            self.access_token = self._get_access_token()

        if not self.access_token:
            return []

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'User-Agent': self.config.get("user_agent", "MuskOrchestrator/1.0")
        }

        try:
            response = requests.get(
                f'https://oauth.reddit.com/r/{subreddit}/{sort}',
                headers=headers,
                params={'limit': limit},
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            posts = []

            for child in data.get('data', {}).get('children', []):
                post = child.get('data', {})
                posts.append({
                    'title': post.get('title', ''),
                    'url': f"https://www.reddit.com{post.get('permalink', '')}",
                    'score': post.get('score', 0),
                    'comments': post.get('num_comments', 0),
                    'subreddit': post.get('subreddit', ''),
                    'author': post.get('author', ''),
                    'created': datetime.fromtimestamp(post.get('created_utc', 0))
                })

            return posts

        except Exception as e:
            print(f"❌ 获取 r/{subreddit} 失败: {e}")
            return []

    def test_connection(self):
        """测试 Reddit API 连接"""
        print("🧪 测试 Reddit API 连接...")
        print()

        posts = self.fetch_subreddit('technology', limit=3)

        if posts:
            print(f"✅ 连接成功! 获取到 {len(posts)} 条帖子")
            print()
            for p in posts[:2]:
                print(f"  📌 {p['title'][:60]}...")
                print(f"     👍 {p['score']} | 💬 {p['comments']} | r/{p['subreddit']}")
            return True
        else:
            print("❌ 连接失败，请检查配置")
            return False


def show_setup_guide():
    """显示配置指南"""
    print("=" * 70)
    print("Reddit API 配置指南")
    print("=" * 70)
    print()
    print("账号信息（用户已提供）:")
    print("  📧 Google 邮箱: linyoujia0886@gmail.com")
    print("  🔑 Google 密码: 13580lwh")
    print("  👤 Reddit 用户名: linyoujia0886")
    print()
    print("配置步骤:")
    print()
    print("1️⃣  访问 Reddit 应用管理页面:")
    print("    https://www.reddit.com/prefs/apps")
    print()
    print("2️⃣  点击 'create another app...'")
    print()
    print("3️⃣  填写应用信息:")
    print("    📛 Name:        MuskOrchestrator")
    print("    📋 Type:        script")
    print("    📝 Description: Personal information aggregator for learning")
    print("    🔗 Redirect URI: http://localhost:8080")
    print()
    print("4️⃣  创建后，复制以下信息到 config/reddit_config.json:")
    print()
    print("    client_id:     在应用名称下方的字符串 (14字符)")
    print("    client_secret: 点击 'edit' 后显示的 secret")
    print()
    print("5️⃣  更新配置文件:")
    print("    文件路径: /Users/linweihao/project/MuskOrchestrator/config/reddit_config.json")
    print()
    print("6️⃣  测试连接:")
    print("    python scripts/fetch_reddit_manual.py --test")
    print()
    print("=" * 70)


if __name__ == "__main__":
    import sys

    fetcher = RedditManualFetcher()

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        fetcher.test_connection()
    elif len(sys.argv) > 1 and sys.argv[1] == "--fetch":
        subreddit = sys.argv[2] if len(sys.argv) > 2 else "startups"
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10

        print(f"🔍 获取 r/{subreddit} 的前 {limit} 条帖子...")
        print()

        posts = fetcher.fetch_subreddit(subreddit, limit)

        if posts:
            for i, p in enumerate(posts, 1):
                print(f"{i}. {p['title']}")
                print(f"   👍 {p['score']} | 💬 {p['comments']} | by u/{p['author']}")
                print(f"   🔗 {p['url']}")
                print()
        else:
            print("❌ 未获取到数据")
    else:
        show_setup_guide()
        print()
        print("正在检查当前配置状态...")
        print()

        if fetcher.config.get("client_id") and fetcher.config["client_id"] != "YOUR_CLIENT_ID":
            print("✅ 检测到已配置 client_id")
            print("🧪 自动测试连接...")
            print()
            fetcher.test_connection()
        else:
            print("❌ 尚未配置 Reddit API")
            print("   请按照上述步骤完成配置")
