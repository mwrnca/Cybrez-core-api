from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.organization_service import (
    OrganizationService,
)
from app.repositories.dashboard_repository import (
    DashboardRepository,
)
from app.repositories.activity_log_repository import (
    ActivityLogRepository,
)


class OrganizationOverviewService:

    @staticmethod
    def get_overview(
        db: Session,
        organization_public_id: UUID,
        current_user: User,
    ):
        organization = OrganizationService.get_by_public_id(
            db,
            organization_public_id,
        )

        stats = DashboardRepository.get_organization_stats(
            db,
            organization.public_id,
        )

        recent_activity = ActivityLogRepository.get_by_organization(
            db,
            organization.id,
        )

        return {
            "organization": organization,
            "stats": stats,
            "recent_activity": recent_activity[:10],
        }