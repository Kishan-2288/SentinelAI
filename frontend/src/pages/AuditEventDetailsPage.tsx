import { useParams } from "react-router-dom";
import PageHeader from "../components/layout/PageHeader";
import LoadingState from "../components/common/LoadingState";
import ErrorMessage from "../components/common/ErrorMessage";
import { useAuditEvent } from "../hooks/useAuditLogs";
import { formatDateTime } from "../utils/formatDate";

export default function AuditEventDetailsPage() {
  const { eventId = "" } = useParams();
  const { data: e, isLoading, isError, error } = useAuditEvent(eventId);
  if (isLoading) return <LoadingState />;
  if (isError || !e) return <ErrorMessage error={error} title="Could not load this event" />;

  return (
    <>
      <PageHeader title={e.event_type} crumbs={[{ label: "Audit logs", to: "/audit" }, { label: `Event #${e.sequence}` }]} />
      <section className="panel space-y-4 p-4">
        <dl className="grid gap-4 sm:grid-cols-3">
          <div><dt className="text-xs text-muted">Event ID</dt><dd className="break-all font-mono text-xs">{e.id}</dd></div>
          <div><dt className="text-xs text-muted">Timestamp</dt><dd className="text-sm">{formatDateTime(e.created_at)}</dd></div>
          <div><dt className="text-xs text-muted">Actor</dt><dd className="text-sm">{e.actor ?? "System"}</dd></div>
        </dl>
        <div><p className="mb-1 text-xs font-medium text-muted">Previous hash</p><p className="break-all rounded border border-line bg-canvas p-2 font-mono text-xs">{e.previous_hash}</p></div>
        <div><p className="mb-1 text-xs font-medium text-muted">Event hash</p><p className="break-all rounded border border-line bg-canvas p-2 font-mono text-xs">{e.event_hash}</p></div>
        <div><p className="mb-1 text-xs font-medium text-muted">Payload</p><pre className="overflow-x-auto rounded border border-line bg-canvas p-3 font-mono text-xs">{JSON.stringify(e.payload, null, 2)}</pre></div>
      </section>
    </>
  );
}
