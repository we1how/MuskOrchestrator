# Kelly Position Sizing

## Description

Calculate optimal position size using Fractional Kelly Criterion.

## When to Use

- Need to determine position size for a trade
- Managing portfolio risk
- Comparing risk/reward ratios

## Parameters

- `win_rate`: Probability of winning (0-1)
- `avg_win`: Average win percentage (e.g., 0.08 for 8%)
- `avg_loss`: Average loss percentage (e.g., 0.04 for 4%)
- `fraction`: Kelly fraction (default 0.25 for 25%)

## Example Usage

```
/kelly-position win_rate=0.55 avg_win=0.08 avg_loss=0.04
```

## Output

Returns recommended position size, Kelly fraction, and risk assessment.
