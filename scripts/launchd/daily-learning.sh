#!/bin/bash
# Daily Micro Learning - Weekday Version
# Triggered at 07:00 on weekdays

PROJECT_DIR="/Users/linweihao/project/MuskOrchestrator"
LOG_FILE="$PROJECT_DIR/logs/daily-learning.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Starting daily micro learning (weekday)..." >> "$LOG_FILE"

# Change to project directory
cd "$PROJECT_DIR"

# Create a marker file to indicate this is an automated task
# Claude Code will detect this and auto-update PROJECT_INVENTORY.md
touch "$PROJECT_DIR/.auto-task-marker"

# Log the task
echo "[$DATE] Daily learning task triggered. Waiting for Claude Code session..." >> "$LOG_FILE"
echo "[$DATE] Note: Please open Claude Code in this directory to execute /daily-learning" >> "$LOG_FILE"

# Optional: Send notification
osascript -e 'display notification "Daily learning task ready. Open Claude Code to execute." with title "MuskOrchestrator"'

echo "[$DATE] Task prepared. Claude Code will execute on next session." >> "$LOG_FILE"
