from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import DashboardRepository


class DashboardService:

    @staticmethod
    def get_dashboard_stats(db: Session):

        stats = DashboardRepository.get_stats(db)

        stats["tasks_by_status"] = (
            DashboardRepository.tasks_by_status(db)
        )

        stats["project_status"] = (
            DashboardRepository.project_counts(db)
        )

        stats["tasks_per_month"] = (
            DashboardRepository.tasks_per_month(db)
        )

        return stats