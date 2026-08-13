from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.task import Task
from app.models.user import User
from app.repositories.comment_repository import CommentRepository
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
)
from app.services.activity_log_service import ActivityLogService


class CommentService:

    @staticmethod
    def create(
        db: Session,
        task: Task,
        current_user: User,
        data: CommentCreate,
    ):
        comment = Comment(
            task_id=task.id,
            user_id=current_user.id,
            content=data.content,
        )

        comment = CommentRepository.create(
            db,
            comment,
        )

        ActivityLogService.log(
            db=db,
            organization_id=task.project.organization.id,
            user_id=current_user.id,
            action="comment_created",
            target_type="comment",
            target_id=comment.id,
            description=f"Added comment to task '{task.title}'",
        )

        return comment

    @staticmethod
    def get_all(
        db: Session,
        task_id: int,
    ):
        return CommentRepository.get_by_task(
            db,
            task_id,
        )

    @staticmethod
    def update(
        db: Session,
        comment: Comment,
        current_user: User,
        data: CommentUpdate,
    ):
        comment.content = data.content

        comment = CommentRepository.update(
            db,
            comment,
        )

        ActivityLogService.log(
            db=db,
            organization_id=comment.task.project.organization.id,
            user_id=current_user.id,
            action="comment_updated",
            target_type="comment",
            target_id=comment.id,
            description="Updated a comment",
        )

        return comment

    @staticmethod
    def delete(
        db: Session,
        comment: Comment,
        current_user: User,
    ):
        CommentRepository.delete(
            db,
            comment,
            current_user.id,
        )

        ActivityLogService.log(
            db=db,
            organization_id=comment.task.project.organization.id,
            user_id=current_user.id,
            action="comment_deleted",
            target_type="comment",
            target_id=comment.id,
            description="Deleted a comment",
        )

    @staticmethod
    def restore(
        db: Session,
        comment: Comment,
        current_user: User,
    ):
        if comment.deleted_at is None:
            raise ValueError("Comment is not deleted")

        comment = CommentRepository.restore(
            db,
            comment,
        )

        ActivityLogService.log(
            db=db,
            organization_id=comment.task.project.organization.id,
            user_id=current_user.id,
            action="comment_restored",
            target_type="comment",
            target_id=comment.id,
            description="Restored a comment",
        )

        return comment