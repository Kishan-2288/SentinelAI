import type { Run, RunStatus } from "../../types/run";

export function filterRuns(runs: Run[], search: string, status: RunStatus | "all"): Run[] {
  const q = search.trim().toLowerCase();
  return runs.filter(
    (r) =>
      (status === "all" || r.status === status) &&
      (!q || [r.name, r.model, r.provider, r.id].some((v) => v.toLowerCase().includes(q)))
  );
}
