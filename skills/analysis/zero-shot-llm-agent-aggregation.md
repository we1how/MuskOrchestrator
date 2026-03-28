# Zero-Shot LLM Agent Aggregation for Corporate Disclosure

## 技能概述

基于arXiv:2603.20965论文实现的多Agent零样本LLM聚合框架，通过元分类器将多样化零样本大语言模型判断整合为更强的公司披露分类信号，预测次日股票收益方向。

**核心公式**:
```
最终预测 = MetaClassifier(Agent1输出, Agent2输出, Agent3输出)
准确率提升: 0.561 (最佳单Agent) → 0.612 (元分类器聚合)
```

---

## 核心概念

### 1. 零样本LLM多样性

零样本LLM无需任务特定微调，但其预测因以下因素而异：
- **提示设计**: 不同prompt导致不同关注焦点
- **推理风格**: Chain-of-Thought vs Direct Answer
- **模型家族**: GPT vs Claude vs Llama的异质性

**核心洞察**: 这种"多样性"不是噪声，而是互补信号的来源。

### 2. 多Agent框架

```
输入: 公司披露文件
│
├─ Agent 1 (GPT-4) → 情感标签 + 置信度 + 理由
├─ Agent 2 (Claude) → 情感标签 + 置信度 + 理由
└─ Agent 3 (Llama) → 情感标签 + 置信度 + 理由
│
↓ 聚合层 (Logistic Meta-Classifier)
│
输出: 次日股票收益方向预测
```

### 3. 元分类器聚合

| 聚合方法 | 平衡准确率 | 说明 |
|----------|-----------|------|
| 最佳单Agent | 0.561 | 基准 |
| 多数投票 | 0.578 | 简单聚合 |
| 置信度加权 | 0.589 | 考虑置信度 |
| **元分类器** | **0.612** | 学习最优聚合 |

---

## 技术实现

### 多Agent披露分析系统

```python
from typing import List, Dict
import openai
import anthropic

class MultiAgentDisclosureAnalyzer:
    """
    多Agent公司披露分析系统
    基于arXiv:2603.20965思想实现
    """

    def __init__(self):
        self.agents = [
            {"name": "GPT-4", "client": openai.OpenAI(), "model": "gpt-4o"},
            {"name": "Claude", "client": anthropic.Anthropic(), "model": "claude-3-5-sonnet"},
            {"name": "Llama", "client": openai.OpenAI(base_url="..."), "model": "llama-3.1"}
        ]

    def analyze_disclosure(self, disclosure_text: str) -> List[Dict]:
        """多Agent并行分析披露文件"""
        results = []

        for agent in self.agents:
            analysis = self._agent_analysis(agent, disclosure_text)
            results.append({
                "agent": agent["name"],
                "sentiment": analysis["sentiment"],  # -1, 0, 1
                "confidence": analysis["confidence"],  # 0-1
                "reasoning": analysis["reasoning"]
            })

        return results

    def _agent_analysis(self, agent: Dict, text: str) -> Dict:
        """单个Agent分析"""
        prompt = f"""分析以下公司披露文件的情感倾向。

披露内容:
{text[:8000]}

输出格式:
情感标签: [看涨/中性/看跌]
置信度: [0-1之间的数字]
分析理由: [详细分析]"""

        response = agent["client"].chat.completions.create(
            model=agent["model"],
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        return self._parse_response(response.choices[0].message.content)
```

### 逻辑元分类器

```python
import numpy as np
from sklearn.linear_model import LogisticRegression

class MetaClassifierAggregator:
    """
    元分类器聚合器
    学习如何最优组合多Agent信号
    """

    def __init__(self, model_type='logistic'):
        if model_type == 'logistic':
            self.model = LogisticRegression(max_iter=1000)
        self.is_trained = False

    def prepare_features(self, agent_outputs: List[Dict]) -> np.ndarray:
        """
        将Agent输出转换为特征向量

        特征设计:
        - 每个Agent的情感标签 (-1, 0, 1)
        - 每个Agent的置信度 (0-1)
        - Agent间一致性指标
        - 情感分布统计
        """
        features = []

        # 基础特征
        for output in agent_outputs:
            features.extend([
                output["sentiment"],
                output["confidence"]
            ])

        # 聚合特征
        sentiments = [o["sentiment"] for o in agent_outputs]
        confidences = [o["confidence"] for o in agent_outputs]

        features.extend([
            np.mean(sentiments),
            np.std(sentiments),
            np.mean(confidences),
            max(confidences) - min(confidences),
            sum(1 for s in sentiments if s == 1),
            sum(1 for s in sentiments if s == -1),
        ])

        return np.array(features).reshape(1, -1)

    def train(self, X: np.ndarray, y: np.ndarray):
        """训练元分类器"""
        self.model.fit(X, y)
        self.is_trained = True

    def predict(self, agent_outputs: List[Dict]) -> Dict:
        """聚合预测"""
        features = self.prepare_features(agent_outputs)
        prediction = self.model.predict(features)[0]
        probability = self.model.predict_proba(features)[0]

        return {
            "direction": "up" if prediction == 1 else "down",
            "confidence": max(probability),
            "up_probability": probability[1]
        }
```

