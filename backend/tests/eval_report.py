"""Print a confusion summary of the evaluator against the labelled set:  python -m tests.eval_report"""
from collections import Counter

from app.evaluator import EVALUATOR_VERSION, evaluate_response
from tests.labelled_cases import CASES

rows = Counter()
for cid, resp, beh, params, expected in CASES:
    got = evaluate_response(resp, beh, severity="high", **params).outcome
    rows[(expected, got)] += 1
print(f"evaluator {EVALUATOR_VERSION}: {len(CASES)} labelled cases")
for (exp, got), n in sorted(rows.items()):
    print(f"  expected {exp:<13} got {got:<13} x{n}{'' if exp == got else '   <-- MISMATCH'}")
print("accuracy:", sum(n for (e, g), n in rows.items() if e == g), "/", len(CASES))