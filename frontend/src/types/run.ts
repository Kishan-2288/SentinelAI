import type { Severity } from "./finding";

export type RunStatus = "queued" | "running" | "completed" | "completed_with_errors" | "failed" | "cancelled";
export type CaseOutcome = "pass" | "fail" | "needs_review" | "error";

export interface RunConfig {
  temperature: number;
  max_tokens: number;
  timeout_seconds: number;
}

export interface CaseResult {
  id: string;
  test_case_id: string;
  category: string;
  prompt: string;
  response: string;
  expected_behavior: string;
  actual_behavior: string;
  error_message?: string | null;
  outcome: CaseOutcome;
  latency_ms: number;
  finding_id?: string | null;
}

export interface Run {
  id: string;
  name: string;
  provider: string;
  model: string;
  suite_id: string | null;
  suite_name?: string | null;
  suite_version?: string | null;
  status: RunStatus;
  total_cases: number;
  completed_cases: number;
  passed_cases: number;
  failed_cases: number;
  created_at: string;
  started_at?: string | null;
  finished_at?: string | null;
  config?: RunConfig;
  results?: CaseResult[];
}

export interface CreateRunPayload {
  name: string;
  provider: string;
  model: string;
  suite_id?: string;
  config?: RunConfig;
}

export interface TestCase {
  id: string;
  title: string;
  category: "prompt_injection" | "refusal" | "data_leakage" | "jailbreak" | "other";
  prompt: string;
  expected_behavior: string;
  evaluation_criteria: string;
  severity: Severity;
  keywords: string[];
}

export interface TestSuite {
  id: string;
  name: string;
  description: string;
  cases: TestCase[];
  updated_at: string;
}
