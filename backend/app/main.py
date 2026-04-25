from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import cases, health, laws, pdfs, trials, verdicts
from app.api.websockets import trial_socket
from app.logging import configure_logging
from app.settings import get_settings

settings = get_settings()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    del app
    configure_logging()
    logger.info("ai_court_starting", env=settings.app_env)
    yield
    logger.info("ai_court_stopping")


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(cases.router, prefix="/api/v1")
app.include_router(trials.router, prefix="/api/v1")
app.include_router(verdicts.router, prefix="/api/v1")
app.include_router(laws.router, prefix="/api/v1")
app.include_router(pdfs.router, prefix="/api/v1")
app.include_router(trial_socket.router, prefix="/api/v1")
