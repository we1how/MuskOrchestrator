#!/bin/bash
# Daily Micro Learning - Weekend Version
# Triggered at 07:00 on weekends

PROJECT_DIR="/Users/linweihao/project/MuskOrchestrator"
LOG_FILE="$PROJECT_DIR/logs/daily-learning-weekend.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] Starting daily micro learning (weekend)..." >> "$LOG_FILE"

# Change to project directory
cd "$PROJECT_DIR"

# Create a marker file to indicate this is an automated task
touch "$PROJECT_DIR/.auto-task-marker"

# Log the task
echo "[$DATE] Weekend learning task triggered. Waiting for Claude Code session..." >> "$LOG_FILE"

# Optional: Send notification
osascript -e 'display notification "Weekend learning task ready. Open Claude Code to execute." with title "MuskOrchestrator"'

echo "[$DATE] Task prepared. Claude Code will execute on next session." >> "$LOG_FILE"
