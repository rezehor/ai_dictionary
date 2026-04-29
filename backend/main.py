import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from app.routers import auth, system

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s (v%s)...", settings.APP_NAME, settings.APP_VERSION)
    yield
    logger.info("Shutting %s down...", settings.APP_NAME)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "Unhandled error on %s %s: %s",
            request.method,
            request.url,
            exc,
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
    app.include_router(system.router)

    return app


app = create_app()
