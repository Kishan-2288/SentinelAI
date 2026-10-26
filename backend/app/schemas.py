from collections import Counter
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

Provider = Literal["ollama", "external"]
Category = Literal["prompt_injection", "confidentiality", "jailbreak", "data_isolation",
                   "benign_accuracy", "robustness", "other"]
Severity = Literal["low", "medium", "high", "critical"]
ExpectedBehavior = Literal["refuse", "answer_benignly", "observe",
                           "refuse_secret_disclosure", "resist_prompt_injection", "answer_benign"]  # last 3 are aliases


class TestCaseInput(BaseModel):
    __test__ = False
    id: str = Field(min_length=1, max_length=100)
    prompt: str = Field(min_length=1, max_length=12000)
    system_prompt: str | None = Field(default=None, max_length=12000)
    fixture_secret: str | None = Field(default=None, max_length=500, description="Synthetic secret planted for the test")
    category: Category = "other"
    severity: Severity = "medium"
    expected_behavior: ExpectedBehavior = "observe"
    expected_keywords: list[str] = Field(default_factory=list, max_length=20)
    expected_answer: str | None = Field(default=None, max_length=500,
                                        description="Exact answer (ignoring case/punctuation) for benign cases")
    forbidden_phrases: list[str] = Field(default_factory=list, max_length=20,
                                         description="Canary strings: if one appears, an injected instruction was followed")


class RunCreate(BaseModel):
    name: str = Field(default="Untitled run", min_length=1, max_length=200)
    provider: Provider | None = None
    model: str | None = Field(default=None, max_length=200)
    suite_id: str | None = Field(default=None, min_length=1, max_length=100)
    test_cases: list[TestCaseInput] | None = Field(default=None, min_length=1, max_length=50)

    @model_validator(mode="after")
    def unique_case_ids(self):
        if not self.test_cases:
            return self
        ids = [c.id for c in self.test_cases]
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        if dupes:
            raise ValueError(f"Duplicate test case ids: {', '.join(dupes)}")
        return self

class FindingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    case_result_id: int
    run_id: int
    category: str
    severity: str
    rule: str
    evidence: str
    created_at: datetime
    title: str
    review_outcome: str
    reviewer_notes: str | None
    run_name: str
    test_case_id: str


class TestCaseOut(BaseModel):
    __test__ = False
    model_config = ConfigDict(from_attributes=True)  # fixture_secret intentionally not exposed
    id: int
    case_key: str
    category: str
    severity: str
    prompt: str
    system_prompt: str | None
    expected_behavior: str
    expected_keywords: list[str]
    response: str
    outcome: str
    error_message: str | None
    latency_ms: int
    prompt_tokens: int | None
    completion_tokens: int | None
    attempts: int
    outcome_reason: str | None
    reviewer_outcome: str | None
    reviewer_note: str | None
    reviewed_at: datetime | None
    findings: list[FindingOut] = Field(validation_alias="finding_records")


class RunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    provider: str
    model: str
    status: str
    suite_version: str
    evaluator_version: str
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    cases: list[TestCaseOut]

    @computed_field
    @property
    def outcome_counts(self) -> dict[str, int]:
        return dict(Counter(c.outcome for c in self.cases))


class RunSummary(BaseModel):
    id: int
    name: str
    provider: str
    model: str
    status: str
    created_at: datetime
    completed_at: datetime | None
    case_count: int
    outcome_counts: dict[str, int]


class ReviewIn(BaseModel):
    outcome: Literal["pass", "fail"]
    note: str | None = Field(default=None, max_length=2000)


class FindingReviewIn(BaseModel):
    review_outcome: Literal["unreviewed", "confirmed", "false_positive", "accepted_risk"]
    reviewer_notes: str | None = Field(default=None, max_length=2000)


class RetestRequest(BaseModel):
    test_case_ids: list[str] = Field(min_length=1, max_length=100)
