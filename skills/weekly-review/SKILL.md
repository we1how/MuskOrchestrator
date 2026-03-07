# Weekly Review Skill

## Description

Execute weekly deep review for agent evolution. Triggered automatically every Sunday 22:00.

## When to Use

- **Automatic**: Sunday 22:00 (configured in jobs.json)
- **Manual**: `/weekly-review` for immediate review

## How It Works

1. Reads HEARTBEAT.md for system state
2. Reads all Agent LEARNING.md files
3. Generates complete "Agent Evolution Report" including:
   - Each agent's weekly learning summary
   - Key insights and action items
   - Cross-agent knowledge fusion points
   - Next week's learning priorities
4. Saves report to `memory/reports/weekly/`
5. Updates MEMORY.md with key insights

## Output

- Weekly report: `memory/reports/weekly/YYYY-WXX-Agent进化报告.md`
- Updates `PROJECT_INVENTORY.md` (auto)

## Example Usage

```
/weekly-review
```
