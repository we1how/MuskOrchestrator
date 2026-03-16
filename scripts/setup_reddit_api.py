#!/usr/bin/env python3
"""
Reddit API 自动配置脚本
使用 Playwright 模拟浏览器行为登录并创建应用
"""

import json
import time
from pathlib import Path


def setup_reddit_api():
    """配置 Reddit API 凭证"""
    config_path = Path("/Users/linweihao/project/MuskOrchestrator/config/reddit_config.json")

    # 用户提供的凭证信息
    credentials = {
        "client_id": "待获取",
        "client_secret": "待获取",
        "user_agent": "MuskOrchestrator/1.0 (by /u/linyoujia0886)",
        "username": "linyoujia0886",
        "password": "13580lwh",
        "login_method": "google",
        "google_email": "linyoujia0886@gmail.com"
    }

    print("=" * 60)
    print("Reddit API 配置向导")
    print("=" * 60)
    print()
    print("由于 Reddit 使用 Google 登录，需要手动步骤:")
    print()
    print("步骤 1: 访问 https://www.reddit.com/prefs/apps")
    print("步骤 2: 使用 Google 账号登录")
    print("   邮箱: linyoujia0886@gmail.com")
    print("   密码: 13580lwh")
    print()
    print("步骤 3: 创建应用")
    print("   - Name: MuskOrchestrator")
    print("   - Type: script")
    print("   - Description: Personal information aggregator for learning")
    print("   - Redirect URI: http://localhost:8080")
    print()
    print("步骤 4: 获取凭证并填写到 config/reddit_config.json")
    print()

    # 检查现有配置
    if config_path.exists():
        with open(config_path) as f:
            existing = json.load(f)
        if existing.get("client_id") and existing["client_id"] != "YOUR_CLIENT_ID":
            print("✓ 检测到已有配置:")
            print(f"  Client ID: {existing['client_id'][:10]}...")
            return True

    # 创建模板配置
    config = {
        "_comment": "Reddit API 配置 - 用于信息聚合系统",
        "client_id": "YOUR_CLIENT_ID",
        "client_secret": "YOUR_CLIENT_SECRET",
        "user_agent": "MuskOrchestrator/1.0 (by /u/linyoujia0886)",
        "username": "linyoujia0886",
        "password": "13580lwh",
        "login_method": "google",
        "google_email": "linyoujia0886@gmail.com",
        "rate_limit": {
            "requests_per_minute": 30,
            "burst_size": 10
        },
        "subreddits": {
            "creator": [
                "entrepreneur",
                "indiehackers",
                "marketing",
                "SaaS",
                "startups",
                "growthhacking"
            ],
            "engineer": [
                "programming",
                "webdev",
                "Python",
                "machinelearning"
            ],
            "analyst": [
                "algotrading",
                "quantfinance",
                "investing"
            ]
        },
        "fetch_settings": {
            "posts_per_subreddit": 10,
            "time_period": "week",
            "min_score": 10
        }
    }

    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"✓ 已创建配置模板: {config_path}")
    print()
    print("请手动完成上述步骤后，编辑该文件填入 client_id 和 client_secret")

    return False


def test_reddit_connection():
    """测试 Reddit API 连接"""
    import sys
    sys.path.insert(0, "/Users/linweihao/project/MuskOrchestrator/scripts")

    try:
        from sources.reddit_fetcher import RedditFetcher

        fetcher = RedditFetcher()

        # 尝试获取一个热门帖子
        posts = fetcher.fetch_subreddit("technology", limit=3)

        if posts:
            print(f"✓ Reddit API 连接成功! 获取到 {len(posts)} 条帖子")
            for p in posts[:2]:
                print(f"  - {p['title'][:50]}...")
            return True
        else:
            print("✗ 未获取到数据，请检查配置")
            return False

    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False


if __name__ == "__main__":
    print("Reddit API 配置工具")
    print("=" * 60)

    # 设置配置
    setup_reddit_api()

    print()
    print("=" * 60)
    print("配置完成后，运行以下命令测试:")
    print("  python scripts/setup_reddit_api.py --test")
