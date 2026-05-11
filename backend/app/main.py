from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import cases, health, laws, pdfs, trials, verdicts
from app.api.websockets import trial_socket
from app.infrastructure.db.base import Base
from app.infrastructure.db.models import HouseLawModel
from app.infrastructure.db.session import SessionLocal, engine
from app.logging import configure_logging
from app.settings import get_settings

settings = get_settings()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    del app
    configure_logging()
    logger.info("ai_court_starting", env=settings.app_env)
    if settings.is_sqlite:
        await initialize_local_database()
    yield
    logger.info("ai_court_stopping")


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
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


async def initialize_local_database() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        existing = await session.get(HouseLawModel, 1)
        if existing is None:
            session.add_all(
                [
                    HouseLawModel(
                        title="Lei da Louca Compartilhada",
                        article_number="Art. 1o",
                        description=(
                            "Quem cozinha nao lava, salvo se sujar panelas demais "
                            "por exibicionismo culinario."
                        ),
                        severity=7,
                    ),
                    HouseLawModel(
                        title="Abandono Textil",
                        article_number="Art. 2o",
                        description=(
                            "Esquecer roupa na maquina por mais de 6 horas "
                            "constitui abandono textil presumido."
                        ),
                        severity=6,
                    ),
                    HouseLawModel(
                        title="Crime Emocional do Ultimo Pedaco",
                        article_number="Art. 3o",
                        description=(
                            "Consumir o ultimo pedaco sem aviso previo "
                            "e ilicito emocional de alta gravidade."
                        ),
                        severity=9,
                    ),
                ]
            )
            await session.commit()
