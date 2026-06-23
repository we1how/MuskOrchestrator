"""
brain/inbox.py — 反向输入通道（邮件捕获）
==========================================
让第二大脑变成双向：你给自己的 QQ 邮箱发一封邮件，主题带标签，系统下次跑时自动收进来。

支持的主题标签（出现在主题任意位置即可，中英文皆可）：
  [进度] / [progress]  → 追加到 brain/wiki/progress-log.md（更新目标进度、今天做了什么）
  [读书] / [book]      → 存进 brain/wiki/raw/，等 /brain-ingest 整理成书摘
  [知识] / [note]      → 存进 brain/wiki/raw/
  [想法] / [idea]      → 存进 brain/wiki/raw/

用同一套 QQ 授权码走 IMAP（imap.qq.com:993 SSL）。读完标记已读，不重复处理。
环境变量：SMTP_USER / SMTP_PASSWORD（与发信复用）。
"""
from __future__ import annotations

import email
import imaplib
import json
import os
import re
import sys
from datetime import date, datetime
from email.header import decode_header
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import llm  # noqa: E402  复用 .env 加载

BRAIN = Path(__file__).resolve().parent
RAW = BRAIN / "wiki" / "raw"
PROGRESS = BRAIN / "wiki" / "progress-log.md"

TAGS = {
    "进度": "progress", "progress": "progress",
    "读书": "book", "book": "book",
    "知识": "note", "note": "note",
    "想法": "idea", "idea": "idea",
}
# 同时匹配半角 [] 与全角 ［］（手机中文输入法常打出全角括号）
_TAG_RE = re.compile(r"[\[［]\s*(" + "|".join(map(re.escape, TAGS)) + r")\s*[\]］]", re.I)


def _decode(s) -> str:
    if not s:
        return ""
    parts = decode_header(s)
    out = ""
    for txt, enc in parts:
        if isinstance(txt, bytes):
            out += txt.decode(enc or "utf-8", "ignore")
        else:
            out += txt
    return out


# 回复/转发时客户端塞进来的引用块、签名的起始标记 —— 从第一处截断，只留你自己写的正文
_QUOTE_MARKERS = (
    "------------------ 原始邮件", "原始邮件", "-----Original Message-----",
    "发自我的iPhone", "发自我的", "发自", "在 20", "On 20", "> ",
)


def _strip_quote(text: str) -> str:
    lines = text.splitlines()
    kept = []
    for line in lines:
        s = line.strip()
        if s.startswith(">") or any(mk in s for mk in _QUOTE_MARKERS):
            break  # 命中引用/签名标记，后面全是原邮件，停
        kept.append(line)
    return "\n".join(kept).strip()


def _body_text(msg) -> str:
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True) or b""
                charset = part.get_content_charset() or "utf-8"
                body = payload.decode(charset, "ignore")
                break
    else:
        payload = msg.get_payload(decode=True) or b""
        body = payload.decode(msg.get_content_charset() or "utf-8", "ignore")
    return _strip_quote(body)


def _slug(s: str) -> str:
    s = re.sub(r"\[[^\]]*\]", "", s)  # 去标签
    s = re.sub(r"(re|fwd|回复|转发)\s*[:：]", "", s, flags=re.I)
    s = re.sub(r"[^\w一-鿿]+", "-", s).strip("-")
    return s[:40] or "untitled"


def _save_raw(kind: str, subject: str, body: str) -> Path:
    RAW.mkdir(parents=True, exist_ok=True)
    fname = f"{date.today().isoformat()}-{kind}-{_slug(subject)}.md"
    p = RAW / fname
    p.write_text(f"# {subject}\n\n_类型：{kind} · 捕获于 {datetime.now():%Y-%m-%d %H:%M}_\n\n{body}\n",
                 encoding="utf-8")
    return p


GOALS = BRAIN / "goals.yaml"


