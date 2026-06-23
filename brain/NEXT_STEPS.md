# NEXT_STEPS — 接下来怎么做

> 2026-06-23 项目复活后的行动清单。对齐 USER.md 的 2026 六大目标与已有计划，
> 分「现在做 / 本周做 / 记录待时机」三档。原则：**反分散——本月只推一条主线。**

---

## 🔴 现在做（今天，5-30 分钟级）

1. **合并 PR #1 让每日邮件上线**
   - 去 https://github.com/we1how/MuskOrchestrator/pull/1 合并到 main。
   - 合并后次日 07:00（北京时间）自动发第一封；也可在 Actions 页点 `daily-briefing → Run workflow` 立即测一次。
2. **填 `brain/goals.yaml` 的进度**
   - 给六个目标各填一个 `进度:` 数字（0-100），让每日「作战简报」有真实进度条。
   - 确认/修改「本月唯一主线」——现在写的是"复活第二大脑"，下月该换成真正的业务主线。
3. **给 DeepSeek 充值（可选）**
   - DeepSeek key 有效但余额不足。充值后它会自动进入 `LLM_CHAIN` 失效备援链（已配在 Secrets）。

## 🟡 本周做

4. **清理坏掉的本地定时任务**（已被云端取代）
   - 8 个 `com.muskorchestrator.*` launchd job 全是坏的(127)或被动弹通知的。手动跑：
     ```bash
     bash /Users/linweihao/project/MuskOrchestrator/scripts/launchd/uninstall.sh
     ```
   - 或逐个 `launchctl bootout gui/$UID/com.muskorchestrator.<名字>` 后删 `~/Library/LaunchAgents/` 对应 plist。
5. **投资落地（目标：盈利到十万）**
   - 把 `memory/learning-plans/quant-restart-plan.md` 的第一周任务真正做掉一项（不是再读）。
   - @analyst 已改造为「投资决策伙伴」：让它对一个你关注的标的跑一次 serenity-method，产出"周一就做"。
6. **出货（目标：上线 1 个产品）**
   - 用 @engineer「出货机器」选定**唯一一个**要 ship 的东西，砍到最小可上线切片，列出"离上线还差几步"。
   - 候选：把 `brain/` 第二大脑本身做成可对外展示的产品？还是 TimeScore？**只选一个。**
7. **破除"记录多分享少"**
   - 用 @creator「影响力引擎」把本次"复活第二大脑"的过程写成第一条小红书/推文（先发 80 分）。

## 🟢 记录待时机（别现在分心，归档进 wiki/raw 或 goals 备注）

- 量化 18 个月路线图（`memory/learning-plans/quant_18month_plan.html`）——主线稳定后再系统推进。
- 三层思维宫殿体系（已迁入 `brain/wiki/concepts/思维宫殿/`）——作为方法论随用随取。
- 周日自动复盘 / 每周内容草稿（计划 E）——等每日简报稳定跑一周后再加云端 workflow。
- 健康量化（减重 110）——本周先定一个可量化周指标（体重/运动次数），交给 @mentor 追踪。

---

## 🔄 怎么把进度 / 新知识 / 书喂回第二大脑（双向通道）

不再是单方面输出。**给你自己的 QQ 邮箱（2698470157@qq.com）发一封邮件，主题带标签**，
下次简报跑时会自动收进来（IMAP 已验证可用）：

| 主题标签 | 用途 | 进了哪里 |
|---------|------|---------|
| `[进度]` | 今天/本周做了什么、目标进展 | 记进 `progress-log.md` **并自动更新 `goals.yaml` 的目标进度**（LLM 按原话匹配，不换算数字）；下封简报会显示"已更新进度：xxx" |
| `[读书]` | 读了什么书、书摘 | `brain/wiki/raw/`，用 `/brain-ingest` 整理成书摘 |
| `[知识]` | 新学的知识点 | `brain/wiki/raw/` |
| `[想法]` | 灵感 | `brain/wiki/raw/` |

例：手机上新建邮件 → 主题 `[读书] 穷查理宝典` → 正文写几句感想 → 发给自己。
搞定。`raw/` 里的材料随后开 Claude Code 用 `/brain-ingest` 一键整理进 wiki。
> 进阶：以后可加云端 IMAP 轮询（现在是每日 briefing 跑时顺带收），实现近实时入库。

## 📌 已搭好的基础设施（复用它们，别重造）
- **每日成长简报引擎**：`brain/daily_briefing.py`（云端 07:00 自动；本地 `--dry-run` 预览）
- **第二大脑 wiki**：`brain/wiki/`（`index.md` 总目录），技能 `/brain-ingest` `/brain-query` `/brain-lint`
- **四教练**：`subagents/{analyst,engineer,mentor,creator}/`（已改造为偏执教练）
- **目标状态**：`brain/goals.yaml`（手改即可影响每日简报）

## 🎯 2026 六大目标 ↔ 谁负责
| 目标 | 主责 agent | 当前卡点 |
|------|-----------|---------|
| 股票盈利到十万 | @analyst | 缺落地纪律 |
| 上线 1 个产品 | @engineer | 并行项目太多 |
| 自媒体 / 对外输出 | @creator | 记录多分享少 |
| 50 本书 / 50 电影 / 12 项目 | @mentor | 缺量化追踪 |
| 减重至 110 / 薄肌 | @mentor | 目标模糊 |
| 每月一城旅游 | — | 顺其自然 |
