from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.membership_repository import MembershipRepository
from app.schemas.membership import (
    MembershipCreate,
    MembershipRoleUpdate,
    MembershipResponse,
)
from app.services.membership_service import MembershipService
from app.core.permissions import (
    require_owner,
    require_role,
)
from app.core.roles import Roles

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
    organization_id: UUID,
    data: MembershipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    organization = OrganizationRepository.get_by_public_id(
        db,
        organization_id,
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found",
        )

    require_role(
        db,
        organization.public_id,
        current_user,
        Roles.MANAGER,
    )

    try:
        return MembershipService.add_member(
            db=db,
            organization_id=organization.public_id,
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
    organization_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    organization = OrganizationRepository.get_by_public_id(
        db,
        organization_id,
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found",
        )

    require_role(
        db,
        organization.public_id,
        current_user,
        Roles.VIEWER,
    )

    return MembershipService.get_members(
        db,
        organization.public_id,
    )


@router.patch(
    "/{organization_id}/members/{user_id}",
    response_model=MembershipResponse,
)
def update_member_role(
    organization_id: UUID,
    user_id: UUID,
    data: MembershipRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    organization = OrganizationRepository.get_by_public_id(
        db,
        organization_id,
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found",
        )

    require_role(
        db,
        organization.public_id,
        current_user,
        Roles.ADMIN,
    )

    membership = MembershipRepository.get_member(
        db,
        organization.public_id,
        user_id,
    )

    if membership is None:
        raise HTTPException(
            status_code=404,
            detail="Member not found",
        )

    try:
        return MembershipService.update_role(
            db,
            membership,
            data.role,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.delete(
    "/{organization_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_member(
    organization_id: UUID,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    organization = OrganizationRepository.get_by_public_id(
        db,
        organization_id,
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

    membership = MembershipRepository.get_member(
        db,
        organization.public_id,
        user_id,
    )

    if membership is None:
        raise HTTPException(
            status_code=404,
            detail="Member not found",
        )

    try:
        MembershipService.remove_member(
            db,
            membership,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.delete(
    "/{organization_id}/leave",
    status_code=status.HTTP_204_NO_CONTENT,
)
def leave_organization(
    organization_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    organization = OrganizationRepository.get_by_public_id(
        db,
        organization_id,
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found",
        )

    membership = MembershipRepository.get_member(
        db,
        organization.public_id,
        current_user.public_id,
    )

    if membership is None:
        raise HTTPException(
            status_code=404,
            detail="You are not a member of this organization",
        )

    try:
        MembershipService.leave_organization(
            db,
            membership,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )