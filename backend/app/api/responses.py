from typing import TypeVar

from fastapi import Request

from app.schemas.common import ApiResponse

T = TypeVar("T")


def build_success_response(
    request: Request,
    *,
    data: T | None = None,
    message: str = "Success.",
    code: str = "success",
) -> ApiResponse[T]:
    request_id = getattr(request.state, "request_id", None)
    return ApiResponse[T](
        code=code,
        message=message,
        data=data,
        request_id=request_id,
    )

