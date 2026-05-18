from fastapi import APIRouter, Depends, Query, Request, status

from app.api.deps import get_current_user
from app.api.responses import build_success_response
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.task import EchoTaskCreate, TaskEnqueueRead, TaskStatusRead
from app.services.task_service import (
    enqueue_echo_task,
    enqueue_user_summary_task,
    get_task_result,
)

router = APIRouter(prefix="/tasks")


@router.post(
    "/echo",
    response_model=ApiResponse[TaskEnqueueRead],
    status_code=status.HTTP_202_ACCEPTED,
)
async def enqueue_echo_task_endpoint(
    request: Request,
    payload: EchoTaskCreate,
    current_user: User = Depends(get_current_user),
) -> ApiResponse[TaskEnqueueRead]:
    task = await enqueue_echo_task(
        message=payload.message,
        requested_by=current_user.id,
    )
    return build_success_response(
        request,
        data=task,
        message="Echo task queued successfully.",
    )


@router.post(
    "/user-summary",
    response_model=ApiResponse[TaskEnqueueRead],
    status_code=status.HTTP_202_ACCEPTED,
)
async def enqueue_user_summary_task_endpoint(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> ApiResponse[TaskEnqueueRead]:
    task = await enqueue_user_summary_task(requested_by=current_user.id)
    return build_success_response(
        request,
        data=task,
        message="User summary task queued successfully.",
    )


@router.get("/{task_id}", response_model=ApiResponse[TaskStatusRead])
async def read_task_result(
    request: Request,
    task_id: str,
    wait: bool = False,
    timeout_seconds: float | None = Query(default=None, ge=0.1, le=300.0),
    current_user: User = Depends(get_current_user),
) -> ApiResponse[TaskStatusRead]:
    _ = current_user
    task_status = await get_task_result(
        task_id=task_id,
        wait=wait,
        timeout_seconds=timeout_seconds,
    )
    return build_success_response(
        request,
        data=task_status,
        message="Task status fetched successfully.",
    )
