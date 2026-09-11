from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    HTTPException,
    Response,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.user import (
    UserCreate,
    UserResponse,
)
from app.models.user import User
from app.api.dependencies import get_current_user
from app.schemas.token import Token, TokenPayload
from app.config.settings import settings
from app.core.rate_limit import (
    ip_rate_limit,
    login_limiter,
    logout_limiter,
    refresh_limiter,
    register_limiter,
)

from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

REFRESH_COOKIE_PATH = f"{settings.API_V1_PREFIX}/auth"
REFRESH_COOKIE_MAX_AGE = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60


def set_refresh_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=REFRESH_COOKIE_MAX_AGE,
        httponly=True,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite="lax",
        path=REFRESH_COOKIE_PATH,
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(ip_rate_limit(register_limiter))],
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
):

    try:
        return AuthService.register(db, user)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=Token,
    dependencies=[Depends(ip_rate_limit(login_limiter))],
)
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    token_data = AuthService.login(
        db,
        form_data.username,
        form_data.password,
    )

    if token_data is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    refresh_token = token_data.pop("refresh_token")
    set_refresh_cookie(response, refresh_token)
    return token_data


@router.post(
    "/refresh",
    response_model=Token,
    dependencies=[Depends(ip_rate_limit(refresh_limiter))],
)
def refresh_token(
    response: Response,
    refresh_token: str | None = Cookie(
        default=None,
        alias=settings.REFRESH_COOKIE_NAME,
    ),
    db: Session = Depends(get_db),
):
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    token_data = AuthService.refresh(db, refresh_token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    new_refresh_token = token_data.pop("refresh_token")
    set_refresh_cookie(response, new_refresh_token)
    return token_data


@router.post(
    "/logout",
    dependencies=[Depends(ip_rate_limit(logout_limiter))],
)
def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    refresh_token: str | None = Cookie(
        default=None,
        alias=settings.REFRESH_COOKIE_NAME,
    ),
    db: Session = Depends(get_db),
):
    if refresh_token is None or not AuthService.logout(
        db,
        current_user,
        refresh_token,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    response.delete_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        path=REFRESH_COOKIE_PATH,
    )
    return {"detail": "Logged out"}


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user