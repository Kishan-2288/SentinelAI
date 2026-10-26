export type ProviderType = "ollama" | "external";

export interface ModelConfig {
  id: number | null;
  provider: string;
  model: string;
  display_name: string | null;
  source: "registry" | "live" | "environment";
  available: boolean | null;
  default: boolean;
  enabled: boolean;
  base_url: string | null;
  secret_configured: boolean;
}
