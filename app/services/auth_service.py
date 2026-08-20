from uuid import UUID
from jose import JWTError
from sqlalchemy.orm import Session
from app.models.enums import UserRole
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class AuthService:

    @staticmethod
    def register(db: Session, user_data: UserCreate):

        existing = UserRepository.get_by_email(
            db,
            user_data.email,
        )

        if existing:
            raise ValueError("Email already exists")

        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hash_password(
                user_data.password
            ),
            role=UserRole.consumer,        
        )

        return UserRepository.create(db, user)

    @staticmethod
    def login(
        db: Session,
        email: str,
        password: str,
    ):

        user = UserRepository.get_by_email(
            db,
            email,
        )

        if not user or not user.is_active or user.deleted_at is not None:
            return None

        if not verify_password(
            password,
            user.hashed_password,
        ):
            return None

        access_token = create_access_token(str(user.public_id))
        refresh_token = create_refresh_token(str(user.public_id))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    def refresh(
        db: Session,
        refresh_token: str,
    ):
        try:
            payload = decode_refresh_token(refresh_token)
            user_public_id = UUID(payload["sub"])
        except (JWTError, KeyError, ValueError):
            return None

        user = (
            db.query(User)
            .filter(
                User.public_id == user_public_id,
                User.is_active.is_(True),
                User.deleted_at.is_(None),
            )
            .first()
        )

        if not user:
            return None

        new_access_token = create_access_token(str(user.public_id))
        new_refresh_token = create_refresh_token(str(user.public_id))

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }