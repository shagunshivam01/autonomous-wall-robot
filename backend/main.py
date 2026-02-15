"""Wall Robot Control API - FastAPI application entry point."""
from contextlib import asynccontextmanager
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging_config import setup_logging, get_correlation_id, set_correlation_id, get_logger
from app.persistence.database import init_db

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    setup_logging(get_settings().log_level)
    init_db()
    logger.info("Application started")
    yield
    logger.info("Application shutdown")


app = FastAPI(
    title="Wall Robot Control API",
    description="API for autonomous wall-finishing robot path planning and trajectory management",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log request/response with timing and correlation ID."""
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    set_correlation_id(correlation_id)
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "Request completed",
        extra={
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
        },
    )
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Response-Time-Ms"] = str(round(duration_ms, 2))
    return response


from app.controllers.trajectory_controller import router as trajectories_router

app.include_router(trajectories_router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
