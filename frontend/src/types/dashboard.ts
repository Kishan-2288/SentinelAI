export interface DashboardSummary {
  total_runs: number;
  pass_rate: number | null;
  open_findings: number;
  critical_findings: number;
  trend: {
    date: string;
    passed: number;
    failed: number;
    review: number;
    errors: number;
    pending: number;
  }[];
  models_available: number;
  models_total: number;
  available_models: number;
  evaluated_results: number;
}

export interface BackendHealth {
  status: "ok" | "degraded" | "down";
  database?: boolean;
  ollama?: boolean;
  version?: string;
}
