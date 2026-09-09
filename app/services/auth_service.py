from datetime import datetime, timezone
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
from app.models.refresh_session import RefreshSession
from app.repositories.refresh_session_repository import RefreshSessionRepository
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
        AuthService._create_refresh_session(
            db,
            user,
            refresh_token,
        )
        db.commit()

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
            refresh_session_id = UUID(payload["jti"])
            expires_at = datetime.fromtimestamp(
                payload["exp"],
                timezone.utc,
            )
        except (JWTError, KeyError, TypeError, ValueError):
            return None

        refresh_session = RefreshSessionRepository.get_by_public_id(
            db,
            refresh_session_id,
        )

        if (
            refresh_session is None
            or refresh_session.user_id != user_public_id
            or refresh_session.revoked_at is not None
            or refresh_session.expires_at <= datetime.now(timezone.utc)
            or expires_at <= datetime.now(timezone.utc)
            or not RefreshSessionRepository.verify_token(
                refresh_session,
                refresh_token,
            )
        ):
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
        new_refresh_session = AuthService._create_refresh_session(
            db,
            user,
            new_refresh_token,
        )
        RefreshSessionRepository.revoke(refresh_session)
        RefreshSessionRepository.mark_replaced(
            refresh_session,
            new_refresh_session.public_id,
        )
        db.commit()

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    def logout(
        db: Session,
        current_user: User,
        refresh_token: str,
    ) -> bool:
        try:
            payload = decode_refresh_token(refresh_token)
            user_public_id = UUID(payload["sub"])
            refresh_session_id = UUID(payload["jti"])
        except (JWTError, KeyError, TypeError, ValueError):
            return False

        if user_public_id != current_user.public_id:
            return False

        refresh_session = RefreshSessionRepository.get_by_public_id(
            db,
            refresh_session_id,
        )

        if (
            refresh_session is None
            or refresh_session.user_id != current_user.public_id
            or not RefreshSessionRepository.verify_token(
                refresh_session,
                refresh_token,
            )
        ):
            return False

        RefreshSessionRepository.revoke(refresh_session)
        db.commit()
        return True

    @staticmethod
    def _create_refresh_session(
        db: Session,
        user: User,
        refresh_token: str,
    ) -> RefreshSession:
        payload = decode_refresh_token(refresh_token)
        refresh_session = RefreshSession(
            public_id=UUID(payload["jti"]),
            user_id=user.public_id,
            token_hash=hash_password(refresh_token),
            expires_at=datetime.fromtimestamp(
                payload["exp"],
                timezone.utc,
            ),
        )
        return RefreshSessionRepository.create(db, refresh_session)