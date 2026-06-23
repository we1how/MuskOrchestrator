# Skill: Daytona AI Agent沙箱集成

## 概述

Daytona是一个专为AI Agent设计的代码执行沙箱基础设施，提供90ms冷启动、Stateful持久化、Computer Use支持等核心能力。本技能涵盖Daytona的架构原理、SDK使用方法和与stock-platform的集成方案。

---

## 核心概念

### 1. 架构设计哲学

```
传统Dev环境          Daytona Agent-Native
─────────────────    ─────────────────────
为人类设计             为AI Agent原生设计
Dashboard交互          API-first
创建慢(分钟级)          90ms冷启动
无状态                 Stateful持久化
单一环境               大规模并行
```

### 2. 技术栈对比

| 特性 | Daytona | E2B | Modal |
|------|---------|-----|-------|
| 隔离技术 | Docker容器 | Firecracker microVM | 自定义 |
| 冷启动 | ~90ms | ~150ms | ~500ms |
| 持久化 | Stateful | Ephemeral | Stateful |
| Computer Use | 支持 | 不支持 | 不支持 |
| 开源 | 部分 | 完全(Apache-2.0) | 部分 |
| 定价 | $0.067/h | $0.083/h | $0.12/h |

### 3. 核心能力矩阵

- **Git操作**: 内置clone/commit/branch管理
- **文件系统**: 完整的upload/download/search API
- **进程执行**: 代码运行、命令执行、PTY交互
- **LSP支持**: Language Server Protocol集成
- **虚拟桌面**: Linux/Windows/macOS GUI自动化

---

## 快速开始

### 安装SDK

```bash
# Python
pip install daytona_sdk

# TypeScript
npm install @daytonaio/sdk

# Go
go get github.com/daytonaio/daytona-go
```

### 基础使用

```python
from daytona_sdk import Daytona, DaytonaConfig

# 初始化
daytona = Daytona(DaytonaConfig(api_key="YOUR_API_KEY"))

# 创建沙箱
sandbox = daytona.create(language="python")

# 执行代码
result = sandbox.process.code_run('print("Hello, Daytona!")')
print(result.result)

# 清理
daytona.remove(sandbox)
```

---

## 高级用法

### 1. 带Git操作的完整工作流

```python
from daytona_sdk import Daytona

daytona = Daytona()

# 创建沙箱
sandbox = daytona.create(
    language="python",
    resources={"cpu": 2, "memory": 4}
)

try:
    # 克隆仓库
    sandbox.git.clone(
        url="https://github.com/user/quant-strategy.git",
        path="/workspace/strategy",
        branch="main"
    )

    # 安装依赖
    sandbox.process.exec("pip install -r /workspace/strategy/requirements.txt")

    # 上传数据文件
    with open("market_data.csv", "rb") as f:
        sandbox.fs.upload_file(
            path="/workspace/strategy/data/market_data.csv",
            content=f.read()
        )

    # 执行回测
    result = sandbox.process.code_run('''
import sys
sys.path.insert(0, "/workspace/strategy")
from backtest import run_backtest

results = run_backtest("/workspace/strategy/data/market_data.csv")
print(f"Sharpe Ratio: {results['sharpe']}")
print(f"Max Drawdown: {results['max_drawdown']}")
''')

    print(result.result)

finally:
    daytona.remove(sandbox)
```

### 2. 多沙箱并行执行

```python
import asyncio
from daytona_sdk import Daytona
from concurrent.futures import ThreadPoolExecutor

daytona = Daytona()

# 参数网格
param_grid = [
    {"fast_ma": 5, "slow_ma": 20},
    {"fast_ma": 10, "slow_ma": 30},
    {"fast_ma": 20, "slow_ma": 60},
]

def test_strategy(params):
    """在隔离沙箱中测试策略"""
    sandbox = daytona.create(language="python")

    try:
        code = f'''
import pandas as pd
import numpy as np

# 加载数据
df = pd.read_csv("data.csv")

# 计算均线
df['fast'] = df['close'].rolling({params['fast_ma']}).mean()
df['slow'] = df['close'].rolling({params['slow_ma']}).mean()

# 回测逻辑
signals = np.where(df['fast'] > df['slow'], 1, -1)
returns = signals * df['close'].pct_change()

sharpe = returns.mean() / returns.std() * np.sqrt(252)
print(f"Params: {params}, Sharpe: {{sharpe:.2f}}")
'''
        result = sandbox.process.code_run(code)
        return {"params": params, "output": result.result}
    finally:
        daytona.remove(sandbox)

# 并行执行
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(test_strategy, param_grid))

print(results)
```

