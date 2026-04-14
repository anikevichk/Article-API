from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError


def get_error_code(status_code: int) -> str:
    return {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        409: "conflict",
        422: "validation_error",
    }.get(status_code, "http_error")


async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": get_error_code(exc.status_code),
                "message": exc.detail,
            }
        },
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Invalid request data",
                "details": exc.errors(),
            }
        },
    )


async def integrity_exception_handler(request: Request, exc: IntegrityError):
    return JSONResponse(
        status_code=409,
        content={
            "error": {
                "code": "conflict",
                "message": "Database constraint violated",
            }
        },
    )
