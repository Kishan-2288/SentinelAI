import { useMutation, useQuery } from "@tanstack/react-query";
import { getAuditEvent, listAuditEvents, verifyAuditChain } from "../services/auditService";

export const useAuditEvents = () => useQuery({ queryKey: ["audit", "events"], queryFn: listAuditEvents });

export const useAuditEvent = (id: string) =>
  useQuery({ queryKey: ["audit", "events", id], queryFn: () => getAuditEvent(id), enabled: Boolean(id) });

export const useChainVerification = () =>
  useQuery({ queryKey: ["audit", "verify"], queryFn: verifyAuditChain, retry: 0 });

export const useVerifyChain = () => useMutation({ mutationFn: verifyAuditChain });
