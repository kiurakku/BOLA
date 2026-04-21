import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { apiFetch, parseJson } from "../api/client";
import type { ReportDetail } from "../api/types";
import { useAuth } from "../auth/AuthContext";

export function ReportPage() {
  const { reportId } = useParams();
  const { user } = useAuth();
  const [report, setReport] = useState<ReportDetail | null>(null);
  const [status, setStatus] = useState<number | null>(null);
  const [errorBody, setErrorBody] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const idNum = Number(reportId);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setLoading(true);
      setReport(null);
      setErrorBody(null);
      setStatus(null);
      if (!Number.isFinite(idNum) || idNum <= 0) {
        setErrorBody("Некоректний ідентифікатор у URL.");
        setLoading(false);
        return;
      }
      const res = await apiFetch(`/api/reports/${idNum}`);
      setStatus(res.status);
      if (!res.ok) {
        try {
          const j = (await res.json()) as { detail?: string };
          setErrorBody(typeof j.detail === "string" ? j.detail : res.statusText);
        } catch {
          setErrorBody(res.statusText);
        }
        if (!cancelled) {
          setLoading(false);
        }
        return;
      }
      const data = await parseJson<ReportDetail>(res);
      if (!cancelled) {
        setReport(data);
      }
      if (!cancelled) {
        setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [idNum]);

  const crossOrg =
    report && user && report.org_id !== user.org_id
      ? {
          title: "Порушення об’єктної авторизації (BOLA)",
          text: "Ви переглядаєте звіт іншої організації: JWT містить ваш org_id, але API повернув об’єкт з іншим org_id. У продакшені так бути не повинно — увімкніть REPORTS_AUTHZ_MODE=secure.",
        }
      : null;

  return (
    <div className="grid narrow">
      <div className="toolbar">
        <Link className="btn ghost" to="/">
          ← До списку
        </Link>
      </div>

      {loading ? <div className="card muted">Завантаження звіту…</div> : null}

      {!loading && status === 403 ? (
        <div className="alert ok">
          <strong>Доступ заборонено (403).</strong> Бекенд відхилив запит: об’єкт не належить вашій
          організації за клеймом JWT (режим <code>secure</code>).
        </div>
      ) : null}

      {!loading && status === 404 ? (
        <div className="alert muted">
          Звіт не знайдено або недоступний.{" "}
          {errorBody ? <span className="mono">{errorBody}</span> : null}
        </div>
      ) : null}

      {!loading && status && status >= 400 && status !== 403 && status !== 404 ? (
        <div className="alert danger">
          Помилка {status}: {errorBody}
        </div>
      ) : null}

      {crossOrg ? (
        <div className="alert leak" role="alert">
          <div className="leak-title">{crossOrg.title}</div>
          <p>{crossOrg.text}</p>
        </div>
      ) : null}

      {report ? (
        <article className="card detail">
          <header className="detail-head">
            <div>
              <p className="eyebrow mono">Звіт #{report.id}</p>
              <h1>{report.title}</h1>
            </div>
            <span className={`sev sev-${report.severity}`}>{report.severity}</span>
          </header>
          <dl className="meta-grid">
            <div>
              <dt>org_id у записі</dt>
              <dd className="mono">{report.org_id}</dd>
            </div>
            <div>
              <dt>Ваш org_id (JWT)</dt>
              <dd className="mono">{user?.org_id}</dd>
            </div>
          </dl>
          <section>
            <h2>Опис</h2>
            <p>{report.summary}</p>
          </section>
          <section>
            <h2>Рекомендації</h2>
            <p>{report.remediation}</p>
          </section>
        </article>
      ) : null}
    </div>
  );
}
