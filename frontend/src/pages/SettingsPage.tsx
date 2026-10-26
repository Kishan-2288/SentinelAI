import PageHeader from "../components/layout/PageHeader";
import { useAuth } from "../app/AuthProvider";

export default function SettingsPage() {
  const { user } = useAuth();
  const name =
    user?.user_metadata?.full_name ??
    user?.user_metadata?.name ??
    user?.user_metadata?.display_name;

  return (
    <>
      <PageHeader title="Settings" description="Your account details." />
      <section className="panel max-w-2xl p-4">
        <h2 className="mb-4 font-medium">User information</h2>
        <dl className="space-y-3 text-sm">
          <div className="flex flex-col gap-1 sm:flex-row sm:justify-between">
            <dt className="text-muted">Name</dt>
            <dd>{typeof name === "string" && name.trim() ? name : "Not provided"}</dd>
          </div>
          <div className="flex flex-col gap-1 sm:flex-row sm:justify-between">
            <dt className="text-muted">Email</dt>
            <dd>{user?.email ?? "Not available"}</dd>
          </div>
        </dl>
      </section>
    </>
  );
}
