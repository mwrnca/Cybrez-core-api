from sqlalchemy.orm import Session
from app.models.enums import UserRole
from app.core.security import (
    create_access_token,
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

        if not user:
            return None

        if not verify_password(
            password,
            user.hashed_password,
        ):
            return None

        return create_access_token(str(user.id))