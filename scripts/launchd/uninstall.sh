#!/bin/bash
# Uninstall launchd定时任务

set -e

LAUNCHD_DIR="$HOME/Library/LaunchAgents"

echo "======================================"
echo "MuskOrchestrator Launchd 卸载脚本"
echo "======================================"
echo ""

echo "1. 停止并卸载定时任务..."

# 停止任务
launchctl stop com.muskorchestrator.daily-learning 2>/dev/null || true
launchctl stop com.muskorchestrator.daily-learning-weekend 2>/dev/null || true
launchctl stop com.muskorchestrator.weekly-review 2>/dev/null || true

# 卸载任务（兼容新旧版本macOS）
launchctl unload "$LAUNCHD_DIR/com.muskorchestrator.daily-learning.plist" 2>/dev/null || true
launchctl unload "$LAUNCHD_DIR/com.muskorchestrator.daily-learning-weekend.plist" 2>/dev/null || true
launchctl unload "$LAUNCHD_DIR/com.muskorchestrator.weekly-review.plist" 2>/dev/null || true

# 尝试使用bootout（新版本macOS）
launchctl bootout gui/$(id -u)/com.muskorchestrator.daily-learning 2>/dev/null || true
launchctl bootout gui/$(id -u)/com.muskorchestrator.daily-learning-weekend 2>/dev/null || true
launchctl bootout gui/$(id -u)/com.muskorchestrator.weekly-review 2>/dev/null || true

echo "2. 删除plist文件..."
rm -f "$LAUNCHD_DIR/com.muskorchestrator.daily-learning.plist"
rm -f "$LAUNCHD_DIR/com.muskorchestrator.daily-learning-weekend.plist"
rm -f "$LAUNCHD_DIR/com.muskorchestrator.weekly-review.plist"

echo ""
echo "======================================"
echo "卸载完成！"
echo "======================================"
echo ""
launchctl list | grep muskorchestrator || echo "所有任务已卸载"
echo ""
