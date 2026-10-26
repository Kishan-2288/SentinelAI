import type { AuditEvent } from "../../types/audit";

/** Checks that each event's previous_hash equals the prior event's event_hash (sorted by sequence). */
export function findBrokenLinks(events: AuditEvent[]): Set<string | number> {
  const sorted = [...events].sort((a, b) => a.sequence - b.sequence);
  const broken = new Set<string | number>();
  for (let i = 1; i < sorted.length; i++) {
    if (sorted[i].previous_hash !== sorted[i - 1].event_hash) broken.add(sorted[i].id);
  }
  return broken;
}
