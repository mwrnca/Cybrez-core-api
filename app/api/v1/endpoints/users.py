from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.schemas.profile import PasswordChange, Message
from app.api.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.profile import UserUpdate
from app.schemas.user import UserResponse
from app.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.patch(
    "/me",
    response_model=UserResponse,
)
def update_current_user(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return UserService.update_profile(
        db,
        current_user,
        data,
    )

@router.patch(
    "/me/password",
    response_model=Message,
)
def change_password(
    data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        UserService.change_password(
            db,
            current_user,
            data,
        )

        return Message(
            message="Password updated successfully"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )