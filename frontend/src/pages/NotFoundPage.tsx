import { Link } from "react-router-dom";
import EmptyState from "../components/common/EmptyState";

export default function NotFoundPage() {
  return (
    <div className="panel">
      <EmptyState title="Page not found" hint="This address does not match any SentinelAI page." action={<Link to="/dashboard" className="btn btn-primary">Go to dashboard</Link>} />
    </div>
  );
}
