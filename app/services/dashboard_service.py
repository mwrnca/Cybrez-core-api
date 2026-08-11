from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.dashboard_repository import DashboardRepository


class DashboardService:

    @staticmethod
    def get_dashboard_stats(
        db: Session,
        current_user: User,
    ):
        return DashboardRepository.get_stats(
            db,
            current_user.id,
        )

    @staticmethod
    def get_tasks_by_status(
        db: Session,
        current_user: User,
    ):
        return DashboardRepository.tasks_by_status(
            db,
            current_user.id,
        )

    @staticmethod
    def get_project_counts(
        db: Session,
        current_user: User,
    ):
        return DashboardRepository.project_counts(
            db,
            current_user.id,
        )

    @staticmethod
    def get_tasks_per_month(
        db: Session,
        current_user: User,
    ):
        return DashboardRepository.tasks_per_month(
            db,
            current_user.id,
        )