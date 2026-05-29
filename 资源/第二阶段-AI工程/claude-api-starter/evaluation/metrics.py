"""评估指标定义。"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class EvalResult:
    """单个测试用例的评估结果。"""

    test_id: str
    category: str
    passed: bool
    score: float  # 0.0 - 1.0
    keyword_hits: int
    keyword_total: int
    response_length: int
    latency_ms: float
    error: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class EvalSummary:
    """评估汇总。"""

    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float
    avg_score: float
    avg_latency_ms: float
    category_scores: dict[str, float]
    results: list[EvalResult]


def calculate_keyword_score(response: str, expected_keywords: list[str]) -> tuple[int, int, float]:
    """计算关键词匹配分数。

    返回: (命中数, 总数, 分数)
    """
    if not expected_keywords:
        return 0, 0, 1.0  # 没有关键词要求时默认通过

    hits = sum(1 for kw in expected_keywords if kw.lower() in response.lower())
    total = len(expected_keywords)
    score = hits / total if total > 0 else 0.0

    return hits, total, score


def evaluate_response(
    response: str,
    expected_keywords: list[str],
    min_length: int = 10,
) -> tuple[bool, float, str]:
    """评估单个响应。

    返回: (是否通过, 分数, 备注)
    """
    # 检查响应长度
    if len(response) < min_length:
        return False, 0.0, f"响应过短 ({len(response)} < {min_length})"

    # 计算关键词分数
    hits, total, score = calculate_keyword_score(response, expected_keywords)

    # 判断是否通过（至少匹配50%的关键词）
    passed = score >= 0.5 if total > 0 else True

    notes = f"关键词命中: {hits}/{total}" if total > 0 else "无关键词要求"

    return passed, score, notes


def generate_summary(results: list[EvalResult]) -> EvalSummary:
    """生成评估汇总。"""

    if not results:
        return EvalSummary(
            total_cases=0,
            passed_cases=0,
            failed_cases=0,
            pass_rate=0.0,
            avg_score=0.0,
            avg_latency_ms=0.0,
            category_scores={},
            results=[],
        )

    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    # 按类别统计
    category_results: dict[str, list[EvalResult]] = {}
    for r in results:
        category_results.setdefault(r.category, []).append(r)

    category_scores = {
        cat: sum(r.score for r in cat_results) / len(cat_results)
        for cat, cat_results in category_results.items()
    }

    return EvalSummary(
        total_cases=len(results),
        passed_cases=passed,
        failed_cases=failed,
        pass_rate=passed / len(results),
        avg_score=sum(r.score for r in results) / len(results),
        avg_latency_ms=sum(r.latency_ms for r in results) / len(results),
        category_scores=category_scores,
        results=results,
    )
