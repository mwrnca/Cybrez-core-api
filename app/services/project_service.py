from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.project import Project
from app.models.user import User

from app.repositories.project_repository import ProjectRepository
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
)
from app.services.activity_log_service import ActivityLogService


class ProjectService:

    @staticmethod
    def create(
        db: Session,
        organization: Organization,
        current_user: User,
        data: ProjectCreate,
    ):
        project = Project(
            organization_id=organization.public_id,
            name=data.name,
            description=data.description,
        )

        project = ProjectRepository.create(
            db,
            project,
        )

        ActivityLogService.log(
            db=db,
            organization_id=organization.id,
            user_id=current_user.id,
            action="project_created",
            target_type="project",
            target_id=project.id,
            description=f"Created project '{project.name}'",
        )

        return project

    @staticmethod
    def get_all(
        db: Session,
        organization_id,
    ):
        return ProjectRepository.get_by_organization(
            db,
            organization_id,
        )

    @staticmethod
    def update(
        db: Session,
        project: Project,
        current_user: User,
        data: ProjectUpdate,
    ):
        if data.name is not None:
            project.name = data.name

        if data.description is not None:
            project.description = data.description

        project = ProjectRepository.update(
            db,
            project,
        )

        ActivityLogService.log(
            db=db,
            organization_id=project.organization.id,
            user_id=current_user.id,
            action="project_updated",
            target_type="project",
            target_id=project.id,
            description=f"Updated project '{project.name}'",
        )

        return project

    @staticmethod
    def delete(
        db: Session,
        project: Project,
        current_user: User,
    ):
        organization_int_id = project.organization.id

        ProjectRepository.delete(
            db,
            project,
            current_user.id,
        )

        ActivityLogService.log(
            db=db,
            organization_id=organization_int_id,
            user_id=current_user.id,
            action="project_deleted",
            target_type="project",
            target_id=project.id,
            description=f"Deleted project '{project.name}'",
        )

    @staticmethod
    def restore(
        db: Session,
        project: Project,
        current_user: User,
    ):
        if project.deleted_at is None:
            raise ValueError("Project is not deleted")

        project = ProjectRepository.restore(
            db,
            project,
        )

        ActivityLogService.log(
            db=db,
            organization_id=project.organization.id,
            user_id=current_user.id,
            action="project_restored",
            target_type="project",
            target_id=project.id,
            description=f"Restored project '{project.name}'",
        )

        return project

    @staticmethod
    def archive(
        db: Session,
        project: Project,
        current_user: User,
    ):
        if project.is_archived:
            raise ValueError("Project is already archived")

        project = ProjectRepository.archive(
            db,
            project,
        )

        ActivityLogService.log(
            db=db,
            organization_id=project.organization.id,
            user_id=current_user.id,
            action="project_archived",
            target_type="project",
            target_id=project.id,
            description=f"Archived project '{project.name}'",
        )

        return project

    @staticmethod
    def unarchive(
        db: Session,
        project: Project,
        current_user: User,
    ):
        if not project.is_archived:
            raise ValueError("Project is not archived")

        project = ProjectRepository.unarchive(
            db,
            project,
        )

        ActivityLogService.log(
            db=db,
            organization_id=project.organization.id,
            user_id=current_user.id,
            action="project_unarchived",
            target_type="project",
            target_id=project.id,
            description=f"Unarchived project '{project.name}'",
        )

        return project