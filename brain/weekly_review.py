#!/usr/bin/env python3
"""
brain/weekly_review.py — 周日自动复盘 + 内容草稿（云端每周日跑）
================================================================
强化措施②③：
  ② 周日自动复盘：汇总本周 wiki/log + 进度日志 + 目标，生成回顾 + 下周唯一重点
  ③ 每周内容草稿：creator 把本周最值得分享的东西，写成一篇今天就能发的小红书/推文草稿
     —— 直击老板"记录多分享少"，把门槛降到复制粘贴。

跑法：
  python brain/weekly_review.py --dry-run
  python brain/weekly_review.py
"""
from __future__ import annotations

import argparse
import html
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

BRAIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BRAIN))

import email_send  # noqa: E402
import state  # noqa: E402
from llm import active_provider, chat  # noqa: E402

LOG = BRAIN / "wiki" / "log.md"
PROGRESS = BRAIN / "wiki" / "progress-log.md"
RAW = BRAIN / "wiki" / "raw"


def _recent_lines(path: Path, days: int = 7) -> list[str]:
    if not path.exists():
        return []
    cutoff = state.cst_today() - timedelta(days=days)
    out = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        for tok in line.split():
            try:
                d = datetime.strptime(tok[:10], "%Y-%m-%d").date()
                if d >= cutoff:
                    out.append(line.strip())
                    break
            except ValueError:
                continue
    return out


def _gather() -> dict:
    goals = state.load_goals()
    logs = _recent_lines(LOG)
    progress = _recent_lines(PROGRESS)
    raw_items = [p.name for p in RAW.glob("*.md")] if RAW.exists() else []
    return {"goals": goals, "logs": logs, "progress": progress, "raw": raw_items}


def _review(g: dict) -> str:
    主线 = g["goals"].get("本月唯一主线", "—")
    ctx = (
        f"本月唯一主线：{主线}\n\n"
        f"本周操作流水（{len(g['logs'])} 条）：\n" + "\n".join(g["logs"][:30]) + "\n\n"
        f"本周进度日志（你自己喂进来的，{len(g['progress'])} 条）：\n" + "\n".join(g["progress"][:30]) + "\n\n"
        f"本周新捕获材料：{', '.join(g['raw'][:20]) or '无'}"
    )
    prompt = (
        ctx + "\n\n你是冷酷高效的 AI CEO，给老板做本周复盘。输出三块：\n"
        "本周真相：2-3 句，本周到底推进了主线没有？别和稀泥，缺数据就直说『没有可证明的进展』。\n"
        "目标盘点：逐条点评老板的目标本周有无动作。\n"
        "下周唯一重点：只给 1 个，反分散。\n直接给。"
    )
    try:
        return chat("你是冷酷、第一性原理、结果导向的 AI CEO。", prompt,
                    temperature=0.7, max_tokens=700)
    except Exception as e:  # noqa: BLE001
        return f"（复盘合成失败：{type(e).__name__}）"


def _content_draft(g: dict) -> str:
    material = "\n".join(g["progress"][:20] + g["logs"][:20]) or "（本周无明确记录，就从『我在搭一个每天给我发成长简报的第二大脑』这件事切入）"
    prompt = (
        "你是『影响力引擎』内容教练。老板盲点是记录多、对外分享几乎为零。"
        "基于本周素材，写一篇**今天就能发**的小红书草稿（直接可复制粘贴）：\n"
        "标题：<emoji + 数字/悬念，吸引点击>\n"
        "正文：<150-300字，干货前置，分点，口语化，结尾一个互动问题>\n"
        "标签：<3-5 个 #标签>\n\n"
        f"本周素材：\n{material}"
    )
    try:
        return chat("你有网感、懂小红书算法、反对完美主义、逼人先发出去。", prompt,
                    temperature=0.85, max_tokens=800)
    except Exception as e:  # noqa: BLE001
        return f"（内容草稿合成失败：{type(e).__name__}）"


def _esc(s: str) -> str:
    return html.escape(s or "")


def _block_html(title, color, text):
    rows = "".join(f'<div style="margin:5px 0;color:#1a1a1a;">{_esc(l)}</div>'
                   for l in text.splitlines() if l.strip())
    return (f'<div style="font-size:13px;font-weight:700;color:{color};letter-spacing:1px;margin:20px 0 6px;">{title}</div>'
            f'<div style="background:#fff;border:1px solid #ececec;border-radius:12px;padding:16px 18px;">{rows}</div>')


def build():
    g = _gather()
    review = _review(g)
    draft = _content_draft(g)
    today = state.cst_today_str()
    text = (
        f"MuskOrchestrator · 周日复盘 — {today}\n{'='*60}\n"
        f"本月唯一主线：{g['goals'].get('本月唯一主线','—')}\n{'='*60}\n\n"
        f"【本周复盘】\n{review}\n\n【本周内容草稿（复制即可发）】\n{draft}\n\n"
        f"{'='*60}\n下周把唯一重点做到底。少即是多。🚀"
    )
    htmlbody = f"""<!DOCTYPE html><html><body style="margin:0;background:#f5f5f3;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;">
<div style="max-width:640px;margin:0 auto;padding:20px;">
  <div style="background:#1a1a1a;color:#fff;border-radius:14px;padding:20px 22px;">
    <div style="font-size:12px;color:#bbb;letter-spacing:2px;">MUSKORCHESTRATOR · 周日复盘</div>
    <div style="font-size:13px;color:#999;margin-top:2px;">{today} · 引擎 {_esc(active_provider())}</div>
    <div style="margin-top:12px;font-size:12px;color:#e74c3c;">本月唯一主线</div>
    <div style="font-size:17px;font-weight:700;">{_esc(g['goals'].get('本月唯一主线','—'))}</div>
  </div>
  {_block_html('🪞 本周复盘', '#c0392b', review)}
  {_block_html('✍️ 本周内容草稿 · 复制即可发', '#2d6a2d', draft)}
  <div style="text-align:center;color:#888;font-size:12px;margin-top:18px;">下周把唯一重点做到底。少即是多。🚀</div>
</div></body></html>"""
    return text, htmlbody


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    text, htmlbody = build()
    if args.dry_run or not email_send.configured():
        print(text)
        return
    try:
        email_send.send(f"[第二大脑] 周日复盘 + 内容草稿 · {state.cst_today_str()}", text, htmlbody)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"- {state.cst_today_str()} · 周日复盘已发送 · 引擎 {active_provider()}\n")
        print("✓ 周日复盘已发送")
    except Exception as e:  # noqa: BLE001
        print(f"发送失败：{type(e).__name__}: {e}\n\n{text}")
        sys.exit(1)


if __name__ == "__main__":
    main()
