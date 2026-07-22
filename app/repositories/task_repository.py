from uuid import UUID

from sqlalchemy.orm import Session

from app.core.soft_delete import soft_delete
from app.models.task import Task


class TaskRepository:

    @staticmethod
    def create(
        db: Session,
        task: Task,
    ):
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def get_by_id(
        db: Session,
        task_id: int,
    ):
        return (
            db.query(Task)
            .filter(
                Task.id == task_id,
                Task.deleted_at.is_(None),
            )
            .first()
        )

    @staticmethod
    def get_by_public_id(
        db,
        public_id,
        include_deleted=False,
    ):
        query = db.query(Task).filter(
            Task.public_id == public_id
        )

        if not include_deleted:
            query = query.filter(
                Task.deleted_at.is_(None)
            )

        return query.first()

    @staticmethod
    def get_by_project(
        db: Session,
        project_id: int,
    ):
        return (
            db.query(Task)
            .filter(
                Task.project_id == project_id,
                Task.deleted_at.is_(None),
            )
            .all()
        )

    @staticmethod
    def update(
        db: Session,
        task: Task,
    ):
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete(
        db: Session,
        task: Task,
        user_id: int | None = None,
    ):
        soft_delete(task, user_id)

        db.commit()
        db.refresh(task)

        return task

    @staticmethod
    def restore(
        db: Session,
        task: Task,
    ):
        task.deleted_at = None
        task.deleted_by = None

        db.commit()
        db.refresh(task)

        return task

    @staticmethod
    def archive(
        db: Session,
        task: Task,
    ):
        task.is_archived = True

        db.commit()
        db.refresh(task)

        return task

    @staticmethod
    def unarchive(
        db: Session,
        task: Task,
    ):
        task.is_archived = False

        db.commit()
        db.refresh(task)

        return task