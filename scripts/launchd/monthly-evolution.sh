#!/bin/bash
# Monthly personality evolution
# Triggered by launchd at 20:00 every Sunday
# Note: Script internally checks if it's the last Sunday of month

cd /Users/linweihao/project/MuskOrchestrator

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting monthly evolution check..."

# Run evolution script (includes last Sunday check)
python3 scripts/monthly_evolution.py

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Monthly evolution check completed."
