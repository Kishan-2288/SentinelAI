import { useState } from "react";
import { Link } from "react-router-dom";
import { ChevronDown, ChevronRight } from "lucide-react";
import EmptyState from "../common/EmptyState";
import { titleCase } from "../../utils/formatStatus";
import type { CaseOutcome, CaseResult } from "../../types/run";

const outcomeStyle: Record<CaseOutcome, string> = {
  pass: "bg-ok-soft text-ok",
  fail: "bg-danger-soft text-danger",
  needs_review: "bg-warn-soft text-warn",
  error: "bg-warn-soft text-warn",
};

function Block({ label, text }: { label: string; text: string }) {
  return (
    <div>
      <p className="mb-1 text-xs font-medium text-muted">{label}</p>
      <pre className="whitespace-pre-wrap rounded-md border border-line bg-canvas p-3 font-mono text-xs">{text}</pre>
    </div>
  );
}

export default function CaseResultsTable({ results }: { results: CaseResult[] }) {
  const [open, setOpen] = useState<string | null>(null);
  if (!results.length) return <EmptyState title="No case results yet" hint="Results appear here as each test case finishes." />;

  return (
    <ul className="divide-y divide-line">
      {results.map((r) => {
        const expanded = open === r.id;
        return (
          <li key={r.id}>
            <button className="flex w-full items-center gap-3 px-4 py-3 text-left hover:bg-canvas" aria-expanded={expanded} onClick={() => setOpen(expanded ? null : r.id)}>
              {expanded ? <ChevronDown className="h-4 w-4" aria-hidden /> : <ChevronRight className="h-4 w-4" aria-hidden />}
              <span className="min-w-0 flex-1 truncate text-sm">{r.prompt}</span>
              <span className="hidden text-xs text-muted sm:inline">{titleCase(r.category)}</span>
              <span className="text-xs text-muted">{r.latency_ms} ms</span>
              <span className={`rounded px-2 py-0.5 text-xs font-medium ${outcomeStyle[r.outcome]}`}>{titleCase(r.outcome)}</span>
            </button>
            {expanded && (
              <div className="grid gap-4 bg-surface px-4 pb-4 pl-11 md:grid-cols-2">
                <Block label="Prompt" text={r.prompt} />
                <Block label="Model response" text={r.response} />
                <Block label="Expected behavior" text={r.expected_behavior} />
                <Block label="Actual behavior" text={r.actual_behavior} />
                {r.error_message && <Block label="Provider error" text={r.error_message} />}
                {r.finding_id && <Link to="/findings" className="text-sm text-brand underline">View related finding</Link>}
              </div>
            )}
          </li>
        );
      })}
    </ul>
  );
}
