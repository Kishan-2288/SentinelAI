import { useQuery } from "@tanstack/react-query";
import { getBackendHealth, getDashboardSummary } from "../services/dashboardService";

export const useDashboardSummary = () =>
  useQuery({ queryKey: ["dashboard-summary"], queryFn: getDashboardSummary, refetchInterval: 30_000 });

export const useBackendHealth = () =>
  useQuery({ queryKey: ["health"], queryFn: getBackendHealth, refetchInterval: 15_000, retry: 0 });
