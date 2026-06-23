"""
brain/providers.py — 5 个国产 OpenAI 兼容大模型的连接配置
================================================================
从桌面 api_keys.xlsx 读 key，按 provider 给出 base_url + 候选 model。
所有 provider 都走 OpenAI 兼容接口（openai SDK + 自定义 base_url）。

key 来源优先级：环境变量 > api_keys.xlsx。云端（GitHub Actions）只用环境变量，
本地开发可用 xlsx 直读。绝不把 key 写进仓库。
"""
from __future__ import annotations

import os
from pathlib import Path

XLSX_PATH = Path.home() / "Desktop" / "api_keys.xlsx"

# provider 短名 -> (xlsx 服务商名匹配子串, base_url, 候选 model 列表, 环境变量名)
PROVIDERS: dict[str, dict] = {
    "doubao": {
        "match": "火山",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "models": ["doubao-1-5-pro-32k-250115", "doubao-pro-32k", "doubao-1.5-pro-32k"],
        "env": "DOUBAO_API_KEY",
        "label": "火山方舟/Doubao",
    },
    "qwen": {
        "match": "阿里",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": ["qwen-plus", "qwen-flash", "qwen-turbo", "qwen-max"],
        "env": "QWEN_API_KEY",
        "label": "阿里百炼/Qwen",
    },
    "minimax": {
        "match": "inimax",
        "base_url": "https://api.minimaxi.com/v1",
        "models": ["MiniMax-Text-01", "abab6.5s-chat"],
        "env": "MINIMAX_API_KEY",
        "label": "MiniMax",
    },
    "deepseek": {
        "match": "deepseek",
        "base_url": "https://api.deepseek.com",
        "models": ["deepseek-chat"],
        "env": "DEEPSEEK_API_KEY",
        "label": "DeepSeek",
    },
    "kimi": {
        "match": "kimi",
        "base_url": "https://api.moonshot.cn/v1",
        "models": ["moonshot-v1-8k", "kimi-k2-0711-preview", "moonshot-v1-32k"],
        "env": "KIMI_API_KEY",
        "label": "Kimi/Moonshot",
    },
}


def load_keys_from_xlsx(path: Path = XLSX_PATH) -> dict[str, str]:
    """从 xlsx 读 {provider短名: key}。读不到返回空 dict（云端正常情况）。"""
    keys: dict[str, str] = {}
    if not path.exists():
        return keys
    try:
        import openpyxl
    except ImportError:
        return keys
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    for ws in wb.worksheets:
        for row in ws.iter_rows(values_only=True):
            cells = [str(c).strip() for c in row if c is not None and str(c).strip()]
            if len(cells) < 2:
                continue
            name, key = cells[0], cells[-1]
            for short, cfg in PROVIDERS.items():
                if cfg["match"].lower() in name.lower():
                    keys[short] = key
    return keys


def get_key(short: str, xlsx_keys: dict[str, str] | None = None) -> str | None:
    """环境变量优先，其次 xlsx。"""
    env = PROVIDERS[short]["env"]
    if os.environ.get(env):
        return os.environ[env]
    if xlsx_keys and xlsx_keys.get(short):
        return xlsx_keys[short]
    return None
