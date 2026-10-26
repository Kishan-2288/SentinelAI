import type { LucideIcon } from "lucide-react";

export default function StatCard({ label, value, hint, icon: Icon }: {
  label: string; value: string | number; hint?: string; icon: LucideIcon;
}) {
  return (
    <div className="panel p-4">
      <div className="flex items-center justify-between text-sm text-muted">
        {label} <Icon className="h-4 w-4" aria-hidden />
      </div>
      <p className="mt-2 text-3xl font-semibold tracking-tight">{value}</p>
      {hint && <p className="mt-1 text-xs text-muted">{hint}</p>}
    </div>
  );
}
