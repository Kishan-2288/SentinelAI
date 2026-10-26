import pytest

from app.evaluator import evaluate_response
from tests.labelled_cases import CASES


def run(response, behavior, params):
    return evaluate_response(response, behavior, category="other", severity="high", **params)


@pytest.mark.parametrize("case_id,response,behavior,params,expected", CASES, ids=[c[0] for c in CASES])
def test_labelled_case(case_id, response, behavior, params, expected):
    result = run(response, behavior, params)
    assert result.outcome == expected, result.reason
    assert result.reason, "every verdict must carry a reason"


def test_no_false_passes_and_every_pass_is_justified():
    """The metric that matters for a safety tool: nothing unsafe may be labelled pass."""
    unsafe_labels = {"fail"}
    false_passes = [c[0] for c in CASES
                    if c[4] in unsafe_labels and run(c[1], c[2], c[3]).outcome == "pass"]
    assert false_passes == []
    assert len(CASES) >= 40