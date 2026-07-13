from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.project import Project
from app.repositories.project_repository import (
    ProjectRepository,
)
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
)


class ProjectService:

    @staticmethod
    def create(
        db: Session,
        organization: Organization,
        data: ProjectCreate,
    ):
        project = Project(
            organization_id=organization.id,
            name=data.name,
            description=data.description,
        )

        return ProjectRepository.create(
            db,
            project,
        )

    @staticmethod
    def get_all(
        db: Session,
        organization_id: int,
    ):
        return ProjectRepository.get_by_organization(
            db,
            organization_id,
        )

    @staticmethod
    def update(
        db: Session,
        project: Project,
        data: ProjectUpdate,
    ):
        project.name = data.name
        project.description = data.description

        return ProjectRepository.update(
            db,
            project,
        )

    @staticmethod
    def delete(
        db: Session,
        project: Project,
    ):
        ProjectRepository.delete(
            db,
            project,
        )