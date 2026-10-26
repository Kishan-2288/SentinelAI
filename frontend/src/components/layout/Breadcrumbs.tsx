import { Link } from "react-router-dom";
import { ChevronRight } from "lucide-react";

export interface Crumb { label: string; to?: string }

export default function Breadcrumbs({ items }: { items: Crumb[] }) {
  return (
    <nav aria-label="Breadcrumb" className="mb-2 flex items-center gap-1 text-sm text-muted">
      {items.map((c, i) => (
        <span key={c.label} className="flex items-center gap-1">
          {i > 0 && <ChevronRight className="h-3.5 w-3.5" aria-hidden />}
          {c.to ? <Link to={c.to} className="hover:text-ink">{c.label}</Link> : <span className="text-ink">{c.label}</span>}
        </span>
      ))}
    </nav>
  );
}
