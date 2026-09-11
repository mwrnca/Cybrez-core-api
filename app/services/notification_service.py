from sqlalchemy.orm import Session
from uuid import UUID

from app.models.notification import Notification
from app.models.user import User
from app.repositories.invitation_repository import InvitationRepository
from app.repositories.notification_repository import NotificationRepository


class NotificationService:

    @staticmethod
    def _response_data(db: Session, notification: Notification):
        reference_id = notification.reference_id
        if notification.type == "invitation" and reference_id:
            invitation = None
            try:
                invitation_id = UUID(reference_id)
            except ValueError:
                invitation_id = None

            if invitation_id is not None:
                invitation = InvitationRepository.get_by_public_id(
                    db,
                    invitation_id,
                )
            if invitation is None:
                invitation = InvitationRepository.get_by_token(
                    db,
                    reference_id,
                )
            reference_id = (
                str(invitation.public_id)
                if invitation is not None
                else None
            )

        return {
            "public_id": notification.public_id,
            "user_public_id": notification.user_public_id,
            "title": notification.title,
            "message": notification.message,
            "type": notification.type,
            "reference_id": reference_id,
            "is_read": notification.is_read,
            "created_at": notification.created_at,
        }

    @staticmethod
    def create(
        db: Session,
        user: User,
        title: str,
        message: str,
        type: str | None = None,
        reference_id: str | None = None,
    ):
        notification = Notification(
            user_id=user.id,
            title=title,
            message=message,
            type=type,
            reference_id=reference_id,
        )
        return NotificationRepository.create(db, notification)

    @staticmethod
    def get_for_user(db: Session, user_id: int):
        return [
            NotificationService._response_data(db, notification)
            for notification in NotificationRepository.get_for_user(db, user_id)
        ]

    @staticmethod
    def mark_as_read(db: Session, notification: Notification):
        notification = NotificationRepository.mark_as_read(db, notification)
        return NotificationService._response_data(db, notification)

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int):
        return [
            NotificationService._response_data(db, notification)
            for notification in NotificationRepository.mark_all_as_read(db, user_id)
        ]

    @staticmethod
    def delete(db: Session, notification: Notification):
        NotificationRepository.delete(db, notification)