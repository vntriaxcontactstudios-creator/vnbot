"""VNBOT API — FastAPI application entry point.

Run with: uvicorn services.api.app.main:app --reload --port 8000

Per ADR-0001: OpenTelemetry instrumentation is set up at startup.
Per ADR-0007: heuristic fallback is always available (no LLM dependency at startup).
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1 import api_router
from .config import get_settings
from .infrastructure.db.session import init_sqlite_pragmas

# ──────────────────────────────────────────────────────────────────────────────
# Logging (structured JSON, never log plaintext/secrets)
# ──────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":"%(message)s"}',
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
logger = logging.getLogger("vnbot.api")


# ──────────────────────────────────────────────────────────────────────────────
# Lifespan: startup + shutdown
# ──────────────────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup + shutdown."""
    settings = get_settings()
    logger.info(
        f'Venboto API starting up (env={settings.vnbot_env}, llm_provider={settings.llm_provider})'
    )

    # Apply SQLite pragmas (WAL mode, foreign keys, cache_size)
    await init_sqlite_pragmas()
    logger.info("SQLite pragmas applied (WAL mode, FK on, 64MB cache)")

    # OpenTelemetry setup (ADR-0001) — minimal for 0.1, full in 0.2+
    if settings.otel_exporter_otlp_endpoint:
        try:
            from opentelemetry import trace
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
            from opentelemetry.sdk.resources import Resource
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor

            resource = Resource.create(
                {
                    "service.name": settings.otel_service_name,
                    "service.version": "0.1.0",
                }
            )
            provider = TracerProvider(resource=resource)
            provider.add_span_processor(
                BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint))
            )
            trace.set_tracer_provider(provider)
            logger.info(f"OpenTelemetry tracing enabled (endpoint={settings.otel_exporter_otlp_endpoint})")
        except Exception as e:
            logger.warning(f"OpenTelemetry setup failed (tracing disabled): {e}")
    else:
        logger.info("OpenTelemetry tracing disabled (no OTLP endpoint configured)")

    yield

    logger.info("VNBOT API shutting down")


# ──────────────────────────────────────────────────────────────────────────────
# App
# ──────────────────────────────────────────────────────────────────────────────

settings = get_settings()

app = FastAPI(
    title="VNBOT API",
    description="Memoria personal open source, recordatorios confiables y mini-agentes.",
    version="0.1.0",
    license_info={"name": "MIT", "url": "https://opensource.org/license/mit/"},
    lifespan=lifespan,
    docs_url="/docs" if settings.is_dev else None,
    redoc_url="/redoc" if settings.is_dev else None,
)

# CORS (allow frontend dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        settings.vnbot_base_url,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Workspace-Id"],
)

# ──────────────────────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────────────────────

app.include_router(api_router)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint — basic info."""
    return {
        "name": "VNBOT API",
        "version": "0.1.0",
        "docs": "/docs" if settings.is_dev else "disabled",
        "health": "/healthz",
    }