### 3. LangChain工具集成

```python
from langchain.agents import Tool, AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain import hub
from daytona_sdk import Daytona

daytona = Daytona()

def safe_python_execute(code: str) -> str:
    """在Daytona沙箱中安全执行Python代码"""
    sandbox = daytona.create(language="python")
    try:
        result = sandbox.process.code_run(code)
        if result.exit_code == 0:
            return result.result
        else:
            return f"Error: {result.stderr}"
    finally:
        daytona.remove(sandbox)

def safe_data_analysis(file_path: str, analysis_code: str) -> str:
    """在沙箱中分析数据文件"""
    sandbox = daytona.create(language="python")
    try:
        # 上传文件
        with open(file_path, "rb") as f:
            sandbox.fs.upload_file(
                path=f"/workspace/{file_path}",
                content=f.read()
            )

        # 执行分析
        code = f'''
import pandas as pd
import numpy as np
import json

df = pd.read_csv("/workspace/{file_path}")
{analysis_code}
'''
        result = sandbox.process.code_run(code)
        return result.result
    finally:
        daytona.remove(sandbox)

# 创建工具
tools = [
    Tool(
        name="PythonExecutor",
        func=safe_python_execute,
        description="Execute Python code in a secure sandbox. Use for calculations, data processing, and algorithm testing."
    ),
    Tool(
        name="DataAnalyzer",
        func=safe_data_analysis,
        description="Analyze data files in a secure environment. Provide file path and analysis code."
    )
]

# 创建Agent
llm = ChatOpenAI(model="gpt-4")
prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 使用Agent
response = agent_executor.invoke({
    "input": "Calculate the mean and std of [1, 2, 3, 4, 5, 100] and identify outliers"
})
```

### 4. Computer Use - 浏览器自动化

```python
from daytona_sdk import Daytona

daytona = Daytona()

# 创建带虚拟桌面的沙箱
sandbox = daytona.create(
    language="python",
    desktop=True,  # 启用虚拟桌面
    desktop_size={"width": 1920, "height": 1080}
)

try:
    # 安装浏览器自动化工具
    sandbox.process.exec("pip install playwright")
    sandbox.process.exec("playwright install chromium")

    # 执行浏览器自动化
    code = '''
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    # 访问金融数据网站
    page.goto("https://finance.yahoo.com/quote/AAPL")
    page.wait_for_load_state("networkidle")

    # 提取数据
    price = page.query_selector('[data-symbol="AAPL"] [data-field="regularMarketPrice"]').inner_text()
    change = page.query_selector('[data-symbol="AAPL"] [data-field="regularMarketChange"]').inner_text()

    print(f"AAPL Price: {price}")
    print(f"AAPL Change: {change}")

    browser.close()
'''
    result = sandbox.process.code_run(code)
    print(result.result)

finally:
    daytona.remove(sandbox)
```

---

## stock-platform集成方案

### 1. 因子计算沙箱

```python
# infrastructure/sandbox/factor_executor.py
from daytona_sdk import Daytona
from typing import Dict, Any, List
import json

class FactorExecutor:
    """基于Daytona的因子计算执行器"""

    def __init__(self, api_key: str):
        self.daytona = Daytona(DaytonaConfig(api_key=api_key))
        self.cache = {}

    def execute_factor(self, factor_code: str, data: pd.DataFrame) -> pd.Series:
        """
        在沙箱中安全执行因子计算代码

        Args:
            factor_code: 因子计算Python代码
            data: 输入数据

        Returns:
            计算结果Series
        """
        sandbox = self.daytona.create(language="python")

        try:
            # 上传数据
            data_json = data.to_json()
            sandbox.fs.upload_file(
                path="/workspace/input_data.json",
                content=data_json.encode()
            )

            # 执行因子计算
            wrapper_code = f'''
import pandas as pd
import numpy as np

# 加载数据
df = pd.read_json("/workspace/input_data.json")

# 用户因子代码
{factor_code}

# 保存结果
result.to_json("/workspace/output.json")
'''
            result = sandbox.process.code_run(wrapper_code)

            if result.exit_code != 0:
                raise FactorExecutionError(result.stderr)

            # 下载结果
            output = sandbox.fs.download_file("/workspace/output.json")
            return pd.read_json(output)

        finally:
            self.daytona.remove(sandbox)

    def batch_execute(self, factors: List[Dict], data: pd.DataFrame) -> Dict[str, pd.Series]:
        """并行执行多个因子"""
        from concurrent.futures import ThreadPoolExecutor

        def execute_single(factor):
            return factor['name'], self.execute_factor(factor['code'], data)

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = dict(executor.map(execute_single, factors))

        return results
```

