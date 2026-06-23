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


# ── 方向雷达（替代旧的"出货机器"）─────────────────────────────
# 老板用 AI 就能造东西，不需要工程深度，要的是"做什么 / 往哪走"。
# 每天从前沿信息里嗅出 3 个值得关注的热点 / 前进方向。

RADAR_SYSTEM = (
    "你是老板的『方向雷达』。老板现在开发高度依赖 AI、不缺工程能力，缺的是"
    "『今天该关注什么、往哪个方向走』。你的任务：从今天的前沿素材里，嗅出 3 个"
    "最值得老板关注的热点 / 前进方向——优先『能赚钱的、有趣的、能借 AI 快速做出来的』。"
    "不要泛泛而谈，每个方向都要具体、有抓手。眼光毒辣，只挑真正有信号的。"
)

RADAR_INSTRUCTION = (
    "下面是今天从多个高质量源抓到的素材。选出 3 个最有信号的热点 / 前进方向，"
    "严格按此格式输出（共 3 块，每块 3 行，不要多余解释）：\n"
    "方向①：<一句话点出这个热点/方向是什么>\n"
    "为什么现在：<一句话，为什么这是个值得现在关注的窗口>\n"
    "借AI做一小步：<一个老板今天就能借 AI 工具开始的具体动作>\n"
    "方向②：…（同上三行）\n"
    "方向③：…（同上三行）\n\n"
    "素材：\n{brief}"
)


def run_radar() -> dict:
    items = sources.gather("radar", per_feed=3, max_items=16)
    brief = sources.as_brief(items)
    used = sorted({it["source"] for it in items})
    try:
        text = chat(RADAR_SYSTEM, RADAR_INSTRUCTION.format(brief=brief),
                    temperature=0.85, max_tokens=700)
    except Exception as e:  # noqa: BLE001
        text = f"（方向雷达今日合成失败：{type(e).__name__}）"
    return {"agent": "radar", "emoji": "🔥", "name": "方向雷达",
            "text": text.strip(), "sources": used}


if __name__ == "__main__":
    for r in run_all():
        print(f"\n{r['emoji']} {r['name']}  (源: {', '.join(r['sources'])})")
        print(r["text"])
    rd = run_radar()
    print(f"\n{rd['emoji']} {rd['name']}  (源: {', '.join(rd['sources'])})")
    print(rd["text"])
