import { useNavigate } from "react-router-dom";
import { ShieldCheck, ShieldX } from "lucide-react";
import PageHeader from "../components/layout/PageHeader";
import LoadingState from "../components/common/LoadingState";
import ErrorMessage from "../components/common/ErrorMessage";
import EmptyState from "../components/common/EmptyState";
import DataTable from "../components/common/DataTable";
import { useAuditEvents, useVerifyChain } from "../hooks/useAuditLogs";
import { formatDateTime } from "../utils/formatDate";
import type { AuditEvent } from "../types/audit";

type AuditRunGroup = {
  key: string;
  runId: number | null;
  runName: string;
  status: string;
  events: AuditEvent[];
};

export default function AuditLogsPage() {
  const events = useAuditEvents();
  const verify = useVerifyChain();
  const navigate = useNavigate();
  if (events.isLoading) return <LoadingState />;
  if (events.isError) return <ErrorMessage error={events.error} />;
  const list = [...(events.data ?? [])].sort((a, b) => b.sequence - a.sequence);
  const groups = Array.from(
    list.reduce((map, event) => {
      const key = event.run_id != null ? `run:${event.run_id}` : "other";
      const group = map.get(key) ?? {
        key,
        runId: event.run_id ?? null,
        runName: event.run_name ?? "Other activity",
        status: event.run_status ?? "activity",
        events: [],
      };
      group.events.push(event);
      if (event.run_status) group.status = event.run_status;
      if (event.run_name) group.runName = event.run_name;
      map.set(key, group);
      return map;
    }, new Map<string, AuditRunGroup>())
    .values()
  ).sort((a, b) => b.events[0].sequence - a.events[0].sequence);
  const result = verify.data;

  return (
    <>
      <PageHeader
        title="Audit logs"
        description="Tamper-evident record of security-relevant actions. Each event stores the hash of the event before it."
        actions={<button className="btn btn-primary" disabled={verify.isPending} onClick={() => verify.mutate()}>{verify.isPending ? "Verifying…" : "Verify chain"}</button>}
      />
      {verify.isError && <div className="mb-4"><ErrorMessage error={verify.error} title="Verification failed to run" /></div>}
      {result && (
        <div role="status" className={`mb-4 flex items-start gap-3 rounded-lg border p-4 text-sm ${result.valid ? "border-ok/30 bg-ok-soft text-ok" : "border-danger/30 bg-danger-soft text-danger"}`}>
          {result.valid ? <ShieldCheck className="h-5 w-5" aria-hidden /> : <ShieldX className="h-5 w-5" aria-hidden />}
          <div>
            <p className="font-medium">{result.valid ? "Chain verified. No tampering found." : "Chain verification failed."}</p>
            <p>{result.checked_events} events checked.{!result.valid && result.failed_sequence != null && ` First failure at sequence #${result.failed_sequence}.`} {result.message}</p>
          </div>
        </div>
      )}
      <div className="panel">
        <DataTable
          rows={groups}
          rowKey={(group) => group.key}
          onRowClick={(group) => group.runId != null ? navigate(`/runs/${group.runId}`) : navigate(`/audit/${group.events[0].id}`)}
          empty={<EmptyState title="No audit activity" hint="Events appear here as actions are recorded." />}
          columns={[
            { key: "run", header: "Run", render: (group) => <span className="font-medium">{group.runName}</span> },
            { key: "runId", header: "Run ID", render: (group) => group.runId ?? "—" },
            { key: "count", header: "Events", render: (group) => group.events.length },
            { key: "status", header: "Status", render: (group) => <span className="capitalize">{group.status.replace(/_/g, " ")}</span> },
            { key: "first", header: "First event", render: (group) => formatDateTime(group.events[group.events.length - 1].created_at) },
            { key: "last", header: "Last event", render: (group) => formatDateTime(group.events[0].created_at) },
          ]}
        />
      </div>
    </>
  );
}
