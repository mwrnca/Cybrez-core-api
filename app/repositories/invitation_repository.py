from sqlalchemy.orm import Session

from app.models.invitation import Invitation


class InvitationRepository:

    @staticmethod
    def create(
        db: Session,
        invitation: Invitation,
    ):
        db.add(invitation)
        db.commit()
        db.refresh(invitation)
        return invitation

    @staticmethod
    def get_by_token(
        db: Session,
        token: str,
    ):
        return (
            db.query(Invitation)
            .filter(Invitation.token == token)
            .first()
        )

    @staticmethod
    def get_by_email(
        db: Session,
        email: str,
    ):
        return (
            db.query(Invitation)
            .filter(Invitation.email == email)
            .all()
        )

