from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.comment import Comment


class CommentRepository:

    @staticmethod
    def create(db: Session, comment: Comment):
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment

    @staticmethod
    def get_by_id(
        db: Session,
        comment_id: int,
        include_deleted: bool = False,
    ):
        query = db.query(Comment).filter(
            Comment.id == comment_id,
        )

        if not include_deleted:
            query = query.filter(
                Comment.deleted_at.is_(None),
            )

        return query.first()

    @staticmethod
    def get_by_task(
        db: Session,
        task_id: int,
    ):
        return (
            db.query(Comment)
            .filter(
                Comment.task_id == task_id,
                Comment.deleted_at.is_(None),
            )
            .all()
        )

    @staticmethod
    def update(
        db: Session,
        comment: Comment,
    ):
        db.commit()
        db.refresh(comment)
        return comment

    @staticmethod
    def delete(
        db: Session,
        comment: Comment,
        user_id: int,
    ):
        comment.deleted_at = func.now()
        comment.deleted_by = user_id
        db.commit()

    @staticmethod
    def restore(
        db: Session,
        comment: Comment,
    ):
        comment.deleted_at = None
        comment.deleted_by = None
        db.commit()
        db.refresh(comment)
        return comment

    @staticmethod
    def get_by_public_id(
        db: Session,
        public_id,
        include_deleted: bool = False,
    ):
        query = db.query(Comment).filter(
            Comment.public_id == public_id,
        )

        if not include_deleted:
            query = query.filter(
                Comment.deleted_at.is_(None),
            )

        return query.first()