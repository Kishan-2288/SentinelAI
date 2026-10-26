import { apiClient } from "./apiClient";
import type { CreateRunPayload, Run, TestSuite } from "../types/run";

type ApiCase = {
  id: number;
  case_key: string;
  category: string;
  prompt: string;
  response: string;
  expected_behavior: string;
  outcome: Run["results"] extends Array<infer R> ? R extends { outcome: infer O } ? O : never : never;
  outcome_reason?: string | null;
  error_message?: string | null;
  latency_ms: number;
  findings?: { id: number }[];
};

type ApiRun = {
  id: number;
  name: string;
  provider: string;
  model: string;
  suite_id?: number | null;
  suite_name?: string | null;
  suite_version?: string;
  status: Run["status"];
  created_at: string;
  started_at?: string | null;
  completed_at?: string | null;
  cases?: ApiCase[];
  case_count?: number;
  outcome_counts?: Record<string, number>;
};

const toRun = (value: ApiRun): Run => {
  const cases = value.cases ?? [];
  const results = cases.map((c) => ({
    id: String(c.id),
    test_case_id: c.case_key,
    category: c.category,
    prompt: c.prompt,
    response: c.response,
    expected_behavior: c.expected_behavior,
    actual_behavior: c.outcome_reason ?? c.outcome,
    error_message: c.error_message,
    outcome: c.outcome,
    latency_ms: c.latency_ms,
    finding_id: c.findings?.[0] ? String(c.findings[0].id) : null,
  }));
  const counts = value.outcome_counts ?? {};
  return {
    id: String(value.id),
    name: value.name,
    provider: value.provider,
    model: value.model,
    suite_id: value.suite_id == null ? null : String(value.suite_id),
    suite_name: value.suite_name ?? value.suite_version ?? null,
    suite_version: value.suite_version ?? null,
    status: value.status,
    total_cases: value.case_count ?? results.length,
    completed_cases: results.filter((r) => r.outcome !== "pending").length,
    passed_cases: counts.pass ?? results.filter((r) => r.outcome === "pass").length,
    failed_cases: counts.fail ?? results.filter((r) => r.outcome === "fail").length,
    created_at: value.created_at,
    started_at: value.started_at,
    finished_at: value.completed_at,
    results,
  };
};

export const listRuns = async () => (await apiClient.get<ApiRun[]>("/runs")).data.map(toRun);
export const getRun = async (id: string) => toRun((await apiClient.get<ApiRun>(`/runs/${id}`)).data);
export const createRun = async (payload: CreateRunPayload) =>
  toRun((await apiClient.post<ApiRun>("/runs", payload)).data);
export const cancelRun = async (id: string) =>
  toRun((await apiClient.post<ApiRun>(`/runs/${id}/cancel`)).data);

export const listTestSuites = async () => (await apiClient.get<TestSuite[]>("/test-suites")).data;
