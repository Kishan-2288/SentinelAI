import { AlertTriangle } from "lucide-react";
import { getErrorMessage } from "../../services/apiClient";

export default function ErrorMessage({ error, title = "Could not load data" }: { error: unknown; title?: string }) {
  return (
    <div role="alert" className="flex gap-3 rounded-lg border border-danger/30 bg-danger-soft p-4 text-sm text-danger">
      <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden />
      <div>
        <p className="font-medium">{title}</p>
        <p>{getErrorMessage(error)}</p>
      </div>
    </div>
  );
}