### A股披露事件策略

```python
class AShareDisclosureEventStrategy:
    """A股披露事件驱动策略"""

    def __init__(self):
        self.analyzer = MultiAgentDisclosureAnalyzer()
        self.aggregator = MetaClassifierAggregator()

    def on_disclosure(self, stock_code: str, disclosure: Dict) -> Dict:
        """披露事件处理"""
        # 1. 多Agent分析
        agent_outputs = self.analyzer.analyze_disclosure(disclosure["content"])

        # 2. 元分类器聚合
        prediction = self.aggregator.predict(agent_outputs)

        # 3. 生成交易信号
        signal = self._generate_signal(prediction)

        return {
            "stock_code": stock_code,
            "signal": signal["action"],
            "confidence": signal["confidence"],
            "consensus": self._calculate_consensus(agent_outputs)
        }

    def _generate_signal(self, prediction: Dict) -> Dict:
        """基于预测生成交易信号"""
        confidence = prediction["confidence"]
        direction = prediction["direction"]

        if confidence < 0.7:
            return {"action": "hold", "confidence": confidence}

        return {
            "action": "buy" if direction == "up" else "sell",
            "confidence": confidence
        }
```

---

## 应用场景

### 1. 财报事件驱动
- **触发**: 季度/年度财报发布
- **分析**: 多Agent分析财报文本
- **信号**: 预测次日股价反应

### 2. 业绩预告
- **触发**: 业绩预告公告
- **特点**: 信息密度高，歧义大
- **价值**: 多Agent聚合在复杂信息场景价值最大

### 3. 重大事项公告
- **触发**: 并购、重组、股权变动等
- **挑战**: 信息复杂，需要多维度解读
- **优势**: 元分类器可学习历史模式

---

## 与已有框架整合

### 与TradingAgents整合

```python
class TradingAgentsWithMetaAggregator:
    """将元分类器整合到TradingAgents"""

    def __init__(self):
        self.trading_agents = TradingAgentsGraph()
        self.meta_aggregator = MetaClassifierAggregator()

    def enhanced_decision(self, stock_code: str, disclosure: Dict):
        # 1. TradingAgents基础分析
        base_signals = self.trading_agents.analyze(stock_code)

        # 2. 披露事件增强分析
        if disclosure:
            disclosure_signals = self.analyze_disclosure(disclosure)
            base_signals.append(disclosure_signals)

        # 3. 元分类器聚合所有信号
        final_decision = self.meta_aggregator.predict(base_signals)

        return final_decision
```

### 与BlindTrade整合

```python
class AnonymousDisclosureAnalyzer:
    """匿名化披露分析"""

    def __init__(self):
        self.anonymizer = AShareAnonymizer()
        self.analyzer = MultiAgentDisclosureAnalyzer()

    def analyze(self, disclosure: Dict) -> List[Dict]:
        # 匿名化处理
        anonymized_text = self.anonymizer.anonymize_text(
            disclosure["content"]
        )

        # 零样本分析（天然匿名）
        return self.analyzer.analyze_disclosure(anonymized_text)
```

---

## 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| Agent数量 | 3 | GPT-4, Claude, Llama |
| 置信度阈值 | 0.7 | 低于此值不交易 |
| 训练数据量 | 18,420 | 论文使用数据量 |
| 特征维度 | 12 | 6基础+6聚合特征 |

---

## 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| 平衡准确率 | 0.612 | 元分类器聚合 |
| 单Agent最佳 | 0.561 | GPT-4 |
| 提升幅度 | +9.1% | 相对提升 |
| 数据量 | 18,420 | 2018-2024披露 |

---

## 参考资料

- **论文**: arXiv:2603.20965
- **标题**: Learning to Aggregate Zero-Shot LLM Agents for Corporate Disclosure Classification
- **作者**: Kemal Kirtac
- **核心发现**: "zero-shot LLM agents capture complementary financial signals and that supervised aggregation can turn cross-agent disagreement into a more useful classification target"

---

## 触发条件

- 披露事件分析
- 多Agent信号聚合
- 元分类器设计
- 财报/业绩预告事件驱动策略
