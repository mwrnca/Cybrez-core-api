from sqlalchemy.orm import Session
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.repositories.task_repository import TaskRepository
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
)
from app.repositories.membership_repository import MembershipRepository

class TaskService:

    @staticmethod
    def create(
        db: Session,
        project: Project,
        data: TaskCreate,
    ):

        if data.assignee_id is not None:

            membership = MembershipRepository.get_by_user_and_organization(
                db,
                data.assignee_id,
                project.organization_id,
            )

            if membership is None:
                raise ValueError(
                    "Assignee is not a member of this organization"
                )

        task = Task(
            project_id=project.id,
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
            assignee_id=data.assignee_id,
            due_date=data.due_date,
        )

        return TaskRepository.create(
            db,
            task,
        )

    @staticmethod
    def get_all(
        db: Session,
        project_id: int,
    ):
        return TaskRepository.get_by_project(
            db,
            project_id,
        )

    @staticmethod
    def update(
        db: Session,
        task: Task,
        data: TaskUpdate,
    ):
        task.title = data.title
        task.description = data.description
        task.status = data.status
        task.priority = data.priority
        task.assignee_id = data.assignee_id
        task.due_date = data.due_date

        return TaskRepository.update(
            db,
            task,
        )
        
    def delete(
        db: Session,
        task: Task,
        current_user: User,
    ):
        return TaskRepository.delete(
            db,
            task,
            current_user.id,
        )

    @staticmethod
    def restore(
        db: Session,
        task: Task,
    ):
        if task.deleted_at is None:
            raise ValueError("Task is not deleted")

        return TaskRepository.restore(
            db,
            task,
        )

    @staticmethod
    def archive(
        db: Session,
        task: Task,
    ):
        if task.is_archived:
            raise ValueError("Task is already archived")

        return TaskRepository.archive(
            db,
            task,
        )

    @staticmethod
    def unarchive(
        db: Session,
        task: Task,
    ):
        if not task.is_archived:
            raise ValueError("Task is not archived")

        return TaskRepository.unarchive(
            db,
            task,
        )