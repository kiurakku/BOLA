import { Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider, useAuth } from "./auth/AuthContext";
import { NavBar } from "./components/NavBar";
import { DashboardPage } from "./pages/DashboardPage";
import { FastLMPage } from "./pages/FastLMPage";
import { HomePage } from "./pages/HomePage";
import { HookifyPage } from "./pages/HookifyPage";
import { LoginPage } from "./pages/LoginPage";
import { ReportPage } from "./pages/ReportPage";
import "./styles.css";

function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="shell">
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand">
            <span className="brand-mark" aria-hidden />
            <div>
              <div className="brand-title">BOLA Lab</div>
              <div className="brand-sub">OWASP API — об’єктна авторизація</div>
            </div>
          </div>
          <NavBar />
        </div>
      </header>
      <main className="main">{children}</main>
      <footer className="footer">
        <span>
          Навчальний стенд: автентифікація ≠ авторизація. Див.{" "}
          <a
            href="https://owasp.org/www-project-api-security/"
            target="_blank"
            rel="noreferrer"
          >
            OWASP API Security
          </a>
          . Суміжні репозиторії:{" "}
          <a href="https://github.com/kiurakku/FastLM-API" target="_blank" rel="noreferrer">
            FastLM-API
          </a>
          ,{" "}
          <a href="https://github.com/kiurakku/Hookify" target="_blank" rel="noreferrer">
            Hookify
          </a>
          .
        </span>
      </footer>
    </div>
  );
}

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <AppLayout>
        <div className="card muted">Завантаження сесії…</div>
      </AppLayout>
    );
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return <AppLayout>{children}</AppLayout>;
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route
          path="/login"
          element={
            <AppLayout>
              <LoginPage />
            </AppLayout>
          }
        />
        <Route
          path="/"
          element={
            <AppLayout>
              <HomePage />
            </AppLayout>
          }
        />
        <Route
          path="/hookify"
          element={
            <AppLayout>
              <HookifyPage />
            </AppLayout>
          }
        />
        <Route
          path="/fastlm"
          element={
            <AppLayout>
              <FastLMPage />
            </AppLayout>
          }
        />
        <Route
          path="/lab"
          element={
            <RequireAuth>
              <DashboardPage />
            </RequireAuth>
          }
        />
        <Route
          path="/reports/:reportId"
          element={
            <RequireAuth>
              <ReportPage />
            </RequireAuth>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}
