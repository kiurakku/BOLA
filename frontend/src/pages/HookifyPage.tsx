export function HookifyPage() {
  return (
    <div className="grid readable">
      <header className="hero">
        <h1>hookify</h1>
        <p className="lede">
          Окремий Python-пакет: реєстр плагінів <code>before_request</code> /{" "}
          <code>after_response</code>. Використовується в FastLM-API після{" "}
          <code>pip install git+https://github.com/kiurakku/Hookify.git</code>.
        </p>
      </header>
      <section className="card">
        <h2>Репозиторій</h2>
        <pre className="mono small-pre">
{`git clone https://github.com/kiurakku/Hookify.git
cd Hookify
pip install -e .`}
        </pre>
        <p>
          <a href="https://github.com/kiurakku/Hookify" target="_blank" rel="noreferrer">
            github.com/kiurakku/Hookify →
          </a>
        </p>
      </section>
      <section className="card">
        <h2>Плагіни</h2>
        <dl className="def-list">
          <dt>audit</dt>
          <dd className="muted">Лог маскованого prompt (stdout / подальша заміна на БД).</dd>
          <dt>pii_mask</dt>
          <dd className="muted">Маскування email і телефонів у повідомленнях.</dd>
          <dt>prompt_injection</dt>
          <dd className="muted">Евристики типових ін’єкцій → HTTP 400.</dd>
          <dt>cost_limit</dt>
          <dd className="muted">Місячний бюджет у ядрі FastLM; слот для розширень.</dd>
        </dl>
      </section>
    </div>
  );
}
