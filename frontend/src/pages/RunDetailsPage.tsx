import { useParams } from "react-router-dom";
import PageHeader from "../components/layout/PageHeader";
import LoadingState from "../components/common/LoadingState";
import ErrorMessage from "../components/common/ErrorMessage";
import RunStatusBadge from "../components/runs/RunStatusBadge";
import RunProgress from "../components/runs/RunProgress";
import CaseResultsTable from "../components/runs/CaseResultsTable";
import { useCancelRun, useRun } from "../hooks/useRuns";
import { formatDateTime, formatDuration } from "../utils/formatDate";

export default function RunDetailsPage() {
  const { runId = "" } = useParams();
  const { data: run, isLoading, isError, error } = useRun(runId);
  const cancel = useCancelRun();

  if (isLoading) return <LoadingState />;
  if (isError || !run) return <ErrorMessage error={error} title="Could not load this run" />;
  const active = run.status === "queued" || run.status === "running";
  const avgLatency = run.results?.length ? Math.round(run.results.reduce((a, r) => a + r.latency_ms, 0) / run.results.length) : null;

  const facts: [string, string][] = [
    ["Provider", run.provider], ["Model", run.model], ["Suite", run.suite_name ?? "—"],
    ["Created", formatDateTime(run.created_at)], ["Started", formatDateTime(run.started_at)],
    ["Finished", formatDateTime(run.finished_at)], ["Duration", formatDuration(run.started_at, run.finished_at)],
    ["Avg. latency", avgLatency === null ? "—" : `${avgLatency} ms`],
  ];

  return (
    <>
      <PageHeader
        title={run.name}
        crumbs={[{ label: "Test runs", to: "/runs" }, { label: run.name }]}
        actions={<div className="flex items-center gap-3"><RunStatusBadge status={run.status} />{active && <button className="btn btn-secondary" disabled={cancel.isPending} onClick={() => cancel.mutate(run.id)}>Cancel run</button>}</div>}
      />
      <section className="panel p-4">
        <dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {facts.map(([k, v]) => (<div key={k}><dt className="text-xs text-muted">{k}</dt><dd className="text-sm font-medium">{v}</dd></div>))}
        </dl>
        <div className="mt-4"><RunProgress run={run} /></div>
        <p className="mt-3 text-sm text-muted">{run.passed_cases} passed · {run.failed_cases} failed</p>
      </section>
      <section className="panel mt-6">
        <h2 className="p-4 pb-2 font-medium">Case results</h2>
        <CaseResultsTable results={run.results ?? []} />
      </section>
    </>
  );
}
