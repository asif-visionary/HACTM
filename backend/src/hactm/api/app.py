"""
FastAPI Main Application for HACTM.
Foundation Architecture - Hierarchical Adaptive Cyber Trust Mesh.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from hactm.api.routers import (
    agents,
    entities,
    evidence,
    fusion,
    health,
    identity,
    ingestion,
    metrics,
    network,
    phishing,
    reports,
    transaction,
    uba,
    adaptive_memory,
    reliability,
    orchestration,
    zerotrust,
    feedback,
    evaluation,
    research,
    zero_day,
    threat_intelligence,
)
from hactm.core.config import settings
from hactm.core.errors import DuplicateError, HACTMError, HACTMValidationError, NotFoundError
from hactm.core.logging import logger
from hactm.storage.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables initialized
    logger.info("Initializing HACTM Multi-Domain Database Tables...")
    init_db()
    logger.info("HACTM Database Ready.")
    yield
    # Shutdown
    logger.info("Shutting down HACTM backend service.")


app = FastAPI(
    title="HACTM API",
    description="Hierarchical Adaptive Cyber Trust Mesh - Multi-Domain Security Evidence Platform API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers enforcing standard error envelope
@app.exception_handler(HACTMValidationError)
async def validation_error_handler(request: Request, exc: HACTMValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
    )


@app.exception_handler(NotFoundError)
async def not_found_error_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
    )


@app.exception_handler(DuplicateError)
async def duplicate_error_handler(request: Request, exc: DuplicateError):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
    )


@app.exception_handler(HACTMError)
async def hactm_error_handler(request: Request, exc: HACTMError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
    )


@app.exception_handler(RequestValidationError)
async def pydantic_validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request payload failed schema validation",
                "details": exc.errors(),
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred. Check system logs for correlation.",
                "details": None,
            }
        },
    )


# Attach routers
app.include_router(health.router)
app.include_router(evidence.router, prefix=settings.API_PREFIX)
app.include_router(entities.router, prefix=settings.API_PREFIX)
app.include_router(ingestion.router, prefix=settings.API_PREFIX)
app.include_router(metrics.router, prefix=settings.API_PREFIX)
app.include_router(reports.router)
app.include_router(network.router, prefix=settings.API_PREFIX)
app.include_router(phishing.router)
app.include_router(uba.router)
app.include_router(identity.router)
app.include_router(transaction.router)
app.include_router(fusion.router)
app.include_router(agents.router)
app.include_router(adaptive_memory.router)
app.include_router(reliability.router)
app.include_router(orchestration.router)
app.include_router(zerotrust.router)
app.include_router(feedback.router)
app.include_router(evaluation.router)
app.include_router(research.router)
app.include_router(zero_day.router)
app.include_router(threat_intelligence.router)