### 2. 策略回测沙箱

```python
# infrastructure/sandbox/backtest_runner.py
from daytona_sdk import Daytona
from dataclasses import dataclass
from typing import Optional

@dataclass
class BacktestResult:
    sharpe_ratio: float
    max_drawdown: float
    total_return: float
    trades: int
    equity_curve: list

class SandboxBacktestRunner:
    """隔离的策略回测执行器"""

    def __init__(self):
        self.daytona = Daytona()

    def run_backtest(
        self,
        strategy_code: str,
        data_path: str,
        start_date: str,
        end_date: str,
        initial_capital: float = 100000
    ) -> BacktestResult:
        """
        在沙箱中运行策略回测

        Args:
            strategy_code: 策略Python代码
            data_path: 历史数据路径
            start_date: 回测开始日期
            end_date: 回测结束日期
            initial_capital: 初始资金
        """
        sandbox = self.daytona.create(
            language="python",
            resources={"cpu": 2, "memory": 4}
        )

        try:
            # 克隆策略框架
            sandbox.git.clone(
                url="https://github.com/stock-platform/backtest-framework.git",
                path="/workspace/framework"
            )

            # 上传策略代码
            sandbox.fs.upload_file(
                path="/workspace/strategy.py",
                content=strategy_code.encode()
            )

            # 执行回测
            result = sandbox.process.code_run(f'''
import sys
sys.path.insert(0, "/workspace/framework")

from backtest import BacktestEngine
from strategy import Strategy

engine = BacktestEngine(
    data_path="{data_path}",
    start_date="{start_date}",
    end_date="{end_date}",
    initial_capital={initial_capital}
)

strategy = Strategy()
results = engine.run(strategy)

# 输出结果
import json
print(json.dumps({{
    "sharpe": results.sharpe_ratio,
    "max_drawdown": results.max_drawdown,
    "total_return": results.total_return,
    "trades": len(results.trades),
    "equity": results.equity_curve
}}))
''')

            # 解析结果
            output = json.loads(result.result)
            return BacktestResult(**output)

        finally:
            self.daytona.remove(sandbox)
```

### 3. 数据获取Agent沙箱

```python
# infrastructure/sandbox/data_agent.py
from daytona_sdk import Daytona
import hashlib

class DataAgentSandbox:
    """
    数据获取Agent的隔离执行环境
    防止爬虫被封，支持IP轮换和请求频率控制
    """

    def __init__(self):
        self.daytona = Daytona()

    def scrape_data(self, scraper_code: str, urls: List[str]) -> List[Dict]:
        """
        在隔离沙箱中执行数据抓取

        Args:
            scraper_code: 爬虫代码
            urls: 目标URL列表

        Returns:
            抓取结果列表
        """
        results = []

        for url in urls:
            # 每个URL使用新沙箱（IP隔离）
            sandbox = self.daytona.create(language="python")

            try:
                code = f'''
{scraper_code}

# 执行抓取
result = scrape("{url}")
import json
print(json.dumps(result))
'''
                output = sandbox.process.code_run(code)
                results.append(json.loads(output.result))

            except Exception as e:
                results.append({"url": url, "error": str(e)})

            finally:
                self.daytona.remove(sandbox)

        return results
```

---

## 最佳实践

### 1. 错误处理

