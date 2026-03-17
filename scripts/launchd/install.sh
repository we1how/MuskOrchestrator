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
cp "$SCRIPT_DIR/com.muskorchestrator.archive-daily.plist" "$LAUNCHD_DIR/"
cp "$SCRIPT_DIR/com.muskorchestrator.git-commit.plist" "$LAUNCHD_DIR/"
cp "$SCRIPT_DIR/com.muskorchestrator.cleanup-weekly.plist" "$LAUNCHD_DIR/"
cp "$SCRIPT_DIR/com.muskorchestrator.monthly-evolution.plist" "$LAUNCHD_DIR/"
cp "$SCRIPT_DIR/com.muskorchestrator.startup-check.plist" "$LAUNCHD_DIR/"
cp "$SCRIPT_DIR/com.muskorchestrator.info-aggregator.plist" "$LAUNCHD_DIR/"

# 替换路径（使用用户的实际路径）
echo "2. 配置路径..."
for plist in daily-learning daily-learning-weekend weekly-review archive-daily git-commit cleanup-weekly monthly-evolution startup-check info-aggregator; do
    sed -i '' "s|/Users/linweihao/project/MuskOrchestrator|$PROJECT_DIR|g" "$LAUNCHD_DIR/com.muskorchestrator.$plist.plist"
done

# 加载定时任务
echo "3. 加载定时任务..."
launchctl load "$LAUNCHD_DIR/com.muskorchestrator.daily-learning.plist" 2>/dev/null || launchctl bootstrap gui/$(id -u) "$LAUNCHD_DIR/com.muskorchestrator.daily-learning.plist"
launchctl load "$LAUNCHD_DIR/com.muskorchestrator.daily-learning-weekend.plist" 2>/dev/null || launchctl bootstrap gui/$(id -u) "$LAUNCHD_DIR/com.muskorchestrator.daily-learning-weekend.plist"
launchctl load "$LAUNCHD_DIR/com.muskorchestrator.weekly-review.plist" 2>/dev/null || launchctl bootstrap gui/$(id -u) "$LAUNCHD_DIR/com.muskorchestrator.weekly-review.plist"
launchctl load "$LAUNCHD_DIR/com.muskorchestrator.archive-daily.plist" 2>/dev/null || launchctl bootstrap gui/$(id -u) "$LAUNCHD_DIR/com.muskorchestrator.archive-daily.plist"
launchctl load "$LAUNCHD_DIR/com.muskorchestrator.git-commit.plist" 2>/dev/null || launchctl bootstrap gui/$(id -u) "$LAUNCHD_DIR/com.muskorchestrator.git-commit.plist"
launchctl load "$LAUNCHD_DIR/com.muskorchestrator.cleanup-weekly.plist" 2>/dev/null || launchctl bootstrap gui/$(id -u) "$LAUNCHD_DIR/com.muskorchestrator.cleanup-weekly.plist"
launchctl load "$LAUNCHD_DIR/com.muskorchestrator.monthly-evolution.plist" 2>/dev/null || launchctl bootstrap gui/$(id -u) "$LAUNCHD_DIR/com.muskorchestrator.monthly-evolution.plist"
launchctl load "$LAUNCHD_DIR/com.muskorchestrator.startup-check.plist" 2>/dev/null || launchctl bootstrap gui/$(id -u) "$LAUNCHD_DIR/com.muskorchestrator.startup-check.plist"
launchctl load "$LAUNCHD_DIR/com.muskorchestrator.info-aggregator.plist" 2>/dev/null || launchctl bootstrap gui/$(id -u) "$LAUNCHD_DIR/com.muskorchestrator.info-aggregator.plist"

echo ""
echo "======================================"
echo "安装完成！"
echo "======================================"
echo ""
echo "已配置的定时任务（9个）："
echo "  📚 学习成长"
echo "    • 信息聚合: 06:30 (每天)"
echo "    • 工作日每日学习: 07:00 (周一到周五)"
echo "    • 周末每日学习: 07:00 (周六、周日)"
echo "    • 每周深度总结: 22:00 (周日)"
echo "    • 月度人格进化: 20:00 (每月最后一个周日)"
echo ""
echo "  🛠️ 系统维护"
echo "    • Agent输出归档: 23:00 (每天)"
echo "    • Git自动提交: 23:30 (每天)"
echo "    • 过期文件清理: 02:00 (每周日)"
echo "    • 启动检查: 系统启动时"
echo ""
echo "💡 启动检查功能:"
echo "  • 每次开机自动检测错过的任务"
echo "  • 如果周日22:00周报未生成，周一开机时自动补生成"
echo "  • 检查日志: logs/startup-check.log"
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
