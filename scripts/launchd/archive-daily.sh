#!/bin/bash
# Archive daily agent outputs
# Triggered by launchd at 23:00 daily

cd /Users/linweihao/project/MuskOrchestrator

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting daily archive..."

# Run archive script
python3 scripts/archive_agent_outputs.py

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Daily archive completed."
