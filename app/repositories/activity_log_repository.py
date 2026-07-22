from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog


class ActivityLogRepository:

    @staticmethod
    def create(
        db: Session,
        activity_log: ActivityLog,
    ):
        db.add(activity_log)
        db.commit()
        db.refresh(activity_log)
        return activity_log

    @staticmethod
    def get_by_organization(
        db: Session,
        organization_id: int,
    ):
        return (
            db.query(ActivityLog)
            .filter(
                ActivityLog.organization_id == organization_id,
            )
            .order_by(
                ActivityLog.created_at.desc(),
            )
            .all()
        )

    @staticmethod
    def get_by_public_id(
        db: Session,
        public_id,
    ):
        return (
            db.query(ActivityLog)
            .filter(
                ActivityLog.public_id == public_id,
            )
            .first()
        )