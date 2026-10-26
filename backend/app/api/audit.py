from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.audit import verify_chain
from app.database import get_db
from app.models import AuditEvent, TestRun
from app.security.auth import CurrentUser, get_current_user

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


def _serialize_event(event: AuditEvent, runs: dict[int, TestRun] | None = None) -> dict:
    payload_run_id = event.payload.get("run_id") if isinstance(event.payload, dict) else None
    run = runs.get(payload_run_id) if runs and isinstance(payload_run_id, int) else None
    return {
        "id": event.id,
        "sequence": event.id,
        "created_at": (
            event.created_at.isoformat()
            if event.created_at
            else None
        ),
        "occurred_at": event.occurred_at,
        "event_type": event.event_type,
        "payload": event.payload,
        "run_id": payload_run_id,
        "run_name": run.name if run else None,
        "run_status": run.status if run else event.payload.get("status") if isinstance(event.payload, dict) else None,
        "previous_hash": event.previous_hash,
        "event_hash": event.event_hash,
    }


@router.get("/verify")
def audit_verify(
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    return verify_chain(db)


@router.get("/events")
def audit_events(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    rows = db.scalars(
        select(AuditEvent)
        .order_by(AuditEvent.id.desc())
        .limit(limit)
        .offset(offset)
    ).all()

    run_ids = {
        event.payload.get("run_id")
        for event in rows
        if isinstance(event.payload, dict) and isinstance(event.payload.get("run_id"), int)
    }
    runs = {
        run.id: run
        for run in db.scalars(select(TestRun).where(TestRun.id.in_(run_ids))).all()
    } if run_ids else {}
    return [_serialize_event(event, runs) for event in rows]


@router.get("/events/{event_id}")
def audit_event(
    event_id: int,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(get_current_user),
):
    event = db.get(AuditEvent, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Audit event not found")

    runs = {}
    if isinstance(event.payload, dict) and isinstance(event.payload.get("run_id"), int):
        run = db.get(TestRun, event.payload["run_id"])
        if run:
            runs[run.id] = run
    return _serialize_event(event, runs)
