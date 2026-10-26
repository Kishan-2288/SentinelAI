export interface AuditEvent {
  id: string | number;
  sequence: number;
  event_type: string;
  actor?: string | null;
  payload: Record<string, unknown>;
  previous_hash: string;
  event_hash: string;
  created_at: string;
  run_id?: number | null;
  run_name?: string | null;
  run_status?: string | null;
}

export interface ChainVerification {
  valid: boolean;
  checked_events: number;
  failed_event_id?: string | number | null;
  failed_sequence?: number | null;
  reason?: string | null;
  head_hash?: string | null;
  message?: string | null;
}
