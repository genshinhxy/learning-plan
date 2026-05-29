"""评估运行器：自动化评估 Claude API 响应质量。"""

import json
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import ClaudeClient
from metrics import EvalResult, evaluate_response, generate_summary


def load_dataset(path: str = None) -> dict:
    """加载评估数据集。"""
    if path is None:
        path = Path(__file__).parent / "eval_dataset.json"

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_single_test(client: ClaudeClient, test_case: dict) -> EvalResult:
    """运行单个测试用例。"""

    test_id = test_case["id"]
    category = test_case["category"]
    user_input = test_case["input"]
    expected_keywords = test_case.get("expected_keywords", [])

    print(f"\n[{test_id}] {category}: {user_input[:50]}...")

    start_time = time.time()

    try:
        response = client.send(user_input)
        latency_ms = (time.time() - start_time) * 1000

        passed, score, notes = evaluate_response(response, expected_keywords)

        status = "✓" if passed else "✗"
        print(f"  {status} 分数: {score:.2f} | 延迟: {latency_ms:.0f}ms | {notes}")

        return EvalResult(
            test_id=test_id,
            category=category,
            passed=passed,
            score=score,
            keyword_hits=sum(1 for kw in expected_keywords if kw.lower() in response.lower()),
            keyword_total=len(expected_keywords),
            response_length=len(response),
            latency_ms=latency_ms,
            notes=notes,
        )

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        print(f"  ✗ 错误: {e}")

        return EvalResult(
            test_id=test_id,
            category=category,
            passed=False,
            score=0.0,
            keyword_hits=0,
            keyword_total=len(expected_keywords),
            response_length=0,
            latency_ms=latency_ms,
            error=str(e),
        )


def run_evaluation(
    dataset_path: str = None,
    model: str = "claude-opus-4-7",
    system: str = "你是一个有帮助的助手，用简洁的中文回答问题。",
) -> None:
    """运行完整评估。"""

    print("=" * 60)
    print("Claude API 评估")
    print("=" * 60)

    # 加载数据集
    dataset = load_dataset(dataset_path)
    test_cases = dataset["test_cases"]

    print(f"\n数据集: {dataset['name']} v{dataset['version']}")
    print(f"测试用例数: {len(test_cases)}")
    print(f"模型: {model}")

    # 创建客户端
    client = ClaudeClient(model=model, system=system)

    # 运行测试
    results = []
    for test_case in test_cases:
        if test_case.get("needs_human_eval"):
            print(f"\n[{test_case['id']}] 跳过（需要人工评估）")
            continue

        result = run_single_test(client, test_case)
        results.append(result)
        client.reset()  # 每个测试用例独立

    # 生成汇总
    summary = generate_summary(results)

    # 打印结果
    print("\n" + "=" * 60)
    print("评估结果汇总")
    print("=" * 60)
    print(f"总测试数: {summary.total_cases}")
    print(f"通过: {summary.passed_cases}")
    print(f"失败: {summary.failed_cases}")
    print(f"通过率: {summary.pass_rate:.1%}")
    print(f"平均分数: {summary.avg_score:.2f}")
    print(f"平均延迟: {summary.avg_latency_ms:.0f}ms")

    print("\n按类别统计:")
    for category, score in summary.category_scores.items():
        print(f"  {category}: {score:.2f}")

    # 保存结果
    output_path = Path(__file__).parent / "eval_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "summary": {
                    "total_cases": summary.total_cases,
                    "passed_cases": summary.passed_cases,
                    "pass_rate": summary.pass_rate,
                    "avg_score": summary.avg_score,
                    "avg_latency_ms": summary.avg_latency_ms,
                    "category_scores": summary.category_scores,
                },
                "results": [
                    {
                        "test_id": r.test_id,
                        "category": r.category,
                        "passed": r.passed,
                        "score": r.score,
                        "latency_ms": r.latency_ms,
                        "notes": r.notes,
                        "error": r.error,
                    }
                    for r in results
                ],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"\n详细结果已保存到: {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="运行 Claude API 评估")
    parser.add_argument("--dataset", help="评估数据集路径")
    parser.add_argument("--model", default="claude-opus-4-7", help="模型名称")
    parser.add_argument("--system", default="你是一个有帮助的助手，用简洁的中文回答问题。", help="系统提示")

    args = parser.parse_args()
    run_evaluation(args.dataset, args.model, args.system)
