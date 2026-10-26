import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import PageHeader from "../components/layout/PageHeader";
import LoadingState from "../components/common/LoadingState";
import ErrorMessage from "../components/common/ErrorMessage";
import EmptyState from "../components/common/EmptyState";
import SeverityBadge from "../components/findings/SeverityBadge";
import FindingDetails from "../components/findings/FindingDetails";
import { useFindings } from "../features/findings/useFindings";
import { severityOrder, titleCase } from "../utils/formatStatus";
import type { FindingFilters, ReviewOutcome, Severity } from "../types/finding";

export default function FindingsPage() {
  const [filters, setFilters] = useState<FindingFilters>({ severity: "", category: "", review_outcome: "" });
  const [open, setOpen] = useState<string | number | null>(null);
  const { data, isLoading, isError, error } = useFindings(filters);
  const set = (patch: Partial<FindingFilters>) => setFilters((f) => ({ ...f, ...patch }));
  const categories = ["prompt_injection", "refusal", "data_leakage", "jailbreak", "other"];

  return (
    <>
      <PageHeader title="Findings" description="Security issues detected during test runs, with evidence and review status." />
      <div className="panel">
        <div className="flex flex-wrap gap-3 border-b border-line p-4">
          <select aria-label="Severity" className="field w-auto" value={filters.severity} onChange={(e) => set({ severity: e.target.value as Severity | "" })}>
            <option value="">All severities</option>{severityOrder.map((s) => <option key={s} value={s}>{titleCase(s)}</option>)}
          </select>
          <select aria-label="Category" className="field w-auto" value={filters.category} onChange={(e) => set({ category: e.target.value })}>
            <option value="">All categories</option>{categories.map((c) => <option key={c} value={c}>{titleCase(c)}</option>)}
          </select>
          <select aria-label="Review outcome" className="field w-auto" value={filters.review_outcome} onChange={(e) => set({ review_outcome: e.target.value as ReviewOutcome | "" })}>
            <option value="">All review outcomes</option>
            {(["unreviewed", "confirmed", "false_positive", "accepted_risk"] as ReviewOutcome[]).map((o) => <option key={o} value={o}>{titleCase(o)}</option>)}
          </select>
        </div>
        {isLoading ? <LoadingState /> : isError ? <div className="p-4"><ErrorMessage error={error} /></div> : !data?.length ? <EmptyState title="No findings" hint="No findings match these filters." /> : (
          <ul className="divide-y divide-line">
            {data.map((f) => (
              <li key={f.id}>
                <button className="flex w-full items-center gap-3 px-4 py-3 text-left hover:bg-canvas" aria-expanded={open === f.id} onClick={() => setOpen(open === f.id ? null : f.id)}>
                  {open === f.id ? <ChevronDown className="h-4 w-4" aria-hidden /> : <ChevronRight className="h-4 w-4" aria-hidden />}
                  <span className="flex-1 text-sm font-medium">{f.title}</span>
                  <SeverityBadge severity={f.severity} />
                  <span className="hidden text-xs text-muted sm:inline">{titleCase(f.review_outcome)}</span>
                </button>
                {open === f.id && <FindingDetails finding={f} />}
              </li>
            ))}
          </ul>
        )}
      </div>
    </>
  );
}
