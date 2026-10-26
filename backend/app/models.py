from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, UTCDateTime


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    """Placeholder for Supabase Auth users (populated in the auth sprint)."""
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True)
    role: Mapped[str] = mapped_column(String(30), default="analyst")
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(timezone=True), default=utcnow)


class TestSuite(Base):
    __test__ = False
    __tablename__ = "test_suites"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(200))
    version: Mapped[str] = mapped_column(String(30), default="1")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    configuration: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(timezone=True), default=utcnow)


class TestRun(Base):
    __test__ = False
    __tablename__ = "test_runs"
    __table_args__ = (Index("ix_test_runs_owner_created", "owner_id", "created_at"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(64), index=True)
    suite_id: Mapped[int | None] = mapped_column(ForeignKey("test_suites.id", ondelete="SET NULL"), nullable=True)
    parent_run_id: Mapped[int | None] = mapped_column(
        ForeignKey("test_runs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    suite_version: Mapped[str] = mapped_column(String(30), default="adhoc")
    evaluator_version: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(200), default="Untitled run")
    provider: Mapped[str] = mapped_column(String(30))
    model: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(30), default="queued", index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(timezone=True), default=utcnow)
    started_at: Mapped[datetime | None] = mapped_column(UTCDateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(UTCDateTime(timezone=True), nullable=True)
    cases: Mapped[list["TestCaseResult"]] = relationship(
        back_populates="run", cascade="all, delete-orphan", order_by="TestCaseResult.id")


class TestCaseResult(Base):
    __test__ = False
    __tablename__ = "test_case_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("test_runs.id", ondelete="CASCADE"), index=True)
    case_key: Mapped[str] = mapped_column(String(100))
    category: Mapped[str] = mapped_column(String(50), default="other")
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    prompt: Mapped[str] = mapped_column(Text)
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    fixture_secret: Mapped[str | None] = mapped_column(String(500), nullable=True)  # synthetic test secret only
    expected_behavior: Mapped[str] = mapped_column(String(100), default="observe")
    expected_keywords: Mapped[list] = mapped_column(JSON, default=list)
    # pending | pass | fail | needs_review | error
    outcome: Mapped[str] = mapped_column(String(30), default="pending", index=True)
    response: Mapped[str] = mapped_column(Text, default="")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    expected_answer: Mapped[str | None] = mapped_column(String(500), nullable=True)
    forbidden_phrases: Mapped[list | None] = mapped_column(JSON, nullable=True)
    outcome_reason: Mapped[str | None] = mapped_column(Text, nullable=True)  # why the verdict was given
    # human review is stored separately and never overwrites the automated outcome
    reviewer_outcome: Mapped[str | None] = mapped_column(String(30), nullable=True)
    reviewer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(UTCDateTime(timezone=True), nullable=True)
    run: Mapped[TestRun] = relationship(back_populates="cases")
    findings: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    finding_records: Mapped[list["Finding"]] = relationship(
        back_populates="case", cascade="all, delete-orphan", order_by="Finding.id")


class Finding(Base):
    __tablename__ = "findings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_result_id: Mapped[int] = mapped_column(ForeignKey("test_case_results.id", ondelete="CASCADE"), index=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("test_runs.id", ondelete="CASCADE"), index=True)
    category: Mapped[str] = mapped_column(String(50), index=True)
    severity: Mapped[str] = mapped_column(String(20), index=True)
    rule: Mapped[str] = mapped_column(String(100))
    evidence: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(timezone=True), default=utcnow)
    review_outcome: Mapped[str] = mapped_column(String(30), default="unreviewed")
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(UTCDateTime(timezone=True), nullable=True)
    case: Mapped[TestCaseResult] = relationship(back_populates="finding_records")

    @property
    def title(self) -> str:
        return f"Security test failed: {self.rule.replace('_', ' ').capitalize()}"

    @property
    def run_name(self) -> str:
        return self.case.run.name if self.case is not None and self.case.run is not None else ""

    @property
    def test_case_id(self) -> str:
        return self.case.case_key if self.case is not None else ""


class ModelConfig(Base):
    """Provider/model metadata. Never store API keys here: keep a reference name (secret_ref) only."""
    __tablename__ = "model_configs"
    __table_args__ = (
        UniqueConstraint("owner_id", "provider", "model", name="uq_model_configs_owner_provider_model"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[str] = mapped_column(String(64), index=True)
    provider: Mapped[str] = mapped_column(String(30))
    model: Mapped[str] = mapped_column(String(200))
    display_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    encrypted_secret: Mapped[str | None] = mapped_column(Text, nullable=True)
    secret_ref: Mapped[str | None] = mapped_column(String(200), nullable=True)
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(timezone=True), default=utcnow)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        UTCDateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )
    occurred_at: Mapped[str] = mapped_column(String(40))
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    previous_hash: Mapped[str] = mapped_column(String(64), unique=True)
    event_hash: Mapped[str] = mapped_column(String(64), unique=True)
