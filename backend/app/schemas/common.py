"""Common schemas."""
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseBase(BaseModel, Generic[T]):
    """Base response schema."""

    code: int = 0
    message: str = "success"
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    """Error response schema."""

    code: int
    message: str
    detail: Optional[str] = None


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = 1
    page_size: int = 20


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response schema."""

    total: int
    page: int
    page_size: int
    items: list[T]
