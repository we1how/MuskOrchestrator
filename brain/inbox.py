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
_TAG_RE = re.compile(r"\[\s*(" + "|".join(map(re.escape, TAGS)) + r")\s*\]", re.I)


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


def _body_text(msg) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True) or b""
                charset = part.get_content_charset() or "utf-8"
                return payload.decode(charset, "ignore").strip()
        return ""
    payload = msg.get_payload(decode=True) or b""
    return payload.decode(msg.get_content_charset() or "utf-8", "ignore").strip()


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


def _log_progress(subject: str, body: str) -> None:
    PROGRESS.parent.mkdir(parents=True, exist_ok=True)
    header = "# 进度日志\n\n> 你通过邮件 [进度] 标签捕获的进展（自动追加）。\n\n" \
        if not PROGRESS.exists() else ""
    entry = f"## {datetime.now():%Y-%m-%d %H:%M} · {_slug(subject)}\n\n{body}\n\n"
    with PROGRESS.open("a", encoding="utf-8") as f:
        if header:
            f.write(header)
        f.write(entry)


def poll(limit: int = 30) -> list[dict]:
    """收未读、按标签路由、标记已读。返回处理摘要列表。"""
    llm._load_env()
    user = os.environ.get("SMTP_USER")
    pw = os.environ.get("SMTP_PASSWORD")
    if not (user and pw):
        return []
    host = os.environ.get("IMAP_HOST", "imap.qq.com")
    port = int(os.environ.get("IMAP_PORT", "993"))

    processed: list[dict] = []
    try:
        M = imaplib.IMAP4_SSL(host, port)
        M.login(user, pw)
        M.select("INBOX")
        typ, data = M.search(None, "UNSEEN")
        ids = data[0].split()[-limit:]
        for num in ids:
            typ, msgdata = M.fetch(num, "(RFC822)")
            if typ != "OK" or not msgdata or not msgdata[0]:
                continue
            msg = email.message_from_bytes(msgdata[0][1])
            subject = _decode(msg.get("Subject"))
            m = _TAG_RE.search(subject or "")
            if not m:
                continue  # 没标签的不动（也不标已读，留着你自己看）
            kind = TAGS[m.group(1).lower()]
            body = _body_text(msg)
            if kind == "progress":
                _log_progress(subject, body)
                dest = "progress-log.md"
            else:
                p = _save_raw(kind, subject, body)
                dest = str(p.relative_to(BRAIN))
            M.store(num, "+FLAGS", "\\Seen")  # 处理过的标已读
            processed.append({"kind": kind, "subject": subject, "dest": dest})
        M.logout()
    except Exception as e:  # noqa: BLE001
        print(f"[inbox] IMAP 失败（不阻断）：{type(e).__name__}: {e}", file=sys.stderr)
    return processed


if __name__ == "__main__":
    got = poll()
    if not got:
        print("收件箱无带标签的新邮件。")
    for g in got:
        print(f"✓ [{g['kind']}] {g['subject']} → {g['dest']}")
