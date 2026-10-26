import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import PageHeader from "../components/layout/PageHeader";
import LoadingState from "../components/common/LoadingState";
import ErrorMessage from "../components/common/ErrorMessage";
import { useModels } from "../features/models/useModels";
import { useCreateRun } from "../hooks/useRuns";
import { createRunSchema } from "../features/runs/runSchema";
import { useTestSuites } from "../features/test-suites/useTestSuites";

export default function CreateRunPage() {
  const navigate = useNavigate();
  const models = useModels();
  const suites = useTestSuites();
  const create = useCreateRun();
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [selectedSuiteId, setSelectedSuiteId] = useState("");

  if (models.isLoading || suites.isLoading) return <LoadingState />;
  if (models.isError) return <ErrorMessage error={models.error} />;
  if (suites.isError) return <ErrorMessage error={suites.error} />;
  const enabled = (models.data ?? []).filter((m) => m.enabled && m.available !== false);
  const availableSuites = suites.data ?? [];
  const selectedSuite = availableSuites.find((suite) => suite.id === selectedSuiteId) ?? availableSuites[0];

  function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const parsed = createRunSchema.safeParse(Object.fromEntries(new FormData(e.currentTarget)));
    if (!parsed.success) {
      const next: Record<string, string> = {};
      parsed.error.issues.forEach((i) => { next[String(i.path[0])] = i.message; });
      setErrors(next);
      return;
    }
    setErrors({});
    const v = parsed.data;
    const model = enabled.find((m) => `${m.provider}:${m.model}` === v.modelId)!;
    create.mutate(
      {
        name: v.name,
        provider: model.provider,
        model: model.model,
        suite_id: v.suite_id,
        config: {
          temperature: v.temperature,
          max_tokens: v.max_tokens,
          timeout_seconds: v.timeout_seconds,
        },
      },
      { onSuccess: (run) => navigate(`/runs/${run.id}`) }
    );
  }

  const Err = ({ k }: { k: string }) => (errors[k] ? <span className="mt-1 block text-xs text-danger">{errors[k]}</span> : null);

  return (
    <>
      <PageHeader title="Create test run" crumbs={[{ label: "Test runs", to: "/runs" }, { label: "New run" }]} description="Choose a model and any available test suite for the security evaluation." />
      <form onSubmit={onSubmit} className="panel max-w-2xl space-y-5 p-6" noValidate>
        <label className="block text-sm font-medium">Run name
          <input name="name" className="field mt-1" placeholder="Prompt injection check" /> <Err k="name" />
        </label>
        <label className="block text-sm font-medium">Test suite
          <select name="suite_id" className="field mt-1" value={selectedSuite?.id ?? ""} onChange={(e) => setSelectedSuiteId(e.target.value)}>
            {availableSuites.map((suite) => <option key={suite.id} value={suite.id}>{suite.name} ({suite.cases.length} tests)</option>)}
          </select>
          <Err k="suite_id" />
          {availableSuites.length === 0 && <span className="mt-1 block text-xs text-warn">No test suites are available.</span>}
        </label>
        {selectedSuite && (
          <section className="rounded-xl border border-line bg-canvas p-4" aria-live="polite">
            <h2 className="font-medium">{selectedSuite.cases.length} test cases available to run</h2>
            <p className="mt-1 text-sm text-muted">Included in {selectedSuite.name}</p>
            <ul className="mt-3 list-inside list-disc space-y-1 text-sm">
              {selectedSuite.cases.map((testCase) => <li key={testCase.id}>{testCase.title}</li>)}
            </ul>
          </section>
        )}
        <div className="grid gap-5">
          <label className="block text-sm font-medium">Model
            <select name="modelId" className="field mt-1" defaultValue="">
              <option value="" disabled>Select a model</option>
              {enabled.map((m) => <option key={`${m.provider}:${m.model}`} value={`${m.provider}:${m.model}`}>{m.provider} / {m.display_name || m.model}</option>)}
            </select>
            <Err k="modelId" />
            {enabled.length === 0 && <span className="mt-1 block text-xs text-warn">No enabled models are available. Enable one on the Models page.</span>}
          </label>
        </div>
        <fieldset className="grid gap-5 sm:grid-cols-3">
          <legend className="mb-2 text-sm font-medium">Test configuration</legend>
          <label className="block text-sm">Temperature<input name="temperature" type="number" step="0.1" defaultValue={0} className="field mt-1" /><Err k="temperature" /></label>
          <label className="block text-sm">Max tokens<input name="max_tokens" type="number" defaultValue={512} className="field mt-1" /><Err k="max_tokens" /></label>
          <label className="block text-sm">Timeout (seconds)<input name="timeout_seconds" type="number" defaultValue={60} className="field mt-1" /><Err k="timeout_seconds" /></label>
        </fieldset>
        {create.isError && <ErrorMessage error={create.error} title="Could not start the run" />}
        <div className="flex gap-3">
          <button type="submit" className="btn btn-primary" disabled={create.isPending}>{create.isPending ? "Starting…" : "Start run"}</button>
          <button type="button" className="btn btn-secondary" onClick={() => navigate("/runs")}>Cancel</button>
        </div>
      </form>
    </>
  );
}
