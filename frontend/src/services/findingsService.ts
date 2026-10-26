import { apiClient } from "./apiClient";
import type { Finding, FindingFilters, ReviewOutcome } from "../types/finding";

export const listFindings = async (filters: FindingFilters = {}) =>
  (await apiClient.get<Finding[]>("/findings", { params: filters })).data;

export const reviewFinding = async (id: string | number, outcome: ReviewOutcome, notes?: string) =>
  (await apiClient.patch<Finding>(`/findings/${id}`, { review_outcome: outcome, reviewer_notes: notes })).data;
