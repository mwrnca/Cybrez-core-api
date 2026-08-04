from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.project import Project
from app.models.task import Task
from app.models.user import User


class SearchRepository:

    @staticmethod
    def search_organizations(db: Session, query: str):
        return (
            db.query(Organization)
            .filter(
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
    def search_projects(db: Session, query: str):
        return (
            db.query(Project)
            .filter(
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
    def search_tasks(db: Session, query: str):
        return (
            db.query(Task)
            .filter(
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
    def search_comments(db: Session, query: str):
        return (
            db.query(Comment)
            .filter(
                Comment.deleted_at.is_(None),
                Comment.content.ilike(f"%{query}%"),
            )
            .limit(10)
            .all()
        )

    @staticmethod
    def search_members(db: Session, query: str):
        return (
            db.query(User)
            .join(Membership)
            .filter(
                User.deleted_at.is_(None),
                or_(
                    User.name.ilike(f"%{query}%"),
                    User.email.ilike(f"%{query}%"),
                ),
            )
            .limit(10)
            .all()
        )