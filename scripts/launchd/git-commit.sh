#!/bin/bash
# Git auto commit daily changes
# Triggered by launchd at 23:30 daily

cd /Users/linweihao/project/MuskOrchestrator

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting git auto commit..."

# Run git auto commit script
./scripts/git_auto_commit.sh

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Git auto commit completed."
