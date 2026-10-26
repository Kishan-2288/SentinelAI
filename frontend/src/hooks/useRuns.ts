import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { cancelRun, createRun, getRun, listRuns } from "../services/runsService";
import type { Run } from "../types/run";

const isActive = (r?: Run) => r?.status === "queued" || r?.status === "running";

export const useRuns = () =>
  useQuery({
    queryKey: ["runs"],
    queryFn: listRuns,
    refetchInterval: (q) => (q.state.data?.some(isActive) ? 4_000 : false),
  });

export const useRun = (id: string) =>
  useQuery({
    queryKey: ["runs", id],
    queryFn: () => getRun(id),
    enabled: Boolean(id),
    refetchInterval: (q) => (isActive(q.state.data) ? 3_000 : false),
  });

export function useCreateRun() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createRun,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["runs"] });
      qc.invalidateQueries({ queryKey: ["dashboard-summary"] });
    },
  });
}

export function useCancelRun() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: cancelRun,
    onSuccess: (run) => qc.invalidateQueries({ queryKey: ["runs", run.id] }),
  });
}
