import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const navLink = (path: string, label: string, loc: string) => (
  <Link
    className={`nav-link${loc === path ? " nav-link-active" : ""}`}
    to={path}
  >
    {label}
  </Link>
);

export function NavBar() {
  const { user, logout } = useAuth();
  const loc = useLocation();
  const path = loc.pathname;

  return (
    <nav className="nav-row" aria-label="Головна навігація">
      <div className="nav-links">
        {navLink("/", "Головна", path)}
        {navLink("/lab", "BOLA Lab", path)}
        {navLink("/fastlm", "FastLM", path)}
        {navLink("/hookify", "hookify", path)}
      </div>
      <div className="nav-auth">
        {user ? (
          <>
            <span className="nav-user muted">
              {user.display_name}{" "}
              <span className="mono">({user.role})</span>
            </span>
            <button type="button" className="btn ghost btn-sm" onClick={() => logout()}>
              Вийти
            </button>
          </>
        ) : (
          <Link className="btn ghost btn-sm" to="/login">
            Увійти
          </Link>
        )}
      </div>
    </nav>
  );
}
