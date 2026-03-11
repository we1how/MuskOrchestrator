# Skill: A股多Agent量化交易框架

## 元信息
- **类型**: analysis
- **来源**: Arxiv q-fin论文整合 (2602.23330, 2603.03671)
- **创建日期**: 2026-03-11
- **版本**: 1.0

---

## 触发条件

使用此技能当：
- 设计A股量化交易策略
- 需要多维度信号融合决策
- 评估策略拥挤度和市场微观结构
- 构建分层决策系统

---

## 核心公式

### 1. 归一化MACD (消除价格偏见)

```python
import pandas as pd
import numpy as np

def normalized_macd(close: pd.Series, fast=12, slow=26, signal=9) -> pd.DataFrame:
    """
    归一化MACD - 使不同价格股票可比

    普通MACD无法比较茅台(1500元)和小票(10元)
    归一化后: nMACD = MACD / Close (表示百分比变化)
    """
    ema_fast = close.ewm(span=fast).mean()
    ema_slow = close.ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    histogram = macd_line - signal_line

    # 归一化：除以收盘价
    n_macd = macd_line / close
    n_signal = signal_line / close
    n_histogram = histogram / close

    return pd.DataFrame({
        'n_macd': n_macd,
        'n_signal': n_signal,
        'n_histogram': n_histogram
    })
```

### 2. Bollinger Z-Score

```python
def bollinger_z_score(close: pd.Series, window=20, num_std=2) -> pd.Series:
    """
    Bollinger Z-Score - 标准化价格位置

    Z > 2: 超买信号
    Z < -2: 超卖信号
    """
    rolling_mean = close.rolling(window).mean()
    rolling_std = close.rolling(window).std()
    z_score = (close - rolling_mean) / rolling_std

    return z_score
```

### 3. 多Agent信号融合

```python
def multi_agent_signal_fusion(signals: dict, weights: dict, confidences: dict) -> dict:
    """
    多Agent信号融合模型

    Args:
        signals: {agent_name: signal} signal ∈ {-1, 0, 1}
        weights: {agent_name: weight} 基于历史准确率
        confidences: {agent_name: confidence} Agent置信度

    Returns:
        {
            'final_signal': float,  # -1.0 ~ 1.0
            'direction': str,       # 'buy'/'hold'/'sell'
            'confidence': float,    # 0.0 ~ 1.0
            'breakdown': dict       # 各Agent贡献
        }
    """
    total_weight = 0
    weighted_sum = 0

    breakdown = {}

    for agent, signal in signals.items():
        w = weights.get(agent, 1.0)
        c = confidences.get(agent, 1.0)
        effective_weight = w * c

        weighted_sum += signal * effective_weight
        total_weight += effective_weight

        breakdown[agent] = {
            'signal': signal,
            'weight': w,
            'confidence': c,
            'contribution': signal * effective_weight
        }

    final_signal = weighted_sum / total_weight if total_weight > 0 else 0

    # 方向判断
    if final_signal > 0.3:
        direction = 'buy'
    elif final_signal < -0.3:
        direction = 'sell'
    else:
        direction = 'hold'

    # 整体置信度
    avg_confidence = np.mean(list(confidences.values()))

    return {
        'final_signal': final_signal,
        'direction': direction,
        'confidence': avg_confidence,
        'breakdown': breakdown
    }

# 使用示例
signals = {
    'technical': 1,      # 技术Agent: 看多
    'fundamental': 0,    # 基本面Agent: 中性
    'macro': 1,          # 宏观Agent: 看多
    'sentiment': -1      # 情绪Agent: 看空
}

weights = {
    'technical': 0.3,
    'fundamental': 0.3,
    'macro': 0.2,
    'sentiment': 0.2
}

confidences = {
    'technical': 0.8,
    'fundamental': 0.7,
    'macro': 0.6,
    'sentiment': 0.5
}

result = multi_agent_signal_fusion(signals, weights, confidences)
print(f"方向: {result['direction']}, 信号强度: {result['final_signal']:.2f}")
```

---

## 分层决策架构

