import { useState, type FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { ShieldCheck } from "lucide-react";
import { useAuth } from "../app/AuthProvider";
import { supabase } from "../services/supabase";

export default function LoginPage() {
  const { user, loading } = useAuth();
  const navigate = useNavigate();

  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        Checking your session...
      </div>
    );
  }

  if (user) return <Navigate to="/dashboard" replace />;

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setMessage("");

    try {
      if (isSignUp) {
        const { data, error: authError } = await supabase.auth.signUp({
          email: email.trim(),
          password,
        });

        if (authError) throw authError;

        if (!data.session) {
          setMessage(
            "Account created. Check your email for a confirmation link, then sign in."
          );
        } else {
          navigate("/dashboard", { replace: true });
        }
      } else {
        const { error: authError } = await supabase.auth.signInWithPassword({
          email: email.trim(),
          password,
        });

        if (authError) throw authError;
        navigate("/dashboard", { replace: true });
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Authentication failed. Please try again."
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-canvas px-4 py-10">
      <section className="panel w-full max-w-md p-8 shadow-sm">
        <div className="mb-8 flex flex-col items-center text-center">
          <div className="mb-4 rounded-xl bg-brand/10 p-3">
            <ShieldCheck className="h-8 w-8 text-brand" aria-hidden />
          </div>
          <h1 className="text-2xl font-semibold">SentinelAI</h1>
          <p className="mt-2 text-sm text-muted">
            {isSignUp
              ? "Create an account to get started"
              : "Sign in to your security dashboard"}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="mb-1 block text-sm font-medium">
              Email address
            </label>
            <input
              id="email"
              className="field"
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
              required
            />
          </div>

          <div>
            <label htmlFor="password" className="mb-1 block text-sm font-medium">
              Password
            </label>
            <input
              id="password"
              className="field"
              type="password"
              autoComplete={isSignUp ? "new-password" : "current-password"}
              minLength={6}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="At least 6 characters"
              required
            />
          </div>

          {error && (
            <p role="alert" className="rounded-md bg-red-50 p-3 text-sm text-red-700">
              {error}
            </p>
          )}

          {message && (
            <p role="status" className="rounded-md bg-green-50 p-3 text-sm text-green-800">
              {message}
            </p>
          )}

          <button
            type="submit"
            className="btn btn-primary w-full justify-center"
            disabled={busy}
          >
            {busy
              ? "Please wait..."
              : isSignUp
                ? "Create account"
                : "Sign in"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-muted">
          {isSignUp ? "Already have an account?" : "New to SentinelAI?"}{" "}
          <button
            type="button"
            className="font-medium text-brand underline"
            onClick={() => {
              setIsSignUp(!isSignUp);
              setError("");
              setMessage("");
            }}
          >
            {isSignUp ? "Sign in" : "Create an account"}
          </button>
        </p>

        <p className="mt-6 text-center text-xs text-muted">
          By continuing, you agree to use SentinelAI responsibly.
        </p>

        <div className="mt-4 text-center">
          <Link to="/login" className="text-xs text-muted hover:underline">
            SentinelAI Authentication
          </Link>
        </div>
      </section>
    </main>
  );
}
