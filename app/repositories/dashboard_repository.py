from uuid import UUID
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.enums import TaskStatus
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.project import Project
from app.models.task import Task


class DashboardRepository:

    @staticmethod
    def get_organization_stats(
        db: Session,
        organization_id: UUID,
    ):
        organizations = (
            db.query(func.count(Organization.id))
            .filter(Organization.public_id == organization_id)
            .scalar()
        )

        projects = (
            db.query(func.count(Project.id))
            .filter(Project.organization_id == organization_id)
            .scalar()
        )

        active_projects = (
            db.query(func.count(Project.id))
            .filter(
                Project.organization_id == organization_id,
                Project.is_archived == False,
            )
            .scalar()
        )

        archived_projects = (
            db.query(func.count(Project.id))
            .filter(
                Project.organization_id == organization_id,
                Project.is_archived == True,
            )
            .scalar()
        )

        tasks = (
            db.query(func.count(Task.id))
            .join(Project)
            .filter(Project.organization_id == organization_id)
            .scalar()
        )

        completed_tasks = (
            db.query(func.count(Task.id))
            .join(Project)
            .filter(
                Project.organization_id == organization_id,
                Task.status == TaskStatus.done,
            )
            .scalar()
        )

        pending_tasks = (
            db.query(func.count(Task.id))
            .join(Project)
            .filter(
                Project.organization_id == organization_id,
                Task.status != TaskStatus.done,
            )
            .scalar()
        )

        members = (
            db.query(func.count(Membership.id))
            .filter(
                Membership.organization_id == organization_id
            )
            .scalar()
        )

        return {
            "organizations": organizations or 0,
            "projects": projects or 0,
            "active_projects": active_projects or 0,
            "archived_projects": archived_projects or 0,
            "tasks": tasks or 0,
            "completed_tasks": completed_tasks or 0,
            "pending_tasks": pending_tasks or 0,
            "members": members or 0,
        }

    @staticmethod
    def get_stats(
        db: Session,
        user_id: UUID,
    ):
        organization_ids = (
            db.query(Membership.organization_id)
            .filter(Membership.user_id == user_id)
            .subquery()
        )

        organizations = (
            db.query(func.count(Organization.id))
            .filter(Organization.public_id.in_(organization_ids))
            .scalar()
        )

        projects = (
            db.query(func.count(Project.id))
            .filter(Project.organization_id.in_(organization_ids))
            .scalar()
        )

        active_projects = (
            db.query(func.count(Project.id))
            .filter(
                Project.organization_id.in_(organization_ids),
                Project.is_archived == False,
            )
            .scalar()
        )

        archived_projects = (
            db.query(func.count(Project.id))
            .filter(
                Project.organization_id.in_(organization_ids),
                Project.is_archived == True,
            )
            .scalar()
        )

        tasks = (
            db.query(func.count(Task.id))
            .join(Project)
            .filter(Project.organization_id.in_(organization_ids))
            .scalar()
        )

        completed_tasks = (
            db.query(func.count(Task.id))
            .join(Project)
            .filter(
                Project.organization_id.in_(organization_ids),
                Task.status == TaskStatus.done,
            )
            .scalar()
        )

        pending_tasks = (
            db.query(func.count(Task.id))
            .join(Project)
            .filter(
                Project.organization_id.in_(organization_ids),
                Task.status != TaskStatus.done,
            )
            .scalar()
        )

        members = (
            db.query(func.count(Membership.id))
            .filter(Membership.organization_id.in_(organization_ids))
            .scalar()
        )

        return {
            "organizations": organizations or 0,
            "projects": projects or 0,
            "active_projects": active_projects or 0,
            "archived_projects": archived_projects or 0,
            "tasks": tasks or 0,
            "completed_tasks": completed_tasks or 0,
            "pending_tasks": pending_tasks or 0,
            "members": members or 0,
        }

    @staticmethod
    def tasks_by_status(
        db: Session,
        user_id: UUID,
    ):
        organization_ids = (
            db.query(Membership.organization_id)
            .filter(Membership.user_id == user_id)
            .subquery()
        )

        rows = (
            db.query(
                Task.status,
                func.count(Task.id),
            )
            .join(Project)
            .filter(
                Project.organization_id.in_(organization_ids)
            )
            .group_by(Task.status)
            .all()
        )

        return [
            {
                "status": status.value if hasattr(status, "value") else status,
                "count": count,
            }
            for status, count in rows
        ]

    @staticmethod
    def project_counts(
        db: Session,
        user_id: UUID,
    ):
        organization_ids = (
            db.query(Membership.organization_id)
            .filter(Membership.user_id == user_id)
            .subquery()
        )

        active = (
            db.query(Project)
            .filter(
                Project.organization_id.in_(organization_ids),
                Project.is_archived == False,
            )
            .count()
        )

        archived = (
            db.query(Project)
            .filter(
                Project.organization_id.in_(organization_ids),
                Project.is_archived == True,
            )
            .count()
        )

        return [
            {"status": "active", "count": active},
            {"status": "archived", "count": archived},
        ]

    @staticmethod
    def tasks_per_month(
        db: Session,
        user_id: UUID,
    ):
        organization_ids = (
            db.query(Membership.organization_id)
            .filter(Membership.user_id == user_id)
            .subquery()
        )

        rows = (
            db.query(
                func.to_char(
                    Task.created_at,
                    "Mon",
                ).label("month"),
                func.count(Task.id).label("count"),
            )
            .join(Project)
            .filter(
                Project.organization_id.in_(organization_ids)
            )
            .group_by("month")
            .order_by(func.min(Task.created_at))
            .all()
        )

        return [
            {"month": month, "count": count}
            for month, count in rows
        ]