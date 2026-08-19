from uuid import UUID
from sqlalchemy.orm import Session

from app.core.soft_delete import soft_delete
from app.models.project import Project


class ProjectRepository:

    @staticmethod
    def create(
        db: Session,
        project: Project,
    ):
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get_by_id(
        db: Session,
        project_id: int,
        include_deleted: bool = False,
    ):
        query = (
            db.query(Project)
            .filter(Project.id == project_id)
        )

        if not include_deleted:
            query = query.filter(
                Project.deleted_at.is_(None)
            )

        return query.first()

    @staticmethod
    def get_by_public_id(
        db: Session,
        public_id,
        include_deleted: bool = False,
    ):
        query = (
            db.query(Project)
            .filter(Project.public_id == public_id)
        )

        if not include_deleted:
            query = query.filter(
                Project.deleted_at.is_(None)
            )

        return query.first()

    @staticmethod
    def get_by_organization_public_id(
        db: Session,
        organization_public_id: UUID,
    ):
        return (
            db.query(Project)
            .filter(
                Project.organization_id == organization_public_id,
                Project.deleted_at.is_(None),
            )
            .all()
        )

    @staticmethod
    def update(
        db: Session,
        project: Project,
    ):
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete(
        db: Session,
        project: Project,
        user_id: int | None = None,
    ):
        soft_delete(
            project,
            user_id,
        )

        db.commit()
        db.refresh(project)

        return project

    @staticmethod
    def restore(
        db: Session,
        project: Project,
    ):
        project.deleted_at = None
        project.deleted_by = None

        db.commit()
        db.refresh(project)

        return project

    @staticmethod
    def archive(
        db: Session,
        project: Project,
    ):
        project.is_archived = True

        db.commit()
        db.refresh(project)

        return project

    @staticmethod
    def unarchive(
        db: Session,
        project: Project,
    ):
        project.is_archived = False

        db.commit()
        db.refresh(project)

        return project