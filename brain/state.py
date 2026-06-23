"""
brain/state.py — 目标读取 / 知识间隔重现 / 当日去重
====================================================
· load_goals(): 读 goals.yaml
· resurface_note(): 从 wiki 里按"间隔重现"翻出一条旧笔记重新激活
· already_sent_today() / mark_sent_today(): 当日去重，防云端重复触发重复发信
"""
from __future__ import annotations

import json
import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

BRAIN = Path(__file__).resolve().parent
WIKI = BRAIN / "wiki"
STATE_FILE = BRAIN / "output" / ".send_state.json"

# 老板在 CST(GMT+8)。云端 runner 是 UTC，统一用北京时间算"今天"，
# 否则早 7 点(=前一天 23:00 UTC)发的邮件日期会差一天，去重也会跨 UTC 日错乱。
_CST = timezone(timedelta(hours=8))


def cst_today() -> date:
    return datetime.now(_CST).date()


def cst_today_str() -> str:
    return cst_today().isoformat()


def load_goals() -> dict:
    import yaml
    p = BRAIN / "goals.yaml"
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _all_notes() -> list[Path]:
    if not WIKI.exists():
        return []
    skip = {"index.md", "log.md"}
    return [p for p in WIKI.rglob("*.md")
            if p.name not in skip and "raw" not in p.parts]


def resurface_note(seed: str | None = None) -> dict | None:
    """间隔重现：用日期做种子，确定性地翻出一条旧笔记 + 它的标题/首段。"""
    notes = _all_notes()
    if not notes:
        return None
    rng = random.Random(seed or cst_today_str())
    note = rng.choice(notes)
    text = note.read_text(encoding="utf-8", errors="ignore").strip()
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    title = next((l.lstrip("# ").strip() for l in lines if l.startswith("#")),
                 note.stem)
    body = next((l for l in lines if not l.startswith("#") and len(l) > 20), "")
    return {
        "title": title,
        "excerpt": body[:200],
        "path": str(note.relative_to(BRAIN)),
    }


def already_sent_today() -> bool:
    if not STATE_FILE.exists():
        return False
    try:
        return json.loads(STATE_FILE.read_text()).get("last_sent") == cst_today_str()
    except Exception:  # noqa: BLE001
        return False


def mark_sent_today() -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps({"last_sent": cst_today_str()}))


if __name__ == "__main__":
    print("goals 主线:", load_goals().get("本月唯一主线"))
    print("resurface:", resurface_note())
