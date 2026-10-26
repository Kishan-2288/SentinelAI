export type Severity = "critical" | "high" | "medium" | "low" | "info";
export type ReviewOutcome = "unreviewed" | "confirmed" | "false_positive" | "accepted_risk";

export interface Finding {
  id: string | number;
  title: string;
  severity: Severity;
  category: string;
  evidence: string;
  run_id: string | number;
  test_case_id: string;
  review_outcome: ReviewOutcome;
  reviewer_notes?: string | null;
  created_at: string;
  rule: string;
  run_name: string;
}

export interface FindingFilters {
  severity?: Severity | "";
  category?: string;
  review_outcome?: ReviewOutcome | "";
}
