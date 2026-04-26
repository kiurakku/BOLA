"""
API Gateway: перевіряє JWT (клейми org_id, username, role), додає довірені заголовки
до внутрішніх сервісів. Клієнт ніколи не надсилає X-Gateway-Token / X-Trusted-Org-Id.
"""

from typing import Annotated, Any, Literal

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic_settings import BaseSettings, SettingsConfigDict
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

ALGORITHM = "HS256"
security = HTTPBearer(auto_error=False)
limiter = Limiter(key_func=get_remote_address)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    jwt_secret: str
    gateway_internal_token: str
    auth_upstream: str = "http://auth:8000"
    reports_upstream: str = "http://reports:8000"
    port: int = 8080
    reports_authz_mode: Literal["vulnerable", "secure"] = "vulnerable"


settings = Settings()
app = FastAPI(title="BOLA Lab — API Gateway", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


def decode_jwt_payload(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недійсний або прострочений токен",
        ) from e


async def require_bearer(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> dict[str, Any]:
    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Потрібен Bearer-токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return decode_jwt_payload(creds.credentials)


def trusted_headers_from_claims(claims: dict[str, Any]) -> dict[str, str]:
    org_id = claims.get("org_id")
    if org_id is None:
        raise HTTPException(status_code=401, detail="У токені немає org_id")
    role = claims.get("role")
    if not role or not isinstance(role, str):
        role = "viewer"
    return {
        "X-Gateway-Token": settings.gateway_internal_token,
        "X-Trusted-Org-Id": str(int(org_id)),
        "X-Trusted-Role": role.lower(),
    }


def with_mode_headers(response: Response) -> Response:
    response.headers["X-Auth-Mode"] = settings.reports_authz_mode
    return response


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "role": "gateway"}


@app.get("/api/mode")
async def api_mode() -> dict[str, str]:
    """Публічний endpoint: режим авторизації звітів (для UI без JWT)."""
    return {"reports_authz_mode": settings.reports_authz_mode}


@app.post("/api/auth/login")
@limiter.limit("30/minute")
async def proxy_login(request: Request) -> Response:
    body = await request.body()
    ct = request.headers.get("content-type", "application/x-www-form-urlencoded")
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(
            f"{settings.auth_upstream}/auth/login",
            content=body,
            headers={"content-type": ct},
        )
    return Response(content=r.content, status_code=r.status_code, media_type="application/json")


@app.get("/api/auth/me")
@limiter.limit("60/minute")
async def proxy_me(
    request: Request,
    claims: Annotated[dict[str, Any], Depends(require_bearer)],
) -> Response:
    username = claims.get("username")
    if not username or not isinstance(username, str):
        raise HTTPException(status_code=401, detail="У токені немає username")
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(
            f"{settings.auth_upstream}/auth/me",
            params={"username": username},
        )
    return with_mode_headers(Response(content=r.content, status_code=r.status_code, media_type="application/json"))


@app.get("/api/reports")
@limiter.limit("20/minute")
async def proxy_reports_list(
    request: Request,
    claims: Annotated[dict[str, Any], Depends(require_bearer)],
) -> Response:
    headers = trusted_headers_from_claims(claims)
    q = request.query_params.get("q")
    params: dict[str, str] = {}
    if q:
        params["q"] = q
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(
            f"{settings.reports_upstream}/reports",
            params=params or None,
            headers=headers,
        )
    return with_mode_headers(Response(content=r.content, status_code=r.status_code, media_type="application/json"))


@app.get("/api/reports/{report_id}")
@limiter.limit("20/minute")
async def proxy_report_detail(
    request: Request,
    report_id: int,
    claims: Annotated[dict[str, Any], Depends(require_bearer)],
) -> Response:
    headers = trusted_headers_from_claims(claims)
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.get(
            f"{settings.reports_upstream}/reports/{report_id}",
            headers=headers,
        )
    return with_mode_headers(Response(content=r.content, status_code=r.status_code, media_type="application/json"))


@app.delete("/api/reports/{report_id}")
@limiter.limit("20/minute")
async def proxy_report_delete(
    request: Request,
    report_id: int,
    claims: Annotated[dict[str, Any], Depends(require_bearer)],
) -> Response:
    headers = trusted_headers_from_claims(claims)
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.delete(
            f"{settings.reports_upstream}/reports/{report_id}",
            headers=headers,
        )
    return with_mode_headers(Response(content=r.content or b"", status_code=r.status_code))
