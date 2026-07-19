"""VNBOT API — Database setup.

SQLAlchemy 2 async engine + session factory.
SQLite WAL mode for better concurrency (multiple readers + 1 writer).
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from ...config import get_settings


class Base(DeclarativeBase):
    """Declarative base for all SQLAlchemy models."""


def _build_engine():
    settings = get_settings()
    connect_args = {}
    if settings.database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    engine = create_async_engine(
        settings.database_url,
        echo=settings.is_dev and False,  # set True for SQL logging
        connect_args=connect_args,
        future=True,
    )
    return engine


engine = _build_engine()
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields an async DB session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_sqlite_pragmas() -> None:
    """Apply SQLite WAL mode + foreign keys for better perf + integrity."""
    settings = get_settings()
    if not settings.database_url.startswith("sqlite"):
        return
    async with engine.begin() as conn:
        await conn.exec_driver_sql("PRAGMA journal_mode=WAL;")
        await conn.exec_driver_sql("PRAGMA foreign_keys=ON;")
        await conn.exec_driver_sql("PRAGMA synchronous=NORMAL;")
        await conn.exec_driver_sql("PRAGMA cache_size=-64000;")  # 64MB cache
