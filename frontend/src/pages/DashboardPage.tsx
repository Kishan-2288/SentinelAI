import { Link } from "react-router-dom";
import { Activity, CheckCircle2, ShieldAlert, ShieldCheck } from "lucide-react";
import PageHeader from "../components/layout/PageHeader";
import StatCard from "../components/dashboard/StatCard";
import RunTrendChart from "../components/dashboard/RunTrendChart";
import RecentRunsTable from "../components/dashboard/RecentRunsTable";
import LoadingState from "../components/common/LoadingState";
import ErrorMessage from "../components/common/ErrorMessage";
import { useDashboardSummary } from "../hooks/useDashboard";
import { useRuns } from "../hooks/useRuns";
import { formatPercent } from "../utils/formatStatus";

export default function DashboardPage() {
  const summary = useDashboardSummary();
  const runs = useRuns();

  if (summary.isLoading) return <LoadingState />;
  if (summary.isError) return <ErrorMessage error={summary.error} />;
  const s = summary.data!;

  return (
    <>
      <PageHeader title="Dashboard" description="Overview of SentinelAI test activity, findings, and audit integrity." />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total test runs" value={s.total_runs} icon={Activity} />
        <StatCard label="Pass rate" value={formatPercent(s.pass_rate)} icon={CheckCircle2} />
        <StatCard label="Open findings" value={s.open_findings} hint={`${s.critical_findings} critical`} icon={ShieldAlert} />
        <StatCard label="Models available" value={`${s.models_available} / ${s.models_total}`} icon={ShieldCheck} />
      </div>

      <div className="mt-6">
        <section className="panel p-4">
          <h2 className="mb-3 font-medium">Results over time</h2>
          <RunTrendChart data={s.trend} />
        </section>
      </div>
      <section className="panel mt-6">
        <div className="flex items-center justify-between p-4 pb-2">
          <h2 className="font-medium">Recent runs</h2>
          <Link to="/runs" className="text-sm text-brand underline">View all</Link>
        </div>
        {runs.isLoading ? <LoadingState /> : runs.isError ? <div className="p-4"><ErrorMessage error={runs.error} /></div> : <RecentRunsTable runs={(runs.data ?? []).slice(0, 5)} />}
      </section>
    </>
  );
}
