
"""Tamper-evident audit log with legacy and v2 hash verification.

New events use hash version v2. Historical events are verified against
supported legacy formats without rewriting or deleting stored records.

Each event hash covers its previous hash, event type, timestamp and payload.
V2 events additionally include the version marker "v2".

case_completed events can carry a hash of the stored case result. Verification
recomputes it from the database to detect edits to responses, outcomes or
findings.

A hash chain alone cannot stop someone with full database access from
rewriting the entire history and recomputing every hash. Export the latest
hash to external storage for stronger tamper evidence.
"""

import hashlib
import json
import threading
from datetime import datetime, timezone

from sqlalchemy import select, text
from sqlalchemy.orm import Session, selectinload

from app.models import AuditEvent, TestCaseResult


GENESIS = "0" * 64
HASH_VERSION = "v2"

_append_lock = threading.RLock()
_PG_LOCK_KEY = 7319001


def canonical_json(value) -> str:
    """Serialize values deterministically for hashing."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        default=str,
    )


def _sha256(value: str) -> str:
    """Return a hexadecimal SHA-256 digest."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def event_digest(
    previous: str,
    event_type: str,
    occurred_at: str,
    payload: dict,
) -> str:
    """Compute the digest used by newly created v2 events."""
    return _sha256(
        canonical_json(
            {
                "v": HASH_VERSION,
                "prev": previous,
                "type": event_type,
                "at": occurred_at,
                "payload": payload,
            }
        )
    )


def legacy_event_digest(
    previous: str,
    event_type: str,
    occurred_at: str,
    payload: dict,
) -> str:
    """Compute the original digest format, without a version marker."""
    return _sha256(
        canonical_json(
            {
                "prev": previous,
                "type": event_type,
                "at": occurred_at,
                "payload": payload,
            }
        )
    )


def _timestamp_candidates(value) -> list[str]:
    """Return common representations of a stored historical timestamp.

    These are verification candidates only. The database value is never
    rewritten. The exact stored representation is always checked first.
    """
    candidates = [str(value)]

    if isinstance(value, datetime):
        dt = value
    else:
        try:
            dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return candidates

    # Historical code may have hashed a datetime's string representation,
    # ISO representation, or a UTC-normalized ISO representation.
    candidates.extend(
        [
            dt.isoformat(),
            str(dt),
        ]
    )

    if dt.tzinfo is not None:
        utc_dt = dt.astimezone(timezone.utc)
        candidates.extend(
            [
                utc_dt.isoformat(),
                str(utc_dt),
            ]
        )

    # Deduplicate while preserving order.
    return list(dict.fromkeys(candidates))


def _event_hash_is_valid(event: AuditEvent) -> bool:
    """Verify the event against supported digest formats.

    No event fields or hashes are changed during verification.
    """
    for timestamp in _timestamp_candidates(event.occurred_at):
        if event.event_hash == event_digest(
            event.previous_hash,
            event.event_type,
            timestamp,
            event.payload,
        ):
            return True

        if event.event_hash == legacy_event_digest(
            event.previous_hash,
            event.event_type,
            timestamp,
            event.payload,
        ):
            return True

    return False


def compute_result_hash(case: TestCaseResult) -> str:
    """Hash the stored case fields and associated findings."""
    findings = sorted(
        [
            finding.category,
            finding.severity,
            finding.rule,
            finding.evidence,
        ]
        for finding in case.finding_records
    )

    return _sha256(
        canonical_json(
            {
                "prompt": case.prompt,
                "system_prompt": case.system_prompt,
                "response": case.response,
                "outcome": case.outcome,
                "error_message": case.error_message,
                "findings": findings,
            }
        )
    )


def append_event(
    db: Session,
    event_type: str,
    payload: dict,
) -> AuditEvent:
    """Append a v2 event and commit the caller's transaction.

    Serializes appends in-process and, on PostgreSQL, across processes.
    """
    with _append_lock:
        if db.get_bind().dialect.name == "postgresql":
            db.execute(
                text("SELECT pg_advisory_xact_lock(:k)"),
                {"k": _PG_LOCK_KEY},
            )

        last_event = db.scalar(
            select(AuditEvent).order_by(AuditEvent.id.desc()).limit(1)
        )

        previous_hash = last_event.event_hash if last_event else GENESIS
        occurred_at = datetime.now(timezone.utc).isoformat()

        event = AuditEvent(
            event_type=event_type,
            occurred_at=occurred_at,
            payload=payload,
            previous_hash=previous_hash,
            event_hash=event_digest(
                previous_hash,
                event_type,
                occurred_at,
                payload,
            ),
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        return event


def _failure(
    events: list,
    event: AuditEvent | None,
    reason: str,
) -> dict:
    """Build a consistent verification failure response."""
    return {
        "valid": False,
        "checked_events": len(events),
        "failed_event_id": event.id if event is not None else None,
        "reason": reason,
        "head_hash": None,
    }


def verify_chain(db: Session) -> dict:
    """Verify chain links, event digests and stored case-result hashes."""
    events = db.scalars(
        select(AuditEvent).order_by(AuditEvent.id.asc())
    ).all()

    if not events:
        return {
            "valid": True,
            "checked_events": 0,
            "failed_event_id": None,
            "reason": None,
            "head_hash": None,
        }

    result_ids = [
        event.payload.get("case_result_id")
        for event in events
        if event.event_type == "case_completed"
        and isinstance(event.payload, dict)
        and event.payload.get("case_result_id") is not None
    ]

    cases: dict[int, TestCaseResult] = {}

    for start in range(0, len(result_ids), 500):
        chunk = result_ids[start : start + 500]

        rows = db.scalars(
            select(TestCaseResult)
            .options(selectinload(TestCaseResult.finding_records))
            .where(TestCaseResult.id.in_(chunk))
        ).all()

        cases.update({case.id: case for case in rows})

    first_event = events[0]

    if first_event.previous_hash != GENESIS:
        return _failure(events, first_event, "missing_chain_prefix")

    previous_hash = GENESIS

    for event in events:
        if event.previous_hash != previous_hash:
            return _failure(events, event, "broken_link")

        if not _event_hash_is_valid(event):
            return _failure(events, event, "hash_mismatch")

        if event.event_type == "case_completed":
            payload = event.payload

            if not isinstance(payload, dict):
                return _failure(events, event, "invalid_case_payload")

            case_result_id = payload.get("case_result_id")
            expected_result_hash = payload.get("result_hash")

            if expected_result_hash is not None:
                if case_result_id is None:
                    return _failure(
                        events, event, "result_reference_missing"
                    )

                case = cases.get(case_result_id)

                if case is None:
                    return _failure(events, event, "result_missing")

                if compute_result_hash(case) != expected_result_hash:
                    return _failure(events, event, "result_mismatch")

        previous_hash = event.event_hash

    return {
        "valid": True,
        "checked_events": len(events),
        "failed_event_id": None,
        "reason": None,
        "head_hash": previous_hash,
    }
