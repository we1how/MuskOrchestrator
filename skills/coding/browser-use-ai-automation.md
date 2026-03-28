# Browser Use - AI浏览器自动化框架

> **来源**: GitHub Trending Python #1 (81K+ stars)
> **链接**: https://github.com/browser-use/browser-use
> **文档**: https://docs.browser-use.com
> **学习日期**: 2026-03-25

---

## 核心概念

Browser Use是一个让AI Agent能够像人类一样控制浏览器的Python框架。核心设计哲学是**"自然语言描述目标，结构化数据返回"**。

```
用户目标（自然语言） → Agent规划 → 浏览器执行 → 结构化数据返回
```

---

## 架构模式

### 双模式部署

| 模式 | 特点 | 适用场景 |
|------|------|----------|
| **Open Source** | 本地Playwright、自带LLM Key、免费 | 开发测试、数据敏感场景 |
| **Cloud** | 隐身浏览器、代理轮换、CAPTCHA解决 | 生产环境、大规模采集 |

### 核心组件

```python
Agent(task="...", llm=..., browser=...)
│
├─ Task: 自然语言描述的目标
├─ LLM: 推理引擎 (OpenAI/Anthropic/Ollama/ChatBrowserUse)
└─ Browser: 浏览器控制 (本地Playwright/Cloud托管)
```

---

## 快速开始

### 开源版安装

```bash
pip install browser-use
export OPENAI_API_KEY=sk-...
# 或
export ANTHROPIC_API_KEY=sk-...
```

### 基础用法

```python
from browser_use import Agent, ChatBrowserUse
import asyncio

async def main():
    agent = Agent(
        task="Find the number of stars of browser-use repo",
        llm=ChatBrowserUse(),  # 优化模型，比其他模型快3-5倍
    )
    result = await agent.run()
    print(result)

asyncio.run(main())
```

### Cloud SDK安装

```bash
pip install browser-use-sdk
export BROWSER_USE_API_KEY=your_key
```

```python
from browser_use_sdk.v3 import AsyncBrowserUse

client = AsyncBrowserUse()
result = await client.run("Find top 3 Hacker News posts")
print(result.output)
```

---

## 核心功能

### 1. 结构化输出（Pydantic Schema）

```python
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: float
    rating: float
    reviews: int

result = await client.run(
    "Extract product info from amazon.com/dp/B08N5WRWNW",
    output_schema=Product
)

# 自动验证和解析
print(result.output)
# Product(name="Kindle Paperwhite", price=139.99, rating=4.7, reviews=15234)
```

### 2. Session持久化

```python
# 创建Session
session = await client.sessions.create(proxy_country_code="us")

# 第一步：登录（保持Session）
result1 = await client.run(
    "Log into example.com",
    session_id=str(session.id),
    keep_alive=True
)

# 第二步：基于登录状态操作
result2 = await client.run(
    "Now click settings",
    session_id=str(session.id)
)

await client.sessions.stop(str(session.id))
```

### 3. Profile跨Session持久化

```bash
# 同步本地浏览器cookies到云端
curl -fsSL https://browser-use.com/profile.sh | sh
```

```python
# 使用已保存的Profile（免重新登录）
result = await client.run(
    "Go to dashboard",
    profile_id="your-profile-uuid"
)
```

### 4. Workspace文件操作

```python
# 创建Workspace
workspace = await client.workspaces.create(name="research-workspace")

# Agent在Workspace中创建文件
result = await client.run(
    "Research Tesla stock and create report.md",
    workspace_id=str(workspace.id)
)

# 获取文件列表
files = await client.workspaces.files(str(workspace.id), include_urls=True)
```

### 5. 文件上传

```python
from browser_use_sdk.v3 import FileUploadItem

upload_resp = await client.sessions.upload_files(
    str(session.id),
    files=[FileUploadItem(name="data.csv", content_type="text/csv")],
)

# 上传后Agent可直接读取
result = await client.run(
    "Read data.csv and create summary report",
    session_id=str(session.id)
)
```

---

## 多LLM提供商支持

