import { Navigate, Route, Routes } from "react-router-dom";
import type { ReactNode } from "react";
import { useAuth } from "./AuthProvider";
import AppLayout from "./AppLayout";
import LoginPage from "../pages/LoginPage";
import DashboardPage from "../pages/DashboardPage";
import RunsPage from "../pages/RunsPage";
import CreateRunPage from "../pages/CreateRunPage";
import RunDetailsPage from "../pages/RunDetailsPage";
import TestSuitesPage from "../pages/TestSuitesPage";
import FindingsPage from "../pages/FindingsPage";
import ModelsPage from "../pages/ModelsPage";
import AuditLogsPage from "../pages/AuditLogsPage";
import AuditEventDetailsPage from "../pages/AuditEventDetailsPage";
import SettingsPage from "../pages/SettingsPage";
import NotFoundPage from "../pages/NotFoundPage";

function RequireAuth({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        Loading SentinelAI...
      </div>
    );
  }

  if (!user) return <Navigate to="/login" replace />;

  return children;
}

export function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route
        element={
          <RequireAuth>
            <AppLayout />
          </RequireAuth>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/runs" element={<RunsPage />} />
        <Route path="/runs/new" element={<CreateRunPage />} />
        <Route path="/runs/:runId" element={<RunDetailsPage />} />
        <Route path="/test-suites" element={<TestSuitesPage />} />
        <Route path="/findings" element={<FindingsPage />} />
        <Route path="/models" element={<ModelsPage />} />
        <Route path="/audit" element={<AuditLogsPage />} />
        <Route path="/audit/:eventId" element={<AuditEventDetailsPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
