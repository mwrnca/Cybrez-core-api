from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.enums import TaskStatus
from app.models.organization import Organization
from app.models.project import Project
from app.models.task import Task
from app.models.membership import Membership


class DashboardRepository:

    @staticmethod
    def get_stats(db: Session):

        organizations = db.query(func.count(Organization.id)).scalar()

        projects = db.query(func.count(Project.id)).scalar()

        active_projects = (
            db.query(func.count(Project.id))
            .filter(Project.is_archived == False)
            .scalar()
        )

        archived_projects = (
            db.query(func.count(Project.id))
            .filter(Project.is_archived == True)
            .scalar()
        )

        tasks = db.query(func.count(Task.id)).scalar()

        completed_tasks = (
            db.query(func.count(Task.id))
            .filter(Task.status == TaskStatus.done)
            .scalar()
        )

        pending_tasks = (
            db.query(func.count(Task.id))
            .filter(Task.status != TaskStatus.done)
            .scalar()
        )

        members = db.query(func.count(Membership.id)).scalar()

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
    def tasks_by_status(db):
        rows = (
            db.query(
                Task.status,
                func.count(Task.id),
            )
            .group_by(Task.status)
            .all()
        )

        return {
            status.value if hasattr(status, "value") else status: count
            for status, count in rows
        }

    @staticmethod
    def project_counts(db):
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

        return {
            "active": active,
            "archived": archived,
        }

    @staticmethod
    def tasks_per_month(db):
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