```python
from browser_use import Agent

# OpenAI
from langchain_openai import ChatOpenAI
agent = Agent(task="...", llm=ChatOpenAI(model="gpt-4o"))

# Anthropic
from langchain_anthropic import ChatAnthropic
agent = Agent(task="...", llm=ChatAnthropic(model="claude-3-5-sonnet-20241022"))

# 本地模型 (Ollama)
from langchain_ollama import ChatOllama
agent = Agent(task="...", llm=ChatOllama(model="qwen2.5:14b"))
```

---

## 自定义工具扩展

```python
from browser_use import Tools

tools = Tools()

@tools.action(description='Send notification to Slack')
def notify_slack(message: str, channel: str = "#alerts") -> str:
    """Send a notification to Slack channel"""
    # 实现Slack通知逻辑
    return f"Sent to {channel}: {message}"

@tools.action(description='Query internal API')
def query_internal_api(endpoint: str) -> dict:
    """Query company internal API"""
    # 实现API查询逻辑
    return {"data": "..."}

agent = Agent(
    task="Check stock price and notify team",
    llm=ChatBrowserUse(),
    tools=tools,
)
```

---

## Cloud API参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `model` | `"bu-mini"` (快) 或 `"bu-max"` (强) | `"bu-mini"` |
| `output_schema` | 结构化输出Schema | None |
| `session_id` | 复用Session | None |
| `keep_alive` | 保持Session活跃 | False |
| `profile_id` | 持久化浏览器Profile | None |
| `proxy_country_code` | 代理国家 (e.g., "us", "cn") | None |
| `max_cost_usd` | 成本上限 | None |

---

## 定价（Cloud）

每1M token:
- 输入: $0.20
- 缓存输入: $0.02
- 输出: $2.00

---

## 与Stock Platform整合方案

```python
class StockDataCollector:
    """基于Browser Use的A股数据收集器"""

    def __init__(self):
        self.client = AsyncBrowserUse()

    async def collect_financial_reports(self, stock_code: str):
        """收集个股财报数据"""
        from pydantic import BaseModel

        class FinancialData(BaseModel):
            revenue: float
            net_profit: float
            eps: float
            roe: float

        result = await self.client.run(
            f"Go to eastmoney.com, search {stock_code}, "
            "extract latest quarterly financial data",
            output_schema=FinancialData,
            proxy_country_code="cn"
        )

        return result.output

    async def monitor_news(self, stock_code: str):
        """监控个股新闻"""
        class NewsItem(BaseModel):
            title: str
            source: str
            time: str
            sentiment: str

        result = await self.client.run(
            f"Search {stock_code} latest news on 10jqka.com.cn, "
            "extract top 5 news with sentiment analysis",
            output_schema=list[NewsItem]
        )

        return result.output
```

---

## 最佳实践

1. **使用结构化输出**：定义Pydantic Schema确保数据格式一致
2. **Session管理**：多步骤任务使用`keep_alive=True`保持状态
3. **错误处理**：捕获`TimeoutError`和`BrowserUseError`
4. **成本控制**：设置`max_cost_usd`限制单次任务成本
5. **代理设置**：访问地域限制网站时使用`proxy_country_code`

---

## 对比其他方案

| 项目 | 特点 | 适用场景 |
|------|------|----------|
| **Browser Use** | 结构化输出、Session持久化、Cloud托管 | AI Agent浏览器控制 |
| **Playwright MCP** | Microsoft官方、Accessibility Tree | 现有Playwright用户 |
| **Stagehand** | Playwright增强、TypeScript | TS技术栈 |
| **Skyvern** | Vision-only、无需Selector | 复杂/不规则页面 |
| **Lightpanda** | 高性能Headless | 大规模爬虫 |

---

## 相关资源

- [GitHub Repository](https://github.com/browser-use/browser-use)
- [官方文档](https://docs.browser-use.com)
- [Cloud控制台](https://cloud.browser-use.com)
- [Manus AI](https://manus.im) - 基于Browser Use构建的通用Agent产品

---

*技能文件创建日期: 2026-03-25*
*触发条件: 网页数据采集、自动化测试、AI Agent浏览器控制*
*核心输出: Agent + Browser + LLM 三组件模式*
