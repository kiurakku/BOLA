# BOLA

![Repo Visibility](https://img.shields.io/badge/visibility-Public-blue)
![Repository Type](https://img.shields.io/badge/type-Source-lightgrey)
![Last Commit](https://img.shields.io/github/last-commit/kiurakku/BOLA)
[![Issues](https://img.shields.io/github/issues/kiurakku/BOLA?style=flat-square&logo=github)](https://github.com/kiurakku/BOLA/issues)
![License](https://img.shields.io/github/license/kiurakku/BOLA)

**Connect:** [![Author](https://img.shields.io/badge/GitHub-kiurakku-181717?style=flat-square&logo=github)](https://github.com/kiurakku) [![Telegram](https://img.shields.io/badge/Telegram-@SyntacticSugar-26A5E4?style=flat-square&logo=telegram&logoColor=white)](https://t.me/SyntacticSugar) [![Email](https://img.shields.io/badge/Email-yanginero%40outlook.com-0078D4?style=flat-square&logo=microsoftoutlook&logoColor=white)](mailto:yanginero@outlook.com)

Hands-on OWASP API security lab for BOLA/IDOR and authorization testing.

## Project Overview

**BOLA** is a **TypeScript** OWASP API security lab for BOLA/IDOR, authorization flaws, and hands-on API testing.

## Tags

engineering, software, automation

## Why This Project

- Demonstrates production-minded implementation and maintainability.
- Captures reusable patterns that can be applied across other systems.
- Serves as a practical reference for development, operations, and quality workflows.

## Key Capabilities

- Clear repository structure for iterative development.
- Standardized development lifecycle: setup, build, test, and deployment flow.
- Continuous integration compatibility through GitHub Actions.
- Documentation-first approach for onboarding and contribution speed.

## How to Install and Use

**Frontend (Vite + React lab UI):**

```bash
git clone https://github.com/kiurakku/BOLA.git
cd BOLA/frontend
npm ci
npm run dev
```

Open the URL printed in the terminal (default Vite dev server). Use **`npm run build`** for a production bundle.

## Proof of Concept (PoC)

- Run the lab UI, exercise **BOLA/IDOR** flows against the bundled or configured API (see repo docs for scenario IDs).
- Capture a **short screen recording or GIF**: request/response showing broken object authorization vs fixed check — attach to issues or docs when demoing.

## Tech Context

- **Primary language:** TypeScript
- **Visibility:** Public
- **Repository role:** Source
- **Default branch:** main
- **License:** MIT License

## Quick Start

See **How to Install and Use** (`cd BOLA/frontend && npm ci && npm run dev`).

## Configuration

- Use environment variables for secrets and environment-specific values.
- Keep local configuration in non-committed files (for example: .env.local).
- Prefer explicit defaults and fail-fast validation for required settings.

## Testing

- Run unit/integration checks before each push.
- Keep tests deterministic and scoped to behavior.
- Add regression tests for every fixed defect.

## CI/CD

This repository is designed to work with GitHub Actions pipelines for:

- Build validation
- Test execution
- Baseline repository health checks

## Roadmap

- Strengthen automated quality gates and security checks.
- Expand coverage of integration and end-to-end scenarios.
- Improve observability, performance benchmarks, and release discipline.

## Contribution Guidelines

- Open an issue describing the change or bug.
- Submit focused pull requests with clear scope.
- Include test evidence for behavioral changes.

## Security Notes

- Do not commit credentials, tokens, or private keys.
- Report sensitive findings privately via maintainer contact channels.

## License

This project is distributed under **MIT License**.

## Maintainer

Maintained by **Kiurakku** as part of a portfolio of software engineering, security engineering, and platform projects.