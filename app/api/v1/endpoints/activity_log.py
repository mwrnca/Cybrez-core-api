from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.repositories.activity_log_repository import (
    ActivityLogRepository,
)
from app.repositories.organization_repository import (
    OrganizationRepository,
)

router = APIRouter(
    prefix="/activity-logs",
    tags=["Activity Logs"],
)


@router.get("/{organization_public_id}")
def list_activity_logs(
    organization_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    organization = OrganizationRepository.get_by_public_id(
        db,
        organization_public_id,
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found",
        )

    return ActivityLogRepository.get_by_organization(
        db,
        organization.id,
    )