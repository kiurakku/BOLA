"""
Сервіс звітів про вразливості.
Доступ лише з API Gateway (заголовок X-Gateway-Token).
Режим REPORTS_AUTHZ_MODE:
- vulnerable — BOLA: GET /reports/{id} повертає запис лише за ID (ігнорує org).
- secure — перевірка відповідності org_id з JWT (через X-Trusted-Org-Id від gateway).
"""

from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import String, Text, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://bola:bola@localhost:5432/bola"
    gateway_internal_token: str
    reports_authz_mode: Literal["vulnerable", "secure"] = "vulnerable"


settings = Settings()
engine = create_async_engine(settings.database_url, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    org_id: Mapped[int] = mapped_column(index=True)
    title: Mapped[str] = mapped_column(String(255))
    severity: Mapped[str] = mapped_column(String(32))
    summary: Mapped[str] = mapped_column(Text())
    remediation: Mapped[str] = mapped_column(Text(), default="")


app = FastAPI(title="BOLA Lab — Reports", version="1.0.0")


class ReportListItem(BaseModel):
    id: int
    title: str
    severity: str
    summary: str


class ReportDetail(BaseModel):
    id: int
    org_id: int = Field(description="У проді не віддавали б сторонньому клієнту явно")
    title: str
    severity: str
    summary: str
    remediation: str


async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


def require_gateway(
    x_gateway_token: Annotated[str | None, Header()] = None,
) -> None:
    if x_gateway_token != settings.gateway_internal_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Прямий доступ заборонено")


def require_trusted_org(
    x_trusted_org_id: Annotated[str | None, Header()] = None,
) -> int:
    if not x_trusted_org_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Відсутня організаційна ідентичність")
    try:
        return int(x_trusted_org_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Некоректний X-Trusted-Org-Id")


def require_trusted_role(
    x_trusted_role: Annotated[str | None, Header()] = None,
) -> str:
    if not x_trusted_role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Відсутня роль у довірених заголовках")
    return x_trusted_role.strip().lower()


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        existing = await session.scalar(select(Report).where(Report.id == 101))
        if existing:
            return
        rows = [
            Report(
                id=101,
                org_id=1,
                title="Витік API-ключа в мобільному білді",
                severity="high",
                summary="Ключ знайдено в артефакті CI; доступ до S3.",
                remediation="Ротація ключів, secret scanning у pipeline.",
            ),
            Report(
                id=102,
                org_id=1,
                title="Застарілий TLS на edge",
                severity="medium",
                summary="Підтримується TLS 1.0 на legacy клієнтах.",
                remediation="Вимкнути TLS < 1.2, оновити клієнтів.",
            ),
            Report(
                id=201,
                org_id=2,
                title="Внутрішній роут без rate limit",
                severity="critical",
                summary="Адмінський endpoint доступний з корпоративної мережі без throttling.",
                remediation="WAF + per-IP limits + MFA для адмінки.",
            ),
            Report(
                id=202,
                org_id=2,
                title="Логи з PII",
                severity="low",
                summary="У логах зберігаються повні номери карток (тестове середовище).",
                remediation="Маскування полів, retention policy.",
            ),
        ]
        session.add_all(rows)
        await session.commit()


@app.on_event("startup")
async def startup() -> None:
    await init_db()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "mode": settings.reports_authz_mode}


@app.get("/reports", response_model=list[ReportListItem])
async def list_reports(
    _: Annotated[None, Depends(require_gateway)],
    trusted_org: Annotated[int, Depends(require_trusted_org)],
    session: Annotated[AsyncSession, Depends(get_session)],
    q: Annotated[str | None, Query(description="Пошук у назві (лише в межах своєї org)")] = None,
) -> list[ReportListItem]:
    stmt = select(Report).where(Report.org_id == trusted_org).order_by(Report.id)
    if q:
        stmt = select(Report).where(
            Report.org_id == trusted_org,
            Report.title.ilike(f"%{q}%"),
        ).order_by(Report.id)
    result = await session.execute(stmt)
    reports = result.scalars().all()
    return [
        ReportListItem(id=r.id, title=r.title, severity=r.severity, summary=r.summary[:160] + ("…" if len(r.summary) > 160 else ""))
        for r in reports
    ]


@app.get("/reports/{report_id}", response_model=ReportDetail)
async def get_report(
    report_id: int,
    _: Annotated[None, Depends(require_gateway)],
    trusted_org: Annotated[int, Depends(require_trusted_org)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ReportDetail:
    result = await session.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Звіт не знайдено")

    if settings.reports_authz_mode == "secure":
        if report.org_id != trusted_org:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ до об'єкта заборонено (перевірка org_id)",
            )
    return ReportDetail(
        id=report.id,
        org_id=report.org_id,
        title=report.title,
        severity=report.severity,
        summary=report.summary,
        remediation=report.remediation,
    )


@app.delete("/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: int,
    _: Annotated[None, Depends(require_gateway)],
    trusted_org: Annotated[int, Depends(require_trusted_org)],
    trusted_role: Annotated[str, Depends(require_trusted_role)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """
    Демо BFLA: у vulnerable перевіряється лише належність звіту до org (без ролі).
    У secure — потрібна роль admin і та сама org.
    """
    result = await session.execute(select(Report).where(Report.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Звіт не знайдено")

    if report.org_id != trusted_org:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ до об'єкта заборонено (інша організація)",
        )

    if settings.reports_authz_mode == "secure":
        if trusted_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Лише адміністратор може видаляти звіти (BFLA закрито)",
            )
    # vulnerable: org співпала — viewer може видалити (поламана авторизація на рівні функції)
    await session.delete(report)
    await session.commit()
