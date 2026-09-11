from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog
from app.models.comment import Comment
from app.models.invitation import Invitation
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.project import Project
from app.models.task import Task


class ActivityLogRepository:

    @staticmethod
    def _attach_target_public_ids(
        db: Session,
        activity_logs: list[ActivityLog],
    ):
        target_ids_by_type: dict[str, set[int]] = {}

        for activity_log in activity_logs:
            target_ids_by_type.setdefault(
                activity_log.target_type,
                set(),
            ).add(activity_log.target_id)

        target_models = {
            "organization": Organization,
            "project": Project,
            "task": Task,
            "comment": Comment,
            "membership": Membership,
            "invitation": Invitation,
        }
        public_ids_by_type: dict[str, dict[int, object]] = {}

        for target_type, target_ids in target_ids_by_type.items():
            model = target_models.get(target_type)
            if model is None:
                continue

            public_ids_by_type[target_type] = {
                target.id: target.public_id
                for target in db.query(model)
                .filter(model.id.in_(target_ids))
                .all()
            }

        for activity_log in activity_logs:
            activity_log.target_public_id = public_ids_by_type.get(
                activity_log.target_type,
                {},
            ).get(activity_log.target_id)

        return activity_logs

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
        activity_logs = (
            db.query(ActivityLog)
            .filter(
                ActivityLog.organization_id == organization_id,
            )
            .order_by(
                ActivityLog.created_at.desc(),
            )
            .all()
        )

        return ActivityLogRepository._attach_target_public_ids(
            db,
            activity_logs,
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