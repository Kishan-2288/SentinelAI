import { apiClient } from "./apiClient";
import type { AuditEvent, ChainVerification } from "../types/audit";

export const listAuditEvents = async () => (await apiClient.get<AuditEvent[]>("/audit/events")).data;
export const getAuditEvent = async (id: string) =>
  (await apiClient.get<AuditEvent>(`/audit/events/${id}`)).data;
export const verifyAuditChain = async () =>
  (await apiClient.get<ChainVerification>("/audit/verify")).data;
