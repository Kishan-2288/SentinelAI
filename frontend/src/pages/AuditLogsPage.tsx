import { useNavigate } from "react-router-dom";
import { ShieldCheck, ShieldX } from "lucide-react";
import PageHeader from "../components/layout/PageHeader";
import LoadingState from "../components/common/LoadingState";
import ErrorMessage from "../components/common/ErrorMessage";
import EmptyState from "../components/common/EmptyState";
import DataTable from "../components/common/DataTable";
import { useAuditEvents, useVerifyChain } from "../hooks/useAuditLogs";
import { findBrokenLinks } from "../features/audit/auditHelpers";
import { formatDateTime } from "../utils/formatDate";
import { shortHash } from "../utils/formatStatus";

export default function AuditLogsPage() {
  const events = useAuditEvents();
  const verify = useVerifyChain();
  const navigate = useNavigate();
  if (events.isLoading) return <LoadingState />;
  if (events.isError) return <ErrorMessage error={events.error} />;
  const list = [...(events.data ?? [])].sort((a, b) => b.sequence - a.sequence);
  const broken = findBrokenLinks(list);
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
          rows={list}
          rowKey={(e) => String(e.id)}
          onRowClick={(e) => navigate(`/audit/${e.id}`)}
          empty={<EmptyState title="No audit events" hint="Events appear here as actions are recorded." />}
          columns={[
            { key: "seq", header: "#", render: (e) => e.sequence },
            { key: "type", header: "Event type", render: (e) => <span className="font-medium">{e.event_type}</span> },
            { key: "time", header: "Time", render: (e) => formatDateTime(e.created_at) },
            { key: "prev", header: "Previous hash", render: (e) => <span className="font-mono text-xs">{shortHash(e.previous_hash)}</span> },
            { key: "hash", header: "Event hash", render: (e) => <span className="font-mono text-xs">{shortHash(e.event_hash)}</span> },
            { key: "link", header: "Link", render: (e) => broken.has(e.id) || (result?.failed_event_id != null && String(result.failed_event_id) === String(e.id)) ? <span className="text-danger">Broken</span> : <span className="text-ok">OK</span> },
          ]}
        />
      </div>
    </>
  );
}