def update_goals_from_text(body: str) -> list[str]:
    """用 LLM 把一条自然语言进度，映射到 goals.yaml 的目标并更新『进度』字段。
    保留注释/结构（按行定位替换，不走 yaml dump）。返回已更新目标的描述列表。"""
    import json

    import yaml
    from llm import chat

    if not GOALS.exists():
        return []
    raw = GOALS.read_text(encoding="utf-8")
    try:
        items = (yaml.safe_load(raw) or {}).get("目标", [])
    except Exception:  # noqa: BLE001
        return []
    if not items:
        return []
    catalog = "\n".join(
        f"- id={g.get('id')} 名称={g.get('名称')} 当前进度={g.get('进度')}" for g in items)
    prompt = (
        f"老板发来一条进度更新：\n『{body}』\n\n现有目标：\n{catalog}\n\n"
        "判断这条更新明确涉及哪些目标，输出 JSON 数组，每项形如 "
        '{"id":"wealth","进度":"4万"}。\n'
        "关键规则：进度值**直接用老板原话里的表述**（如『4万』『11本』『124斤』『已上线』），"
        "**绝不自行换算成阿拉伯数字、绝不编造或推断数字**——宁可原样照抄。\n"
        "只输出能明确对应的目标；无法对应就输出 []。只输出 JSON，不要解释。"
    )
    try:
        out = chat("你只输出 JSON。", prompt, temperature=0, max_tokens=300)
        m = re.search(r"\[.*\]", out, re.S)
        updates = json.loads(m.group(0)) if m else []
    except Exception:  # noqa: BLE001
        return []

    upd_map = {str(u.get("id")): str(u.get("进度", "")).strip()
               for u in updates if u.get("id") and str(u.get("进度", "")).strip()}
    if not upd_map:
        return []

    lines = raw.splitlines()
    cur = None
    changed: list[str] = []
    for i, line in enumerate(lines):
        mid = re.match(r"(\s*)-\s*id:\s*(\S+)", line)
        if mid:
            cur = mid.group(2)
            continue
        if cur in upd_map and re.match(r"\s*进度\s*:", line):
            indent = line[: len(line) - len(line.lstrip())]
            val = upd_map[cur]
            yval = val if re.fullmatch(r"-?\d+(\.\d+)?", val) else '"' + val.replace('"', "") + '"'
            lines[i] = f"{indent}进度: {yval}"
            changed.append(f"{cur}={val}")
            cur = None  # 每个目标只改第一处进度
    if changed:
        GOALS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return changed


def _log_progress(subject: str, body: str) -> None:
    PROGRESS.parent.mkdir(parents=True, exist_ok=True)
    header = "# 进度日志\n\n> 你通过邮件 [进度] 标签捕获的进展（自动追加）。\n\n" \
        if not PROGRESS.exists() else ""
    entry = f"## {datetime.now():%Y-%m-%d %H:%M} · {_slug(subject)}\n\n{body}\n\n"
    with PROGRESS.open("a", encoding="utf-8") as f:
        if header:
            f.write(header)
        f.write(entry)


PROC_STATE = BRAIN / "output" / ".inbox_uids.json"


def _load_processed() -> set[str]:
    if PROC_STATE.exists():
        try:
            return set(json.loads(PROC_STATE.read_text()))
        except Exception:  # noqa: BLE001
            return set()
    return set()


def _save_processed(uids: set[str]) -> None:
    PROC_STATE.parent.mkdir(parents=True, exist_ok=True)
    PROC_STATE.write_text(json.dumps(sorted(uids)[-500:]))  # 只留近 500 个，防无限增长


def poll(limit: int = 40) -> list[dict]:
    """按 UID 处理带标签邮件，与已读/未读无关；用持久化 UID 集去重，避免重复入库。"""
    llm._load_env()
    user = os.environ.get("SMTP_USER")
    pw = os.environ.get("SMTP_PASSWORD")
    if not (user and pw):
        return []
    host = os.environ.get("IMAP_HOST", "imap.qq.com")
    port = int(os.environ.get("IMAP_PORT", "993"))

    done = _load_processed()
    processed: list[dict] = []
    try:
        M = imaplib.IMAP4_SSL(host, port)
        M.login(user, pw)
        M.select("INBOX")
        typ, data = M.uid("SEARCH", None, "ALL")  # 不限已读/未读，靠 UID 去重
        uids = data[0].split()[-limit:]
        for uid in uids:
            uid_s = uid.decode() if isinstance(uid, bytes) else str(uid)
            if uid_s in done:
                continue
            typ, msgdata = M.uid("FETCH", uid, "(RFC822)")
            if typ != "OK" or not msgdata or not msgdata[0]:
                continue
            msg = email.message_from_bytes(msgdata[0][1])
            subject = _decode(msg.get("Subject"))
            m = _TAG_RE.search(subject or "")
            if not m:
                continue  # 没标签的不碰，也不计入已处理（将来补标签还能收）
            kind = TAGS[m.group(1).lower()]
            body = _body_text(msg)
            goal_changes: list[str] = []
            if kind == "progress":
                _log_progress(subject, body)
                dest = "progress-log.md"
                goal_changes = update_goals_from_text(body)
            else:
                p = _save_raw(kind, subject, body)
                dest = str(p.relative_to(BRAIN))
            done.add(uid_s)
            processed.append({"kind": kind, "subject": subject, "dest": dest,
                              "goal_changes": goal_changes})
        M.logout()
        _save_processed(done)
    except Exception as e:  # noqa: BLE001
        print(f"[inbox] IMAP 失败（不阻断）：{type(e).__name__}: {e}", file=sys.stderr)
    return processed


if __name__ == "__main__":
    got = poll()
    if not got:
        print("收件箱无带标签的新邮件。")
    for g in got:
        print(f"✓ [{g['kind']}] {g['subject']} → {g['dest']}")
        if g.get("goal_changes"):
            print(f"   ✅ 已更新目标进度：{'、'.join(g['goal_changes'])}")
