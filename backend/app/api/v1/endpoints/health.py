from fastapi import APIRouter, Request

from app.api.responses import build_success_response
from app.schemas.common import ApiResponse

router = APIRouter()


@router.get("/health", response_model=ApiResponse[dict[str, str]])
async def health_check(request: Request) -> ApiResponse[dict[str, str]]:
    return build_success_response(
        request,
        data={"status": "ok"},
        message="Health check succeeded.",
    )
