import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { listFindings, reviewFinding } from "../../services/findingsService";
import type { FindingFilters, ReviewOutcome } from "../../types/finding";

export const useFindings = (filters: FindingFilters) =>
  useQuery({ queryKey: ["findings", filters], queryFn: () => listFindings(filters) });

export function useReviewFinding() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (v: { id: string | number; outcome: ReviewOutcome; notes?: string }) =>
      reviewFinding(v.id, v.outcome, v.notes),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["findings"] });
      qc.invalidateQueries({ queryKey: ["dashboard-summary"] });
    },
  });
}
