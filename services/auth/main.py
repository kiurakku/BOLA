"""Сервіс автентифікації: видає JWT з клеймами sub та org_id."""

from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

ALGORITHM = "HS256"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://bola:bola@localhost:5432/bola"
    jwt_secret: str
    jwt_expire_minutes: int = 60


settings = Settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

engine = create_async_engine(settings.database_url, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    org_id: Mapped[int] = mapped_column(index=True)
    display_name: Mapped[str] = mapped_column(String(128), default="")


app = FastAPI(title="BOLA Lab — Auth", version="1.0.0")


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserPublic(BaseModel):
    username: str
    org_id: int
    display_name: str


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(*, username: str, org_id: int, sub: str) -> tuple[str, int]:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    exp_ts = int(expire.timestamp())
    payload = {
        "sub": sub,
        "username": username,
        "org_id": org_id,
        "exp": exp_ts,
        "iat": int(datetime.now(timezone.utc).timestamp()),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)
    ttl = exp_ts - int(datetime.now(timezone.utc).timestamp())
    return token, max(ttl, 0)


async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        existing = await session.scalar(select(User).where(User.username == "alice"))
        if existing:
            return
        users = [
            User(
                username="alice",
                password_hash=pwd_context.hash("K7m!pQ2$vL9#"),
                org_id=1,
                display_name="Alice (Org Alpha)",
            ),
            User(
                username="bob",
                password_hash=pwd_context.hash("R4n@xY8wZ1%"),
                org_id=2,
                display_name="Bob (Org Beta)",
            ),
        ]
        session.add_all(users)
        await session.commit()


@app.on_event("startup")
async def startup() -> None:
    await init_db()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/login", response_model=TokenOut)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TokenOut:
    result = await session.execute(select(User).where(User.username == form.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірні облікові дані",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token, ttl = create_token(username=user.username, org_id=user.org_id, sub=str(user.id))
    return TokenOut(access_token=token, expires_in=ttl)


@app.get("/auth/me", response_model=UserPublic)
async def me(
    session: Annotated[AsyncSession, Depends(get_session)],
    username: Annotated[str, Query(description="Ім'я користувача після перевірки JWT на gateway")],
) -> UserPublic:
    """Внутрішній виклик від gateway (передає username після перевірки JWT)."""
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")
    return UserPublic(username=user.username, org_id=user.org_id, display_name=user.display_name)
