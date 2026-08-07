from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.enums import TaskStatus
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.project import Project
from app.models.task import Task


class DashboardRepository:

    @staticmethod
    def get_stats(
        db: Session,
        organization_id: int | None = None,
    ):
        organizations = db.query(
            func.count(Organization.id)
        ).scalar()

        projects_query = db.query(Project)

        if organization_id is not None:
            projects_query = projects_query.filter(
                Project.organization_id == organization_id
            )

        projects = projects_query.count()

        active_query = db.query(Project).filter(
            Project.is_archived == False
        )

        if organization_id is not None:
            active_query = active_query.filter(
                Project.organization_id == organization_id
            )

        active_projects = active_query.count()

        archived_query = db.query(Project).filter(
            Project.is_archived == True
        )

        if organization_id is not None:
            archived_query = archived_query.filter(
                Project.organization_id == organization_id
            )

        archived_projects = archived_query.count()

        tasks_query = db.query(Task)

        if organization_id is not None:
            tasks_query = (
                tasks_query
                .join(Project)
                .filter(
                    Project.organization_id == organization_id
                )
            )

        tasks = tasks_query.count()

        completed_query = db.query(Task).filter(
            Task.status == TaskStatus.done
        )

        if organization_id is not None:
            completed_query = (
                completed_query
                .join(Project)
                .filter(
                    Project.organization_id == organization_id
                )
            )

        completed_tasks = completed_query.count()

        pending_query = db.query(Task).filter(
            Task.status != TaskStatus.done
        )

        if organization_id is not None:
            pending_query = (
                pending_query
                .join(Project)
                .filter(
                    Project.organization_id == organization_id
                )
            )

        pending_tasks = pending_query.count()

        members_query = db.query(Membership)

        if organization_id is not None:
            members_query = members_query.filter(
                Membership.organization_id == organization_id
            )

        members = members_query.count()

        return {
            "organizations": organizations,
            "projects": projects,
            "active_projects": active_projects,
            "archived_projects": archived_projects,
            "tasks": tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "members": members,
        }

    @staticmethod
    def tasks_by_status(db: Session):
        rows = (
            db.query(
                Task.status,
                func.count(Task.id),
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
    def project_counts(db: Session):
        active = (
            db.query(Project)
            .filter(Project.is_archived == False)
            .count()
        )

        archived = (
            db.query(Project)
            .filter(Project.is_archived == True)
            .count()
        )

        return [
            {
                "status": "active",
                "count": active,
            },
            {
                "status": "archived",
                "count": archived,
            },
        ]

    @staticmethod
    def tasks_per_month(db: Session):
        rows = (
            db.query(
                func.to_char(
                    Task.created_at,
                    "Mon",
                ).label("month"),
                func.count(Task.id).label("count"),
            )
            .group_by("month")
            .order_by(func.min(Task.created_at))
            .all()
        )

        return [
            {
                "month": month,
                "count": count,
            }
            for month, count in rows
        ]