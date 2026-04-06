from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.security import setup_security
from app.etl.scheduler import start_etl_scheduler, stop_etl_scheduler


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    scheduler = start_etl_scheduler()
    try:
        yield
    finally:
        stop_etl_scheduler(scheduler)

app = FastAPI(
    title="DeudaMundi API",
    version="0.1.0",
    description="API REST para visualización de deuda soberana global.",
    lifespan=lifespan,
)

setup_security(app)

app.include_router(api_router, prefix=settings.api_v1_prefix)
