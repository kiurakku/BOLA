import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiFetch, parseJson } from "../api/client";
import type { ReportListItem } from "../api/types";
import { useAuth } from "../auth/AuthContext";

export function DashboardPage() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [reports, setReports] = useState<ReportListItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [manualId, setManualId] = useState("201");
  const [q, setQ] = useState("");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setError(null);
      const params = new URLSearchParams();
      if (q.trim()) {
        params.set("q", q.trim());
      }
      const res = await apiFetch(`/api/reports${params.toString() ? `?${params}` : ""}`);
      if (!res.ok) {
        if (!cancelled) {
          setError("Не вдалося завантажити список звітів");
          setReports(null);
        }
        return;
      }
      const data = await parseJson<ReportListItem[]>(res);
      if (!cancelled) {
        setReports(data);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [q]);

  function onJump(e: FormEvent) {
    e.preventDefault();
    const id = Number(manualId);
    if (!Number.isFinite(id) || id <= 0) {
      return;
    }
    navigate(`/reports/${id}`);
  }

  return (
    <div className="grid">
      <div className="toolbar">
        <div>
          <h1>Звіти вашої організації</h1>
          <p className="muted">
            Ви увійшли як <strong>{user?.display_name}</strong> (org_id:{" "}
            <span className="mono">{user?.org_id}</span>). Список обмежений вашою org — це очікувана
            поведінка.
          </p>
        </div>
        <button type="button" className="btn ghost" onClick={() => logout()}>
          Вийти
        </button>
      </div>

      <section className="card lab-panel">
        <h2>Сценарій атаки (IDOR)</h2>
        <p>
          Зловмисник з автентифікованою сесією може підбирати числові ідентифікатори в URL, навіть
          якщо «чужі» звіти не показані в списку. Введіть ID і перейдіть на сторінку деталей — у
          режимі <code>REPORTS_AUTHZ_MODE=vulnerable</code> сервіс може віддати чужий об’єкт.
        </p>
        <form className="inline-form" onSubmit={onJump}>
          <label>
            <span className="sr-only">ID звіту</span>
            <input
              className="mono"
              value={manualId}
              onChange={(e) => setManualId(e.target.value)}
              inputMode="numeric"
              aria-label="ID звіту для переходу"
            />
          </label>
          <button type="submit" className="btn danger-outline">
            Відкрити /reports/[id]
          </button>
        </form>
      </section>

      <div className="row">
        <label className="field grow">
          <span>Пошук у назві (лише свої звіти)</span>
          <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="наприклад, TLS" />
        </label>
      </div>

      {error ? <div className="alert danger">{error}</div> : null}

      <div className="report-grid">
        {reports === null ? (
          <div className="card muted">Завантаження…</div>
        ) : reports.length === 0 ? (
          <div className="card muted">Немає звітів за фільтром.</div>
        ) : (
          reports.map((r) => (
            <Link key={r.id} className="report-card" to={`/reports/${r.id}`}>
              <div className="report-card-top">
                <span className={`sev sev-${r.severity}`}>{r.severity}</span>
                <span className="mono">#{r.id}</span>
              </div>
              <h3>{r.title}</h3>
              <p className="excerpt">{r.summary}</p>
            </Link>
          ))
        )}
      </div>
    </div>
  );
}
