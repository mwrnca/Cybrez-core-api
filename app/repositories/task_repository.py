from sqlalchemy.orm import Session

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
            .filter(Task.id == task_id)
            .first()
        )

    @staticmethod
    def get_by_project(
        db: Session,
        project_id: int,
    ):
        return (
            db.query(Task)
            .filter(Task.project_id == project_id)
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
    ):
        db.delete(task)
        db.commit()