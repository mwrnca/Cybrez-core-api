from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog
from app.repositories.activity_log_repository import (
    ActivityLogRepository,
)


class ActivityLogService:

    @staticmethod
    def log(
        db: Session,
        organization_id: int,
        user_id: int | None,
        action: str,
        target_type: str,
        target_id: int,
        description: str | None = None,
    ):
        activity = ActivityLog(
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            description=description,
        )

        return ActivityLogRepository.create(
            db,
            activity,
        )

    @staticmethod
    def get_organization_logs(
        db: Session,
        organization_id: int,
    ):
        return ActivityLogRepository.get_by_organization(
            db,
            organization_id,
        )