```
┌─────────────────────────────────────────────┐
│  Level 3: PM层 (组合管理)                     │
│  - 权重分配                                  │
│  - 仓位控制                                  │
│  - 最终决策                                  │
└─────────────────────────────────────────────┘
                    ↑
┌─────────────────────────────────────────────┐
│  Level 2: 校准层 (Context校准)               │
│  - 行业对标                                  │
│  - 宏观环境校准                              │
│  - 信号权重调整                              │
└─────────────────────────────────────────────┘
                    ↑
┌─────────────────────────────────────────────┐
│  Level 1: 分析师层 (信号提取)                 │
│  - 技术指标计算                              │
│  - 基本面分析                                │
│  - 噪声过滤                                  │
└─────────────────────────────────────────────┘
```

```python
class LayeredDecisionSystem:
    """分层决策系统"""

    def __init__(self):
        self.level1_extractors = {
            'technical': self._extract_technical_signals,
            'fundamental': self._extract_fundamental_signals,
            'macro': self._extract_macro_signals
        }

    def _extract_technical_signals(self, data: pd.DataFrame) -> dict:
        """Level 1: 技术指标信号提取"""
        close = data['close']

        # 计算归一化MACD
        n_macd_df = normalized_macd(close)
        macd_signal = 1 if n_macd_df['n_macd'].iloc[-1] > n_macd_df['n_signal'].iloc[-1] else -1

        # 计算Bollinger Z-Score
        z_score = bollinger_z_score(close)
        z_signal = -1 if z_score.iloc[-1] < -2 else (1 if z_score.iloc[-1] > 2 else 0)

        return {
            'macd': macd_signal,
            'bollinger': z_signal,
            'confidence': 0.8
        }

    def _extract_fundamental_signals(self, data: dict) -> dict:
        """Level 1: 基本面信号提取"""
        # PE、PB、ROE等指标分析
        pe = data.get('pe_ratio', 0)

        # 简单的估值信号
        if pe < 10:
            signal = 1  # 低估
        elif pe > 30:
            signal = -1  # 高估
        else:
            signal = 0

        return {'valuation': signal, 'confidence': 0.7}

    def _extract_macro_signals(self, data: dict) -> dict:
        """Level 1: 宏观信号提取"""
        # 市场情绪、流动性等
        vix = data.get('vix', 20)

        if vix > 30:  # 恐慌
            signal = 1  # 逆向买入
        elif vix < 15:  # 贪婪
            signal = -1
        else:
            signal = 0

        return {'sentiment': signal, 'confidence': 0.6}

    def level2_calibrate(self, signals: dict, context: dict) -> dict:
        """Level 2: 信号校准"""
        # 根据市场环境调整权重
        market_state = context.get('market_state', 'neutral')

        if market_state == 'trending':
            # 趋势市场：技术信号权重增加
            adjusted = {k: v * 1.2 if k == 'technical' else v * 0.9
                       for k, v in signals.items()}
        elif market_state == 'ranging':
            # 震荡市场：基本面信号权重增加
            adjusted = {k: v * 1.2 if k == 'fundamental' else v * 0.9
                       for k, v in signals.items()}
        else:
            adjusted = signals

        return adjusted

    def level3_decide(self, calibrated_signals: dict, portfolio: dict) -> dict:
        """Level 3: 最终决策"""
        # 信号融合
        final = multi_agent_signal_fusion(
            calibrated_signals,
            weights={'technical': 0.4, 'fundamental': 0.35, 'macro': 0.25},
            confidences={'technical': 0.8, 'fundamental': 0.7, 'macro': 0.6}
        )

        # 仓位控制（根据置信度）
        position_size = min(final['confidence'], 0.3)  # 最大30%仓位

        return {
            'action': final['direction'],
            'size': position_size,
            'confidence': final['confidence'],
            'reason': final['breakdown']
        }
```

---

## 超跌反弹策略

