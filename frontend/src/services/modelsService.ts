import { apiClient } from "./apiClient";
import type { ModelConfig, ProviderType } from "../types/model";

export interface CreateModelInput {
  provider: ProviderType;
  model: string;
  display_name?: string | null;
  enabled: boolean;
  base_url?: string | null;
  api_key?: string;
  settings?: Record<string, number>;
}

export interface UpdateModelInput {
  display_name?: string | null;
  base_url?: string | null;
  api_key?: string;
}

export const listModels = async () =>
  (await apiClient.get<{ models: ModelConfig[]; warnings: string[] }>("/models")).data.models;

export const createModel = async (payload: CreateModelInput) =>
  (await apiClient.post<ModelConfig>("/model-configs", payload)).data;

export const setModelEnabled = async (id: string, enabled: boolean) =>
  (await apiClient.patch<ModelConfig>(`/model-configs/${id}`, { enabled })).data;

export const updateModel = async (id: string, payload: UpdateModelInput) =>
  (await apiClient.patch<ModelConfig>(`/model-configs/${id}`, payload)).data;
