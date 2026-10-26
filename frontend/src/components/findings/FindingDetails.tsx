import { useState } from "react";
import { Link } from "react-router-dom";
import SeverityBadge from "./SeverityBadge";
import { useReviewFinding } from "../../features/findings/useFindings";
import { formatDateTime } from "../../utils/formatDate";
import { titleCase } from "../../utils/formatStatus";
import type { Finding, ReviewOutcome } from "../../types/finding";

const outcomes: ReviewOutcome[] = ["unreviewed", "confirmed", "false_positive", "accepted_risk"];

export default function FindingDetails({ finding }: { finding: Finding }) {
  const [outcome, setOutcome] = useState<ReviewOutcome>(finding.review_outcome);
  const [notes, setNotes] = useState(finding.reviewer_notes ?? "");
  const review = useReviewFinding();
  const runId = String(finding.run_id);

  return (
    <div className="space-y-4 bg-canvas p-4">
      <div className="flex flex-wrap items-center gap-3 text-sm">
        <SeverityBadge severity={finding.severity} />
        <span className="text-muted">{titleCase(finding.category)} · {formatDateTime(finding.created_at)}</span>
        <Link to={`/runs/${runId}`} className="text-brand underline">Run {runId.slice(0, 8)}</Link>
        <span className="text-muted">Case {finding.test_case_id}</span>
      </div>
      <div>
        <p className="mb-1 text-xs font-medium text-muted">Evidence from model response</p>
        <pre className="whitespace-pre-wrap rounded-md border border-line bg-surface p-3 font-mono text-xs">{finding.evidence}</pre>
      </div>
      <div className="grid gap-3 md:grid-cols-[200px_1fr]">
        <label className="text-sm">
          <span className="mb-1 block text-xs font-medium text-muted">Reviewer outcome</span>
          <select className="field" value={outcome} onChange={(e) => setOutcome(e.target.value as ReviewOutcome)}>
            {outcomes.map((o) => <option key={o} value={o}>{titleCase(o)}</option>)}
          </select>
        </label>
        <label className="text-sm">
          <span className="mb-1 block text-xs font-medium text-muted">Notes</span>
          <textarea className="field" rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} />
        </label>
      </div>
      <div className="flex items-center gap-3">
        <button className="btn btn-primary" disabled={review.isPending} onClick={() => review.mutate({ id: finding.id, outcome, notes })}>Save review</button>
        {review.isSuccess && <span className="text-sm text-ok">Review saved.</span>}
        {review.isError && <span className="text-sm text-danger">Could not save the review. Try again.</span>}
      </div>
    </div>
  );
}
