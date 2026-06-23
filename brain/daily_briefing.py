#!/usr/bin/env python3
"""
brain/daily_briefing.py — 每日三段式成长简报（主编排，对标 stock_platform/daily_run.py）
========================================================================================
先收『反向输入』（inbox 邮件捕获）→ 再合成三段式简报 → 发 HTML 邮件。
① 作战简报：本月唯一主线（反分散硬约束·首行）+ 目标进度 + 今日 Top3 + 盲点提醒
② 四教练洞察：各 1 条可执行洞察 + 原文链接
③ 知识激活：间隔重现旧笔记 + 你最近喂进来的材料 + 1 个待解问题

跑法：
  python brain/daily_briefing.py --dry-run   # 打印纯文本，不发信
  python brain/daily_briefing.py             # 收输入 + 合成 + 发 HTML 邮件
  python brain/daily_briefing.py --force     # 忽略当日去重
"""
from __future__ import annotations

import argparse
import html
import sys
from datetime import date
from pathlib import Path

BRAIN = Path(__file__).resolve().parent
sys.path.insert(0, str(BRAIN))

import agents  # noqa: E402
import email_send  # noqa: E402
import inbox  # noqa: E402
import state  # noqa: E402
from llm import active_provider, chat  # noqa: E402

BAR = "=" * 60
LOG = BRAIN / "wiki" / "log.md"

C_INK = "#1a1a1a"
C_RED = "#c0392b"
C_MUTE = "#888"
C_BG = "#f5f5f3"
C_CARD = "#ffffff"
C_LINE = "#ececec"


def _append_log(subject: str) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"- {date.today().isoformat()} · 已发送『{subject}』 · 引擎 {active_provider()}\n")


# ── 内容合成（LLM） ─────────────────────────────────────────────

def _ceo_briefing(goals: dict, goals_block: str) -> str:
    主线 = goals.get("本月唯一主线", "（未设置）")
    prompt = (
        f"老板本月唯一主线：{主线}\n北极星：{goals.get('北极星','')}\n\n目标清单：\n{goals_block}\n\n"
        "你是冷酷高效的 AI CEO。输出两块：\n"
        "今日Top3：3 个今天最该做、且都服务于『本月唯一主线』的具体动作（每个一行，动词开头）。\n"
        "盲点提醒：1 句，针对老板『精力分散/记录多分享少』，今天最该警惕什么。\n"
        "直接给，不要客套。"
    )
    try:
        return chat("你是冷酷、第一性原理、结果导向的 AI CEO。", prompt,
                    temperature=0.7, max_tokens=500)
    except Exception as e:  # noqa: BLE001
        return f"（CEO 简报合成失败：{type(e).__name__}）"


def _knowledge_q(note: dict) -> str:
    try:
        return chat("你是逼人多想一层的导师。",
                    f"针对这条旧笔记《{note['title']}》：{note['excerpt']}\n"
                    "提 1 个尖锐的、能让老板把它用起来的问题。只输出问题本身。",
                    temperature=0.8, max_tokens=120).strip()
    except Exception:  # noqa: BLE001
        return ""


# ── 纯文本版 ─────────────────────────────────────────────────

def _progress_label(p) -> str:
    """进度可以是数字(0-100)、自由文本('10本'/'126斤')、或 null。一律安全转成展示字符串。"""
    if p is None or p == "":
        return "—"
    if isinstance(p, bool):
        return str(p)
    if isinstance(p, (int, float)):
        return f"{p:g}"
    return str(p)


def _progress_pct(p):
    """仅当进度是 0-100 的纯数字时返回百分比，否则 None（不画进度条）。"""
    if isinstance(p, (int, float)) and not isinstance(p, bool) and 0 <= p <= 100:
        return int(p)
    return None


def _goals_block(goals: dict) -> str:
    rows = []
    for g in goals.get("目标", []):
        label = _progress_label(g.get("进度"))
        note = f"  · {g['备注']}" if g.get("备注") else ""
        rows.append(f"  ▸ {g['名称']}：{label}{note}")
    return "\n".join(rows) if rows else "  （goals.yaml 无目标）"


