from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.api.responses import build_success_response
from app.api.error_handlers import register_exception_handlers
from app.api.router import api_router
from app.core.logging import configure_logging, get_logger
from app.core.middleware import RequestContextLogMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.schemas.common import ApiResponse
from app.core.settings import BaseAppSettings, settings
from app.db.database import close_db_connections, init_db


def create_app(
    *,
    app_settings: BaseAppSettings | None = None,
    run_init_db: bool = True,
) -> FastAPI:
    configured_settings = app_settings or settings
    configure_logging(configured_settings)
    logger = get_logger(__name__)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.settings = configured_settings
        if run_init_db:
            await init_db()
            logger.info("Database initialization complete.")
        yield
        await close_db_connections()

    app = FastAPI(
        title=configured_settings.app_name,
        lifespan=lifespan,
        default_response_class=ORJSONResponse,
        version=configured_settings.version,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=configured_settings.cors_origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)  # 仅对大于 1000 字节的响应进行压缩
    app.add_middleware(RequestContextLogMiddleware)
    app.add_middleware(
        CorrelationIdMiddleware,
        header_name="X-Request-ID",
        update_request_header=True,
        validator=None,
    )
    register_exception_handlers(app)
    app.include_router(api_router, prefix=configured_settings.api_v1_prefix)

    @app.get("/", tags=["root"], response_model=ApiResponse[dict[str, str]])
    async def root(request: Request) -> ApiResponse[dict[str, str]]:
        return build_success_response(
            request,
            data={"message": f"{configured_settings.app_name} is running"},
            message="Application is running.",
        )

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
    }
    uvicorn.run(app, host=settings.app_host, port=settings.app_port, log_config=log_config)
