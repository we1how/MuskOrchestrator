# Skill: Fractional Kelly仓位管理

## 元信息
- **类型**: analysis
- **来源**: Quantitative Finance Research + Kelly Criterion
- **链接**: https://mcginniscommawill.com/posts/2026-01-16-fractional-kelly/
- **创建日期**: 2026-03-12
- **版本**: 1.0

---

## 触发条件

使用此技能当：
- 需要计算最优仓位大小
- 设计资金管理策略
- 评估风险收益比
- 多策略组合仓位分配

---

## 核心概念

### Kelly公式

最优仓位比例：

```
f* = (bp - q) / b

其中:
- f* = 最优仓位比例 (0-1)
- b = 平均盈利 / 平均亏损 (赔率)
- p = 胜率 (0-1)
- q = 1 - p = 败率
```

### Fractional Kelly

专业标准使用 **10-25%** 的完整Kelly比例：

```
实际仓位 = f* × fraction

fraction建议值:
- 0.10 (保守): 波动小，回撤控制严格
- 0.25 (平衡): 标准专业做法
- 0.50 (激进): 高风险承受能力
```

---

## Python实现

```python
import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass

@dataclass
class KellyResult:
    """Kelly计算结果"""
    kelly_fraction: float      # 完整Kelly比例
    recommended_fraction: float # 建议仓位比例
    expected_growth: float     # 预期增长率
    max_drawdown_estimate: float  # 预估最大回撤
    confidence: float          # 计算置信度

class FractionalKellySizer:
    """Fractional Kelly仓位管理器"""

    def __init__(
        self,
        fraction: float = 0.25,
        max_position: float = 0.30,
        min_position: float = 0.01
    ):
        """
        Args:
            fraction: Kelly比例 (0.1-0.5)
            max_position: 单个仓位上限
            min_position: 单个仓位下限
        """
        self.fraction = fraction
        self.max_position = max_position
        self.min_position = min_position

    def calculate_kelly(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        sample_size: Optional[int] = None
    ) -> KellyResult:
        """
        计算Kelly仓位

        Args:
            win_rate: 胜率 (0-1)
            avg_win: 平均盈利 (%)
            avg_loss: 平均亏损 (%)
            sample_size: 样本数（用于计算置信度）

        Returns:
            KellyResult
        """
        # 赔率
        b = avg_win / avg_loss if avg_loss > 0 else float('inf')

        # 完整Kelly公式
        kelly = (b * win_rate - (1 - win_rate)) / b

        # 边界处理
        if kelly <= 0:
            return KellyResult(
                kelly_fraction=0,
                recommended_fraction=0,
                expected_growth=0,
                max_drawdown_estimate=0,
                confidence=0
            )

        # Fractional Kelly
        recommended = kelly * self.fraction

        # 应用上下限
        recommended = min(recommended, self.max_position)
        recommended = max(recommended, self.min_position)

        # 预期对数增长率
        expected_growth = (
            win_rate * np.log(1 + kelly * avg_win) +
            (1 - win_rate) * np.log(1 - kelly * avg_loss)
        )

        # 预估最大回撤 (简化估算)
        max_dd = self._estimate_max_drawdown(win_rate, avg_win, avg_loss, kelly)

        # 置信度（基于样本量）
        confidence = min(1.0, np.sqrt(sample_size / 100)) if sample_size else 0.5

        return KellyResult(
            kelly_fraction=kelly,
            recommended_fraction=recommended,
            expected_growth=expected_growth,
            max_drawdown_estimate=max_dd,
            confidence=confidence
        )

    def _estimate_max_drawdown(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        kelly: float
    ) -> float:
        """估算最大回撤"""
        # 简化模型: 连续N次亏损后的回撤
        n_consecutive = int(1 / (1 - win_rate))
        dd_per_trade = kelly * avg_loss
        max_dd = 1 - (1 - dd_per_trade) ** n_consecutive
        return min(max_dd, 0.5)  # 上限50%

    def batch_optimize(
        self,
        strategies: list
    ) -> dict:
        """
        多策略仓位优化

        Args:
            strategies: [
                {'name': '策略A', 'win_rate': 0.6, 'avg_win': 0.05, 'avg_loss': 0.03},
                ...
            ]

        Returns:
            {策略名: KellyResult}
        """
        results = {}
        total_kelly = 0

        # 第一轮：计算各策略Kelly
        for s in strategies:
            result = self.calculate_kelly(
                win_rate=s['win_rate'],
                avg_win=s['avg_win'],
                avg_loss=s['avg_loss'],
                sample_size=s.get('sample_size', 50)
            )
            results[s['name']] = result
            total_kelly += result.recommended_fraction

        # 第二轮：归一化（如果总和超过100%）
        if total_kelly > 1.0:
            scale = 1.0 / total_kelly
            for name, result in results.items():
                result.recommended_fraction *= scale

        return results


# 使用示例
sizer = FractionalKellySizer(fraction=0.25)

# 单一策略
result = sizer.calculate_kelly(
    win_rate=0.55,
    avg_win=0.08,    # 8%盈利
    avg_loss=0.04,   # 4%亏损
    sample_size=100
)

print(f"完整Kelly: {result.kelly_fraction:.2%}")
print(f"建议仓位: {result.recommended_fraction:.2%}")
print(f"预期增长率: {result.expected_growth:.4f}")
print(f"预估最大回撤: {result.max_drawdown_estimate:.2%}")
```

