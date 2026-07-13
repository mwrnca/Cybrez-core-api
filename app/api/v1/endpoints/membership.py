from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.session import get_db
from app.models.organization import Organization
from app.models.user import User
from app.repositories.membership_repository import MembershipRepository
from app.schemas.membership import (
    MembershipCreate,
    MembershipResponse,
)
from app.services.membership_service import MembershipService
from app.core.permissions import require_owner

router = APIRouter(
    prefix="/organizations",
    tags=["Memberships"],
)


@router.post(
    "/{organization_id}/members",
    response_model=MembershipResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_member(
    organization_id: int,
    data: MembershipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    organization = (
        db.query(Organization)
        .filter(Organization.id == organization_id)
        .first()
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found",
        )

    require_owner(
        organization,
        current_user,
    )

    try:
        return MembershipService.add_member(
            db=db,
            organization_id=organization.id,
            user_id=data.user_id,
            role=data.role,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
        
@router.get(
    "/{organization_id}/members",
    response_model=list[MembershipResponse],
)

def list_members(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print("Reached list_members")
    organization = (
        db.query(Organization)
        .filter(
            Organization.id == organization_id
        )
        .first()
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found",
        )

    require_owner(
        organization,
        current_user,
    )

    return MembershipService.get_members(
        db,
        organization_id,
    )

    