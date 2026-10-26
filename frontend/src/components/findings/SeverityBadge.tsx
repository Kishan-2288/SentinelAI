import type { Severity } from "../../types/finding";
import { titleCase } from "../../utils/formatStatus";

const styles: Record<Severity, string> = {
  critical: "bg-danger text-white",
  high: "bg-danger-soft text-danger",
  medium: "bg-warn-soft text-warn",
  low: "bg-info-soft text-info",
  info: "bg-canvas text-muted",
};

export default function SeverityBadge({ severity }: { severity: Severity }) {
  return <span className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${styles[severity]}`}>{titleCase(severity)}</span>;
}
