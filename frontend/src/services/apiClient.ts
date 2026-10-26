import axios from "axios";
import { supabase } from "./supabase";

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1",
  headers: { "Content-Type": "application/json" },
  timeout: 30_000,
});

apiClient.interceptors.request.use(async (config) => {
  const { data, error } = await supabase.auth.getSession();

  if (error) {
    throw error;
  }

  const accessToken = data.session?.access_token;

  if (accessToken) {
    config.headers.set("Authorization", `Bearer ${accessToken}`);
  }

  return config;
});

/** Turns FastAPI errors into a readable message. */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      const messages = detail.map((item: unknown) => {
        if (typeof item === "string") return item;
        if (!item || typeof item !== "object") return "";
        const validation = item as { loc?: unknown; msg?: unknown };
        const message = typeof validation.msg === "string" ? validation.msg : "Invalid value";
        const location = Array.isArray(validation.loc)
          ? validation.loc.filter((part): part is string | number => typeof part === "string" || typeof part === "number").join(" → ")
          : "";
        return location ? `${location}: ${message}` : message;
      }).filter(Boolean);
      if (messages.length) return messages.join("; ");
    }
    if (detail && typeof detail === "object" && typeof detail.msg === "string") return detail.msg;
    if (!error.response) return "Cannot reach the SentinelAI backend. Check that it is running.";
    return `Request failed (${error.response.status}).`;
  }
  return error instanceof Error ? error.message : "Something went wrong.";
}
