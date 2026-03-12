# Skill: 分歧加权仓位管理

## 元信息
- **类型**: analysis
- **来源**: Quantpedia - ML vs Trend分歧交易
- **链接**: https://quantpedia.com/can-we-profit-from-disagreements-between-machine-learning-and-trend-following-models/
- **创建日期**: 2026-03-13
- **版本**: 1.0

---

## 触发条件

使用此技能当：
- 多个模型/Agent对同一标的给出不同预测
- 需要基于预测分歧程度调整仓位
- 构建多策略融合系统

---

## 核心概念

### 模型分歧即信号

传统方法：取预测平均值 → 决策
分歧方法：**分歧程度本身就是交易信号**

```
分歧越大 → 不确定性越高 → 降低仓位
分歧越小且方向一致 → 置信度高 → 增加仓位
分歧但方向一致 → 趋势确认 → 标准仓位
```

### 核心公式

```python
# 1. 计算分歧
Signal_Strength = |ML_Prediction - Trend_Prediction|

# 2. 仓位调整
Position_Size = Base_Size × (1 + Signal_Strength × k)

# 3. 方向确定
Direction = sign(Consensus_Pred)

# 4. 分歧阈值
if Signal_Strength > Threshold:
    # 模型严重分歧，观望或小仓位
    Position_Size = Minimal_Size
elif Signal_Strength < Low_Threshold:
    # 模型高度一致，满仓
    Position_Size = Full_Size
```

---

## Python实现

```python
import numpy as np
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class ModelPrediction:
    """模型预测结果"""
    model_name: str
    direction: int  # 1: 做多, -1: 做空, 0: 观望
    confidence: float  # 0-1
    expected_return: float  # 预期收益

class DisagreementPositionSizer:
    """基于模型分歧的仓位管理器"""

    def __init__(
        self,
        base_size: float = 0.1,      # 基础仓位10%
        max_size: float = 0.3,       # 最大仓位30%
        min_size: float = 0.02,      # 最小仓位2%
        k: float = 2.0,              # 分歧敏感度系数
        high_threshold: float = 0.5, # 高分歧阈值
        low_threshold: float = 0.1   # 低分歧阈值
    ):
        self.base_size = base_size
        self.max_size = max_size
        self.min_size = min_size
        self.k = k
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold

    def calculate_position(
        self,
        predictions: List[ModelPrediction],
        current_price: float,
        volatility: float
    ) -> Dict:
        """
        基于模型分歧计算仓位

        Args:
            predictions: 各模型的预测结果
            current_price: 当前价格
            volatility: 波动率 (用于风险调整)

        Returns:
            {
                'direction': int,
                'position_size': float,
                'confidence': float,
                'disagreement_score': float,
                'rationale': str
            }
        """
        if not predictions:
            return {'direction': 0, 'position_size': 0, 'confidence': 0}

        # 1. 计算共识方向
        weighted_direction = sum(
            p.direction * p.confidence for p in predictions
        ) / sum(p.confidence for p in predictions)

        direction = np.sign(weighted_direction)
        if direction == 0:
            return {
                'direction': 0,
                'position_size': 0,
                'confidence': 0,
                'disagreement_score': 0,
                'rationale': '无明确方向共识'
            }

        # 2. 计算分歧度
        # 方法1: 预测方向的标准差
        directions = [p.direction * p.confidence for p in predictions]
        disagreement_std = np.std(directions)

        # 方法2: 预期收益的分歧
        returns = [p.expected_return for p in predictions]
        return_disagreement = np.std(returns) / (np.mean(np.abs(returns)) + 1e-6)

        # 综合分歧度 (0-1)
        disagreement_score = (disagreement_std + return_disagreement) / 2

        # 3. 基于分歧度计算仓位
        if disagreement_score > self.high_threshold:
            # 高分歧：最小仓位或观望
            position_size = self.min_size
            rationale = f"模型严重分歧({disagreement_score:.2f})，谨慎参与"

        elif disagreement_score < self.low_threshold:
            # 低分歧：满仓
            position_size = self.max_size
            rationale = f"模型高度一致({disagreement_score:.2f})，满仓参与"

        else:
            # 中等分歧：基于分歧度调整
            # 分歧越大，仓位越小
            adjustment = 1 - (disagreement_score - self.low_threshold) / \
                        (self.high_threshold - self.low_threshold)
            position_size = self.base_size + (self.max_size - self.base_size) * adjustment
            rationale = f"模型分歧适中({disagreement_score:.2f})，动态调整仓位"

        # 4. 波动率调整
        vol_adjustment = 0.2 / (volatility + 0.1)  # 波动越大，仓位越小
        position_size *= vol_adjustment

        # 5. 计算整体置信度
        avg_confidence = np.mean([p.confidence for p in predictions])
        consensus_strength = 1 - disagreement_score
        overall_confidence = avg_confidence * consensus_strength

        return {
            'direction': int(direction),
            'position_size': min(position_size, self.max_size),
            'confidence': overall_confidence,
            'disagreement_score': disagreement_score,
            'predictions_breakdown': [
                {'model': p.model_name, 'pred': p.direction, 'conf': p.confidence}
                for p in predictions
            ],
            'rationale': rationale
        }

    def batch_signals(
        self,
        universe_signals: Dict[str, List[ModelPrediction]],
        max_total_exposure: float = 1.0
    ) -> List[Dict]:
        """
        批量处理多个标的的信号，考虑组合风险

        Args:
            universe_signals: {symbol: [predictions]}
            max_total_exposure: 最大总敞口

        Returns:
            排序后的交易信号列表
        """
        signals = []

        for symbol, preds in universe_signals.items():
            signal = self.calculate_position(preds, 0, 0.2)
            if signal['direction'] != 0:
                signals.append({
                    'symbol': symbol,
                    **signal,
                    'score': signal['confidence'] * (1 - signal['disagreement_score'])
                })

        # 按综合评分排序
        signals.sort(key=lambda x: x['score'], reverse=True)

        # 根据总敞口限制截断
        total_exposure = 0
        selected = []
        for s in signals:
            if total_exposure + s['position_size'] <= max_total_exposure:
                selected.append(s)
                total_exposure += s['position_size']
            else:
                # 剩余仓位不足以支持该标的
                remaining = max_total_exposure - total_exposure
                if remaining >= self.min_size:
                    s['position_size'] = remaining
                    selected.append(s)
                break

        return selected


# 使用示例
sizer = DisagreementPositionSizer(
    base_size=0.1,
    max_size=0.25,
    k=2.0
)

# 多模型预测
predictions = [
    ModelPrediction('LSTM', 1, 0.8, 0.05),
    ModelPrediction('Transformer', 1, 0.75, 0.04),
    ModelPrediction('Trend_Following', -1, 0.6, -0.02),
    ModelPrediction('RL_Agent', 1, 0.7, 0.03)
]

result = sizer.calculate_position(predictions, 100.0, 0.15)
print(f"方向: {'做多' if result['direction'] == 1 else '做空'}")
print(f"仓位: {result['position_size']:.2%}")
print(f"分歧度: {result['disagreement_score']:.2f}")
print(f"置信度: {result['confidence']:.2f}")
print(f"理由: {result['rationale']}")
```

