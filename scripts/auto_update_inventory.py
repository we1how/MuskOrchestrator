#!/usr/bin/env python3
"""
自动更新 PROJECT_INVENTORY.md
- 定时任务触发时自动执行
- 新增/修改文件记录
- 保持格式一致性
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path("/Users/linweihao/project/MuskOrchestrator")
INVENTORY_FILE = PROJECT_DIR / "PROJECT_INVENTORY.md"

def get_file_description(file_path):
    """根据文件路径生成描述"""
    descriptions = {
        "CLAUDE.md": "主人格定义（冷酷CEO+可反驳模式）",
        "AGENTS.md": "Agent团队协作规范",
        "HEARTBEAT.md": "自我成长系统配置",
        "USER.md": "用户画像",
        "MEMORY.md": "长期记忆",
        "PROJECT_INVENTORY.md": "本文件（项目清单）",
        "LEARNING.md": "学习记录",
        "GROWTH_PLAN.md": "成长计划",
    }

    filename = file_path.name
    return descriptions.get(filename, "自动添加的文件")

def update_inventory(changes):
    """
    更新项目清单
    changes: list of (path, action, source) tuples
    """
    if not INVENTORY_FILE.exists():
        print(f"错误: {INVENTORY_FILE} 不存在")
        return False

    today = datetime.now().strftime("%Y-%m-%d")

    # 读取现有内容
    content = INVENTORY_FILE.read_text(encoding='utf-8')

    # 更新最后修改时间
    content = re.sub(
        r'> \*\*最后更新\*\*：\d{4}-\d{2}-\d{2}',
        f'> **最后更新**：{today}',
        content
    )

    # 在TODO部分添加变更记录
    if changes:
        todo_section = "### ✅ 最近更新 (Recent Updates)\n\n"
        todo_section += "| 日期 | 类型 | 文件路径 | 操作 | 触发源 |\n"
        todo_section += "|------|------|----------|------|--------|\n"

        for path, action, source in changes:
            rel_path = str(path).replace(str(PROJECT_DIR) + "/", "")
            todo_section += f"| {today} | 自动 | `{rel_path}` | {action} | {source} |\n"

        # 在TODO部分插入
        if "### ✅ 最近更新" not in content:
            # 在第一个### 🔴 之前插入
            content = re.sub(
                r'(### 🔴 进行中)',
                f'{todo_section}\n\\1',
                content
            )
        else:
            # 更新现有部分
            pass

    # 写回文件
    INVENTORY_FILE.write_text(content, encoding='utf-8')
    print(f"已更新 {INVENTORY_FILE}")
    return True

def scan_for_changes():
    """扫描文件变化（简化版）"""
    changes = []

    # 检查 .auto-task-marker 文件
    marker = PROJECT_DIR / ".auto-task-marker"
    if marker.exists():
        changes.append((marker, "任务触发", "launchd"))
        marker.unlink()  # 删除标记文件

    # 检查 .weekly-review-marker 文件
    weekly_marker = PROJECT_DIR / ".weekly-review-marker"
    if weekly_marker.exists():
        changes.append((weekly_marker, "周报生成", "weekly-review"))
        weekly_marker.unlink()

    return changes

def main():
    """主函数"""
    print(f"[{datetime.now()}] 自动更新项目清单...")

    changes = scan_for_changes()

    if changes:
        update_inventory(changes)
        print(f"记录了 {len(changes)} 个变更")
    else:
        print("无变更需要记录")

    return 0

if __name__ == "__main__":
    sys.exit(main())
