#!/bin/bash
# Weekly cleanup of expired workspaces
# Triggered by launchd at 02:00 every Sunday

cd /Users/linweihao/project/MuskOrchestrator

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting weekly cleanup..."

# Run cleanup script
python3 scripts/archive_agent_outputs.py --cleanup

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Weekly cleanup completed."
