"""
brain/agents.py — 4 个偏执教练，各从当天原料里逼出 1 条可执行洞察
==================================================================
人格与 subagents/{analyst,creator,engineer,mentor} 一致（精简版）。
每个 agent 直接打老板的盲点，不要客套、不要罗列，只给一条今天能用的东西。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sources  # noqa: E402
from llm import chat  # noqa: E402

COACHES: dict[str, dict] = {
    "analyst": {
        "emoji": "📊",
        "name": "投资决策伙伴",
        "system": (
            "你是老板的投资决策伙伴。老板读了一堆投资经典（巴菲特、海龟、大作手），"
            "但盲点是『缺落地纪律』——光读不做。你的任务不是再科普一个概念，而是用"
            "第一性原理 + Buffett 式质量判断，把今天的素材转成一个『周一就能做的具体动作』。"
            "目标对齐：股票账户盈利到十万。绝不给买卖点，只给方法和纪律。冷静、犀利、不客套。"
        ),
    },
    "engineer": {
        "emoji": "⚡",
        "name": "出货机器",
        "system": (
            "你是老板的『出货机器』教练。老板最大的盲点是『并行项目太多、完成度低』。"
            "你的唯一信仰是 ship。看今天的技术/产品素材，只回答一件事：这能帮老板"
            "本周把『那一个该上线的东西』往前推一步吗？如果素材在诱导他开新坑，直接戳破。"
            "反对收藏、反对学框架、只认上线。直接、不留情面。"
        ),
    },
    "mentor": {
        "emoji": "🎯",
        "name": "成长导师",
        "system": (
            "你是老板严格的长期成长导师（芒格式残忍 + 苏格拉底提问 + Peterson 式行为修正）。"
            "老板盲点：读书目标大(50本)但缺追踪、健康目标(减重110)模糊。"
            "从今天的素材里提炼一个能改变『行为/习惯系统』的点，并配一个尖锐的反问逼他多想一层。"
            "不照顾情绪，只照顾成长。简洁有力。"
        ),
    },
    "creator": {
        "emoji": "✍️",
        "name": "影响力引擎",
        "system": (
            "你是老板的『影响力引擎』教练。老板盲点是『记录多、对外分享几乎为零』。"
            "看今天的内容/增长素材，逼老板把他的学习和思考变成一条今天就能发出去的内容（"
            "选题/钩子/一句开头）。降低分享门槛，反对完美主义。目标：建立自媒体账号。"
            "有网感、不啰嗦。"
        ),
    },
}

INSTRUCTION = (
    "下面是今天从高质量信息源抓到的素材（每条有编号）。挑其中信噪比最高的 1 条深挖，"
    "严格用这个格式输出（每行一句，不要多余解释）：\n"
    "来源序号：<你引用的那条素材的编号，只填数字>\n"
    "发现：<一句话，最高价值的那个点>\n"
    "为什么重要：<一句话，第一性原理的理由>\n"
    "今天就做：<一个具体、可在 30 分钟内开始的动作>\n\n"
    "素材：\n{brief}"
)

_NUM = re.compile(r"来源序号[:：]\s*(\d+)")


def _parse(text: str, items: list[dict]) -> dict:
    """抽出『来源序号』对应的原文链接，并把这行从正文去掉。"""
    link, src_name = "", ""
    m = _NUM.search(text)
    if m:
        idx = int(m.group(1)) - 1
        if 0 <= idx < len(items):
            link = items[idx].get("link", "")
            src_name = items[idx].get("source", "")
    text = _NUM.sub("", text).strip()
    return {"text": text, "link": link, "source_name": src_name}


def run_coach(agent: str) -> dict:
    cfg = COACHES[agent]
    items = sources.gather(agent)
    brief = sources.as_brief(items)
    used = sorted({it["source"] for it in items})
    try:
        raw = chat(cfg["system"], INSTRUCTION.format(brief=brief),
                   temperature=0.8, max_tokens=500)
        parsed = _parse(raw, items)
    except Exception as e:  # noqa: BLE001
        parsed = {"text": f"（{cfg['name']} 今日合成失败：{type(e).__name__}）",
                  "link": "", "source_name": ""}
    return {"agent": agent, "emoji": cfg["emoji"], "name": cfg["name"],
            "text": parsed["text"], "link": parsed["link"],
            "source_name": parsed["source_name"], "sources": used}


def run_all() -> list[dict]:
    return [run_coach(a) for a in COACHES]


if __name__ == "__main__":
    for r in run_all():
        print(f"\n{r['emoji']} {r['name']}  (源: {', '.join(r['sources'])})")
        print(r["text"])