```python
class OversoldReboundStrategy:
    """
    超跌反弹策略 - 均值回归

    理论基础: Fama & French (1988) 均值回归 + 行为金融学
    """

    def __init__(self):
        self.drop_threshold = 0.40  # 40%跌幅
        self.profit_ratio_threshold = 0.10  # 获利比例<10%
        self.rebound_trigger = 0.125  # 反弹12.5%触发买入

    def calculate_drawdown(self, close: pd.Series) -> float:
        """计算当前回撤"""
        peak = close.rolling(window=252, min_periods=1).max()
        drawdown = (close - peak) / peak
        return drawdown.iloc[-1]

    def calculate_profit_ratio(self, close: pd.Series, window=60) -> float:
        """
        估算获利比例（简化版）
        实际应使用筹码分布数据
        """
        avg_cost = close.rolling(window).mean()
        profit_ratio = (close > avg_cost).rolling(window).mean()
        return profit_ratio.iloc[-1]

    def detect_oversold(self, data: pd.DataFrame) -> dict:
        """检测超跌信号"""
        close = data['close']

        drawdown = self.calculate_drawdown(close)
        profit_ratio = self.calculate_profit_ratio(close)

        # 反弹检测
        recent_return = (close.iloc[-1] - close.iloc[-5]) / close.iloc[-5]

        is_oversold = (
            drawdown <= -self.drop_threshold and
            profit_ratio <= self.profit_ratio_threshold
        )

        rebound_signal = recent_return >= self.rebound_trigger

        return {
            'is_oversold': is_oversold,
            'rebound_triggered': rebound_signal,
            'drawdown': drawdown,
            'profit_ratio': profit_ratio,
            'recent_return': recent_return,
            'signal': 1 if (is_oversold and rebound_signal) else 0
        }
```

---

## 策略拥挤度监控

```python
class StrategyCrowdingMonitor:
    """
    策略拥挤度监控 - 基于arXiv:2603.03671

    关键发现:
    - 基本面策略拥挤 → 收益下降
    - 技术策略拥挤 → 收益上升（A股特点）
    """

    def calculate_factor_crowding(self, factor_values: pd.Series,
                                   window=60) -> dict:
        """
        计算因子拥挤度

        指标:
        1. 因子波动率（收益率标准差）
        2. 因子换手率
        3. 因子估值分位
        """
        # 因子收益率
        factor_return = factor_values.pct_change()

        # 拥挤度指标
        volatility = factor_return.rolling(window).std()
        turnover = factor_values.diff().abs().rolling(window).mean()

        # 综合拥挤度评分 (0-1)
        vol_score = (volatility.iloc[-1] - volatility.min()) / (volatility.max() - volatility.min())
        turnover_score = min(turnover.iloc[-1] / turnover.mean(), 1.0)

        crowding_score = (vol_score + turnover_score) / 2

        return {
            'crowding_score': crowding_score,
            'volatility': volatility.iloc[-1],
            'turnover': turnover.iloc[-1],
            'is_crowded': crowding_score > 0.7
        }

    def adjust_weights_by_crowding(self, signals: dict,
                                    crowding_data: dict) -> dict:
        """根据拥挤度动态调整权重"""
        adjusted = signals.copy()

        for factor, data in crowding_data.items():
            if data['is_crowded']:
                if factor in ['value', 'quality']:  # 基本面因子
                    # 拥挤时降低权重
                    adjusted[factor] *= 0.7
                elif factor in ['momentum', 'technical']:  # 技术因子
                    # A股特点：技术因子拥挤时可能更有效
                    adjusted[factor] *= 1.2

        return adjusted
```

---

## A股特殊考虑

### 1. 散户效应
- A股散户占比高，情绪驱动明显
- 技术策略在A股可能更有效（与论文一致）

### 2. 涨跌停限制
- 需考虑10%/20%涨跌停对策略的影响
- 流动性突变风险

### 3. T+1交易制度
- 不能日内回转
- 策略需考虑持仓隔夜风险

### 4. 动态阈值调整

```python
def dynamic_threshold_adjustment(market_regime: str) -> dict:
    """
    根据市场状态动态调整阈值

    Args:
        market_regime: 'panic', 'normal', 'euphoria'
    """
    thresholds = {
        'panic': {
            'oversold_drawdown': 0.30,  # 恐慌期30%即算超跌
            'position_size_max': 0.20   # 降低仓位
        },
        'normal': {
            'oversold_drawdown': 0.40,
            'position_size_max': 0.30
        },
        'euphoria': {
            'oversold_drawdown': 0.50,  # 乐观期需要更深跌幅
            'position_size_max': 0.15   # 控制追涨风险
        }
    }

    return thresholds.get(market_regime, thresholds['normal'])
```

---

## 执行清单

使用此框架时：

1. [ ] 确定信号维度（技术/基本面/宏观/情绪）
2. [ ] 实现归一化指标（消除价格偏见）
3. [ ] 设置分层决策流程
4. [ ] 加入策略拥挤度监控
5. [ ] 根据A股特点调整参数
6. [ ] 回测验证并迭代
