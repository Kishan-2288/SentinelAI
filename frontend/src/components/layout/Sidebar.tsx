import { NavLink } from "react-router-dom";
import { Activity, Boxes, ClipboardList, Cpu, LayoutDashboard, ScrollText, Settings, ShieldAlert, ShieldCheck, X } from "lucide-react";

const nav = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/runs", label: "Test runs", icon: Activity },
  { to: "/test-suites", label: "Test suites", icon: ClipboardList },
  { to: "/findings", label: "Findings", icon: ShieldAlert },
  { to: "/models", label: "Models", icon: Cpu },
  { to: "/audit", label: "Audit logs", icon: ScrollText },
  { to: "/settings", label: "Settings", icon: Settings },
];

interface SidebarProps {
  collapsed: boolean;
  mobileOpen: boolean;
  onNavigate: () => void;
}

export default function Sidebar({ collapsed, mobileOpen, onNavigate }: SidebarProps) {
  return (
    <>
      {mobileOpen && <button type="button" aria-label="Close navigation menu" className="fixed inset-0 z-40 bg-black/60" onClick={onNavigate} />}
      <aside aria-label="Sidebar" aria-hidden={!mobileOpen} className={`fixed inset-y-0 left-0 z-50 flex w-60 shrink-0 flex-col border-r border-white/5 bg-ink-soft text-white transition-transform duration-200 ${mobileOpen ? "translate-x-0" : "-translate-x-full"}`}>
      <div className={`flex h-20 shrink-0 items-center ${collapsed ? "md:justify-center md:px-2" : "gap-2.5 px-5"}`}>
        <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand text-ink shadow-lg shadow-brand/10">
          <ShieldCheck className="h-5 w-5" aria-hidden />
        </span>
        <span className={`${collapsed ? "md:hidden" : ""} text-lg font-semibold tracking-tight`}>SentinelAI</span>
        <button type="button" className="icon-button ml-auto text-white md:hidden" aria-label="Close navigation menu" onClick={onNavigate}><X className="h-5 w-5" aria-hidden /></button>
      </div>
      <nav aria-label="Main" className="flex-1 space-y-1 px-3">
        {nav.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            title={collapsed ? label : undefined}
            onClick={onNavigate}
            className={({ isActive }) =>
              `group flex items-center rounded-xl border border-transparent py-2.5 text-sm transition-all duration-150 ${collapsed ? "md:justify-center md:px-0" : "gap-3 px-3"} ${isActive ? "bg-canvas text-white shadow-inner shadow-black/20" : "text-white/60 hover:border-white/5 hover:bg-canvas/70 hover:text-white"}`
            }
          >
            <Icon className="h-4 w-4 shrink-0 transition-transform duration-150 group-hover:scale-110 group-hover:text-brand" aria-hidden /> <span className={collapsed ? "md:hidden" : ""}>{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className={`flex items-center border-t border-white/10 py-4 text-xs text-white/50 ${collapsed ? "md:justify-center md:px-2" : "gap-2 px-5"}`} title={collapsed ? "AI security testing" : undefined}>
        <Boxes className="h-3.5 w-3.5 shrink-0" aria-hidden /> <span className={collapsed ? "md:hidden" : ""}>AI security testing</span>
      </div>
      </aside>
    </>
  );
}
