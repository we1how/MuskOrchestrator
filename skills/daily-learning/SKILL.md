# Daily Learning Skill

## Description

Execute daily micro-learning for all agents. Triggered automatically by cron or manually via `/daily-learning`.

## When to Use

- **Automatic**: Weekdays 07:00, Weekends 07:00 (configured in jobs.json)
- **Manual**: When you want to trigger immediate learning update

## How It Works

1. Reads HEARTBEAT.md for current learning focus
2. Spawns 4 subagents in parallel for micro-learning:
   - **@analyst**: Arxiv q-fin papers + GitHub trending quant repos
   - **@engineer**: GitHub trending Python/AI + HackerNews top
   - **@mentor**: Farnam Street + Wait But Why + LessWrong
   - **@creator**: Indie Hackers + Reddit + HN Show HN
3. Each agent selects 1 highest-value item
4. **CRITICAL**: Write detailed learning record to LEARNING.md
5. Create skill file if content passes quality filter
6. Report key insights

## CRITICAL: Detailed Learning Record Format

**每个Agent必须在LEARNING.md中添加详细记录**，不仅仅是索引更新：

```markdown
---

## YYYY-MM-DD 学习记录

### 📚 今日学习
**来源**: [具体来源]
**标题/项目**: [名称]
**链接**: [URL]
**学习时长**: [X分钟]

---

### 🎯 核心主题
[一句话总结核心主题]

---

### 💡 关键洞察（3-5点）

**1. [洞察标题]**
[详细解释，包含数据/公式/案例]

**2. [洞察标题]**
...

---

### 🔧 技术实现/执行步骤
[可执行的代码、SOP、或行动清单]

---

### 📊 信息差价值
- **国外热度**: ⭐⭐⭐⭐⭐
- **国内讨论度**: ⭐⭐⭐
- **可复刻性**: ⭐⭐⭐⭐⭐
- **对项目价值**: [高/中/低]

---

### 🎯 可应用性路径
**短期（本周）**:
- [ ] 具体行动

**中期（本月）**:
- [ ] 具体行动

---

### 🔖 相关资源
- 原文: [URL]
- 技能文件: `skills/xxx/xxx.md` (如创建)

---

### 📋 技能内化（如适用）
- **技能文件**: `skills/xxx/xxx.md`
- **触发条件**: [何时使用]
- **核心输出**: [关键产出]

---

*Learning Date: YYYY-MM-DD*

*Learning Date: [上一天日期]*
```

## Quality Filter for Skill Creation

技能化标准（必须全部满足）：
1. ✅ **可执行**: 有具体代码/SOP/步骤
2. ✅ **高价值**: 直接解决当前项目问题
3. ✅ **可复用**: 跨场景适用

不满足标准的内容：
- 只更新索引，不创建技能文件
- 但详细学习记录**仍然必须写入**

## Output

- Updates `memory/agents/{agent}/LEARNING.md` (detailed record)
- Updates index in LEARNING.md (auto)
- Creates `skills/{category}/{skill}.md` (if passes filter)
- Updates `PROJECT_INVENTORY.md` (auto)
- Reports key insights

## Example Usage

```
/daily-learning
```

## Configuration

See `scripts/cron/jobs.json` for scheduling configuration.
