"""
Інтеграційні тести проти піднятого docker compose (gateway на API_BASE).
Запуск: API_BASE=http://127.0.0.1:23456 pytest BOLA/tests -v
"""

from __future__ import annotations

import os

import httpx
import pytest

API_BASE = os.environ.get("API_BASE", "http://127.0.0.1:23456").rstrip("/")
ALICE_PASS = os.environ.get("ALICE_PASSWORD", "K7m!pQ2$vL9#")


@pytest.fixture(scope="module")
def client() -> httpx.Client:
    return httpx.Client(base_url=API_BASE, timeout=30.0)


def _login(client: httpx.Client, username: str, password: str) -> str:
    r = client.post(
        "/api/auth/login",
        data={
            "username": username,
            "password": password,
            "grant_type": "password",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, r.text
    token = r.json().get("access_token")
    assert token
    return str(token)


def test_mode_public(client: httpx.Client) -> None:
    r = client.get("/api/mode")
    assert r.status_code == 200
    data = r.json()
    assert data.get("reports_authz_mode") in ("vulnerable", "secure")


def test_reports_unauthorized(client: httpx.Client) -> None:
    r = client.get("/api/reports/101")
    assert r.status_code == 401


def test_reports_invalid_id(client: httpx.Client) -> None:
    token = _login(client, "alice", ALICE_PASS)
    r = client.get("/api/reports/not-an-int", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 422


def test_idor_vulnerable_or_secure(client: httpx.Client) -> None:
    mode = client.get("/api/mode").json().get("reports_authz_mode")
    token = _login(client, "alice", ALICE_PASS)
    r = client.get("/api/reports/201", headers={"Authorization": f"Bearer {token}"})
    if mode == "vulnerable":
        assert r.status_code == 200
        body = r.json()
        assert body.get("org_id") == 2
    else:
        assert r.status_code == 403


def test_me_includes_role(client: httpx.Client) -> None:
    token = _login(client, "alice", ALICE_PASS)
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json().get("role") == "viewer"
