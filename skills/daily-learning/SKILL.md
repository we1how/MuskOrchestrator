# Daily Learning Skill

## Description

Execute daily micro-learning for all agents. Triggered automatically by cron or manually via `/daily-learning`.

## When to Use

- **Automatic**: Weekdays 07:00, Weekends 07:00 (configured in jobs.json)
- **Manual**: When you want to trigger immediate learning update

## How It Works

1. Reads HEARTBEAT.md for current learning focus
2. Spawns 4 subagents in parallel for micro-learning:
   - **@analyst**: Arxiv q-fin papers (5) + GitHub trending quant repos
   - **@engineer**: GitHub trending Python/AI + HackerNews top 5
   - **@mentor**: Book reviews/reading suggestions
   - **@creator**: Social media trends analysis
3. Each agent selects 1 highest-value item, 3-5 lines record
4. Results appended to respective LEARNING.md
5. Active proposals reported immediately

## Output

- Updates `memory/agents/{agent}/LEARNING.md`
- Updates `PROJECT_INVENTORY.md` (auto)
- Reports key insights

## Example Usage

```
/daily-learning
```

## Configuration

See `scripts/cron/jobs.json` for scheduling configuration.
