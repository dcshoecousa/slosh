from taskiq.exceptions import (
    ResultGetError,
    ResultIsReadyError,
    TaskiqResultTimeoutError,
)
from taskiq.task import AsyncTaskiqTask

from app.core.exceptions import ServiceUnavailableException
from app.core.settings import settings
from app.schemas.task import TaskEnqueueRead, TaskResultRead, TaskStatusRead
from app.task.broker import broker
from app.task.tasks import echo_message_task, generate_user_summary_task


def ensure_taskiq_enabled() -> None:
    if settings.taskiq_enabled:
        return

    raise ServiceUnavailableException(
        "Task queue is disabled. Set TASKIQ_ENABLED=true to enqueue and read tasks."
    )


async def enqueue_echo_task(*, message: str, requested_by: int) -> TaskEnqueueRead:
    ensure_taskiq_enabled()
    task = await echo_message_task.kiq(message=message, requested_by=requested_by)
    return TaskEnqueueRead(task_id=task.task_id, task_name="tasks.echo")


async def enqueue_user_summary_task(*, requested_by: int) -> TaskEnqueueRead:
    ensure_taskiq_enabled()
    task = await generate_user_summary_task.kiq(requested_by=requested_by)
    return TaskEnqueueRead(
        task_id=task.task_id,
        task_name="tasks.generate_user_summary",
    )


def _build_task(task_id: str) -> AsyncTaskiqTask:
    return AsyncTaskiqTask(task_id=task_id, result_backend=broker.result_backend)


def _build_completed_status(task_id: str, result) -> TaskStatusRead:
    return TaskStatusRead(
        task_id=task_id,
        status="failed" if result.is_err else "completed",
        details=TaskResultRead(
            is_err=result.is_err,
            execution_time=result.execution_time,
            result=result.return_value,
            error=str(result.error) if result.error else None,
        ),
    )


async def get_task_result(
    *,
    task_id: str,
    wait: bool = False,
    timeout_seconds: float | None = None,
) -> TaskStatusRead:
    ensure_taskiq_enabled()
    task = _build_task(task_id)

    try:
        if wait:
            result = await task.wait_result(
                check_interval=settings.taskiq_poll_interval_seconds,
                timeout=timeout_seconds if timeout_seconds is not None else -1.0,
            )
            return _build_completed_status(task_id, result)

        is_ready = await task.is_ready()
        if not is_ready:
            return TaskStatusRead(task_id=task_id, status="queued")

        result = await task.get_result()
        return _build_completed_status(task_id, result)
    except TaskiqResultTimeoutError:
        return TaskStatusRead(task_id=task_id, status="queued")
    except (ResultGetError, ResultIsReadyError):
        return TaskStatusRead(task_id=task_id, status="queued")
