# AI工程评估方法论

## 核心理念

> 写出来不难，知道它什么时候错、为什么错、怎么防止下次错，才值钱。

AI系统的评估是区分"demo级"和"生产级"的关键能力。本指南覆盖四个核心维度。

---

## 1. 评估数据集设计原则

### 1.1 数据集结构

```
评估数据集
├── 功能测试 (Functional Tests)
│   ├── 正常路径 (Happy Path)
│   ├── 边界条件 (Edge Cases)
│   └── 异常输入 (Error Cases)
├── 质量测试 (Quality Tests)
│   ├── 准确性 (Accuracy)
│   ├── 一致性 (Consistency)
│   └── 安全性 (Safety)
└── 性能测试 (Performance Tests)
    ├── 延迟 (Latency)
    ├── 吞吐量 (Throughput)
    └── 成本 (Cost)
```

### 1.2 设计原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **代表性** | 覆盖真实用户场景 | 客服机器人：包含退款、查询、投诉等典型场景 |
| **可衡量** | 每个用例有明确的通过/失败标准 | "回答包含订单号" vs "回答有帮助" |
| **可复现** | 相同输入应产生可预测的输出 | 使用固定种子、确定性参数 |
| **分层** | 从简单到复杂逐步覆盖 | 先测单轮，再测多轮，最后测工具调用 |
| **持续更新** | 随产品迭代补充新用例 | 每次bug修复后添加回归测试 |

### 1.3 数据集格式示例

```json
{
  "test_cases": [
    {
      "id": "qa-001",
      "category": "问答",
      "input": "什么是机器学习？",
      "expected": {
        "keywords": ["算法", "数据", "学习"],
        "min_length": 50,
        "forbidden": ["不知道", "无法回答"],
        "semantic_check": "解释机器学习的基本概念"
      },
      "metadata": {
        "difficulty": "easy",
        "priority": "high"
      }
    }
  ]
}
```

### 1.4 评估维度

**硬指标（自动评估）：**
- 关键词命中率
- 格式正确性（JSON、Markdown等）
- 响应长度
- API调用成功率

**软指标（需要人工或LLM判断）：**
- 回答准确性
- 语言流畅度
- 有害内容检测
- 指令遵循度

---

## 2. LLM-as-Judge 方法

### 2.1 基本原理

用一个更强的LLM来评估另一个LLM的输出质量。适用于难以用规则判断的场景。

### 2.2 评估Prompt模板

```python
JUDGE_PROMPT = """你是一个专业的AI输出质量评估员。

## 评估任务
用户问题: {question}
AI回答: {answer}

## 评估标准
1. 准确性 (0-5分): 回答是否事实正确？
2. 完整性 (0-5分): 是否覆盖了问题的所有方面？
3. 清晰度 (0-5分): 表达是否清晰易懂？
4. 相关性 (0-5分): 是否紧扣问题，没有跑题？

## 输出格式
请以JSON格式输出评估结果:
{
  "accuracy": {"score": X, "reason": "..."},
  "completeness": {"score": X, "reason": "..."},
  "clarity": {"score": X, "reason": "..."},
  "relevance": {"score": X, "reason": "..."},
  "overall_score": X,
  "pass": true/false
}
"""
```

### 2.3 实现示例

```python
import anthropic
import json

client = anthropic.Anthropic()

def llm_judge(question: str, answer: str) -> dict:
    """使用Claude评估回答质量。"""

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": JUDGE_PROMPT.format(
                question=question,
                answer=answer
            )
        }]
    )

    result_text = response.content[0].text
    return json.loads(result_text)
```

### 2.4 LLM-as-Judge的局限性

| 局限 | 解决方案 |
|------|----------|
| 评估者自身可能出错 | 多次评估取平均，或用多个模型交叉验证 |
| 成本较高 | 只对高优先级用例使用，低优先级用规则评估 |
| 可能有偏见 | 设计明确的评分标准，减少主观判断 |
| 无法评估事实正确性 | 结合知识库检索进行事实核查 |

### 2.5 最佳实践

1. **明确评分标准**：给Judge清晰的rubric，不要让它自己判断
2. **使用结构化输出**：要求JSON格式，便于自动化处理
3. **设置通过阈值**：如overall_score >= 3.5为通过
4. **人工抽检**：定期抽查Judge的评估结果，校准评分
5. **记录评估历史**：用于分析Judge自身的准确性

---

## 3. 回归测试策略

### 3.1 什么是AI回归测试

当修改prompt、模型、参数或工具后，确保现有功能没有退化。

### 3.2 回归测试触发时机

```
代码变更
├── Prompt修改 → 必须运行回归测试
├── 模型升级 → 必须运行回归测试
├── 参数调整 → 建议运行回归测试
├── 工具变更 → 必须运行回归测试
└── 依赖更新 → 建议运行回归测试
```

### 3.3 实现方案

