# Hermes Agent - 自适应学习Agent框架

## 概述

Hermes Agent是Nous Research出品的**自适应AI Agent框架**，具备闭环学习系统、自主技能创建、跨会话用户建模能力。31.8K stars，是首个将"持续学习"作为核心架构设计的Agent框架。

**核心定位**: 不是工具调用器，而是终身学习者

---

## 核心特性

### 1. 闭环学习系统 (Learning Loop)

```
经验 → 技能提取 → 使用优化 → 知识沉淀
```

- **自动技能创建**: Agent从交互中提取可复用模式
- **使用即改进**: 技能在使用过程中持续优化
- **FTS5 + LLM摘要**: 跨会话记忆检索
- **Honcho用户建模**: 跨会话个性化

### 2. 六终端后端架构

| 后端 | 适用场景 | 特点 |
|------|----------|------|
| Local | 开发测试 | 零依赖 |
| Docker | 标准部署 | 隔离环境 |
| SSH | 远程服务器 | 已有基础设施 |
| Daytona | AI沙箱 | 90ms冷启动 |
| Singularity | HPC环境 | 科研计算 |
| Modal | Serverless | 按需付费 |

### 3. 多平台消息网关

单一Agent实例，全渠道响应：
- Telegram、Discord、Slack、WhatsApp、Signal
- Email网关
- 统一gateway进程管理

---

## 快速开始

### 安装

```bash
pip install hermes-agent
# 或
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent && pip install -e .
```

### 基础配置

```bash
# 设置API密钥
export OPENROUTER_API_KEY="your-key"
# 或
export OPENAI_API_KEY="your-key"

# 启动交互式CLI
hermes

# 切换模型
hermes model
```

### Python SDK

```python
from hermes import Agent

# 创建具备学习能力的Agent
agent = Agent(
    name="research_assistant",
    learning_enabled=True,
    user_modeling=True,
)

# 执行并学习
result = agent.run("分析这份CSV文件")
# 后续调用自动使用学习到的技能
```

---

## 技能系统

### 技能定义 (agentskills.io标准)

```python
from hermes import skill, Tool

@skill(
    name="data_analysis",
    description="自动分析数据并生成可视化",
    triggers=["分析数据", "生成图表"],
    learning_mode="auto_improve"
)
class DataAnalysisSkill:
    tools = ["pandas", "matplotlib"]

    async def execute(self, file_path: str):
        # 实现逻辑
        pass
```

### 技能自动发现

```python
# 放置技能文件到目录
# ./skills/finance_analysis.py
# ./skills/technical_indicators.py

# Agent自动加载并学习使用
agent.discover_skills("./skills")
```

---

## 记忆系统

### 跨会话记忆

```python
# 存储记忆
agent.memory.store(
    content="用户偏好科技股",
    category="user_preference",
    tags=["investment", "tech"]
)

# 检索记忆
memories = agent.memory.recall(
    query="用户投资偏好",
    session_scope="all",  # 跨所有会话
    limit=5
)
```

### 用户建模 (Honcho集成)

```python
# 自动构建用户画像
agent.user_model.update(
    trait="risk_tolerance",
    value="high",
    confidence=0.85,
    source="trading_history_analysis"
)

# 使用用户画像个性化响应
profile = agent.user_model.get_profile()
```

---

## 与Daytona集成

```python
from hermes import Agent
from hermes.backends import DaytonaBackend

# 配置Daytona后端
backend = DaytonaBackend(
    api_key="your-daytona-key",
    template="python-3.11"
)

agent = Agent(
    name="secure_researcher",
    backend=backend,
    learning_enabled=True
)

# 代码在Daytona沙箱中安全执行
result = agent.run("""
    下载并分析 https://example.com/data.csv
    生成技术分析图表
""")
```

---

## Docker部署

```yaml
version: '3.8'
services:
  hermes:
    image: nousresearch/hermes:latest
    environment:
      - HERMES_MODEL_PROVIDER=openrouter
      - HERMES_LEARNING_LOOP=true
      - HERMES_MEMORY_BACKEND=sqlite
      - HERMES_GATEWAY_ENABLED=true
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    volumes:
      - ./skills:/app/skills
      - ./memory:/app/memory
    ports:
      - "8080:8080"
```

---

## 量化场景应用

### 场景1: 财报分析Agent

```python
@skill(name="earnings_analysis")
class EarningsAnalysisSkill:
    """自动下载、解析、分析公司财报"""

    async def execute(self, ticker: str, quarter: str):
        # 1. 下载财报PDF
        # 2. 提取关键指标
        # 3. 对比预期vs实际
        # 4. 生成分析摘要
        pass
```

### 场景2: 多Agent辩论系统

```python
# 创建多头Agent
bull_agent = Agent(name="bull_analyst", persona="乐观分析师")
bear_agent = Agent(name="bear_analyst", persona="悲观分析师")

# 并行分析
def debate_analysis(stock: str):
    bull_view = bull_agent.run(f"分析{stock}的上涨理由")
    bear_view = bear_agent.run(f"分析{stock}的下跌风险")

    # 综合判断
    judge = Agent(name="judge", role="中立裁判")
    decision = judge.run(f"基于以下观点做出判断:\n多头:{bull_view}\n空头:{bear_view}")
    return decision
```

### 场景3: 交易信号推送

```python
# 配置Telegram网关
hermes gateway --platform telegram --bot-token $BOT_TOKEN

# 信号生成时自动推送
async def on_signal_generated(signal: TradingSignal):
    await agent.notify(
        platform="telegram",
        message=f"🚨 交易信号\n股票: {signal.ticker}\n方向: {signal.direction}\n置信度: {signal.confidence}"
    )
```

---

## 最佳实践

### 1. 技能设计原则

- **单一职责**: 每个技能只做一件事
- **明确触发词**: 让Agent能准确识别何时使用
- **提供示例**: 帮助Agent理解技能用途
- **版本控制**: 技能也是代码，需要版本管理

### 2. 记忆管理

- **分类存储**: 使用category区分记忆类型
- **定期清理**: 避免记忆膨胀影响检索速度
- **敏感信息**: 使用加密存储API密钥等敏感数据

### 3. 学习循环调优

```python
# 控制学习频率
agent.learning.configure(
    min_interactions_before_skill=5,  # 至少5次交互才创建技能
    skill_improvement_threshold=0.1,   # 改进幅度>10%才更新
    max_skills_per_session=3          # 每会话最多创建3个技能
)
```

---

## 故障排查

### 技能未被调用

```python
# 检查技能注册
print(agent.skills.list())

# 查看触发词匹配
agent.debug.match_triggers("你的查询文本")
```

### 记忆检索失败

```python
# 重建FTS索引
agent.memory.rebuild_index()

# 检查存储状态
agent.memory.stats()
```

### 网关连接问题

```bash
# 检查网关状态
hermes gateway status

# 重启网关
hermes gateway restart

# 查看日志
hermes logs --follow
```

---

## 相关资源

- **GitHub**: https://github.com/NousResearch/hermes-agent
- **文档**: https://github.com/NousResearch/hermes-agent/tree/main/docs
- **agentskills.io**: 开放技能标准
- **Honcho**: https://honcho.dev/
- **Daytona**: https://www.daytona.io/

---

*Skill File: hermes-adaptive-agent-framework.md*
*Created: 2026-04-08*
*Source: Nous Research Hermes Agent*
