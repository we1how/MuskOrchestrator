# MiroThinker 深度研究Agent技能

## 技能概述

**来源**: https://github.com/MiroMindAI/MiroThinker
**核心能力**: 深度研究Agent框架，针对复杂研究和预测任务优化
**金融优化**: v1.5版本专门针对金融预测场景
**适用场景**: 深度个股研究、复杂预测任务、多源数据整合分析

---

## 核心特性

### 1. 交互式扩展机制（Interactive Scaling）

```python
class InteractiveResearchAgent:
    """
    支持动态深度扩展的研究Agent
    关键参数：max_iterations控制研究深度
    """

    def __init__(self, max_iterations=50, confidence_threshold=0.85):
        self.max_iterations = max_iterations
        self.confidence_threshold = confidence_threshold
        self.tool_calls = 0
        self.max_tool_calls = 300  # MiroThinker标准

    def research(self, query, context=None):
        """迭代式深度研究"""
        context = context or {}

        for iteration in range(self.max_iterations):
            # 1. 当前状态分析
            analysis = self._analyze_current_state(context)

            # 2. 检查是否达到置信度阈值
            if analysis["confidence"] >= self.confidence_threshold:
                return self._finalize(context, analysis)

            # 3. 确定下一步研究方向
            next_step = self._plan_next_step(analysis)

            # 4. 执行工具调用收集更多信息
            if self.tool_calls < self.max_tool_calls:
                new_data = self._execute_tool(next_step)
                context = self._integrate(context, new_data)
                self.tool_calls += 1
            else:
                break

        return self._finalize(context, analysis)
```

### 2. 长上下文处理（256K Context Window）

```python
class LongContextProcessor:
    """
    处理长文档和时序数据的上下文管理
    """

    def __init__(self, max_tokens=256000):
        self.max_tokens = max_tokens
        self.token_buffer = 0.9  # 保留10%缓冲

    def process_financial_reports(self, reports: list, price_data: pd.DataFrame):
        """
        整合财报和行情数据
        """
        # 1. 文档分块与重要性排序
        chunks = self._chunk_documents(reports)
        ranked_chunks = self._rank_by_relevance(chunks)

        # 2. 时序数据摘要
        price_summary = self._summarize_price_data(price_data)

        # 3. 构建上下文
        context = self._build_context(ranked_chunks, price_summary)

        return context

    def _chunk_documents(self, documents):
        """智能分块，保持语义完整性"""
        chunks = []
        for doc in documents:
            # 按段落/章节分块
            sections = self._split_by_sections(doc)
            for section in sections:
                if self._estimate_tokens(section) < self.max_tokens * 0.1:
                    chunks.append(section)
                else:
                    # 大块进一步细分
                    chunks.extend(self._further_split(section))
        return chunks
```

### 3. 工具增强推理（Tool-Augmented Reasoning）

```python
class ToolRegistry:
    """
    标准化工具注册与调用
    """

    def __init__(self):
        self.tools = {}
        self.traces = []  # Trace Collection

    def register(self, name: str, tool):
        """注册工具"""
        self.tools[name] = tool

    def execute(self, tool_name: str, params: dict) -> dict:
        """执行工具并记录Trace"""
        start_time = time.time()

        try:
            result = self.tools[tool_name].run(**params)
            status = "success"
        except Exception as e:
            result = {"error": str(e)}
            status = "error"

        elapsed = time.time() - start_time

        # 记录Trace
        self.traces.append({
            "tool": tool_name,
            "params": params,
            "result": result,
            "status": status,
            "elapsed_time": elapsed,
            "timestamp": datetime.now()
        })

        return result

    def get_traces(self):
        """获取完整调用链（用于审计和优化）"""
        return self.traces
```

---

## A股深度研究Agent实现

