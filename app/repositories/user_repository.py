from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:

    @staticmethod
    def create(
        db: Session,
        user: User,
    ):
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_by_email(
        db: Session,
        email: str,
    ):
        return (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

    @staticmethod
    def get_by_public_id(
        db: Session, 
        public_id: UUID
    ):
        return (
            db.query(User)
            .filter(User.public_id == public_id)
            .first()
        )

    @staticmethod
    def update(
        db: Session,
        user: User,
    ):
        db.commit()
        db.refresh(user)
        return user