#!/usr/bin/env python3
"""
brain/probe_keys.py — 实测 5 个国产大模型，选主 + 备
======================================================
对每个 provider 的候选 model 逐个尝试同一个"合成测试 prompt"，记录：
  · auth/调用是否成功
  · 首个可用 model
  · 延迟（秒）
  · 输出文本（供人工判断质量）

跑法：
  python brain/probe_keys.py            # 实测并打印排名 + 各家样例输出
结果不写任何 key 到磁盘；选定后由人工/后续步骤写入 .env 与 GitHub Secrets。
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from providers import PROVIDERS, get_key, load_keys_from_xlsx  # noqa: E402

# 一个"既考验中文表达又考验结构化"的测试任务（贴近每日简报合成）
TEST_PROMPT = (
    "你是一个严格的成长教练。用户今天的目标是『股票账户盈利到十万』。"
    "请用不超过 80 字，给出一条今天就能执行的具体行动，并说明第一性原理的理由。"
    "直接给结论，不要客套。"
)


def probe_one(short: str, key: str) -> dict:
    from openai import OpenAI

    cfg = PROVIDERS[short]
    client = OpenAI(api_key=key, base_url=cfg["base_url"], timeout=40.0, max_retries=0)
    for model in cfg["models"]:
        t0 = time.time()
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": TEST_PROMPT}],
                temperature=0.7,
                max_tokens=300,
            )
            dt = time.time() - t0
            text = (resp.choices[0].message.content or "").strip()
            return {
                "short": short, "label": cfg["label"], "ok": True,
                "model": model, "latency": round(dt, 2),
                "chars": len(text), "text": text, "error": "",
            }
        except Exception as e:  # noqa: BLE001
            last = f"{model}: {type(e).__name__}: {str(e)[:160]}"
            continue
    return {
        "short": short, "label": cfg["label"], "ok": False,
        "model": "", "latency": 0.0, "chars": 0, "text": "", "error": last,
    }


def main() -> None:
    xlsx = load_keys_from_xlsx()
    results = []
    for short in PROVIDERS:
        key = get_key(short, xlsx)
        if not key:
            results.append({"short": short, "label": PROVIDERS[short]["label"],
                            "ok": False, "model": "", "latency": 0, "chars": 0,
                            "text": "", "error": "无 key"})
            continue
        print(f"探测 {PROVIDERS[short]['label']} ...", flush=True)
        results.append(probe_one(short, key))

    ok = [r for r in results if r["ok"]]
    ok.sort(key=lambda r: r["latency"])  # 先按延迟，质量人工看输出

    print("\n" + "=" * 64)
    print("探测结果（可用的按延迟升序）")
    print("=" * 64)
    for r in results:
        if r["ok"]:
            print(f"✅ {r['label']:<16} model={r['model']:<28} {r['latency']}s {r['chars']}字")
        else:
            print(f"❌ {r['label']:<16} {r['error']}")

    print("\n" + "-" * 64)
    print("各家样例输出（人工判断质量）")
    print("-" * 64)
    for r in ok:
        print(f"\n【{r['label']} / {r['model']} / {r['latency']}s】\n{r['text']}")

    if len(ok) >= 2:
        print("\n" + "=" * 64)
        print(f"建议  主: {ok[0]['label']} ({ok[0]['model']})")
        print(f"      备: {ok[1]['label']} ({ok[1]['model']})")
        print("=" * 64)
    elif len(ok) == 1:
        print(f"\n仅 1 家可用：{ok[0]['label']}")
    else:
        print("\n无可用 provider，检查 key / 网络。")


if __name__ == "__main__":
    main()
