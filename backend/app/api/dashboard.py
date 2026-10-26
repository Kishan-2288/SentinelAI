from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.runs import to_summary
from app.database import get_db
from app.models import Finding, ModelConfig, TestCaseResult, TestRun
from app.security.auth import CurrentUser, get_current_user

router = APIRouter(prefix="/api/v1", tags=["dashboard"])


@router.get("/dashboard/summary")
def dashboard_summary(db: Session = Depends(get_db), user: CurrentUser = Depends(get_current_user)):
    mine = TestRun.owner_id == user.id

    def grouped(col, *where):
        rows = db.execute(select(col, func.count()).select_from(TestRun).join(
            TestCaseResult, TestCaseResult.run_id == TestRun.id, isouter=False).where(mine, *where).group_by(col)).all()
        return {k: v for k, v in rows}

    outcome_counts = {k: v for k, v in db.execute(
        select(TestCaseResult.outcome, func.count()).join(TestRun, TestCaseResult.run_id == TestRun.id)
        .where(mine).group_by(TestCaseResult.outcome)).all()}
    run_status = {k: v for k, v in db.execute(
        select(TestRun.status, func.count()).where(mine).group_by(TestRun.status)).all()}
    by_severity = {k: v for k, v in db.execute(
        select(Finding.severity, func.count()).join(TestRun, Finding.run_id == TestRun.id)
        .where(mine).group_by(Finding.severity)).all()}
    by_category = {k: v for k, v in db.execute(
        select(Finding.category, func.count()).join(TestRun, Finding.run_id == TestRun.id)
        .where(mine).group_by(Finding.category)).all()}
    latency = db.execute(
        select(TestRun.provider, TestRun.model, func.avg(TestCaseResult.latency_ms), func.count())
        .join(TestCaseResult, TestCaseResult.run_id == TestRun.id)
        .where(mine, TestCaseResult.outcome != "pending", TestCaseResult.outcome != "error")
        .group_by(TestRun.provider, TestRun.model)).all()
    recent = db.scalars(select(TestRun).options(selectinload(TestRun.cases)).where(mine)
                        .order_by(TestRun.id.desc()).limit(5)).all()
    evaluated = sum(count for outcome, count in outcome_counts.items() if outcome in {"pass", "fail"})
    passed = outcome_counts.get("pass", 0)
    open_findings = db.scalar(
        select(func.count()).select_from(Finding).join(TestRun, Finding.run_id == TestRun.id)
        .where(mine, Finding.review_outcome.in_(("unreviewed", "confirmed")))
    ) or 0
    available_models = db.scalar(
        select(func.count()).select_from(ModelConfig)
        .where(ModelConfig.owner_id == user.id, ModelConfig.enabled.is_(True))
    ) or 0
    trend_rows = db.execute(
        select(func.date(TestRun.created_at), TestCaseResult.outcome, func.count())
        .join(TestCaseResult, TestCaseResult.run_id == TestRun.id)
        .where(mine)
        .group_by(func.date(TestRun.created_at), TestCaseResult.outcome)
        .order_by(func.date(TestRun.created_at))
    ).all()
    trend_by_date: dict[str, dict[str, int]] = {}
    for day, outcome, count in trend_rows:
        point = trend_by_date.setdefault(
            str(day),
            {"date": str(day), "passed": 0, "failed": 0, "review": 0, "errors": 0, "pending": 0},
        )
        if outcome == "pass":
            point["passed"] += count
        elif outcome == "fail":
            point["failed"] += count
        elif outcome == "needs_review":
            point["review"] += count
        elif outcome == "error":
            point["errors"] += count
        elif outcome == "pending":
            point["pending"] += count
    return {
        "total_runs": sum(run_status.values()),
        "total_cases": sum(outcome_counts.values()),
        "outcome_counts": outcome_counts,
        "run_status_counts": run_status,
        "findings_by_severity": by_severity,
        "findings_by_category": by_category,
        "latency_by_model": [{"provider": p, "model": m, "avg_latency_ms": round(float(a or 0)),
                              "cases": n} for p, m, a, n in latency],
        "recent_runs": [to_summary(r) for r in recent],
        "pass_rate": round(passed * 100 / evaluated, 2) if evaluated else None,
        "evaluated_results": evaluated,
        "open_findings": open_findings,
        "available_models": available_models,
        "models_available": available_models,
        "models_total": available_models,
        "critical_findings": by_severity.get("critical", 0),
        "trend": list(trend_by_date.values()),
    }
