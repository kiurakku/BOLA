# BOLA / IDOR — навчальний стенд (OWASP API)

[![CI](https://github.com/kiurakku/BOLA/actions/workflows/ci.yml/badge.svg)](https://github.com/kiurakku/BOLA/actions/workflows/ci.yml)
[![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Веб-сайт (головна, BOLA Lab, короткі сторінки про суміжні репозиторії), API Gateway з JWT, сервіси **auth** і **reports**, PostgreSQL, Docker Compose. Демонструються **BOLA/IDOR** і **BFLA**.

## Екосистема з трьох репозиторіїв

| Репозиторій | Роль |
|-------------|------|
| **BOLA** (цей репо) | Навчальний стенд OWASP API Security |
| [FastLM-API](https://github.com/kiurakku/FastLM-API) | Реалістичний LLM-шлюз із квотами та webhooks |
| [Hookify](https://github.com/kiurakku/Hookify) | Бібліотека before/after плагінів для таких шлюзів |

Рекомендовані **topics** на GitHub: `security`, `owasp`, `api-security`, `bola`, `idor`, `fastapi`, `docker`, `education`.

## Запуск

```bash
git clone https://github.com/kiurakku/BOLA.git
cd BOLA
cp .env.example .env
# Задайте JWT_SECRET, GATEWAY_INTERNAL_TOKEN
docker compose up --build
```

Веб: [http://localhost:3005](http://localhost:3005), gateway: [http://localhost:23456](http://localhost:23456).

### Secure-режим

```bash
docker compose -f docker-compose.yml -f docker-compose.secure.yml up --build
```

## Архітектура

- **web** — nginx + React: `/`, `/lab`, `/login`, `/reports/:id`, статичні `/fastlm` та `/hookify` з посиланнями на GitHub; проксує лише `/api/*` на gateway.
- **gateway** — JWT, `slowapi`, `GET /api/mode`, `X-Auth-Mode`, проксі до auth/reports, заголовки `X-Trusted-*`.
- **auth**, **reports**, **postgres** — мережа `bola_internal` (internal); **gateway** + **web** — `edge`.

## Тестові облікові записи

| Користувач | Пароль | org_id | Роль |
|------------|--------|--------|------|
| `alice` | `K7m!pQ2$vL9#` | 1 | viewer |
| `bob` | `R4n@xY8wZ1%` | 2 | viewer |
| `dana` | `Adm!n#9zXq2` | 1 | admin |

ID звітів: **101–102** (org 1), **201–202** (org 2).

## Демо-атака (`scripts/bola_attack_demo.py`)

Після `docker compose up` можна показати різницю режимів без браузера:

```bash
python scripts/bola_attack_demo.py
```

Приклад виводу в **вразливому** режимі (alice з org 1 читає звіт `201` org 2 — `200` і `org_id: 2`):

```
API: http://127.0.0.1:23456
GET /api/auth/me -> 200 {"username":"alice",...}
GET /api/reports/201 -> 200
{
  "id": 201,
  "org_id": 2,
  ...
}

[!] BOLA: alice (org 1) отримала об'єкт іншої організації — вразливий режим або некоректна авторизація.
```

У **secure**-режимі (`docker-compose.secure.yml`) для того ж запиту очікується `403` і рядок на кшталт:

```
GET /api/reports/201 -> 403

[OK] Доступ заборонено — типова відповідь у secure-режимі.
```

## Тести

```bash
pip install -r tests/requirements.txt
# Після docker compose up:
API_BASE=http://127.0.0.1:23456 pytest tests -v
```

## Git: коміт і push

```bash
cd /шлях/до/BOLA
git status
git add -A
git commit -m "Ваш опис змін"
git remote -v   # має бути origin → https://github.com/kiurakku/BOLA.git
git push -u origin main
```

Рекомендований порядок першого деплою суміжних репо: **Hookify → FastLM-API → BOLA** (щоб збірка FastLM бачила Hookify на GitHub).

## Посилання

- [OWASP API1 — BOLA](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/)

Навчальний стенд; не використовуйте вразливий режим у проді.
