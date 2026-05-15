from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: str = "success"
    message: str = "Success."
    data: T | None = None
    request_id: str | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: list[dict] | dict | str | None = None
    request_id: str | None = None
