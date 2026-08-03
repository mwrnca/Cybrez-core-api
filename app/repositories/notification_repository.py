from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationRepository:

    @staticmethod
    def create(db: Session, notification: Notification):
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def get_by_public_id(db: Session, public_id):
        return (
            db.query(Notification)
            .filter(Notification.public_id == public_id)
            .first()
        )

    @staticmethod
    def get_for_user(db: Session, user_id: int):
        return (
            db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .all()
        )

    @staticmethod
    def mark_as_read(db: Session, notification: Notification):
        notification.is_read = True
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int):
        notifications = (
            db.query(Notification)
            .filter(Notification.user_id == user_id, Notification.is_read.is_(False))
            .all()
        )

        for notification in notifications:
            notification.is_read = True

        db.commit()
        return notifications

    @staticmethod
    def delete(db: Session, notification: Notification):
        db.delete(notification)
        db.commit()
