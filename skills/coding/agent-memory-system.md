# Skill: Agent Memory系统实现

## 元信息
- **类型**: coding
- **来源**: Hindsight (GitHub Trending)
- **链接**: https://github.com/vectorize-io/hindsight
- **创建日期**: 2026-03-13
- **版本**: 1.0

---

## 触发条件

使用此技能当：
- 需要让Agent具备长期学习和记忆能力
- 当前Agent只能记住对话历史，无法积累知识
- 需要Agent从经验中学习并改进

---

## 核心概念

### 仿生记忆架构

传统Agent Memory vs Hindsight Memory:

| 维度 | 传统记忆 | Hindsight记忆 |
|------|----------|---------------|
| 存储 | 对话历史 | 结构化知识 |
| 检索 | 相似度匹配 | 多策略融合 |
| 学习 | 无 | 反思生成洞察 |
| 连接 | 孤立记录 | 知识图谱关联 |

### 三大核心操作

```python
retain(content)   # 存储并提取实体/关系/时序
recall(query)     # 4种策略并行检索
reflect(query)    # 生成洞察，建立新连接
```

---

## Python实现

```python
from typing import List, Dict, Optional
import numpy as np
from dataclasses import dataclass

@dataclass
class MemoryEntry:
    """记忆条目"""
    content: str
    timestamp: float
    entities: List[str]
    relations: List[tuple]
    embedding: np.ndarray
    importance: float

class AgentMemory:
    """仿生Agent记忆系统"""

    def __init__(self, embedding_model, cross_encoder):
        self.entries: List[MemoryEntry] = []
        self.entity_index: Dict[str, List[int]] = {}
        self.temporal_index: List[tuple] = []  # (timestamp, entry_id)
        self.embedding_model = embedding_model
        self.cross_encoder = cross_encoder

    def retain(self, content: str, metadata: Optional[dict] = None) -> int:
        """
        存储信息，提取实体、关系、时序

        Args:
            content: 记忆内容
            metadata: 元数据（时间、来源等）

        Returns:
            entry_id
        """
        import time

        # 1. 提取实体
        entities = self._extract_entities(content)

        # 2. 提取关系
        relations = self._extract_relations(content, entities)

        # 3. 计算嵌入
        embedding = self.embedding_model.encode(content)

        # 4. 评估重要性
        importance = self._calculate_importance(content)

        # 5. 创建条目
        entry = MemoryEntry(
            content=content,
            timestamp=metadata.get('timestamp', time.time()),
            entities=entities,
            relations=relations,
            embedding=embedding,
            importance=importance
        )

        entry_id = len(self.entries)
        self.entries.append(entry)

        # 6. 更新索引
        for entity in entities:
            if entity not in self.entity_index:
                self.entity_index[entity] = []
            self.entity_index[entity].append(entry_id)

        self.temporal_index.append((entry.timestamp, entry_id))

        return entry_id

    def recall(self, query: str, top_k: int = 5) -> List[MemoryEntry]:
        """
        4种策略并行检索，融合排序

        策略:
        1. 语义检索 (向量相似度)
        2. 关键词检索 (BM25)
        3. 图谱检索 (实体关联)
        4. 时序检索 (最近相关)
        """
        # 1. 语义检索
        query_embedding = self.embedding_model.encode(query)
        semantic_scores = [
            (i, np.dot(query_embedding, e.embedding))
            for i, e in enumerate(self.entries)
        ]

        # 2. 关键词检索
        query_entities = self._extract_entities(query)
        keyword_scores = []
        for i, entry in enumerate(self.entries):
            score = sum(1 for e in query_entities if e in entry.entities)
            keyword_scores.append((i, score))

        # 3. 图谱检索 (实体关联扩展)
        graph_scores = []
        for i, entry in enumerate(self.entries):
            score = 0
            for qe in query_entities:
                if qe in entry.entities:
                    score += 1
                    # 关联实体也得分
                    for rel in entry.relations:
                        if qe in rel:
                            score += 0.5
            graph_scores.append((i, score))

        # 4. 时序检索 (最近+重要性加权)
        import time
        now = time.time()
        temporal_scores = [
            (i, entry.importance / (1 + (now - entry.timestamp) / 86400))
            for i, entry in enumerate(self.entries)
        ]

        # 使用Reciprocal Rank Fusion合并结果
        fused_scores = self._reciprocal_rank_fusion([
            semantic_scores,
            keyword_scores,
            graph_scores,
            temporal_scores
        ])

        # Cross-encoder重排序
        candidates = [self.entries[i] for i, _ in fused_scores[:top_k*2]]
        reranked = self._rerank_with_cross_encoder(query, candidates)

        return reranked[:top_k]

    def reflect(self, query: str) -> str:
        """
        生成洞察，建立记忆间的新连接
        """
        # 1. 检索相关记忆
        memories = self.recall(query, top_k=10)

        # 2. 分析模式
        patterns = self._analyze_patterns(memories)

        # 3. 生成洞察
        insight = self._generate_insight(query, memories, patterns)

        # 4. 存储洞察作为新记忆
        self.retain(
            f"Insight: {insight}",
            metadata={'type': 'insight', 'source_memories': [m.content for m in memories]}
        )

        return insight

    def _extract_entities(self, text: str) -> List[str]:
        """提取实体 (可使用NER模型)"""
        # 简化实现：提取大写名词
        import re
        words = re.findall(r'\b[A-Z][a-zA-Z]+\b', text)
        return list(set(words))

    def _extract_relations(self, text: str, entities: List[str]) -> List[tuple]:
        """提取实体间关系"""
        relations = []
        for i, e1 in enumerate(entities):
            for e2 in entities[i+1:]:
                if e1 in text and e2 in text:
                    # 简单判断：同一句话中出现则建立关系
                    sentences = text.split('.')
                    for sent in sentences:
                        if e1 in sent and e2 in sent:
                            relations.append((e1, e2, 'co_occur'))
        return relations

    def _calculate_importance(self, content: str) -> float:
        """计算内容重要性"""
        # 启发式：长度、关键词密度、实体数量
        base = min(len(content) / 1000, 1.0)
        entities = len(self._extract_entities(content))
        return min(base + entities * 0.1, 1.0)

    def _reciprocal_rank_fusion(
        self,
        score_lists: List[List[tuple]]
    ) -> List[tuple]:
        """
        Reciprocal Rank Fusion算法合并多源排序
        """
        k = 60  # 平滑参数
        fused_scores = {}

        for scores in score_lists:
            sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
            for rank, (idx, _) in enumerate(sorted_scores):
                if idx not in fused_scores:
                    fused_scores[idx] = 0
                fused_scores[idx] += 1 / (k + rank + 1)

        return sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)

    def _rerank_with_cross_encoder(
        self,
        query: str,
        candidates: List[MemoryEntry]
    ) -> List[MemoryEntry]:
        """使用Cross-encoder重排序"""
        pairs = [(query, c.content) for c in candidates]
        scores = self.cross_encoder.predict(pairs)

        scored = list(zip(candidates, scores))
        scored.sort(key=lambda x: x[1], reverse=True)

        return [c for c, _ in scored]

    def _analyze_patterns(self, memories: List[MemoryEntry]) -> Dict:
        """分析记忆中的模式"""
        # 统计高频实体、时间分布、关系模式
        all_entities = []
        for m in memories:
            all_entities.extend(m.entities)

        from collections import Counter
        entity_freq = Counter(all_entities)

        return {
            'top_entities': entity_freq.most_common(5),
            'time_span': max(m.timestamp for m in memories) - min(m.timestamp for m in memories),
            'avg_importance': np.mean([m.importance for m in memories])
        }

    def _generate_insight(
        self,
        query: str,
        memories: List[MemoryEntry],
        patterns: Dict
    ) -> str:
        """生成洞察 (可接入LLM)"""
        # 简化实现：基于模式生成结构化洞察
        insight_parts = [
            f"基于{len(memories)}条相关记忆",
            f"最常出现的概念: {', '.join([e for e, _ in patterns['top_entities'][:3]])}",
            f"这些记忆的时间跨度: {patterns['time_span']:.1f}天",
        ]

        return "; ".join(insight_parts)
```