def render_text(data: dict) -> str:
    g = data["goals"]
    parts = [
        f"MuskOrchestrator · 每日成长简报 — {data['today']}", BAR,
        f"本月唯一主线：{g.get('本月唯一主线','—')}",
        "→ 今天，你为这条主线做了什么？", BAR, "",
    ]
    if data["captured"]:
        parts.append("📥 已收到你的输入：")
        for c in data["captured"]:
            parts.append(f"  · [{c['kind']}] {c['subject']} → {c['dest']}")
        parts.append("")
    parts += ["① 作战简报", "-" * 60,
              f"目标进度：\n{data['goals_block']}\n", data["ceo"], ""]
    parts += ["② 四教练洞察", "-" * 60]
    for r in data["coaches"]:
        src = "、".join(r["sources"]) if r["sources"] else "无源"
        parts.append(f"\n{r['emoji']} {r['name']}〔源：{src}〕\n{r['text']}")
        if r["link"]:
            parts.append(f"   阅读原文：{r['link']}")
    parts += ["", "③ 知识激活", "-" * 60]
    n = data["note"]
    if n:
        parts.append(f"📂 重新激活：{n['title']}")
        if n["excerpt"]:
            parts.append(f"   {n['excerpt']}")
        parts.append(f"   （{n['path']}）")
        if data["kq"]:
            parts.append(f"❓ 待解：{data['kq']}")
    else:
        parts.append("（wiki 暂无笔记。）")
    parts += ["", BAR,
              "把进度/书摘/想法喂回来：给本邮箱发邮件，主题加标签",
              "  [进度] 今天做了什么   [读书] 书名   [知识] 笔记   [想法] 灵感",
              "下次简报就会自动收进第二大脑。", BAR,
              "第一性原理 · 永不懈怠 · 改变世界 🚀"]
    return "\n".join(parts)


# ── HTML 版 ─────────────────────────────────────────────────

def _esc(s: str) -> str:
    return html.escape(s or "")


def _coach_card(r: dict) -> str:
    chips = "".join(
        f'<span style="display:inline-block;background:{C_BG};color:{C_MUTE};'
        f'font-size:11px;padding:2px 8px;border-radius:10px;margin:0 4px 4px 0;">{_esc(s)}</span>'
        for s in r["sources"])
    rows = ""
    for line in r["text"].splitlines():
        line = line.strip()
        if not line:
            continue
        if "：" in line and line.split("：", 1)[0] in ("发现", "为什么重要", "今天就做"):
            label, val = line.split("：", 1)
            color = C_RED if label == "今天就做" else C_INK
            weight = "600" if label == "今天就做" else "400"
            rows += (f'<div style="margin:6px 0;"><span style="color:{C_MUTE};font-size:12px;">'
                     f'{_esc(label)}</span><br><span style="color:{color};font-weight:{weight};">'
                     f'{_esc(val)}</span></div>')
        else:
            rows += f'<div style="margin:6px 0;color:{C_INK};">{_esc(line)}</div>'
    link = ""
    if r["link"]:
        link = (f'<a href="{_esc(r["link"])}" style="display:inline-block;margin-top:8px;'
                f'color:{C_RED};text-decoration:none;font-size:13px;font-weight:600;">'
                f'阅读原文（{_esc(r["source_name"] or "source")}）→</a>')
    return (
        f'<div style="background:{C_CARD};border:1px solid {C_LINE};border-radius:12px;'
        f'padding:16px 18px;margin:12px 0;">'
        f'<div style="font-size:16px;font-weight:700;color:{C_INK};margin-bottom:4px;">'
        f'{r["emoji"]} {_esc(r["name"])}</div>'
        f'<div style="margin-bottom:8px;">{chips}</div>'
        f'{rows}{link}</div>'
    )


def _bar_row(g: dict) -> str:
    p = g.get("进度")
    label = _progress_label(p)
    pct = _progress_pct(p)
    note = f' <span style="color:{C_MUTE};font-size:12px;">{_esc(g.get("备注",""))}</span>' if g.get("备注") else ""
    head = (f'<div style="font-size:13px;color:{C_INK};margin-bottom:3px;">{_esc(g["名称"])}'
            f' <b style="color:{C_RED};">{_esc(label)}</b>{note}</div>')
    bar = ""
    if pct is not None:  # 只有纯 0-100 数字才画进度条，自由文本只显示状态
        bar = (f'<div style="background:{C_BG};border-radius:6px;height:6px;overflow:hidden;">'
               f'<div style="background:{C_RED};height:6px;width:{pct}%;"></div></div>')
    return f'<div style="margin:8px 0;">{head}{bar}</div>'


def _section_title(t: str) -> str:
    return (f'<div style="font-size:13px;font-weight:700;color:{C_RED};letter-spacing:1px;'
            f'margin:22px 0 6px;">{t}</div>')