```python
from daytona_sdk import Daytona, DaytonaError

class SandboxManager:
    def __init__(self):
        self.daytona = Daytona()

    def execute_with_retry(self, code: str, max_retries: int = 3):
        """带重试的沙箱执行"""
        for attempt in range(max_retries):
            sandbox = None
            try:
                sandbox = self.daytona.create(language="python")
                result = sandbox.process.code_run(code)

                if result.exit_code == 0:
                    return result.result
                else:
                    raise ExecutionError(result.stderr)

            except DaytonaError as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # 指数退避

            finally:
                if sandbox:
                    self.daytona.remove(sandbox)
```

### 2. 资源管理

```python
from contextlib import contextmanager

@contextmanager
def sandbox_session(language="python", resources=None):
    """沙箱会话上下文管理器"""
    daytona = Daytona()
    sandbox = None
    try:
        sandbox = daytona.create(
            language=language,
            resources=resources or {"cpu": 1, "memory": 1}
        )
        yield sandbox
    finally:
        if sandbox:
            daytona.remove(sandbox)

# 使用
with sandbox_session(language="python") as sandbox:
    result = sandbox.process.code_run("print('Hello')")
```

### 3. 缓存策略

```python
import hashlib
import redis

class CachedSandboxExecutor:
    def __init__(self, redis_client: redis.Redis):
        self.daytona = Daytona()
        self.cache = redis_client

    def execute(self, code: str) -> str:
        # 计算代码哈希
        code_hash = hashlib.sha256(code.encode()).hexdigest()

        # 检查缓存
        cached = self.cache.get(f"daytona:{code_hash}")
        if cached:
            return cached.decode()

        # 执行
        with sandbox_session() as sandbox:
            result = sandbox.process.code_run(code)

        # 缓存结果（TTL 1小时）
        self.cache.setex(
            f"daytona:{code_hash}",
            3600,
            result.result
        )

        return result.result
```

---

## 成本优化

### 1. 沙箱复用

```python
class SandboxPool:
    """沙箱池化复用"""

    def __init__(self, size: int = 5):
        self.daytona = Daytona()
        self.pool = queue.Queue()
        self.size = size

        # 预创建沙箱
        for _ in range(size):
            sandbox = self.daytona.create(language="python")
            self.pool.put(sandbox)

    def acquire(self):
        return self.pool.get(timeout=30)

    def release(self, sandbox):
        # 清理状态
        sandbox.process.exec("rm -rf /workspace/*")
        self.pool.put(sandbox)

    def destroy(self):
        while not self.pool.empty():
            sandbox = self.pool.get()
            self.daytona.remove(sandbox)
```

### 2. 智能调度

```python
class SmartScheduler:
    """根据任务复杂度智能选择执行环境"""

    def __init__(self):
        self.daytona = Daytona()

    def execute(self, code: str, complexity: str = "low"):
        """
        根据复杂度选择资源配置

        complexity: low/medium/high
        """
        resources = {
            "low": {"cpu": 1, "memory": 1},
            "medium": {"cpu": 2, "memory": 4},
            "high": {"cpu": 4, "memory": 8}
        }

        sandbox = self.daytona.create(
            language="python",
            resources=resources[complexity]
        )

        try:
            return sandbox.process.code_run(code)
        finally:
            self.daytona.remove(sandbox)
```

---

## 故障排查

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 沙箱创建超时 | 资源不足 | 增加超时时间或检查配额 |
| 代码执行无响应 | 死循环/资源耗尽 | 设置执行超时，限制资源使用 |
| 文件上传失败 | 大小限制 | 分片上传或使用外部存储 |
| Git克隆失败 | 网络/认证问题 | 检查URL和凭证 |

### 调试技巧

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 沙箱状态检查
sandbox = daytona.create(language="python")
print(f"Sandbox ID: {sandbox.id}")
print(f"Status: {sandbox.status}")

# 执行诊断
result = sandbox.process.exec("df -h && free -m")
print(result.result)
```

---

## 参考资源

- [Daytona官方文档](https://www.daytona.io/docs/)
- [Python SDK](https://pypi.org/project/daytona-sdk/)
- [TypeScript SDK](https://www.npmjs.com/package/@daytonaio/sdk)
- [GitHub仓库](https://github.com/daytonaio/daytona)
- [LangChain集成](https://python.langchain.com/docs/integrations/tools/daytona/)

---

*Skill Version: 1.0*
*Created: 2026-04-05*
*Last Updated: 2026-04-05*
