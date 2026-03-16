#!/usr/bin/env python3
"""
Reddit Fetcher
Fetches posts from marketing and growth related subreddits.
Targets: creator (marketing discussions, growth strategies)
"""

import re
import requests
from datetime import datetime
from typing import List, Optional

from .base import BaseFetcher, ContentItem


class RedditFetcher(BaseFetcher):
    """Fetch posts from Reddit."""

    # Subreddits to monitor
    SUBREDDITS = {
        'marketing': ['marketing', 'digital_marketing', 'content_marketing', 'socialmedia'],
        'growth': ['growthhacking', 'startups', 'SaaS', 'Entrepreneur'],
        'product': ['ProductManagement', 'userexperience', 'design_critiques'],
    }

    # Keywords for categorization
    MARKETING_KEYWORDS = [
        'marketing', 'seo', 'content', 'social media', 'ads', 'advertising',
        'conversion', 'funnel', 'lead generation', 'email marketing'
    ]

    GROWTH_KEYWORDS = [
        'growth', 'acquisition', 'retention', 'viral', 'referral', 'onboarding',
        'churn', 'mrr', 'arr', 'revenue'
    ]

    def __init__(self, cache_dir=None, cache_ttl_hours=3):
        super().__init__(cache_dir, cache_ttl_hours)
        self.api_base = "https://www.reddit.com"

    def fetch(self, days: int = 30, limit: int = 20) -> List[ContentItem]:
        """Fetch recent posts from Reddit."""
        # Try cache first
        cached = self.load_from_cache()
        if cached:
            return self.filter_by_date(cached, days)[:limit]

        items = []

        # Fetch from different subreddits
        all_subreddits = []
        for category, subs in self.SUBREDDITS.items():
            all_subreddits.extend(subs)

        for subreddit in all_subreddits[:6]:  # Limit to avoid rate limits
            try:
                sub_items = self._fetch_subreddit(subreddit, limit=limit//3 + 2)
                items.extend(sub_items)
            except Exception as e:
                print(f"Warning: Failed to fetch r/{subreddit}: {e}")

        # Deduplicate and save
        items = self.deduplicate(items)
        self.save_to_cache(items)

        return self.filter_by_date(items, days)[:limit]

    def _fetch_subreddit(self, subreddit: str, limit: int = 10) -> List[ContentItem]:
        """Fetch hot posts from a subreddit."""
        items = []

        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; InfoAggregator/1.0; Contact: bot@example.com)'
        }

        # Try to fetch from both 'hot' and 'top' (week)
        endpoints = ['hot', 'top']

        for endpoint in endpoints:
            try:
                url = f"{self.api_base}/r/{subreddit}/{endpoint}.json"
                params = {'limit': limit}
                if endpoint == 'top':
                    params['t'] = 'week'

                response = requests.get(url, headers=headers, params=params, timeout=30)

                if response.status_code == 429:
                    print(f"Rate limited on r/{subreddit}, skipping...")
                    break

                response.raise_for_status()
                data = response.json()

                for post in data.get('data', {}).get('children', []):
                    try:
                        item = self._parse_post(post.get('data', {}), subreddit)
                        if item:
                            items.append(item)
                    except Exception as e:
                        print(f"Warning: Failed to parse Reddit post: {e}")
                        continue

            except Exception as e:
                print(f"Error fetching r/{subreddit}/{endpoint}: {e}")

        return items

    def _parse_post(self, post_data: dict, subreddit: str) -> Optional[ContentItem]:
        """Parse a Reddit post into ContentItem."""
        title = post_data.get('title', '')
        url = post_data.get('url', '')
        permalink = f"https://reddit.com{post_data.get('permalink', '')}"

        # Skip stickied posts and common low-value content
        if post_data.get('stickied') or post_data.get('is_self') is False:
            # External links might still be valuable
            if not self._is_valuable_external_link(url):
                return None

        # Use permalink for discussion, external URL for content
        final_url = url if not post_data.get('is_self', True) else permalink

        # Skip if score is too low
        score = post_data.get('score', 0)
        if score < 10:
            return None

        # Extract selftext if available
        description = post_data.get('selftext', '')[:500]
        if len(description) > 500:
            description = description[:500] + "..."

        # Get author
        author = post_data.get('author', '')

        # Parse timestamp
        created_utc = post_data.get('created_utc', 0)
        published_date = datetime.fromtimestamp(created_utc) if created_utc else datetime.now()

        # Get engagement metrics
        num_comments = post_data.get('num_comments', 0)
        upvote_ratio = post_data.get('upvote_ratio', 0)

        # Determine agent target
        agent_target = self._determine_agent_target(title, description, subreddit)

        # Extract tags
        tags = ['reddit', subreddit.lower()]
        flair = post_data.get('link_flair_text', '')
        if flair:
            tags.append(flair.lower())

        return ContentItem(
            title=title,
            url=final_url,
            source='reddit',
            source_type='discussion',
            agent_target=agent_target,
            description=description,
            author=author,
            published_date=published_date,
            tags=tags,
            metrics={
                'score': score,
                'comments': num_comments,
                'upvote_ratio': upvote_ratio,
                'subreddit': subreddit,
            }
        )

    def _is_valuable_external_link(self, url: str) -> bool:
        """Check if an external link is valuable enough to include."""
        # Skip common low-value domains
        skip_domains = [
            'imgur.com', 'i.redd.it', 'v.redd.it', 'youtube.com', 'youtu.be',
            'twitter.com', 'x.com', 'tiktok.com'
        ]

        return not any(domain in url.lower() for domain in skip_domains)

    def _determine_agent_target(self, title: str, description: str, subreddit: str) -> str:
        """Determine which agent this content is most relevant for."""
        text = f"{title} {description} {subreddit}".lower()

        # Check for marketing content
        if any(kw in text for kw in self.MARKETING_KEYWORDS):
            return 'creator'

        # Check for growth content
        if any(kw in text for kw in self.GROWTH_KEYWORDS):
            return 'creator'

        # Check for product content
        if subreddit.lower() in ['productmanagement', 'userexperience']:
            return 'planner'

        # Default to creator
        return 'creator'
