import { Link } from "react-router-dom";

const GH_FASTLM = "https://github.com/kiurakku/FastLM-API";
const GH_HOOKIFY = "https://github.com/kiurakku/Hookify";
const GH_BOLA = "https://github.com/kiurakku/BOLA";

export function HomePage() {
  return (
    <div className="grid landing">
      <section className="hero hero-large">
        <p className="eyebrow">Навчальний стенд OWASP API</p>
        <h1>BOLA Lab</h1>
        <p className="lede lede-wide">
          Цей репозиторій — консоль звітів, gateway і демонстрація <strong>BOLA/IDOR</strong> та{" "}
          <strong>BFLA</strong>. Окремо живуть суміжні pet-проєкти:{" "}
          <a href={GH_FASTLM} target="_blank" rel="noreferrer">
            FastLM-API
          </a>{" "}
          (OpenAI-сумісний шлюз) та{" "}
          <a href={GH_HOOKIFY} target="_blank" rel="noreferrer">
            Hookify
          </a>{" "}
          (плагіни навколо запитів).
        </p>
        <div className="cta-row">
          <Link className="btn primary" to="/lab">
            Перейти до BOLA Lab
          </Link>
          <a className="btn ghost" href={GH_BOLA} target="_blank" rel="noreferrer">
            Репозиторій на GitHub
          </a>
        </div>
      </section>

      <div className="three-col">
        <article className="card feature">
          <h2>BOLA / IDOR (цей репо)</h2>
          <p className="muted">
            JWT на gateway не замінює авторизацію об’єкта. Режими <code>vulnerable</code> та{" "}
            <code>secure</code>, демо видалення (BFLA).
          </p>
          <Link to="/lab">Консоль звітів →</Link>
        </article>
        <article className="card feature">
          <h2>FastLM-API</h2>
          <p className="muted">
            Окремий репозиторій: chat completions, ключі, Redis, стримінг SSE, Python SDK у каталозі{" "}
            <code>sdk/</code>.
          </p>
          <a href={GH_FASTLM} target="_blank" rel="noreferrer">
            github.com/kiurakku/FastLM-API →
          </a>
          <div style={{ marginTop: "0.5rem" }}>
            <Link to="/fastlm">Короткий опис у цьому сайті →</Link>
          </div>
        </article>
        <article className="card feature">
          <h2>Hookify</h2>
          <p className="muted">
            Пакет плагінів (audit, PII, prompt injection) для інтеграції в FastLM або власні сервіси.
          </p>
          <a href={GH_HOOKIFY} target="_blank" rel="noreferrer">
            github.com/kiurakku/Hookify →
          </a>
          <div style={{ marginTop: "0.5rem" }}>
            <Link to="/hookify">Опис можливостей →</Link>
          </div>
        </article>
      </div>

      <section className="card">
        <h2>Швидкий старт (лише BOLA)</h2>
        <ol className="muted tight-list">
          <li>
            <code className="mono">git clone https://github.com/kiurakku/BOLA.git && cd BOLA</code>
          </li>
          <li>
            Скопіюйте <code>.env.example</code> у <code>.env</code>, задайте секрети.
          </li>
          <li>
            <code className="mono">docker compose up --build</code> →{" "}
            <a href="http://localhost:3005">localhost:3005</a>
          </li>
        </ol>
      </section>
    </div>
  );
}