def render_html(data: dict) -> str:
    g = data["goals"]
    ceo_html = "".join(f'<div style="margin:4px 0;color:{C_INK};">{_esc(l)}</div>'
                       for l in data["ceo"].splitlines() if l.strip())
    bars = "".join(_bar_row(x) for x in g.get("目标", []))
    cards = "".join(_coach_card(r) for r in data["coaches"])

    captured = ""
    if data["captured"]:
        items = "".join(f'<li>[{_esc(c["kind"])}] {_esc(c["subject"])}</li>' for c in data["captured"])
        captured = (f'<div style="background:#eef7ee;border-radius:10px;padding:10px 14px;'
                    f'margin:10px 0;font-size:13px;color:#2d6a2d;">📥 已收到你的输入：<ul style="margin:6px 0;">{items}</ul></div>')

    n = data["note"]
    know = "<div style='color:#888;'>（wiki 暂无笔记）</div>"
    if n:
        q = (f'<div style="margin-top:8px;color:{C_RED};font-weight:600;">❓ {_esc(data["kq"])}</div>'
             if data["kq"] else "")
        know = (
            f'<div style="background:{C_CARD};border:1px solid {C_LINE};border-radius:12px;padding:16px 18px;">'
            f'<div style="font-weight:700;color:{C_INK};">📂 {_esc(n["title"])}</div>'
            f'<div style="color:{C_INK};margin:6px 0;">{_esc(n["excerpt"])}</div>'
            f'<div style="color:{C_MUTE};font-size:12px;">{_esc(n["path"])}</div>{q}</div>'
        )

    return f"""<!DOCTYPE html><html><body style="margin:0;background:{C_BG};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'PingFang SC','Microsoft YaHei',sans-serif;">
<div style="max-width:640px;margin:0 auto;padding:20px;">
  <div style="background:{C_INK};color:#fff;border-radius:14px;padding:20px 22px;">
    <div style="font-size:12px;color:#bbb;letter-spacing:2px;">MUSKORCHESTRATOR · 每日成长简报</div>
    <div style="font-size:13px;color:#999;margin-top:2px;">{data['today']} · 引擎 {_esc(active_provider())}</div>
    <div style="margin-top:14px;font-size:12px;color:#e74c3c;letter-spacing:1px;">本月唯一主线</div>
    <div style="font-size:18px;font-weight:700;margin-top:2px;">{_esc(g.get('本月唯一主线','—'))}</div>
    <div style="margin-top:8px;font-size:14px;color:#f1c40f;">→ 今天，你为这条主线做了什么？</div>
  </div>
  {captured}
  {_section_title('① 作战简报')}
  <div style="background:{C_CARD};border:1px solid {C_LINE};border-radius:12px;padding:16px 18px;">
    <div style="font-size:12px;color:{C_MUTE};margin-bottom:6px;">目标进度</div>
    {bars}
    <div style="border-top:1px solid {C_LINE};margin:12px 0;"></div>
    {ceo_html}
  </div>
  {_section_title('② 四教练洞察')}
  {cards}
  {_section_title('③ 知识激活')}
  {know}
  <div style="background:{C_INK};color:#ddd;border-radius:12px;padding:16px 18px;margin-top:22px;font-size:13px;">
    <b style="color:#fff;">把进度 / 书 / 想法喂回第二大脑</b><br>
    给本邮箱发邮件，主题加标签即可，下次简报自动收进来：<br>
    <span style="color:#f1c40f;">[进度]</span> 今天做了什么
    <span style="color:#f1c40f;">[读书]</span> 书名
    <span style="color:#f1c40f;">[知识]</span> 笔记
    <span style="color:#f1c40f;">[想法]</span> 灵感
  </div>
  <div style="text-align:center;color:{C_MUTE};font-size:12px;margin-top:16px;">第一性原理 · 永不懈怠 · 改变世界 🚀</div>
</div></body></html>"""


# ── 编排 ─────────────────────────────────────────────────────

def build(poll_inbox: bool = True) -> dict:
    goals = state.load_goals()
    captured = inbox.poll() if poll_inbox else []
    coaches = agents.run_all()
    note = state.resurface_note()
    gblock = _goals_block(goals)
    return {
        "today": date.today().isoformat(),
        "goals": goals,
        "goals_block": gblock,
        "captured": captured,
        "ceo": _ceo_briefing(goals, gblock),
        "coaches": coaches,
        "note": note,
        "kq": _knowledge_q(note) if note else "",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只打印纯文本，不发信、不收件")
    ap.add_argument("--force", action="store_true", help="忽略当日去重")
    args = ap.parse_args()

    if not args.dry_run and not args.force and state.already_sent_today():
        print("今日已发过，跳过（--force 可强发）。")
        return

    data = build(poll_inbox=not args.dry_run)
    text = render_text(data)
    subject = f"[第二大脑] 每日成长简报 · {data['today']}"

    if args.dry_run:
        print(text)
        return

    if not email_send.configured():
        print("未配置 SMTP，打印纯文本：\n\n" + text)
        return

    try:
        email_send.send(subject, text, render_html(data))
        state.mark_sent_today()
        _append_log(subject)
        print(f"✓ 已发送：{subject}")
    except Exception as e:  # noqa: BLE001
        print(f"发送失败：{type(e).__name__}: {e}\n\n{text}")
        sys.exit(1)


if __name__ == "__main__":
    main()
