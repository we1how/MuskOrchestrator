"""
brain/llm.py — 带自动 failover 的 LLM 客户端
==============================================
按 LLM_CHAIN（如 "kimi,minimax,deepseek"）顺序尝试，遇到余额不足/限流/超时/
连接错误自动切下一家。云端只读环境变量；本地自动加载 brain/.env。

用法：
    from llm import chat
    text = chat("system prompt", "user prompt")
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

# 部分模型（如 Kimi）会把 <|...|> 控制 token 泄进正文，统一清掉
_CTRL = re.compile(r"<\|[^|>]*\|>")


def _sanitize(text: str) -> str:
    return _CTRL.sub("", text).strip()

sys.path.insert(0, str(Path(__file__).resolve().parent))
from providers import PROVIDERS, get_key, load_keys_from_xlsx  # noqa: E402

_ENV_LOADED = False


def _load_env() -> None:
    """本地：加载 brain/.env 到 os.environ（不覆盖已存在的，云端 Secrets 优先）。"""
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())
    _ENV_LOADED = True


def _chain() -> list[str]:
    _load_env()
    raw = os.environ.get("LLM_CHAIN", "kimi,minimax,deepseek")
    return [s.strip() for s in raw.split(",") if s.strip() in PROVIDERS]


def chat(system: str, user: str, *, temperature: float = 0.7,
         max_tokens: int = 1200) -> str:
    """按链路尝试，返回首个成功的回复文本。全失败则抛 RuntimeError。"""
    _load_env()
    from openai import OpenAI

    xlsx = load_keys_from_xlsx()
    errors: list[str] = []
    for short in _chain():
        key = get_key(short, xlsx)
        if not key:
            errors.append(f"{short}: 无 key")
            continue
        cfg = PROVIDERS[short]
        client = OpenAI(api_key=key, base_url=cfg["base_url"],
                        timeout=60.0, max_retries=0)
        for model in cfg["models"]:
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                text = _sanitize(resp.choices[0].message.content or "")
                if text:
                    print(f"[llm] {cfg['label']} / {model} ✓", file=sys.stderr)
                    return text
            except Exception as e:  # noqa: BLE001
                errors.append(f"{short}/{model}: {type(e).__name__}: {str(e)[:120]}")
                break  # 同 provider 多半同因（余额/网络），直接切下一家
    raise RuntimeError("所有 LLM provider 均失败:\n  " + "\n  ".join(errors))


def active_provider() -> str:
    """返回当前链路第一个有 key 的 provider 短名（用于日志/报告）。"""
    _load_env()
    xlsx = load_keys_from_xlsx()
    for short in _chain():
        if get_key(short, xlsx):
            return short
    return "none"


if __name__ == "__main__":
    print("chain:", _chain())
    print(chat("你是个简洁的助手。", "用一句话证明你在线。"))
