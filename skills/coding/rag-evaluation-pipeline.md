# Skill: RAG评估流水线

## 元信息
- **类型**: coding
- **来源**: Promptfoo (GitHub 25k+ stars)
- **链接**: https://github.com/promptfoo/promptfoo
- **创建日期**: 2026-03-12
- **版本**: 1.0

---

## 触发条件

使用此技能当：
- 部署或修改RAG系统前需要质量验证
- 需要量化评估检索和生成质量
- 生产环境RAG系统需要持续监控
- 比较不同RAG配置的效果

---

## 核心概念

RAG评估三大支柱：

| 评估维度 | 说明 | 关键指标 |
|----------|------|----------|
| **Context Faithfulness** | 答案是否基于检索的上下文 | 事实一致性 |
| **Answer Relevance** | 答案是否切题 | 相关性评分 |
| **Retrieval Quality** | 检索的文档是否相关 | 召回率、精确率 |

---

## 安装

```bash
npm install -g promptfoo
# 或
npx promptfoo@latest
```

---

## 配置文件

### 基础配置 (promptfooconfig.yaml)

```yaml
# 提示词模板
prompts:
  - "基于以下上下文回答问题：\n{{context}}\n\n问题：{{question}}"
  - "请根据提供的资料回答：\n{{context}}\n\n用户问题：{{question}}"

#  providers
providers:
  - openai:gpt-4
  - anthropic:claude-3-sonnet
  - azure:chat:my-deployment

# 测试用例
tests:
  - vars:
      question: "苹果公司最新财报营收是多少？"
      context: "{{fetch_context 'AAPL Q4 2024'}}"
    assert:
      - type: context-faithfulness
        threshold: 0.9
      - type: factuality
        value: "苹果Q4 2024营收896亿美元"
      - type: answer-relevance
        threshold: 0.8

  - vars:
      question: "特斯拉的CEO是谁？"
      context: "{{fetch_context 'Tesla leadership'}}"
    assert:
      - type: contains
        value: "Elon Musk"
      - type: contains
        value: "埃隆·马斯克"
```

---

## Python集成

```python
import promptfoo
from typing import List, Dict

def evaluate_rag_pipeline(
    questions: List[str],
    contexts: List[str],
    expected_answers: List[str]
) -> Dict:
    """
    评估RAG流水线质量

    Args:
        questions: 测试问题列表
        contexts: 检索到的上下文列表
        expected_answers: 期望答案列表

    Returns:
        {
            'faithfulness': float,  # 事实一致性
            'relevance': float,     # 答案相关性
            'retrieval_score': float,  # 检索质量
            'details': List[Dict]   # 详细结果
        }
    """
    results = []

    for q, ctx, expected in zip(questions, contexts, expected_answers):
        # 调用RAG生成答案
        generated_answer = your_rag_system.query(q, ctx)

        # 评估指标
        faithfulness = promptfoo.metrics.faithfulness(
            generated_answer, ctx
        )

        relevance = promptfoo.metrics.relevance(
            generated_answer, q
        )

        factuality = promptfoo.metrics.factuality(
            generated_answer, expected
        )

        results.append({
            'question': q,
            'faithfulness': faithfulness,
            'relevance': relevance,
            'factuality': factuality,
            'score': (faithfulness + relevance + factuality) / 3
        })

    # 汇总
    avg_faithfulness = sum(r['faithfulness'] for r in results) / len(results)
    avg_relevance = sum(r['relevance'] for r in results) / len(results)
    avg_retrieval = sum(r['factuality'] for r in results) / len(results)

    return {
        'faithfulness': avg_faithfulness,
        'relevance': avg_relevance,
        'retrieval_score': avg_retrieval,
        'overall': (avg_faithfulness + avg_relevance + avg_retrieval) / 3,
        'details': results
    }

# 使用示例
test_cases = [
    {
        'question': '苹果公司最新财报营收是多少？',
        'context': '苹果2024财年第四季度营收896亿美元...',
        'expected': '苹果Q4 2024营收896亿美元'
    }
]

results = evaluate_rag_pipeline(
    [t['question'] for t in test_cases],
    [t['context'] for t in test_cases],
    [t['expected'] for t in test_cases]
)

print(f"事实一致性: {results['faithfulness']:.2f}")
print(f"答案相关性: {results['relevance']:.2f}")
print(f"整体评分: {results['overall']:.2f}")
```

---

## CI/CD集成

```yaml
# .github/workflows/rag-eval.yml
name: RAG Evaluation

on: [push, pull_request]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install Promptfoo
        run: npm install -g promptfoo

      - name: Run RAG Evaluation
        run: promptfoo eval --config promptfooconfig.yaml
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      - name: Check Thresholds
        run: |
          # 确保关键指标达到阈值
          promptfoo eval --config promptfooconfig.yaml --threshold faithfulness:0.85,relevance:0.80
```

---

## 自定义评估指标

```python
import promptfoo
from typing import Callable

def custom_factuality_scorer(
    generated: str,
    reference: str
) -> float:
    """
    自定义事实性评分器
    针对金融领域的精确数字匹配
    """
    import re

    # 提取数字
    gen_numbers = set(re.findall(r'\d+\.?\d*', generated))
    ref_numbers = set(re.findall(r'\d+\.?\d*', reference))

    if not ref_numbers:
        return 1.0

    # 计算数字匹配率
    matches = len(gen_numbers & ref_numbers)
    return matches / len(ref_numbers)

# 注册自定义 scorer
promptfoo.register_metric('financial_factuality', custom_factuality_scorer)
```

---

## 评估检查清单

RAG系统上线前检查：

- [ ] 准备至少50个测试用例（覆盖常见问题和边界情况）
- [ ] 事实一致性(faithfulness) > 0.85
- [ ] 答案相关性(relevance) > 0.80
- [ ] 检索准确率(retrieval precision) > 0.75
- [ ] 在CI中集成自动化评估
- [ ] 设置监控告警（评分下降时通知）

---

## 与Stock Platform集成

```python
# Stock Platform RAG评估模块
def evaluate_report_generation(
    stock_code: str,
    quarter: str
):
    """评估研报生成质量"""

    # 1. 获取真实财报数据（ground truth）
    ground_truth = fetch_financial_data(stock_code, quarter)

    # 2. 生成研报
    report = generate_research_report(stock_code, quarter)

    # 3. 提取关键事实进行评估
    test_cases = [
        {
            'question': f'{stock_code} {quarter}营收是多少？',
            'generated': report.revenue_section,
            'expected': f'{ground_truth.revenue}亿元'
        },
        {
            'question': f'{stock_code} {quarter}净利润增长率？',
            'generated': report.profit_section,
            'expected': f'{ground_truth.profit_growth}%'
        }
    ]

    # 4. 运行评估
    results = evaluate_rag_pipeline(
        [t['question'] for t in test_cases],
        [report.context for _ in test_cases],
        [t['expected'] for t in test_cases]
    )

    return results
```

---

## 最佳实践

1. **持续监控**: 生产环境定期抽样评估，不要只测一次
2. **对抗测试**: 包含故意误导性的问题，测试系统鲁棒性
3. **版本对比**: 每次RAG配置变更都要对比评估结果
4. **人工标注**: 关键测试用例需要人工验证ground truth
