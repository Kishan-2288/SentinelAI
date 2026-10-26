import type { Run } from "../../types/run";

export default function RunProgress({ run }: { run: Run }) {
  const pct = run.total_cases ? Math.round((run.completed_cases / run.total_cases) * 100) : 0;
  return (
    <div>
      <div className="mb-1 flex justify-between text-xs text-muted">
        <span>{run.completed_cases} of {run.total_cases} cases</span><span>{pct}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded bg-canvas" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
        <div className="h-full bg-brand" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
