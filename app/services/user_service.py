from sqlalchemy.orm import Session

from app.core.security import (
    verify_password,
    hash_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.profile import (
    PasswordChange,
    UserUpdate,
)


class UserService:

    @staticmethod
    def update_profile(
        db: Session,
        current_user: User,
        data: UserUpdate,
    ):
        if data.full_name is not None:
            current_user.full_name = data.full_name

        return UserRepository.update(
            db,
            current_user,
        )

    @staticmethod
    def change_password(
        db: Session,
        current_user: User,
        data: PasswordChange,
    ):
        if not verify_password(
            data.current_password,
            current_user.hashed_password,
        ):
            raise ValueError("Current password is incorrect")

        current_user.hashed_password = hash_password(
            data.new_password
        )

        return UserRepository.update(
            db,
            current_user,
        )