---

## A股适配

```python
class AShareKellySizer(FractionalKellySizer):
    """A股适配的Kelly仓位管理器"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.t1_penalty = 0.95  # T+1限制惩罚系数
        self.limit_penalty = 0.90  # 涨跌停惩罚系数

    def calculate_position(
        self,
        signal_strength: float,  # 信号强度 (0-1)
        historical_trades: list,  # 历史交易记录
        market_regime: str = 'normal'  # 'bull'|'normal'|'bear'
    ) -> dict:
        """
        A股专用仓位计算

        Args:
            signal_strength: 当前信号强度
            historical_trades: [{'pnl': 0.05, 'exit_type': 'normal'}, ...]
            market_regime: 市场状态
        """
        # 计算历史胜率赔率
        wins = [t['pnl'] for t in historical_trades if t['pnl'] > 0]
        losses = [abs(t['pnl']) for t in historical_trades if t['pnl'] <= 0]

        win_rate = len(wins) / len(historical_trades) if historical_trades else 0.5
        avg_win = np.mean(wins) if wins else 0.03
        avg_loss = np.mean(losses) if losses else 0.02

        # 基础Kelly
        result = self.calculate_kelly(
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss,
            sample_size=len(historical_trades)
        )

        # A股特殊调整
        position = result.recommended_fraction

        # 信号强度调整
        position *= signal_strength

        # 市场环境调整
        regime_mult = {'bull': 1.2, 'normal': 1.0, 'bear': 0.7}
        position *= regime_mult.get(market_regime, 1.0)

        # T+1和涨跌停限制
        position *= self.t1_penalty * self.limit_penalty

        return {
            'base_kelly': result.kelly_fraction,
            'adjusted_position': min(position, self.max_position),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'factors': {
                'signal': signal_strength,
                'market_regime': regime_mult.get(market_regime, 1.0),
                't1_penalty': self.t1_penalty,
                'limit_penalty': self.limit_penalty
            }
        }
```

---

## 连续分布Kelly公式

对于连续收益分布：

```python
def continuous_kelly(
    returns: np.ndarray,
    risk_free_rate: float = 0.02
) -> float:
    """
    连续分布Kelly公式
    f* = (μ - r) / σ²

    Args:
        returns: 历史收益率数组
        risk_free_rate: 无风险利率

    Returns:
        最优仓位比例
    """
    mean_return = np.mean(returns)
    variance = np.var(returns)

    if variance == 0:
        return 0

    kelly = (mean_return - risk_free_rate) / variance
    return max(0, min(kelly, 1.0))  # 限制在0-1
```

---

## 风险提醒

⚠️ **Kelly公式的局限性**:

1. **估计误差敏感**: 胜率/赔率的估计误差会被放大
2. **样本量要求**: 需要足够的历史数据支撑
3. **尾部风险**: 假设收益分布稳定，无法应对黑天鹅
4. **相关性忽略**: 多策略时未考虑策略间相关性

⚠️ **建议使用原则**:
- 只用 Fractional Kelly (≤25%)
- 单仓位上限30%
- 定期重新估计参数
- 结合止损策略使用
