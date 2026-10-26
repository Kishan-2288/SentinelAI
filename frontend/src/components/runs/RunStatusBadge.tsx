import type { RunStatus } from "../../types/run";
import { runStatusLabel } from "../../utils/formatStatus";

const styles: Record<RunStatus, string> = {
  queued: "bg-canvas text-muted border-line",
  running: "bg-info-soft text-info border-info/30",
  completed: "bg-ok-soft text-ok border-ok/30",
  completed_with_errors: "bg-warn-soft text-warn border-warn/30",
  failed: "bg-danger-soft text-danger border-danger/30",
  cancelled: "bg-warn-soft text-warn border-warn/30",
};

export default function RunStatusBadge({ status }: { status: RunStatus }) {
  return <span className={`inline-block rounded border px-2 py-0.5 text-xs font-medium ${styles[status]}`}>{runStatusLabel[status]}</span>;
}
