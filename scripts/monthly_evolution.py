#!/usr/bin/env python3
"""
Monthly Personality Evolution Script
Triggered by: cron (last Sunday of month 20:00) / manual / skill
Generates: evolution proposals for each agent

Usage:
    python scripts/monthly_evolution.py
"""

import os
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("/Users/linweihao/project/MuskOrchestrator")
MEMORY_DIR = BASE_DIR / "memory" / "agents"
EVOLUTION_HISTORY = BASE_DIR / "memory" / "evolution-history.md"

def get_current_month():
    return datetime.now().strftime("%Y-%m")

def check_if_last_sunday():
    """Check if today is the last Sunday of the month"""
    today = datetime.now()
    if today.weekday() != 6:  # 6 = Sunday
        return False

    # Check if next Sunday is in next month
    next_week = today.day + 7
    # If next_week > days_in_month, today is last Sunday
    import calendar
    _, days_in_month = calendar.monthrange(today.year, today.month)
    return next_week > days_in_month

def read_agent_learning(agent_name):
    """Read agent's LEARNING.md content"""
    learning_file = MEMORY_DIR / agent_name / "LEARNING.md"
    if learning_file.exists():
        return learning_file.read_text(encoding='utf-8')
    return f"*{agent_name} has no learning records yet.*"

def generate_evolution_proposal(agent_name):
    """Generate evolution proposal for agent"""
    month = get_current_month()

    proposal = f"""## 人格进化提案 - @{agent_name} - {month}

### 洞察来源
- 学习记录: `memory/agents/{agent_name}/LEARNING.md`
- 验证次数: [待填写]

### 进化类型
- [ ] 短期技巧 (Skill/Workflow)
- [ ] 方法论升级 (AGENT.md)
- [ ] 价值观进化 (CLAUDE.md)

### 当前状态
[描述当前人格特点]

### 进化提案
[具体的人格更新内容]

### 验证记录
1. [第一次验证 - 日期/场景/结果]
2. [第二次验证 - 日期/场景/结果]

### 预期效果
[这次进化将带来什么提升]

---
"""
    return proposal

def update_evolution_history():
    """Update evolution history file"""
    month = get_current_month()

    if EVOLUTION_HISTORY.exists():
        content = EVOLUTION_HISTORY.read_text(encoding='utf-8')
    else:
        content = "# Agent 人格进化历史\n\n> 记录每次人格进化的轨迹\n\n"

    # Check if this month already exists
    if f"## {month}" in content:
        return

    # Add new month section
    new_section = f"""
## {month} - 人格进化记录

### 执行时间
{datetime.now().strftime("%Y-%m-%d %H:%M")}

### 进化提案汇总

"""

    agents = ["planner", "engineer", "analyst", "mentor", "creator", "reviewer"]
    for agent in agents:
        new_section += f"#### @{agent}\n- 状态: [待提交提案]\n- 类型: [待定]\n\n"

    new_section += "---\n"

    EVOLUTION_HISTORY.parent.mkdir(parents=True, exist_ok=True)
    EVOLUTION_HISTORY.write_text(content + new_section, encoding='utf-8')
    print(f"Updated: {EVOLUTION_HISTORY}")

def main():
    """Execute monthly personality evolution"""
    month = get_current_month()

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Monthly Personality Evolution - {month}")
    print()

    if not check_if_last_sunday():
        print("⚠️  Today is not the last Sunday of the month.")
        print("   This script should run on the last Sunday at 20:00.")
        print("   Continuing anyway (manual execution)...")
        print()

    agents = ["planner", "engineer", "analyst", "mentor", "creator", "reviewer"]

    print("=" * 60)
    print("生成人格进化提案")
    print("=" * 60)
    print()

    for agent in agents:
        print(f"\n{'='*40}")
        print(f"@{agent}")
        print(f"{'='*40}")
        print(generate_evolution_proposal(agent))

    print()
    print("=" * 60)
    print("更新进化历史")
    print("=" * 60)
    update_evolution_history()

    print()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Evolution scaffold completed.")
    print()
    print("下一步:")
    print("1. 各Agent填写自己的进化提案")
    print("2. @planner 汇总提交给用户审批")
    print("3. 批准后更新相应人格文件")

if __name__ == "__main__":
    main()