```python
class AShareDeepResearchAgent:
    """
    基于MiroThinker思想的A股深度研究Agent
    专门针对A股市场特点优化
    """

    def __init__(self):
        self.max_iterations = 30  # 适中深度，避免过拟合
        self.confidence_threshold = 0.80
        self.tool_registry = ToolRegistry()
        self._register_default_tools()

    def _register_default_tools(self):
        """注册A股专用工具"""
        self.tool_registry.register("price_data", AkSharePriceTool())
        self.tool_registry.register("financial_data", TushareFinancialTool())
        self.tool_registry.register("sentiment", EastMoneySentimentTool())
        self.tool_registry.register("news", FinancialNewsTool())
        self.tool_registry.register("sector", SectorAnalysisTool())
        self.tool_registry.register("macro", MacroDataTool())

    def deep_research(self, stock_code: str, research_question: str) -> dict:
        """
        执行深度研究

        Args:
            stock_code: 股票代码（如 "000001.SZ"）
            research_question: 研究问题（如 "未来7天走势预测"）

        Returns:
            包含预测结果、置信度、推理过程的字典
        """
        context = {
            "stock_code": stock_code,
            "question": research_question,
            "collected_data": {},
            "insights": [],
            "confidence": 0.0
        }

        # Phase 1: 基础数据收集
        context = self._collect_basic_data(context)

        # Phase 2: 迭代深度分析
        for i in range(self.max_iterations):
            analysis = self._analyze(context)
            context["confidence"] = analysis["confidence"]

            if analysis["confidence"] >= self.confidence_threshold:
                break

            # 确定信息缺口并补充
            gaps = analysis["information_gaps"]
            if not gaps:
                break

            context = self._fill_gaps(context, gaps)

        # Phase 3: 生成预测
        prediction = self._generate_prediction(context)

        return {
            "stock_code": stock_code,
            "prediction": prediction,
            "confidence": context["confidence"],
            "reasoning": context["insights"],
            "traces": self.tool_registry.get_traces(),
            "iterations": len(self.tool_registry.get_traces())
        }

    def _collect_basic_data(self, context: dict) -> dict:
        """收集基础数据（并行工具调用）"""
        stock_code = context["stock_code"]

        # 并行收集多维度数据
        data = {
            "price": self.tool_registry.execute("price_data", {"code": stock_code, "period": "1y"}),
            "financial": self.tool_registry.execute("financial_data", {"code": stock_code}),
            "sentiment": self.tool_registry.execute("sentiment", {"code": stock_code}),
        }

        context["collected_data"].update(data)
        return context

    def _analyze(self, context: dict) -> dict:
        """分析当前数据，识别信息缺口"""
        data = context["collected_data"]

        # 1. 数据完整性检查
        completeness = self._check_completeness(data)

        # 2. 初步分析
        insights = self._extract_insights(data)

        # 3. 置信度评估
        confidence = self._calculate_confidence(completeness, insights)

        # 4. 识别信息缺口
        gaps = self._identify_gaps(data, insights)

        return {
            "completeness": completeness,
            "insights": insights,
            "confidence": confidence,
            "information_gaps": gaps
        }

    def _fill_gaps(self, context: dict, gaps: list) -> dict:
        """根据信息缺口补充数据"""
        for gap in gaps:
            if gap["type"] == "sector_analysis":
                result = self.tool_registry.execute("sector", {
                    "industry": gap["industry"]
                })
                context["collected_data"]["sector"] = result

            elif gap["type"] == "macro_context":
                result = self.tool_registry.execute("macro", {
                    "indicators": ["PMI", "CPI", "M2"]
                })
                context["collected_data"]["macro"] = result

            elif gap["type"] == "news_events":
                result = self.tool_registry.execute("news", {
                    "code": context["stock_code"],
                    "days": 7
                })
                context["collected_data"]["news"] = result

        return context

    def _generate_prediction(self, context: dict) -> dict:
        """生成概率化预测"""
        # 基于收集的数据生成预测
        # 输出格式：方向 + 置信度 + 关键驱动因素
        return {
            "direction": "bullish",  # bullish/bearish/neutral
            "probability": 0.75,
            "target_price": None,
            "key_drivers": context["insights"],
            "risk_factors": []
        }

    def _check_completeness(self, data: dict) -> float:
        """检查数据完整性（0-1）"""
        required_fields = ["price", "financial", "sentiment"]
        optional_fields = ["sector", "macro", "news"]

        required_score = sum(1 for f in required_fields if f in data) / len(required_fields)
        optional_score = sum(1 for f in optional_fields if f in data) / len(optional_fields)

        return required_score * 0.7 + optional_score * 0.3

    def _extract_insights(self, data: dict) -> list:
        """从数据中提取洞察"""
        insights = []

        # 技术面洞察
        if "price" in data:
            price_insights = self._analyze_technical(data["price"])
            insights.extend(price_insights)

        # 基本面洞察
        if "financial" in data:
            fundamental_insights = self._analyze_fundamental(data["financial"])
            insights.extend(fundamental_insights)

        # 情绪面洞察
        if "sentiment" in data:
            sentiment_insights = self._analyze_sentiment(data["sentiment"])
            insights.extend(sentiment_insights)

        return insights

    def _calculate_confidence(self, completeness: float, insights: list) -> float:
        """计算整体置信度"""
        # 基础置信度来自数据完整性
        base_confidence = completeness * 0.6

        # 洞察质量加分
        insight_bonus = min(len(insights) * 0.05, 0.3)

        # 洞察一致性加分
        consistency_bonus = self._check_consistency(insights) * 0.1

        return min(base_confidence + insight_bonus + consistency_bonus, 1.0)

    def _identify_gaps(self, data: dict, insights: list) -> list:
        """识别信息缺口"""
        gaps = []

        if "sector" not in data:
            gaps.append({"type": "sector_analysis", "priority": "high"})

        if "macro" not in data:
            gaps.append({"type": "macro_context", "priority": "medium"})

        if "news" not in data:
            gaps.append({"type": "news_events", "priority": "high"})

        return gaps

    def _check_consistency(self, insights: list) -> float:
        """检查洞察之间的一致性"""
        # 简化实现：检查方向一致性
        directions = [i.get("direction") for i in insights if "direction" in i]
        if not directions:
            return 0.0

        # 多数方向占比
        from collections import Counter
        most_common = Counter(directions).most_common(1)[0][1]
        return most_common / len(directions)
```

