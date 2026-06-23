"""
brain/email_send.py — SMTP 发信（复刻 stock_platform 模式）
==========================================================
smtplib + STARTTLS + MIMEText(utf-8)。环境变量同 stock_platform：
SMTP_HOST/PORT/USER/PASSWORD/NOTIFY_EMAIL。失败抛异常由上层处理。
"""
from __future__ import annotations

import os
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import llm  # noqa: E402  -- 复用其 .env 加载


def configured() -> bool:
    llm._load_env()
    return bool(os.environ.get("SMTP_USER") and os.environ.get("SMTP_PASSWORD"))


def send(subject: str, text_body: str, html_body: str | None = None) -> None:
    llm._load_env()
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASSWORD"]
    recipients = [e.strip() for e in os.environ.get("NOTIFY_EMAIL", user).split(",")]

    if html_body:
        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText(text_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))  # 后者优先显示
    else:
        msg = MIMEText(text_body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP(host, port) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(user, password)
        smtp.sendmail(user, recipients, msg.as_bytes())
