# Knowledge Archive Skill

## Description

Automatically archive agent outputs and extract insights. Runs daily at 23:00.

## When to Use

- **Automatic**: Daily 23:00
- **Manual**: `/archive-now` for immediate archiving
- **Cleanup**: Weekly cleanup every Sunday 02:00

## How It Works

1. Scans all agent work directories
2. Archives completed outputs to `memory/reports/archive/`
3. Extracts insights and updates MEMORY.md
4. (Cleanup mode) Removes expired workspaces (>7 days)

## Scripts

- `scripts/archive_agent_outputs.py` - Main archive logic
- `scripts/git_auto_commit.sh` - Git auto commit at 23:30

## Example Usage

```
/archive-now
```

## Output

- Archive JSON files with timestamps
- Updated MEMORY.md with extracted insights
- Git commit with daily changes
