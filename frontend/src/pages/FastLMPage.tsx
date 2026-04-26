export function FastLMPage() {
  return (
    <div className="grid readable">
      <header className="hero">
        <h1>FastLM API</h1>
        <p className="lede">
          Окремий репозиторій: OpenAI-сумісний шлюз, hookify, стримінг, SDK. Цей сайт (BOLA) не
          проксує FastLM — підніміть сервіс локально з іншого клону.
        </p>
      </header>
      <section className="card">
        <h2>Клонування та запуск</h2>
        <pre className="mono small-pre">
{`git clone https://github.com/kiurakku/FastLM-API.git
cd FastLM-API
cp .env.example .env
# задайте FASTLM_ADMIN_SECRET; опційно OPENAI_API_KEY
docker compose up --build
# API: http://localhost:8001`}
        </pre>
        <p className="muted">
          Потрібен попередньо опублікований пакет{" "}
          <a href="https://github.com/kiurakku/Hookify" target="_blank" rel="noreferrer">
            Hookify
          </a>{" "}
          (Dockerfile тягне <code>git+https://github.com/kiurakku/Hookify.git@main</code>).
        </p>
        <p>
          <a href="https://github.com/kiurakku/FastLM-API" target="_blank" rel="noreferrer">
            Відкрити репозиторій FastLM-API на GitHub →
          </a>
        </p>
      </section>
    </div>
  );
}
