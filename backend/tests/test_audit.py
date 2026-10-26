import threading

from app.audit import append_event, verify_chain
from app.models import AuditEvent


def test_empty_chain_valid(session_factory):
    with session_factory() as db:
        assert verify_chain(db)["valid"] is True


def test_chain_valid_and_head_hash(session_factory):
    with session_factory() as db:
        for i in range(5):
            append_event(db, "x", {"i": i})
        r = verify_chain(db)
        assert r["valid"] and r["checked_events"] == 5 and len(r["head_hash"]) == 64


def test_payload_tamper_detected(session_factory):
    with session_factory() as db:
        for i in range(3):
            append_event(db, "x", {"i": i})
        ev = db.get(AuditEvent, 2)
        ev.payload = {"i": 999}
        db.commit()
        r = verify_chain(db)
        assert not r["valid"] and r["failed_event_id"] == 2 and r["reason"] == "hash_mismatch"


def test_timestamp_tamper_detected(session_factory):
    with session_factory() as db:
        append_event(db, "x", {})
        db.get(AuditEvent, 1).occurred_at = "2001-01-01T00:00:00+00:00"
        db.commit()
        assert verify_chain(db)["valid"] is False


def test_deleted_event_detected(session_factory):
    with session_factory() as db:
        for i in range(3):
            append_event(db, "x", {"i": i})
        db.delete(db.get(AuditEvent, 2))
        db.commit()
        r = verify_chain(db)
        assert not r["valid"] and r["reason"] == "broken_link"


def test_concurrent_appends_do_not_fork_chain(session_factory):
    errors = []

    def worker(n):
        try:
            with session_factory() as db:
                for i in range(10):
                    append_event(db, "w", {"worker": n, "i": i})
        except Exception as exc:  # pragma: no cover
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(8)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert not errors
    with session_factory() as db:
        r = verify_chain(db)
        assert r["valid"] and r["checked_events"] == 80
