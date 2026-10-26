import { Link, useNavigate } from "react-router-dom";
import { LogOut, PanelLeftClose, PanelLeftOpen, Plus, ShieldCheck } from "lucide-react";
import { useBackendHealth } from "../../hooks/useDashboard";
import { useAuth } from "../../app/AuthProvider";

interface TopbarProps {
  sidebarCollapsed: boolean;
  onToggleSidebar: () => void;
}

export default function Topbar({ sidebarCollapsed, onToggleSidebar }: TopbarProps) {
  const { data, isError } = useBackendHealth();
  const { signOut } = useAuth();
  const navigate = useNavigate();

  const status = isError ? "down" : data?.status ?? "degraded";
  const dot =
    status === "ok"
      ? "bg-ok"
      : status === "degraded"
        ? "bg-warn"
        : "bg-danger";
  const label =
    status === "ok"
      ? "Backend online"
      : status === "degraded"
        ? "Backend degraded"
        : "Backend offline";

  async function handleSignOut() {
    try {
      await signOut();
      navigate("/login", { replace: true });
    } catch (error) {
      console.error("Sign out failed:", error);
    }
  }

  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-line bg-surface/80 px-4 backdrop-blur-md md:px-6">
      <div className="flex items-center gap-2">
        <button type="button" className="icon-button" onClick={onToggleSidebar} aria-label={sidebarCollapsed ? "Open navigation menu" : "Close navigation menu"} title={sidebarCollapsed ? "Open navigation menu" : "Close navigation menu"}>
          {sidebarCollapsed ? <PanelLeftOpen className="h-5 w-5" aria-hidden /> : <PanelLeftClose className="h-5 w-5" aria-hidden />}
        </button>
        <div className="flex items-center gap-2 md:hidden">
          <ShieldCheck className="h-5 w-5 text-brand" aria-hidden />
          <span className="font-semibold">SentinelAI</span>
        </div>
      </div>
      <div className="hidden items-center gap-2 text-sm text-muted md:flex" title={label}>
        <span className={`h-2 w-2 rounded-full ${dot} shadow-[0_0_10px_currentColor]`} aria-hidden /> {label}
      </div>
      <div className="flex items-center gap-2 sm:gap-3">
        <Link to="/runs/new" className="btn btn-primary">
          <Plus className="h-4 w-4" aria-hidden />
          <span className="hidden sm:inline">New run</span>
        </Link>

        <button
          type="button"
          className="btn btn-secondary"
          onClick={handleSignOut}
          title="Sign out"
        >
          <LogOut className="h-4 w-4" aria-hidden />
          <span className="hidden sm:inline">Sign out</span>
        </button>
      </div>
    </header>
  );
}
