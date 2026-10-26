import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createModel,
  listModels,
  setModelEnabled,
  updateModel,
  type CreateModelInput,
  type UpdateModelInput,
} from "../../services/modelsService";

export const useModels = () =>
  useQuery({ queryKey: ["models"], queryFn: listModels });

export function useCreateModel() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (payload: CreateModelInput) => createModel(payload),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["models"] }),
  });
}

export function useToggleModel() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (v: { id: number; enabled: boolean }) =>
      setModelEnabled(String(v.id), v.enabled),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["models"] }),
  });
}

export function useUpdateModel() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (v: { id: number; changes: UpdateModelInput }) =>
      updateModel(String(v.id), v.changes),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["models"] }),
  });
}
