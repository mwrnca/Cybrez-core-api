from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.comment import Comment
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.project import Project
from app.models.task import Task
from app.models.user import User


class SearchRepository:

    @staticmethod
    def _organization_ids_for_user(user_id: UUID):
        return select(Membership.organization_id).where(
            Membership.user_id == user_id,
        )

    @staticmethod
    def search_organizations(
        db: Session,
        query: str,
        user_id: UUID,
    ):
        return (
            db.query(Organization)
            .filter(
                Organization.public_id.in_(
                    SearchRepository._organization_ids_for_user(user_id)
                ),
                Organization.deleted_at.is_(None),
                or_(
                    Organization.name.ilike(f"%{query}%"),
                    Organization.description.ilike(f"%{query}%"),
                ),
            )
            .limit(10)
            .all()
        )

    @staticmethod
    def search_projects(
        db: Session,
        query: str,
        user_id: UUID,
    ):
        return (
            db.query(Project)
            .filter(
                Project.organization_id.in_(
                    SearchRepository._organization_ids_for_user(user_id)
                ),
                Project.deleted_at.is_(None),
                or_(
                    Project.name.ilike(f"%{query}%"),
                    Project.description.ilike(f"%{query}%"),
                ),
            )
            .limit(10)
            .all()
        )

    @staticmethod
    def search_tasks(
        db: Session,
        query: str,
        user_id: UUID,
    ):
        return (
            db.query(Task)
            .join(Project)
            .filter(
                Project.organization_id.in_(
                    SearchRepository._organization_ids_for_user(user_id)
                ),
                Task.deleted_at.is_(None),
                or_(
                    Task.title.ilike(f"%{query}%"),
                    Task.description.ilike(f"%{query}%"),
                ),
            )
            .limit(10)
            .all()
        )

    @staticmethod
    def search_comments(
        db: Session,
        query: str,
        user_id: UUID,
    ):
        return (
            db.query(Comment)
            .join(Task)
            .join(Project)
            .filter(
                Project.organization_id.in_(
                    SearchRepository._organization_ids_for_user(user_id)
                ),
                Comment.deleted_at.is_(None),
                Comment.content.ilike(f"%{query}%"),
            )
            .limit(10)
            .all()
        )

    @staticmethod
    def search_members(
        db: Session,
        query: str,
        user_id: UUID,
    ):
        return (
            db.query(User)
            .join(Membership)
            .filter(
                Membership.organization_id.in_(
                    SearchRepository._organization_ids_for_user(user_id)
                ),
                User.deleted_at.is_(None),
                or_(
                    User.full_name.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%"),
                ),
            )
            .limit(10)
            .all()
        )