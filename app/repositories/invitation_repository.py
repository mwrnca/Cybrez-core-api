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
            .filter(
                Invitation.token == token,
            )
            .first()
        )

    @staticmethod
    def get_by_email(
        db: Session,
        email: str,
    ):
        return (
            db.query(Invitation)
            .filter(
                Invitation.email == email,
            )
            .all()
        )

    @staticmethod
    def update(
        db: Session,
        invitation: Invitation,
    ):
        db.commit()
        db.refresh(invitation)
        return invitation

    @staticmethod
    def delete(
        db: Session,
        invitation: Invitation,
    ):
        db.delete(invitation)
        db.commit()

    @staticmethod
    def get_by_id(
        db: Session,
        invitation_id: UUID,
    ):
        return (
            db.query(Invitation)
            .filter(
                Invitation.public_id == invitation_id,
            )
            .first()
        )

    @staticmethod
    def get_by_public_id(
        db: Session,
        public_id,
    ):
        return (
            db.query(Invitation)
            .filter(
                Invitation.public_id == public_id,
            )
            .first()
        )