from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from app.database.session import get_db
from app.models.user import User
from app.core.security import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = decode_access_token(token)
        user_public_id = UUID(payload["sub"])

    except (JWTError, KeyError, ValueError):
        raise credentials_exception

    user = (
        db.query(User)
        .filter(
            User.public_id == user_public_id,
            User.is_active.is_(True),
            User.deleted_at.is_(None),
        )
        .first()
    )

    if user is None:
        raise credentials_exception

    return user