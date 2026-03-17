#!/bin/bash

# 信息聚合定时任务脚本
# 每天 06:30 执行，在 daily-learning 之前

cd /Users/linweihao/project/MuskOrchestrator

# 记录开始时间
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始信息聚合..."

# 激活虚拟环境（如果存在）
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

# 运行信息聚合器
python scripts/daily_aggregator.py --quiet

# 检查执行结果
if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 信息聚合完成"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 信息聚合失败"
    exit 1
fi

# 可选：推送到远程（如果配置了git自动提交）
# git add memory/agents/*/DAILY_FEED.md
# git commit -m "Daily info aggregation $(date '+%Y-%m-%d')"
# git push origin main

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 完成"
