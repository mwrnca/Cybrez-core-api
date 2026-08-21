from sqlalchemy.orm import Session

from app.models.user import User
from app.models.project import Project
from app.models.task import Task

from app.repositories.membership_repository import MembershipRepository
from app.repositories.task_repository import TaskRepository

from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:

    @staticmethod
    def _resolve_assignee(
        db: Session,
        user_public_id,
        organization_id: int,
    ) -> int | None:

        if user_public_id is None:
            return None

        user = (
            db.query(User)
            .filter(User.public_id == user_public_id)
            .first()
        )

        if user is None:
            raise ValueError("Assignee not found")

        membership = (
            MembershipRepository.get_by_user_and_organization(
                db,
                user.public_id,
                organization_id,
            )
        )

        if membership is None:
            raise ValueError(
                "Assignee is not a member of this organization"
            )

        return user.id

    @staticmethod
    def create(
        db: Session,
        project: Project,
        data: TaskCreate,
    ):
        assignee_id = TaskService._resolve_assignee(
            db,
            data.assignee_id,
            project.organization_id,
        )

        task = Task(
            project_id=project.id,
            title=data.title,
            description=data.description,
            status=data.status,
            priority=data.priority,
            assignee_id=assignee_id,
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
        assignee_id = TaskService._resolve_assignee(
            db,
            data.assignee_id,
            task.project.organization_id,
        )

        task.title = data.title
        task.description = data.description
        task.status = data.status
        task.priority = data.priority
        task.assignee_id = assignee_id
        task.due_date = data.due_date

        return TaskRepository.update(
            db,
            task,
        )

    @staticmethod
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