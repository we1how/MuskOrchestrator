"""
brain/sources.py — 升级版取料层（高信噪比 RSS 源池）
======================================================
不再局限旧的 10 个源。每个 agent 配一组高质量 RSS（海外 GitHub runner 可达性好），
中文源经 RSSHub 作 best-effort。取料失败静默跳过，国际源作可靠核心。

返回：每个 agent -> [{title, summary, link, source}]，已截断 summary、去 HTML。
"""
from __future__ import annotations

import html
import re
import socket
from concurrent.futures import ThreadPoolExecutor

socket.setdefaulttimeout(15)

# 每个 agent 的高信噪比源池（name -> rss url）
FEEDS: dict[str, dict[str, str]] = {
    "analyst": {
        "Alpha Architect": "https://alphaarchitect.com/feed/",
        "A Wealth of Common Sense": "https://awealthofcommonsense.com/feed/",
        "Marginal Revolution": "https://marginalrevolution.com/feed",
        "Klement on Investing": "https://klementoninvesting.substack.com/feed",
        "Arxiv q-fin": "https://rss.arxiv.org/rss/q-fin.PM",
    },
    # 方向雷达：机会/热点富集的源（赚钱的、有趣的、能借 AI 快速做的）
    "radar": {
        "Hacker News Front": "https://hnrss.org/frontpage?points=150",
        "Hacker News Show": "https://hnrss.org/show",
        "Product Hunt": "https://www.producthunt.com/feed",
        "Indie Hackers": "https://www.indiehackers.com/feed.xml",
        "Trends.vc": "https://trends.vc/feed/",
        "Latent Space": "https://www.latent.space/feed",
        "Simon Willison": "https://simonwillison.net/atom/everything/",
    },
    "mentor": {
        "Farnam Street": "https://fs.blog/feed/",
        "Collab Fund (Housel)": "https://collabfund.com/blog/feed/",
        "Paul Graham Essays": "http://www.aaronsw.com/2002/feeds/pgessays.rss",
        "Ness Labs": "https://nesslabs.com/feed",
        "Marginal Revolution": "https://marginalrevolution.com/feed",
    },
    "creator": {
        "Lenny's Newsletter": "https://www.lennysnewsletter.com/feed",
        "Indie Hackers": "https://www.indiehackers.com/feed.xml",
        "Trends.vc": "https://trends.vc/feed/",
        "Every": "https://every.to/feed.xml",
        "Hacker News Show": "https://hnrss.org/show",
    },
}

_TAG = re.compile(r"<[^>]+>")


def _clean(text: str, limit: int = 320) -> str:
    text = html.unescape(_TAG.sub("", text or "")).strip()
    text = re.sub(r"\s+", " ", text)
    return text[:limit]


def _fetch_feed(name: str, url: str, per_feed: int) -> list[dict]:
    try:
        import feedparser
        d = feedparser.parse(url)
        items = []
        for e in d.entries[:per_feed]:
            title = _clean(getattr(e, "title", ""), 200)
            if not title:
                continue
            summary = _clean(getattr(e, "summary", "") or getattr(e, "description", ""))
            items.append({
                "title": title,
                "summary": summary,
                "link": getattr(e, "link", ""),
                "source": name,
            })
        return items
    except Exception:  # noqa: BLE001
        return []


def gather(agent: str, per_feed: int = 3, max_items: int = 12) -> list[dict]:
    """并发抓该 agent 的所有源，合并、去重、截断。"""
    feeds = FEEDS.get(agent, {})
    out: list[dict] = []
    with ThreadPoolExecutor(max_workers=min(8, len(feeds) or 1)) as ex:
        for items in ex.map(lambda kv: _fetch_feed(kv[0], kv[1], per_feed),
                            feeds.items()):
            out.extend(items)
    seen, dedup = set(), []
    for it in out:
        k = it["title"].lower()[:60]
        if k in seen:
            continue
        seen.add(k)
        dedup.append(it)
    return dedup[:max_items]


def as_brief(items: list[dict]) -> str:
    """把原料拼成喂给 LLM 的紧凑文本。"""
    if not items:
        return "（今日各源未取到内容，请基于你的领域知识给一条高价值通用建议。）"
    lines = []
    for i, it in enumerate(items, 1):
        lines.append(f"{i}. [{it['source']}] {it['title']}")
        if it["summary"]:
            lines.append(f"   {it['summary']}")
    return "\n".join(lines)


if __name__ == "__main__":
    for ag in FEEDS:
        items = gather(ag)
        got = sorted({it["source"] for it in items})
        print(f"\n=== {ag}: {len(items)} 条，来源 {got} ===")
        for it in items[:3]:
            print(f"  · [{it['source']}] {it['title']}")
