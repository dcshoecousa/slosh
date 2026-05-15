from typing import Any


class AppException(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found.") -> None:
        super().__init__(status_code=404, code="not_found", message=message)


class ConflictException(AppException):
    def __init__(self, message: str = "Resource already exists.") -> None:
        super().__init__(status_code=409, code="conflict", message=message)


class AuthenticationException(AppException):
    def __init__(self, message: str = "Authentication failed.") -> None:
        super().__init__(status_code=401, code="authentication_error", message=message)


class AuthorizationException(AppException):
    def __init__(self, message: str = "You do not have permission.") -> None:
        super().__init__(status_code=403, code="authorization_error", message=message)


class DatabaseException(AppException):
    def __init__(self, message: str = "Database operation failed.") -> None:
        super().__init__(status_code=500, code="database_error", message=message)
