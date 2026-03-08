#!/usr/bin/env python3
"""
Startup Check Script
Triggered by: macOS login / manual
Checks for: Missed cron tasks due to shutdown

Usage:
    python scripts/startup_check.py
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path("/Users/linweihao/project/MuskOrchestrator")
SCRIPTS_DIR = BASE_DIR / "scripts"
REPORTS_DIR = BASE_DIR / "memory" / "reports" / "weekly"

def check_daily_learning_status():
    """Check if today's daily learning was completed"""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = BASE_DIR / "logs" / "daily-learning.log"

    if not log_file.exists():
        return False, "No log file found"

    content = log_file.read_text(encoding='utf-8')
    if today in content:
        return True, "Today's learning completed"
    return False, "Today's learning not found in logs"

def check_weekly_report_status():
    """Check if this week's report was generated"""
    today = datetime.now()
    week_str = today.strftime("%Y-W%W")
    report_file = REPORTS_DIR / f"{week_str}-Agent进化报告.md"

    if report_file.exists():
        return True, f"Report exists: {report_file.name}"
    return False, f"Missing report: {week_str}"

def check_missed_daily_learning():
    """Check for missed daily learning entries"""
    today = datetime.now()
    log_file = BASE_DIR / "logs" / "daily-learning.log"

    if not log_file.exists():
        return []

    # Check last 7 days
    missed_days = []
    content = log_file.read_text(encoding='utf-8')

    for i in range(7):
        check_date = today - timedelta(days=i)
        date_str = check_date.strftime("%Y-%m-%d")
        weekday = check_date.weekday()

        # Skip weekends for daily learning check (weekends have separate job)
        if weekday >= 5:  # Saturday=5, Sunday=6
            continue

        if date_str not in content:
            missed_days.append(check_date)

    return missed_days

def main():
    """Execute startup checks"""
    print("=" * 60)
    print("MuskOrchestrator Startup Check")
    print("=" * 60)
    print(f"Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    issues_found = []
    actions_needed = []

    # Check 1: Daily Learning Status
    print("📚 Daily Learning Status:")
    daily_ok, daily_msg = check_daily_learning_status()
    if daily_ok:
        print(f"  ✅ {daily_msg}")
    else:
        print(f"  ⚠️  {daily_msg}")
        issues_found.append("daily_learning")
        actions_needed.append("Run: launchctl start com.muskorchestrator.daily-learning")
    print()

    # Check 2: Weekly Report Status
    print("📊 Weekly Report Status:")
    weekly_ok, weekly_msg = check_weekly_report_status()
    if weekly_ok:
        print(f"  ✅ {weekly_msg}")
    else:
        print(f"  ⚠️  {weekly_msg}")
        issues_found.append("weekly_report")
        actions_needed.append("Run: python scripts/weekly_review.py")
    print()

    # Check 3: Missed Daily Learning (last 7 days)
    print("🔍 Missed Daily Learning (last 7 weekdays):")
    missed_days = check_missed_daily_learning()
    if missed_days:
        print(f"  ⚠️  Missed {len(missed_days)} day(s):")
        for day in missed_days:
            print(f"    - {day.strftime('%Y-%m-%d %A')}")
        issues_found.append("missed_daily")
        actions_needed.append("Manually review learning records for missed days")
    else:
        print("  ✅ All recent weekdays covered")
    print()

    # Summary
    print("=" * 60)
    if not issues_found:
        print("✅ All systems operational. No missed tasks detected.")
    else:
        print(f"⚠️  Found {len(issues_found)} issue(s):")
        for action in actions_needed:
            print(f"  → {action}")
        print()
        print("💡 Recommended Actions:")
        print("  1. Run missed tasks manually")
        print("  2. Review generated reports")
        print("  3. Consider keeping system awake during scheduled tasks")
    print("=" * 60)

    return len(issues_found)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
