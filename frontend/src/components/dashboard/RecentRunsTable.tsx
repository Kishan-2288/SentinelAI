import { Link, useNavigate } from "react-router-dom";
import DataTable from "../common/DataTable";
import EmptyState from "../common/EmptyState";
import RunStatusBadge from "../runs/RunStatusBadge";
import { formatDateTime } from "../../utils/formatDate";
import type { Run } from "../../types/run";

export default function RecentRunsTable({ runs }: { runs: Run[] }) {
  const navigate = useNavigate();
  return (
    <DataTable
      rows={runs}
      rowKey={(r) => r.id}
      onRowClick={(r) => navigate(`/runs/${r.id}`)}
      empty={<EmptyState title="No test runs yet" hint="Start a run to evaluate a model against a test suite." action={<Link to="/runs/new" className="btn btn-primary">New run</Link>} />}
      columns={[
        { key: "name", header: "Run", render: (r) => <span className="font-medium">{r.name}</span> },
        { key: "model", header: "Model", render: (r) => `${r.provider} / ${r.model}` },
        { key: "status", header: "Status", render: (r) => <RunStatusBadge status={r.status} /> },
        { key: "created", header: "Started", render: (r) => formatDateTime(r.created_at) },
      ]}
    />
  );
}
