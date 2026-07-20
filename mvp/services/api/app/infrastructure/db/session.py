"""VNBOT API — Database setup.

SQLAlchemy 2 async engine + session factory.
Supports both SQLite (local/dev) and PostgreSQL+pgvector (server).

Per ADR-0002: SQLite for local, PostgreSQL for server.
Per docs/07 §13: pgvector for semantic search (Fase 0.5+).
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from ...config import get_settings


class Base(DeclarativeBase):
    """Declarative base for all SQLAlchemy models."""
    pass


def _build_engine():
    settings = get_settings()
    connect_args: dict = {}
    engine_kwargs: dict = {
        "echo": settings.is_dev and False,
        "future": True,
    }

    if settings.database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    elif settings.database_url.startswith("postgresql"):
        # PostgreSQL with asyncpg
        engine_kwargs["pool_size"] = 10
        engine_kwargs["max_overflow"] = 20
        engine_kwargs["pool_pre_ping"] = True

    engine_kwargs["connect_args"] = connect_args
    engine = create_async_engine(settings.database_url, **engine_kwargs)
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


async def init_db_pragmas() -> None:
    """Apply DB-specific optimizations.

    SQLite: WAL mode, foreign keys, cache size.
    PostgreSQL: pgvector extension (if available).
    """
    settings = get_settings()

    if settings.database_url.startswith("sqlite"):
        async with engine.begin() as conn:
            await conn.exec_driver_sql("PRAGMA journal_mode=WAL;")
            await conn.exec_driver_sql("PRAGMA foreign_keys=ON;")
            await conn.exec_driver_sql("PRAGMA synchronous=NORMAL;")
            await conn.exec_driver_sql("PRAGMA cache_size=-64000;")  # 64MB cache
    elif settings.database_url.startswith("postgresql"):
        async with engine.begin() as conn:
            # Create pgvector extension if not exists
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            except Exception:
                pass  # pgvector may not be installed — semantic search deferred
