"""Helpers for comparing persisted test outcomes without exposing prompt data."""


def summarize_results(results: list[dict]) -> dict:
    total = len(results)
    passed = sum(result.get("status", result.get("outcome")) in {"pass", "passed"} for result in results)
    failed = sum(result.get("status", result.get("outcome")) in {"fail", "failed"} for result in results)
    inconclusive = sum(
        result.get("status", result.get("outcome")) in {"inconclusive", "needs_review"}
        for result in results
    )
    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "inconclusive": inconclusive,
        "pass_rate": round(100 * passed / total, 2) if total else None,
    }


def compare_runs(original: list[dict], retest: list[dict]) -> dict:
    before = summarize_results(original)
    after = summarize_results(retest)
    changes = []
    original_by_case = {result["case_key"]: result for result in original}
    for result in retest:
        previous = original_by_case.get(result["case_key"])
        if previous is not None:
            changes.append({
                "test_case_id": result["case_key"],
                "before": previous["outcome"],
                "after": result["outcome"],
                "changed": previous["outcome"] != result["outcome"],
            })
    return {
        "original": before,
        "retest": after,
        "pass_rate_change": (
            round(after["pass_rate"] - before["pass_rate"], 2)
            if before["pass_rate"] is not None and after["pass_rate"] is not None
            else None
        ),
        "failed_change": after["failed"] - before["failed"],
        "cases": changes,
    }
