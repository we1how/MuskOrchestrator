#!/bin/bash
# Install launchd定时任务
# 运行此脚本配置macOS定时任务

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"

echo "======================================"
echo "MuskOrchestrator Launchd 安装脚本"
echo "======================================"
echo ""

# 创建LaunchAgents目录（如果不存在）
mkdir -p "$LAUNCHD_DIR"
mkdir -p "$PROJECT_DIR/logs"

# 复制plist文件
echo "1. 复制定时任务配置..."
cp "$SCRIPT_DIR/com.muskorchestrator.daily-learning.plist" "$LAUNCHD_DIR/"
cp "$SCRIPT_DIR/com.muskorchestrator.daily-learning-weekend.plist" "$LAUNCHD_DIR/"
cp "$SCRIPT_DIR/com.muskorchestrator.weekly-review.plist" "$LAUNCHD_DIR/"

# 替换路径（使用用户的实际路径）
echo "2. 配置路径..."
sed -i '' "s|/Users/linweihao/project/MuskOrchestrator|$PROJECT_DIR|g" "$LAUNCHD_DIR/com.muskorchestrator.daily-learning.plist"
sed -i '' "s|/Users/linweihao/project/MuskOrchestrator|$PROJECT_DIR|g" "$LAUNCHD_DIR/com.muskorchestrator.daily-learning-weekend.plist"
sed -i '' "s|/Users/linweihao/project/MuskOrchestrator|$PROJECT_DIR|g" "$LAUNCHD_DIR/com.muskorchestrator.weekly-review.plist"

# 加载定时任务
echo "3. 加载定时任务..."
launchctl load "$LAUNCHD_DIR/com.muskorchestrator.daily-learning.plist" 2>/dev/null || launchctl bootstrap gui/$(id -u) "$LAUNCHD_DIR/com.muskorchestrator.daily-learning.plist"
launchctl load "$LAUNCHD_DIR/com.muskorchestrator.daily-learning-weekend.plist" 2>/dev/null || launchctl bootstrap gui/$(id -u) "$LAUNCHD_DIR/com.muskorchestrator.daily-learning-weekend.plist"
launchctl load "$LAUNCHD_DIR/com.muskorchestrator.weekly-review.plist" 2>/dev/null || launchctl bootstrap gui/$(id -u) "$LAUNCHD_DIR/com.muskorchestrator.weekly-review.plist"

echo ""
echo "======================================"
echo "安装完成！"
echo "======================================"
echo ""
echo "已配置的定时任务："
echo "  • 工作日每日学习: 07:00 (周一到周五)"
echo "  • 周末每日学习: 07:00 (周六、周日)"
echo "  • 每周深度总结: 22:00 (周日)"
echo ""
echo "查看任务状态:"
echo "  launchctl list | grep muskorchestrator"
echo ""
echo "手动测试任务:"
echo "  launchctl start com.muskorchestrator.daily-learning"
echo ""
echo "卸载任务:"
echo "  $SCRIPT_DIR/uninstall.sh"
echo ""
