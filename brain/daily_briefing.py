#!/usr/bin/env python3
"""
brain/daily_briefing.py — 每日三段式成长简报（主编排，对标 stock_platform/daily_run.py）
========================================================================================
① 作战简报：本月唯一主线 + 目标进度 + 今日 Top3 + 1 条盲点提醒
② Agent 洞察：analyst/engineer/mentor/creator 各 1 条可执行洞察
③ 知识激活：从 wiki 间隔重现翻出 1 条旧笔记 + 1 个待解问题

跑法：
  python brain/daily_briefing.py --dry-run   # 只打印，不发信
  python brain/daily_briefing.py             # 合成并发邮件
  python brain/daily_briefing.py --force     # 忽略当日去重
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

BRAIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BRAIN))

import agents  # noqa: E402
import email_send  # noqa: E402
import state  # noqa: E402
from llm import active_provider, chat  # noqa: E402

BAR = "=" * 60
LOG = BRAIN / "wiki" / "log.md"


def _append_log(subject: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"- {date.today().isoformat()} · 已发送『{subject}』 · 引擎 {active_provider()}\n"
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line)


def _section_briefing(goals: dict) -> str:
    主线 = goals.get("本月唯一主线", "（未设置，去 brain/goals.yaml 填）")
    北极星 = goals.get("北极星", "")
    rows = []
    for g in goals.get("目标", []):
        p = g.get("进度")
        bar = "—" if p is None else f"{int(p)}%"
        note = f"  · {g['备注']}" if g.get("备注") else ""
        rows.append(f"  [{bar:>4}] {g['名称']}{note}")
    goals_block = "\n".join(rows) if rows else "  （goals.yaml 无目标）"

    # 让 LLM 基于主线 + 目标，给今日 Top3 + 1 条盲点提醒
    prompt = (
        f"老板本月唯一主线：{主线}\n北极星：{北极星}\n\n目标清单：\n{goals_block}\n\n"
        "你是冷酷高效的 AI CEO。基于以上，输出：\n"
        "今日Top3：列 3 个今天最该做、且都服务于『本月唯一主线』的具体动作（每个一行，动词开头）。\n"
        "盲点提醒：1 句，针对老板『精力分散/记录多分享少』的盲点，今天最该警惕什么。\n"
        "直接给，不要客套。"
    )
    try:
        ceo = chat("你是冷酷、第一性原理、结果导向的 AI CEO。", prompt,
                   temperature=0.7, max_tokens=500)
    except Exception as e:  # noqa: BLE001
        ceo = f"（CEO 简报合成失败：{type(e).__name__}）"

    return (
        "① 作战简报\n" + "-" * 60 + "\n"
        f"本月唯一主线：{主线}\n\n"
        f"目标进度：\n{goals_block}\n\n"
        f"{ceo}\n"
    )


def _section_agents(coach_results: list[dict]) -> str:
    out = ["② 四教练洞察", "-" * 60]
    for r in coach_results:
        src = "、".join(r["sources"]) if r["sources"] else "无源(用通识)"
        out.append(f"\n{r['emoji']} {r['name']}  〔源：{src}〕\n{r['text']}")
    return "\n".join(out) + "\n"


def _section_knowledge() -> str:
    note = state.resurface_note()
    out = ["③ 知识激活", "-" * 60]
    if note:
        out.append(f"📂 重新激活：{note['title']}")
        if note["excerpt"]:
            out.append(f"   {note['excerpt']}")
        out.append(f"   （{note['path']}）")
        try:
            q = chat("你是逼人多想一层的导师。",
                     f"针对这条旧笔记《{note['title']}》：{note['excerpt']}\n"
                     "提 1 个尖锐的、能让老板把它用起来的问题。只输出问题本身。",
                     temperature=0.8, max_tokens=120)
            out.append(f"❓ 待解：{q.strip()}")
        except Exception:  # noqa: BLE001
            pass
    else:
        out.append("（wiki 暂无笔记。先把 knowledge/ 沉淀进 brain/wiki/，知识才能被复利。）")
    return "\n".join(out) + "\n"


def build(dry: bool) -> tuple[str, str]:
    goals = state.load_goals()
    coaches = agents.run_all()
    today = date.today().isoformat()

    body = (
        f"MuskOrchestrator · 每日成长简报 — {today}\n{BAR}\n"
        f"引擎：{active_provider()}    主线：{goals.get('本月唯一主线','—')}\n{BAR}\n\n"
        + _section_briefing(goals) + "\n"
        + _section_agents(coaches) + "\n"
        + _section_knowledge() + "\n"
        + BAR + "\n第一性原理 · 永不懈怠 · 改变世界 🚀\n"
    )
    subject = f"[第二大脑] 每日成长简报 · {today}"
    return subject, body


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只打印不发信")
    ap.add_argument("--force", action="store_true", help="忽略当日去重")
    args = ap.parse_args()

    if not args.dry_run and not args.force and state.already_sent_today():
        print("今日已发过，跳过（--force 可强发）。")
        return

    subject, body = build(args.dry_run)

    if args.dry_run:
        print(body)
        return

    if not email_send.configured():
        print("未配置 SMTP，打印到终端：\n")
        print(body)
        return

    try:
        email_send.send(subject, body)
        state.mark_sent_today()
        _append_log(subject)
        print(f"✓ 已发送：{subject}")
    except Exception as e:  # noqa: BLE001
        print(f"发送失败：{type(e).__name__}: {e}")
        print("\n--- 简报全文 ---\n" + body)
        sys.exit(1)


if __name__ == "__main__":
    main()