---

## A股适配

```python
class AShareDisagreementSizer(DisagreementPositionSizer):
    """A股适配的分歧仓位管理器"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.t1_constraint = 0.95  # T+1约束系数
        self.limit_constraint = 0.90  # 涨跌停约束

    def calculate_position(
        self,
        predictions: List[ModelPrediction],
        current_price: float,
        volatility: float,
        market_regime: str = 'normal'
    ) -> Dict:
        """A股专用仓位计算"""

        # 基础计算
        result = super().calculate_position(predictions, current_price, volatility)

        # A股特殊调整
        position = result['position_size']

        # 市场环境调整
        regime_mult = {'bull': 1.2, 'normal': 1.0, 'bear': 0.7}
        position *= regime_mult.get(market_regime, 1.0)

        # T+1和涨跌停限制
        position *= self.t1_constraint * self.limit_constraint

        result['position_size'] = min(position, self.max_size)
        result['factors'] = {
            'market_regime': regime_mult.get(market_regime, 1.0),
            't1_constraint': self.t1_constraint,
            'limit_constraint': self.limit_constraint
        }

        return result
```

---

## 与已有技能关联

- **Fractional Kelly**: 分歧仓位可以作为Kelly公式的输入参数
- **Multi-Agent Framework**: 多Agent信号融合后使用分歧仓位
- **Crisis Hedge**: 高分歧时自动触发危机对冲

---

## 关键洞察

1. **分歧即信息**: 模型分歧不是噪声，而是有价值的风险信号
2. **动态调整**: 仓位应随分歧度动态变化，而非固定比例
3. **方向优先**: 分歧再大，方向一致仍可参与（小仓位）
4. **波动率联动**: 高分歧+高波动=最小仓位或观望
