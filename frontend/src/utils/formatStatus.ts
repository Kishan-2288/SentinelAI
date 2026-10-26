import type { RunStatus } from "../types/run";
import type { Severity } from "../types/finding";

export const runStatusLabel: Record<RunStatus, string> = {
  queued: "Queued",
  running: "Running",
  completed: "Completed",
  completed_with_errors: "Completed with errors",
  failed: "Failed",
  cancelled: "Cancelled",
};

export const severityOrder: Severity[] = ["critical", "high", "medium", "low", "info"];

export function titleCase(value: string | null | undefined): string {
  if (!value) return "Unknown";
  return value.replace(/_/g, " ").replace(/^\w/, (c) => c.toUpperCase());
}

export function formatPercent(value: number | null | undefined): string {
  if (value == null || !Number.isFinite(value)) {
    return "N/A";
  }

  return `${Math.round(value * 10) / 10}%`;
}

export function shortHash(hash: string, size = 10): string {
  return hash.length > size * 2 ? `${hash.slice(0, size)}…${hash.slice(-6)}` : hash;
}
