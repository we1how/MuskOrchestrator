#!/bin/bash
# Git Auto Commit Script
# Triggered by: cron (daily 23:30)
# Commits all changes to git repository

set -e

PROJECT_DIR="/Users/linweihao/project/MuskOrchestrator"
cd "$PROJECT_DIR"

# Check if there are changes
if git diff --quiet && git diff --cached --quiet; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] No changes to commit"
    exit 0
fi

# Add all changes
git add -A

# Commit with timestamp
COMMIT_MSG="Auto backup: $(date '+%Y-%m-%d %H:%M:%S')"
git commit -m "$COMMIT_MSG"

# Push to remote (if configured)
if git remote get-url origin > /dev/null 2>&1; then
    git push origin main
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Committed and pushed: $COMMIT_MSG"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Committed (no remote): $COMMIT_MSG"
fi
