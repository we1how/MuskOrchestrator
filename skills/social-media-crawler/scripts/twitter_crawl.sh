#!/bin/bash
# twitter_crawl.sh - 使用 MediaCrawler 的环境运行 Twitter 爬取

cd /Users/linweihao/project/MuskOrchestrator/tools/MediaCrawler

# 使用 uv 运行 Python 脚本
uv run python /Users/linweihao/project/MuskOrchestrator/skills/social-media-crawler/scripts/twitter_crawler.py