---

## 与Stock Platform集成

```python
# 量化分析Agent的记忆系统
class QuantAgentMemory(AgentMemory):
    """专为量化分析优化的记忆系统"""

    def retain_signal(self, signal_data: dict):
        """存储交易信号"""
        content = f"""
        股票: {signal_data['symbol']}
        信号: {signal_data['direction']} (强度: {signal_data['strength']})
        原因: {signal_data['reasoning']}
        结果: {signal_data.get('result', 'pending')}
        """
        return self.retain(content, metadata={
            'type': 'trade_signal',
            'symbol': signal_data['symbol'],
            'timestamp': signal_data['timestamp']
        })

    def recall_similar_market_conditions(
        self,
        current_conditions: dict,
        top_k: int = 5
    ) -> List[MemoryEntry]:
        """检索相似市场条件下的历史决策"""
        query = f"""
        市场状态: {current_conditions['regime']}
        VIX: {current_conditions.get('vix', 'N/A')}
        趋势: {current_conditions.get('trend', 'N/A')}
        """
        return self.recall(query, top_k)

    def reflect_on_strategy_performance(self, strategy_name: str) -> str:
        """反思策略表现，生成改进建议"""
        query = f"{strategy_name}策略的历史表现和失败案例"
        return self.reflect(query)
```

---

## 最佳实践

1. **定期反思**: 每天/每周让Agent自动reflect一次，生成洞察
2. **重要性过滤**: 低重要性记忆定期归档，避免噪音
3. **多Agent共享**: 可以通过共享entity_index实现多Agent知识共享
4. **版本控制**: 重大insight应该版本化，追踪Agent认知演进

---

## 与已有技能关联

- **Multi-Agent Framework**: 每个Agent可以有独立Memory，通过共享图谱连接
- **OODA决策**: Observe阶段调用recall，Orient阶段调用reflect
- **Kelly仓位**: retain交易结果，reflect优化仓位策略
