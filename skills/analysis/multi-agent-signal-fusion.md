# Multi-Agent Signal Fusion（多Agent信号融合）

**类型**: analysis
**来源**: 多Agent交易系统论文深化 (2026-03-10)
**创建日期**: 2026-03-10
**最后验证**: 2026-03-10
**有效性**: ⭐⭐⭐⭐⭐
**使用次数**: 0

---

## 触发条件

- 多维度量化策略需要综合多个信号源
- 不同Agent/模型给出不同判断
- 需要可解释的加权决策机制

---

## 执行步骤

1. **信号标准化**
   - 所有信号映射到统一尺度：`{prediction: -1/0/1, confidence: 0-1}`
   - 归一化处理消除价格偏见

2. **动态权重计算**
   ```python
   weight_i = f(历史准确率, 当前市场环境, 信号时效性)
   ```

3. **加权融合**
   ```
   final_signal = Σ(agent_i.signal × agent_i.confidence × weight_i)
   ```

4. **分层过滤**（可选）
   - Layer 1: 信号提取（Technical/Fundamental/Macro）
   - Layer 2: 校准对齐（行业对标、宏观调整）
   - Layer 3: 综合决策（权重分配）

---

## 代码/模板

```python
# 归一化指标计算（消除价格偏见）
def normalized_macd(close, fast=12, slow=26):
    """归一化MACD = MACD / Close"""
    ema12 = close.ewm(span=fast).mean()
    ema26 = close.ewm(span=slow).mean()
    macd = ema12 - ema26
    return macd / close

def bollinger_zscore(close, window=20):
    """Bollinger Z-Score = (Price - MA) / Std"""
    ma = close.rolling(window=window).mean()
    std = close.rolling(window=window).std()
    return (close - ma) / std

# 多Agent信号融合
def fuse_signals(signals: List[Signal], weights: List[float]) -> Signal:
    """
    signals: [{value: -1/0/1, confidence: 0-1, source: str}]
    weights: 与signals对应的权重列表
    """
    total_weight = sum(weights)
    weighted_sum = sum(
        s['value'] * s['confidence'] * w
        for s, w in zip(signals, weights)
    )

    final_value = np.sign(weighted_sum)
    final_confidence = abs(weighted_sum) / total_weight

    return Signal(
        value=final_value,
        confidence=final_confidence,
        breakdown=[...]  # 各Agent贡献详情
    )
```

---

## 验证结果

- [ ] 待验证：应用于超跌反弹策略优化

---

## A股应用场景

1. **超跌反弹策略增强**
   - 超跌信号 + 基本面过滤 + 宏观择时
   - 分层过滤避免价值陷阱

2. **动态阈值调整**
   - 根据VIX替代指标动态调整跌幅阈值
   - 恐慌期：阈值30% | 平稳期：阈值50%

---

## 关键公式摘要

| 指标 | 公式 | 用途 |
|------|------|------|
| 归一化MACD | (EMA₁₂ - EMA₂₆) / Pₜ | 跨标的比较 |
| Bollinger Z-Score | (P - MA₂₀) / Std₂₀ | 均值回归判断 |
| 多周期RoC | [ROC₅, ROC₁₀, ROC₂₀...] | 多时间维度动量 |
