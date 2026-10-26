import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Plus, Search } from "lucide-react";
import PageHeader from "../components/layout/PageHeader";
import DataTable from "../components/common/DataTable";
import EmptyState from "../components/common/EmptyState";
import LoadingState from "../components/common/LoadingState";
import ErrorMessage from "../components/common/ErrorMessage";
import RunStatusBadge from "../components/runs/RunStatusBadge";
import { useRuns } from "../hooks/useRuns";
import { filterRuns } from "../features/runs/runFilters";
import { formatDateTime } from "../utils/formatDate";
import { runStatusLabel } from "../utils/formatStatus";
import type { RunStatus } from "../types/run";

export default function RunsPage() {
  const { data, isLoading, isError, error } = useRuns();
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState<RunStatus | "all">("all");
  const rows = useMemo(() => filterRuns(data ?? [], search, status), [data, search, status]);

  return (
    <>
      <PageHeader
        title="Test runs"
        description="Every evaluation executed against a model."
        actions={<Link to="/runs/new" className="btn btn-primary"><Plus className="h-4 w-4" aria-hidden /> New run</Link>}
      />
      <div className="panel">
        <div className="flex flex-wrap gap-3 border-b border-line p-4">
          <label className="relative min-w-60 flex-1">
            <span className="sr-only">Search runs</span>
            <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-muted" aria-hidden />
            <input className="field pl-9" placeholder="Search by name, model, or ID" value={search} onChange={(e) => setSearch(e.target.value)} />
          </label>
          <label>
            <span className="sr-only">Filter by status</span>
            <select className="field" value={status} onChange={(e) => setStatus(e.target.value as RunStatus | "all")}>
              <option value="all">All statuses</option>
              {(Object.keys(runStatusLabel) as RunStatus[]).map((s) => <option key={s} value={s}>{runStatusLabel[s]}</option>)}
            </select>
          </label>
        </div>
        {isLoading ? <LoadingState /> : isError ? <div className="p-4"><ErrorMessage error={error} /></div> : (
          <DataTable
            rows={rows}
            rowKey={(r) => r.id}
            onRowClick={(r) => navigate(`/runs/${r.id}`)}
            empty={<EmptyState title="No runs match" hint="Change the filters or start a new run." />}
            columns={[
              { key: "name", header: "Run", render: (r) => <span className="font-medium">{r.name}</span> },
              { key: "provider", header: "Provider", render: (r) => r.provider },
              { key: "model", header: "Model", render: (r) => r.model },
              { key: "status", header: "Status", render: (r) => <RunStatusBadge status={r.status} /> },
              { key: "result", header: "Passed", render: (r) => `${r.passed_cases} / ${r.total_cases}` },
              { key: "created", header: "Created", render: (r) => formatDateTime(r.created_at) },
            ]}
          />
        )}
      </div>
    </>
  );
}
