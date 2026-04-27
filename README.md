# BOLA Lab (OWASP API Security)

[![CI](https://github.com/kiurakku/BOLA/actions/workflows/ci.yml/badge.svg)](https://github.com/kiurakku/BOLA/actions/workflows/ci.yml)
[![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Hands-on security lab for Broken Object Level Authorization (BOLA/IDOR) and Broken Function Level Authorization (BFLA).

This repository ships a full runnable stack: React UI, API Gateway, auth service, reports service, PostgreSQL, test suite, and CI matrix for vulnerable vs secure behavior.

## Position in the 3-project stack

- **BOLA**: controlled security training environment.
- [FastLM-API](https://github.com/kiurakku/FastLM-API): practical LLM gateway implementation.
- [Hookify](https://github.com/kiurakku/Hookify): plugin/hook framework used by FastLM.

## What you can demonstrate

- **BOLA (IDOR)** on `GET /api/reports/{id}`:
  - `vulnerable`: object is returned by ID without org ownership check.
  - `secure`: object is returned only if token org matches report org.
- **BFLA** on `DELETE /api/reports/{id}`:
  - `vulnerable`: any user from same org can delete.
  - `secure`: only `admin` role can delete.

## Architecture overview

```text
Browser (React)
  -> Nginx web (port 3005)
     -> /api/* -> Gateway (port 23456)
         -> Auth service    (token issuance + /auth/me)
         -> Reports service (report list/detail/delete)
         -> PostgreSQL

Networks:
  edge          : web <-> gateway
  bola_internal : gateway <-> auth/reports/postgres (internal-only)
```

## Tech stack

- **Frontend**: React 18 + TypeScript + Vite.
- **Gateway**: FastAPI + JWT verification + `slowapi` rate limits.
- **Auth service**: FastAPI + JWT issuing (`HS256`) + bcrypt password verification.
- **Reports service**: FastAPI + SQLAlchemy async + mode-based authorization checks.
- **Runtime**: Docker Compose + PostgreSQL 16.

## Run locally

```bash
git clone https://github.com/kiurakku/BOLA.git
cd BOLA
cp .env.example .env
# set JWT_SECRET and GATEWAY_INTERNAL_TOKEN
docker compose up --build
```

- UI: `http://localhost:3005`
- API Gateway: `http://localhost:23456`

### Secure mode

```bash
docker compose -f docker-compose.yml -f docker-compose.secure.yml up --build
```

## Demo accounts

| Username | Password | org_id | role |
|---|---|---|---|
| `alice` | `K7m!pQ2$vL9#` | 1 | viewer |
| `bob` | `R4n@xY8wZ1%` | 2 | viewer |
| `dana` | `Adm!n#9zXq2` | 1 | admin |

Report IDs:

- org 1: `101`, `102`
- org 2: `201`, `202`

## Attack demo script

Run:

```bash
python scripts/bola_attack_demo.py
```

Expected output pattern:

- `vulnerable` mode: `GET /api/reports/201 -> 200` for `alice` (org 1) and response contains `"org_id": 2`.
- `secure` mode: `GET /api/reports/201 -> 403`.

## API endpoints (gateway)

| Method | Path | Notes |
|---|---|---|
| `GET` | `/health` | Gateway health |
| `GET` | `/api/mode` | Public mode indicator (`vulnerable` / `secure`) |
| `POST` | `/api/auth/login` | Login and receive JWT |
| `GET` | `/api/auth/me` | JWT-protected user profile |
| `GET` | `/api/reports` | JWT-protected report list (scoped by org) |
| `GET` | `/api/reports/{id}` | BOLA behavior depends on mode |
| `DELETE` | `/api/reports/{id}` | BFLA behavior depends on mode |

## Tests

### Local integration tests

```bash
pip install -r tests/requirements.txt
API_BASE=http://127.0.0.1:23456 pytest tests -v --tb=short
```

### CI behavior

GitHub Actions matrix runs tests in **both** modes:

- `REPORTS_AUTHZ_MODE=vulnerable`
- `REPORTS_AUTHZ_MODE=secure`

This ensures regression visibility for educational vulnerable flow and hardened flow.

## Repository structure

```text
gateway/             # JWT verification, upstream proxy, rate limits
services/auth/       # login + token issuance + profile endpoint
services/reports/    # report CRUD with mode-specific auth checks
frontend/            # React lab UI
tests/               # end-to-end API behavior tests
scripts/             # quick attack demonstration scripts
```

## Security disclaimer

This project intentionally includes insecure behavior in `vulnerable` mode for learning and demonstrations.
Never deploy vulnerable mode in production.

---

Recommended GitHub topics:

`security`, `owasp`, `api-security`, `bola`, `idor`, `fastapi`, `docker`, `education`
