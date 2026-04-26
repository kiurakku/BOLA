import { FormEvent, useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

export function LoginPage() {
  const { user, login } = useAuth();
  const [username, setUsername] = useState("alice");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  if (user) {
    return <Navigate to="/lab" replace />;
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await login(username.trim(), password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Помилка входу");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid narrow">
      <section className="hero">
        <h1>Вхід у консоль звітів</h1>
        <p className="lede">
          Після автентифікації клієнт отримує JWT з клеймом <code>org_id</code>. Gateway перевіряє
          підпис і передає довірений ідентифікатор організації внутрішньому API — але якщо бекенд
          звітів не звіряє власника об’єкта, можливий <strong>BOLA / IDOR</strong>.
        </p>
      </section>

      <form className="card form-card" onSubmit={onSubmit}>
        <label className="field">
          <span>Користувач</span>
          <input
            autoComplete="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </label>
        <label className="field">
          <span>Пароль</span>
          <input
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        {error ? <div className="alert danger">{error}</div> : null}
        <button className="btn primary" type="submit" disabled={busy}>
          {busy ? "Вхід…" : "Увійти"}
        </button>
        <p className="hint">
          Облікові записи: <code>alice</code> (viewer, org 1), <code>bob</code> (viewer, org 2),{" "}
          <code>dana</code> (admin, org 1) — паролі в README репозиторію, лише для локального
          навчання.
        </p>
      </form>
    </div>
  );
}
