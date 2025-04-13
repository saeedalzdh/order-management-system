import logging

from app.api.v1.router import router as api_v1_router
from app.core.database import init_db
from app.core.logger import setup_logger
from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from prometheus_fastapi_instrumentator import Instrumentator

setup_logger()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Restaurant Order API",
    version="1.0.0",
    openapi_tags=[
        {"name": "Orders", "description": "Order management endpoints"},
        {"name": "Analytics", "description": "Analytics endpoints"}
    ],
)

app.include_router(api_v1_router)

router = APIRouter()

Instrumentator().instrument(app).expose(app)

@router.get("/health")
async def health() -> PlainTextResponse:
    return PlainTextResponse("OK")
app.include_router(router)

init_db(app)


@app.exception_handler(Exception)
async def global_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unhandled exception occurred: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
