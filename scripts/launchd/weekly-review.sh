#!/bin/bash
# Weekly Deep Review
# Triggered at 22:00 on Sunday

PROJECT_DIR="/Users/linweihao/project/MuskOrchestrator"
LOG_FILE="$PROJECT_DIR/logs/weekly-review.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')
WEEK_DATE=$(date '+%Y-%m-%d')

echo "[$DATE] Starting weekly deep review..." >> "$LOG_FILE"

# Change to project directory
cd "$PROJECT_DIR"

# Create a marker file for weekly review
touch "$PROJECT_DIR/.weekly-review-marker"

# Log the task
echo "[$DATE] Weekly review task triggered for week ending $WEEK_DATE" >> "$LOG_FILE"
echo "[$DATE] Tasks: Archive learnings, generate weekly report, update MEMORY.md" >> "$LOG_FILE"

# Optional: Send notification
osascript -e 'display notification "Weekly review task ready. Open Claude Code to execute." with title "MuskOrchestrator"'

echo "[$DATE] Weekly review task prepared." >> "$LOG_FILE"
