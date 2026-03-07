# Monthly Personality Evolution Skill

## Description

Execute monthly personality evolution for all agents. Triggered on the last Sunday of each month at 20:00.

## When to Use

- **Automatic**: Last Sunday of month 20:00 (configured in jobs.json)
- **Manual**: `/evolve` for immediate evolution check

## How It Works

### Phase 1: Review & Extract (每个Agent独立执行)

1. Read `HEARTBEAT.md` Phase 5 guidelines
2. Read own `LEARNING.md` from past month
3. Read `MEMORY.md` for accumulated insights
4. Identify evolution candidates

### Phase 2: Evolution Classification

| Type | Criteria | Target File | Example |
|------|----------|-------------|---------|
| **Short-term Skill** | Useful technique | Skill/Workflow | New data source |
| **Methodology Upgrade** | Process improvement | AGENT.md | Improved planning approach |
| **Values Evolution** | Core belief change | CLAUDE.md/AGENT.md | Decision-making principles |

### Phase 3: Generate Evolution Proposal

每个Agent提交：
```markdown
## 人格进化提案 - {Agent} - {Month}

### 洞察来源
- 学习记录：[相关学习内容]
- 验证次数：[X次实践验证]

### 进化类型
[ ] 短期技巧  [ ] 方法论升级  [ ] 价值观进化

### 当前状态
[当前人格描述]

### 进化提案
[具体的人格更新内容]

### 验证记录
1. [第一次验证]
2. [第二次验证]
...

### 预期效果
[这次进化将带来什么提升]
```

### Phase 4: Integration & Update

- @planner 汇总所有提案
- 提交给用户审批
- 批准后更新相应人格文件
- 记录进化历史到 `memory/evolution-history.md`

## Output

- Evolution proposals per agent
- Updated personality files (after approval)
- Evolution history record

## Example Usage

```
/evolve
```

## Configuration

See `scripts/cron/jobs.json` for scheduling.
Last Sunday detection uses conditional logic in execution script.

## Evolution History

All evolutions recorded in: `memory/evolution-history.md`

Format:
```markdown
## 2026-03 - 人格进化记录

### @engineer
- 进化类型: 方法论升级
- 内容: [描述]
- 验证: [验证记录]

### @analyst
...
```
