from time import perf_counter

from asgi_correlation_id import correlation_id
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.logging import get_logger

logger = get_logger(__name__)


class RequestContextLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = correlation_id.get() or request.headers.get("X-Request-ID") or "-"
        request.state.request_id = request_id
        start_time = perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (perf_counter() - start_time) * 1000
            logger.exception(
                "Request failed: {} {} ({:.2f} ms) [request_id={}]",
                request.method,
                request.url.path,
                duration_ms,
                request_id,
            )
            raise

        request_id = correlation_id.get() or request_id
        request.state.request_id = request_id
        duration_ms = (perf_counter() - start_time) * 1000
        logger.info(
            "Request completed: {} {} -> {} ({:.2f} ms) [request_id={}]",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
        )
        return response
