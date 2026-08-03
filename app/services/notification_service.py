from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User
from app.repositories.notification_repository import NotificationRepository


class NotificationService:

    @staticmethod
    def create(db: Session, user: User, title: str, message: str):
        notification = Notification(
            user_id=user.id,
            title=title,
            message=message,
        )
        return NotificationRepository.create(db, notification)

    @staticmethod
    def get_for_user(db: Session, user_id: int):
        return NotificationRepository.get_for_user(db, user_id)

    @staticmethod
    def mark_as_read(db: Session, notification: Notification):
        return NotificationRepository.mark_as_read(db, notification)

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int):
        return NotificationRepository.mark_all_as_read(db, user_id)

    @staticmethod
    def delete(db: Session, notification: Notification):
        NotificationRepository.delete(db, notification)
