#!/usr/bin/env python3
"""
Daily Micro Learning Script
Triggered by: cron / manual / skill
Updates: memory/agents/{agent}/LEARNING.md

Integrates with daily_aggregator.py for information aggregation.
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path("/Users/linweihao/project/MuskOrchestrator")
MEMORY_DIR = BASE_DIR / "memory" / "agents"
HEARTBEAT_FILE = BASE_DIR / "HEARTBEAT.md"
AGENT_SCRIPT = BASE_DIR / "scripts" / "daily_aggregator.py"

def get_today():
    return datetime.now().strftime("%Y-%m-%d")

def read_heartbeat():
    """Read current learning focus from HEARTBEAT"""
    if HEARTBEAT_FILE.exists():
        content = HEARTBEAT_FILE.read_text(encoding='utf-8')
        # Extract current focus
        focus = "General"
        for line in content.split('\n'):
            if line.startswith('**Current Focus**:'):
                focus = line.split(':', 1)[1].strip()
                break
        return focus
    return "General"

def run_aggregator():
    """Run the daily aggregator to fetch fresh content."""
    print(f"\n[{get_today()}] Running information aggregator...")

    try:
        result = subprocess.run(
            [sys.executable, str(AGENT_SCRIPT), "--days", "30", "--limit", "15"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode == 0:
            print("  ✓ Aggregator completed successfully")
            if result.stdout:
                # Print summary lines
                for line in result.stdout.split('\n')[-20:]:
                    if line.strip():
                        print(f"    {line}")
            return True
        else:
            print(f"  ✗ Aggregator failed with code {result.returncode}")
            if result.stderr:
                print(f"    Error: {result.stderr[:200]}")
            return False

    except subprocess.TimeoutExpired:
        print("  ✗ Aggregator timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"  ✗ Error running aggregator: {e}")
        return False

def update_agent_learning(agent_name, content_type, source, insight):
    """Append learning entry to agent's LEARNING.md"""
    agent_dir = MEMORY_DIR / agent_name
    agent_dir.mkdir(parents=True, exist_ok=True)

    learning_file = agent_dir / "LEARNING.md"

    entry = f"""
## {get_today()} - {content_type}

**Source**: {source}
**Focus**: {read_heartbeat()}

{insight}

---
"""

    if learning_file.exists():
        with open(learning_file, 'a', encoding='utf-8') as f:
            f.write(entry)
    else:
        header = f"# {agent_name.upper()} - Learning Log\n\n> Daily micro-learning records\n\n"
        with open(learning_file, 'w', encoding='utf-8') as f:
            f.write(header + entry)

def check_daily_feeds():
    """Check which agents have daily feeds available."""
    agents = ["planner", "analyst", "engineer", "mentor", "creator"]
    feeds_available = {}

    for agent in agents:
        feed_file = MEMORY_DIR / agent / "DAILY_FEED.md"
        if feed_file.exists():
            # Check if feed is from today
            mtime = datetime.fromtimestamp(feed_file.stat().st_mtime)
            is_today = mtime.date() == datetime.now().date()
            feeds_available[agent] = {
                'exists': True,
                'is_today': is_today,
                'items': 0
            }

            # Count items in feed
            try:
                content = feed_file.read_text(encoding='utf-8')
                feeds_available[agent]['items'] = content.count('### ')
            except:
                pass
        else:
            feeds_available[agent] = {'exists': False}

    return feeds_available

def main():
    """Execute daily micro learning"""
    print(f"[{get_today()}] Starting Daily Micro Learning...")
    print(f"Current Focus: {read_heartbeat()}")

    # Ensure directory structure exists
    agents = ["planner", "analyst", "engineer", "mentor", "creator", "reviewer"]
    for agent in agents:
        agent_dir = MEMORY_DIR / agent
        agent_dir.mkdir(parents=True, exist_ok=True)

    # Check current feed status
    print("\nChecking daily feeds...")
    feeds = check_daily_feeds()
    needs_refresh = False

    for agent, status in feeds.items():
        if not status['exists']:
            print(f"  ⚠ {agent}: No feed available")
            needs_refresh = True
        elif not status['is_today']:
            print(f"  ⚠ {agent}: Feed is outdated")
            needs_refresh = True
        else:
            print(f"  ✓ {agent}: {status['items']} items")

    # Run aggregator if needed
    if needs_refresh:
        print("\nRefreshing feeds via aggregator...")
        success = run_aggregator()
        if not success:
            print("Warning: Aggregator failed, using existing feeds if available")
    else:
        print("\nAll feeds are up to date, skipping aggregation")

    # Record learning session
    print(f"\n[{get_today()}] Daily Micro Learning complete!")
    print("\nNext steps:")
    print("  1. Review DAILY_FEED.md for each agent")
    print("  2. Select high-value items for deep learning")
    print("  3. Update LEARNING.md with insights")

if __name__ == "__main__":
    main()