---

## 与TradingAgents的整合

```python
class EnhancedTradingSystem:
    """
    整合MiroThinker深度研究能力到TradingAgents架构
    """

    def __init__(self):
        # TradingAgents核心组件
        self.analysts = {
            "fundamental": FundamentalAnalyst(),
            "technical": TechnicalAnalyst(),
            "sentiment": SentimentAnalyst(),
            "news": NewsAnalyst()
        }

        self.bullish_researcher = BullishResearcher()
        self.bearish_researcher = BearishResearcher()
        self.trader = TradingAgent()
        self.risk_manager = RiskManager()

        # MiroThinker增强：深度研究模块
        self.deep_researcher = AShareDeepResearchAgent()

    def make_trading_decision(self, stock_code: str) -> dict:
        """
        综合决策流程
        """
        # Step 1: 快速信号收集（TradingAgents模式）
        signals = {}
        for name, analyst in self.analysts.items():
            signals[name] = analyst.analyze(stock_code)

        # Step 2: 判断是否需要深度研究
        signal_variance = self._calculate_variance(signals)
        avg_confidence = np.mean([s.get("confidence", 0) for s in signals.values()])

        deep_insight = None
        if signal_variance > 0.3 or avg_confidence < 0.6:
            # 信号分歧大或置信度低时，触发深度研究
            deep_insight = self.deep_researcher.deep_research(
                stock_code,
                research_question=f"分析{stock_code}的投资价值和短期走势"
            )

        # Step 3: 研究员辩论
        research_report = self._conduct_research(
            stock_code, signals, deep_insight
        )

        # Step 4: 交易决策
        trade_decision = self.trader.decide(research_report)

        # Step 5: 风控审批
        final_decision = self.risk_manager.evaluate(trade_decision)

        return final_decision

    def _calculate_variance(self, signals: dict) -> float:
        """计算信号分歧程度"""
        directions = [s.get("signal", 0) for s in signals.values()]
        return np.var(directions)

    def _conduct_research(self, stock_code: str, signals: dict, deep_insight: dict = None) -> dict:
        """研究员综合报告"""
        # 整合快速信号和深度研究洞察
        report = {
            "stock_code": stock_code,
            "quick_signals": signals,
            "deep_insight": deep_insight,
            "recommendation": None
        }

        # 看涨研究员论证
        bullish_case = self.bullish_researcher.build_case(report)

        # 看跌研究员论证
        bearish_case = self.bearish_researcher.build_case(report)

        # 综合平衡
        report["recommendation"] = self._balance_cases(bullish_case, bearish_case)

        return report

    def _balance_cases(self, bullish: dict, bearish: dict) -> dict:
        """平衡多空观点"""
        # 基于证据强度加权
        bullish_strength = bullish.get("evidence_strength", 0.5)
        bearish_strength = bearish.get("evidence_strength", 0.5)

        total = bullish_strength + bearish_strength
        if total == 0:
            return {"signal": 0, "confidence": 0.5}  # 中性

        bullish_weight = bullish_strength / total
        bearish_weight = bearish_strength / total

        # 净信号
        net_signal = bullish.get("signal", 0) * bullish_weight - bearish.get("signal", 0) * bearish_weight

        return {
            "signal": np.sign(net_signal),
            "confidence": abs(net_signal),
            "direction": "bullish" if net_signal > 0 else "bearish" if net_signal < 0 else "neutral"
        }
```

---

## 关键参数与最佳实践

### 参数配置

| 参数 | 默认值 | 说明 | 调优建议 |
|------|--------|------|----------|
| max_iterations | 30 | 最大迭代深度 | 简单研究: 10-20, 深度研究: 30-50 |
| confidence_threshold | 0.80 | 置信度阈值 | 高要求: 0.85+, 平衡: 0.80 |
| max_tool_calls | 300 | 最大工具调用 | 受API限制调整 |
| context_window | 256K | 上下文窗口 | 根据模型能力调整 |

### A股特殊考虑

1. **T+1制度**: 研究周期应覆盖至少2-3个交易日
2. **涨跌停限制**: 价格数据需标记涨跌停状态
3. **散户情绪**: 情绪分析权重应高于美股
4. **政策影响**: 宏观工具需包含政策数据源

---

## 待实现功能

- [ ] AkShare/Tushare工具封装
- [ ] 情绪数据源接入（东方财富、雪球）
- [ ] Trace Collection可视化
- [ ] FutureX风格评估基准
- [ ] 与TradingAgents完整集成

---

**创建时间**: 2026-03-18
**版本**: v1.0
**关联项目**: TradingAgents, Stock Platform
