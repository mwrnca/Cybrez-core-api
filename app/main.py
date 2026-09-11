import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.config.settings import settings

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    api_router,
    prefix=settings.API_V1_PREFIX,
)


@app.exception_handler(Exception)
async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Catch-all handler for unhandled exceptions.

    FastAPI's own HTTPException and RequestValidationError handlers are
    registered at a higher priority and are NOT intercepted here.  This
    handler only fires for truly unexpected errors (programming bugs,
    database connectivity failures, etc.).

    Client response: a generic 500 with no implementation details.
    Internal log:    full traceback at ERROR level for debugging.
    """
    # Let FastAPI's built-in handlers deal with expected exception types.
    if isinstance(exc, (HTTPException, RequestValidationError)):
        raise exc

    logger.exception(
        "Unhandled internal error — %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.get("/")
def root():
    return {
        "message": "CYBREZ API running"
    }