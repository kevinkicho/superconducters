"""FastAPI application factory."""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from superconductors.config import Settings
from superconductors.repository import CandidateRepository

from .auth import LoginRateLimiter
from .errors import ApplicationDataError, DuplicateCandidateError
from .routes import router
from .services import ApplicationService
from .store import ApplicationStore

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    app = FastAPI(title="Superconductivity Pipeline API", version="1.1.0")
    app.state.settings = settings
    app.state.login_limiter = LoginRateLimiter()
    app.state.service = ApplicationService(
        CandidateRepository(settings.database_path),
        ApplicationStore(settings.state_database_path),
    )
    app.include_router(router)

    @app.middleware("http")
    async def request_context(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        started = time.perf_counter()
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request method=%s path=%s status=%s duration_ms=%.2f request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            (time.perf_counter() - started) * 1000,
            request_id,
        )
        return response

    @app.exception_handler(ApplicationDataError)
    async def application_data_error(_: Request, exc: ApplicationDataError) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    @app.exception_handler(DuplicateCandidateError)
    async def duplicate_candidate(_: Request, exc: DuplicateCandidateError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    return app
