from typing import Any, Literal

from pydantic import BaseModel, Field


class EchoTaskCreate(BaseModel):
    message: str = Field(min_length=1, max_length=500)


class TaskEnqueueRead(BaseModel):
    task_id: str
    task_name: str
    status: Literal["queued"] = "queued"


class TaskResultRead(BaseModel):
    is_err: bool
    execution_time: float
    result: Any | None = None
    error: str | None = None


class TaskStatusRead(BaseModel):
    task_id: str
    status: Literal["queued", "completed", "failed"]
    details: TaskResultRead | None = None
