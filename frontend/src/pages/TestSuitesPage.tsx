import { useState } from "react";
import PageHeader from "../components/layout/PageHeader";
import LoadingState from "../components/common/LoadingState";
import ErrorMessage from "../components/common/ErrorMessage";
import EmptyState from "../components/common/EmptyState";
import DataTable from "../components/common/DataTable";
import SeverityBadge from "../components/findings/SeverityBadge";
import { useTestSuites } from "../features/test-suites/useTestSuites";
import { titleCase } from "../utils/formatStatus";
import { formatDateTime } from "../utils/formatDate";

export default function TestSuitesPage() {
  const { data, isLoading, isError, error } = useTestSuites();
  const [selected, setSelected] = useState<string | null>(null);
  if (isLoading) return <LoadingState />;
  if (isError) return <ErrorMessage error={error} />;
  const suites = data ?? [];
  const current = suites.find((s) => s.id === selected) ?? suites[0];

  return (
    <>
      <PageHeader title="Test suites" description="Reusable groups of prompt-injection, refusal, and other security test cases." />
      {suites.length === 0 ? <div className="panel"><EmptyState title="No test suites" hint="Add suites in the backend to make them available for runs." /></div> : (
        <div className="grid gap-4 lg:grid-cols-[280px_1fr]">
          <ul className="panel divide-y divide-line self-start">
            {suites.map((s) => (
              <li key={s.id}>
                <button onClick={() => setSelected(s.id)} aria-current={current?.id === s.id} className={`w-full p-4 text-left hover:bg-canvas ${current?.id === s.id ? "bg-brand-soft" : ""}`}>
                  <p className="font-medium">{s.name}</p>
                  <p className="text-xs text-muted">{s.cases.length} cases · updated {formatDateTime(s.updated_at)}</p>
                </button>
              </li>
            ))}
          </ul>
          {current && (
            <section className="panel">
              <div className="p-4 pb-2"><h2 className="font-medium">{current.name}</h2><p className="text-sm text-muted">{current.description}</p></div>
              <DataTable
                rows={current.cases}
                rowKey={(c) => c.id}
                columns={[
                  { key: "title", header: "Case", render: (c) => <div><p className="font-medium">{c.title}</p><p className="mt-0.5 text-xs text-muted">{c.evaluation_criteria}</p></div> },
                  { key: "cat", header: "Category", render: (c) => titleCase(c.category) },
                  { key: "exp", header: "Expected behavior", render: (c) => c.expected_behavior },
                  { key: "sev", header: "Severity", render: (c) => <SeverityBadge severity={c.severity} /> },
                  { key: "kw", header: "Keywords", render: (c) => <span className="font-mono text-xs">{c.keywords.join(", ") || "—"}</span> },
                ]}
              />
            </section>
          )}
        </div>
      )}
    </>
  );
}
