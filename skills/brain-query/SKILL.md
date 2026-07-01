---
name: brain-query
description: 对第二大脑 wiki 做问答检索。当用户问"我关于X都记了什么"、"我的知识库里有没有Y"、"brain-query"、"查我的笔记"时使用。
---

# brain-query — 问答你的第二大脑

针对 `brain/wiki/` 回答问题，只用 wiki 里的内容，标注出处。

## 流程
1. 读 `brain/wiki/index.md` 定位候选页面。
2. 用 Grep/Read 在 `brain/wiki/` 下检索关键词（含同义词）。
3. 综合命中的页面回答，**每个论点标注来源页面路径**（`sources/...` / `concepts/...`）。
4. 若 wiki 里没有：明说"知识库里没有"，并建议把相关材料丢进 `raw/` 用 `/brain-ingest` 补上。

## 原则
- 答案优先来自 wiki，不要用通识冒充用户的笔记。
- 顺带指出可深挖的关联 `[[页面]]`。
