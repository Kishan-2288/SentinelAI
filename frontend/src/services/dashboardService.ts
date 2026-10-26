import { apiClient } from "./apiClient";
import type { BackendHealth, DashboardSummary } from "../types/dashboard";

export const getDashboardSummary = async () =>
  (await apiClient.get<DashboardSummary>("/dashboard/summary")).data;

export const getBackendHealth = async () =>
  (await apiClient.get<BackendHealth>("/health")).data;
