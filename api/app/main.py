from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title="DeudaMundi API",
    version="0.1.0",
    description="API REST para visualización de deuda soberana global.",
)

app.include_router(api_router, prefix=settings.api_v1_prefix)
