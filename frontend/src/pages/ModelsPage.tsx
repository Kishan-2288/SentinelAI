import { useState, type FormEvent } from "react";
import { KeyRound, Plus, X } from "lucide-react";
import PageHeader from "../components/layout/PageHeader";
import LoadingState from "../components/common/LoadingState";
import ErrorMessage from "../components/common/ErrorMessage";
import EmptyState from "../components/common/EmptyState";
import DataTable from "../components/common/DataTable";
import { useCreateModel, useModels, useToggleModel } from "../features/models/useModels";
import { getErrorMessage } from "../services/apiClient";
import type { ProviderType } from "../types/model";

export default function ModelsPage() {
  const { data, isLoading, isError, error } = useModels();
  const toggle = useToggleModel();
  const create = useCreateModel();

  const [showForm, setShowForm] = useState(false);
  const [provider, setProvider] = useState<ProviderType>("ollama");
  const [model, setModel] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [baseUrl, setBaseUrl] = useState("http://localhost:11434");
  const [apiKey, setApiKey] = useState("");
  const [enabled, setEnabled] = useState(true);
  const [formError, setFormError] = useState("");

  if (isLoading) return <LoadingState />;
  if (isError) return <ErrorMessage error={error} />;

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError("");
    const modelName = model.trim();
    if (!modelName) {
      setFormError("Enter a model name.");
      return;
    }

    if (provider === "external" && !baseUrl.trim().startsWith("https://")) {
      setFormError("External provider URLs must start with https://.");
      return;
    }

    create.mutate(
      {
        provider,
        model: modelName,
        display_name: displayName.trim() || null,
        enabled,
        base_url: baseUrl.trim() || null,
        ...(provider === "external" && apiKey.trim() ? { api_key: apiKey.trim() } : {}),
      },
      {
        onSuccess: () => {
          setModel("");
          setDisplayName("");
          setApiKey("");
          setShowForm(false);
        },
        onError: (err) => {
          const response = err as {
            response?: { status?: number };
          };
          setFormError(
            response.response?.status === 403
              ? "You are not allowed to register this model."
              : getErrorMessage(err),
          );
        },
      },
    );
  }

  return (
    <>
      <PageHeader
        title="Models"
        description="Local Ollama models and external API providers available for test runs. External API keys are encrypted before they are stored on the backend."
      />
      <div className="mb-4 flex justify-end">
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => {
            setFormError("");
            setShowForm((value) => !value);
          }}
        >
          {showForm ? <X className="mr-2 inline h-4 w-4" /> : <Plus className="mr-2 inline h-4 w-4" />}
          {showForm ? "Cancel" : "Add model"}
        </button>
      </div>

      {showForm && (
        <form onSubmit={onSubmit} className="panel mb-5 max-w-2xl space-y-4 p-6">
          <h2 className="text-lg font-semibold">Register a model</h2>

          <label className="block text-sm font-medium">
            Provider
            <select
              className="field mt-1"
              value={provider}
              onChange={(event) => {
                const next = event.target.value as ProviderType;
                setProvider(next);
                setBaseUrl(next === "ollama" ? "http://localhost:11434" : "https://api.openai.com/v1");
              }}
            >
              <option value="ollama">Ollama (local)</option>
              <option value="external">External API</option>
            </select>
          </label>

          <label className="block text-sm font-medium">
            Model identifier
            <input
              className="field mt-1"
              value={model}
              onChange={(event) => setModel(event.target.value)}
              placeholder={provider === "ollama" ? "qwen2.5:3b" : "your-model-id"}
              required
            />
          </label>

          <label className="block text-sm font-medium">
            Display name (optional)
            <input
              className="field mt-1"
              value={displayName}
              onChange={(event) => setDisplayName(event.target.value)}
              placeholder="Friendly model name"
            />
          </label>

          <label className="block text-sm font-medium">
            Base URL
            <input className="field mt-1" type="url" value={baseUrl} onChange={(event) => setBaseUrl(event.target.value)} required />
          </label>

          {provider === "external" && (
            <label className="block text-sm font-medium">
              API key (optional)
              <input
                className="field mt-1"
                type="password"
                autoComplete="new-password"
                value={apiKey}
                onChange={(event) => setApiKey(event.target.value)}
                placeholder="Paste provider API key"
              />
              <span className="mt-1 block text-xs text-muted">
                The key is sent only to the backend and is never returned by the API. Leave blank to use the backend environment key.
              </span>
            </label>
          )}

          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={enabled} onChange={(event) => setEnabled(event.target.checked)} />
            Enable for test runs
          </label>

          {formError && <p className="text-sm text-danger">{formError}</p>}
          {create.isError && !formError && <ErrorMessage error={create.error} title="Could not register model" />}

          <button type="submit" className="btn btn-primary" disabled={create.isPending}>
            {create.isPending ? "Registering..." : "Register model"}
          </button>
        </form>
      )}

      <div className="panel">
        <DataTable
          rows={data ?? []}
          rowKey={(m) => `${m.provider}:${m.model}`}
          empty={<EmptyState title="No models discovered" hint="Check that Ollama is running, or register a model." />}
          columns={[
            {
              key: "name",
              header: "Model",
              render: (m) => <span className="font-medium">{m.display_name || m.model}{m.default ? " (default)" : ""}</span>,
            },
            {
              key: "provider",
              header: "Provider",
              render: (m) => `${m.provider} (${m.provider === "ollama" ? "local" : "external API"})`,
            },
            {
              key: "avail",
              header: "Availability",
              render: (m) => (
                <span className={m.available === false ? "text-danger" : "text-ok"}>
                  {m.available === false ? "Unavailable" : m.available === null ? "Managed externally" : "Available"}
                </span>
              ),
            },
            { key: "endpoint", header: "Endpoint", render: (m) => <span className="font-mono text-xs">{m.base_url ?? "-"}</span> },
            {
              key: "secret",
              header: "Secret",
              render: (m) => m.secret_configured ? (
                <span className="flex items-center gap-1 font-mono text-xs"><KeyRound className="h-3.5 w-3.5" aria-hidden />Configured</span>
              ) : "None",
            },
            {
              key: "enabled",
              header: "Enabled",
              render: (m) => (
                <label className="inline-flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={m.enabled}
                    disabled={toggle.isPending || m.id === null}
                    onChange={(event) => m.id !== null && toggle.mutate({ id: m.id, enabled: event.target.checked })}
                  />
                  {m.id === null ? m.source : m.enabled ? "On" : "Off"}
                </label>
              ),
            },
          ]}
        />
      </div>

      {toggle.isError && <div className="mt-4"><ErrorMessage error={toggle.error} title="Could not update the model" /></div>}
    </>
  );
}
