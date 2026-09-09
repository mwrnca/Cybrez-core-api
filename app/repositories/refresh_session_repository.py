from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.security import verify_refresh_token
from app.models.refresh_session import RefreshSession


class RefreshSessionRepository:

    @staticmethod
    def create(
        db: Session,
        refresh_session: RefreshSession,
    ):
        db.add(refresh_session)
        db.flush()
        return refresh_session

    @staticmethod
    def get_by_public_id(
        db: Session,
        public_id: UUID,
    ):
        return (
            db.query(RefreshSession)
            .filter(RefreshSession.public_id == public_id)
            .first()
        )

    @staticmethod
    def revoke(
        refresh_session: RefreshSession,
    ):
        refresh_session.revoked_at = datetime.now(timezone.utc)
        return refresh_session

    @staticmethod
    def mark_replaced(
        refresh_session: RefreshSession,
        replaced_by_id: UUID,
    ):
        refresh_session.replaced_by_id = replaced_by_id
        return refresh_session

    @staticmethod
    def verify_token(
        refresh_session: RefreshSession,
        token: str,
    ) -> bool:
        return verify_refresh_token(token, refresh_session.token_hash)