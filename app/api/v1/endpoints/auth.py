from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
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
from app.schemas.token import RefreshTokenRequest, Token, TokenPayload

from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
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
)
def login(
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

    return token_data


@router.post(
    "/refresh",
    response_model=Token,
)
def refresh_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    token_data = AuthService.refresh(db, data.refresh_token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    return token_data


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user