```python
class RegressionTestSuite:
    """AI系统回归测试套件。"""

    def __init__(self, dataset_path: str):
        self.test_cases = self.load_dataset(dataset_path)
        self.results = []

    def run(self, agent_fn, baseline_path: str = None):
        """运行回归测试，可选对比基线。"""

        baseline = self.load_baseline(baseline_path) if baseline_path else {}

        for case in self.test_cases:
            current = agent_fn(case["input"])
            result = self.evaluate(current, case["expected"])

            # 对比基线
            if case["id"] in baseline:
                previous = baseline[case["id"]]
                result["regression"] = self.detect_regression(
                    current, previous, case
                )

            self.results.append(result)

        return self.generate_report()

    def detect_regression(self, current, previous, case) -> dict:
        """检测是否出现回归。"""

        regressions = []

        # 检查通过状态变化
        if previous["passed"] and not current["passed"]:
            regressions.append("从通过变为失败")

        # 检查分数下降
        score_drop = previous["score"] - current["score"]
        if score_drop > 0.2:  # 阈值
            regressions.append(f"分数下降 {score_drop:.2f}")

        # 检查延迟增加
        latency_increase = current["latency_ms"] - previous["latency_ms"]
        if latency_increase > 1000:  # 超过1秒
            regressions.append(f"延迟增加 {latency_increase:.0f}ms")

        return {
            "has_regression": len(regressions) > 0,
            "details": regressions
        }
```

### 3.4 CI/CD集成

```yaml
# .github/workflows/ai-regression.yml
name: AI Regression Tests

on:
  pull_request:
    paths:
      - 'prompts/**'
      - 'config/**'
      - 'tools/**'

jobs:
  regression:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run regression tests
        run: python -m evaluation.regression --fail-on-regression

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: regression-results
          path: evaluation/results/
```

---

## 4. Trace分析方法

### 4.1 什么是Trace

Trace记录了AI系统执行的完整过程，包括：
- 输入输出
- 中间推理步骤
- 工具调用
- Token使用
- 延迟分布

### 4.2 Trace数据结构

```python
@dataclass
class Trace:
    """单次执行的完整追踪。"""

    trace_id: str
    timestamp: datetime
    input: str
    output: str

    # 执行细节
    steps: list[Step]
    tool_calls: list[ToolCall]
    errors: list[Error]

    # 性能指标
    total_latency_ms: float
    llm_latency_ms: float
    tool_latency_ms: float

    # 资源消耗
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int
    cost_usd: float
```

### 4.3 常见问题诊断

| 症状 | 可能原因 | 排查方法 |
|------|----------|----------|
| 回答质量下降 | Prompt被污染、模型变更 | 对比新旧trace的prompt内容 |
| 延迟增加 | 工具调用变多、模型变慢 | 分析各步骤耗时分布 |
| 成本飙升 | Token用量增加、缓存失效 | 检查cache命中率和token统计 |
| 工具调用失败 | 工具定义变更、权限问题 | 查看tool_call的错误信息 |
| 无限循环 | 没有终止条件、工具返回异常 | 检查循环次数和停止条件 |

### 4.4 Trace分析工具

**LangSmith（推荐）**
- 可视化trace时间线
- 自动统计token和成本
- 支持A/B测试对比
- 集成LangChain/LangGraph

**Anthropic Console**
- 官方API调用记录
- 查看原始请求响应
- Token使用统计

**自建方案**
```python
import json
from datetime import datetime

class TraceCollector:
    """简易trace收集器。"""

    def __init__(self, output_dir: str = "./traces"):
        self.output_dir = output_dir
        self.current_trace = None

    def start_trace(self, trace_id: str, input_data: str):
        self.current_trace = {
            "trace_id": trace_id,
            "timestamp": datetime.now().isoformat(),
            "input": input_data,
            "steps": [],
            "errors": []
        }

    def add_step(self, step_type: str, data: dict):
        self.current_trace["steps"].append({
            "type": step_type,
            "timestamp": datetime.now().isoformat(),
            **data
        })

    def end_trace(self, output: str, metrics: dict):
        self.current_trace["output"] = output
        self.current_trace["metrics"] = metrics

        # 保存到文件
        path = f"{self.output_dir}/{self.current_trace['trace_id']}.json"
        with open(path, "w") as f:
            json.dump(self.current_trace, f, indent=2, ensure_ascii=False)
```

### 4.5 失败案例归因流程

```
发现失败案例
    ↓
查看完整trace
    ↓
定位失败环节
├── Prompt问题 → 修改prompt
├── 模型能力不足 → 升级模型或拆分任务
├── 工具调用失败 → 修复工具或添加fallback
├── 输入异常 → 添加输入校验
└── 随机性问题 → 调整temperature或添加重试
    ↓
添加到回归测试集
    ↓
验证修复效果
```

---

## 学习资源

### 官方文档
- [Anthropic Evaluations Guide](https://docs.anthropic.com/claude/docs/evaluations)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [OpenAI Evals Framework](https://github.com/openai/evals)

### 推荐阅读
- [Building LLM Applications for Production](https://huyenchip.com/2023/04/11/llm-engineering.html)
- [Evaluating LLM Applications](https://www.anthropic.com/research/evaluating-llm-applications)
- [The Art of AI Evaluation](https://simonwillison.net/2024/Oct/7/ai-evaluation/)

### 实践项目
1. 为你之前构建的Claude API应用设计评估数据集
2. 实现一个LLM-as-Judge评估器
3. 搭建回归测试pipeline
4. 使用LangSmith分析trace
