from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.invitation_repository import InvitationRepository
from app.repositories.organization_repository import OrganizationRepository
from app.core.permissions import require_owner
from app.api.dependencies import get_current_user
from app.core.permissions import require_owner
from app.database.session import get_db
from app.models.user import User
from app.repositories.organization_repository import (
    OrganizationRepository,
)
from app.repositories.invitation_repository import (
    InvitationRepository,
)
from app.schemas.invitation import (
    InvitationCreate,
    InvitationResponse,
)
from app.services.invitation_service import InvitationService
from uuid import UUID

router = APIRouter(
    prefix="/invitations",
    tags=["Invitations"],
)


@router.post(
    "/{organization_id}/invite",
    response_model=InvitationResponse,
)
def invite_user(
    organization_id: UUID,
    data: InvitationCreate,
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

    return InvitationService.create_invitation(
        db,
        organization,
        data,
    )


@router.post(
    "/accept/{token}",
)
def accept_invitation(
    token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invitation = InvitationRepository.get_by_token(
        db,
        token,
    )

    if invitation is None:
        raise HTTPException(
            status_code=404,
            detail="Invitation not found",
        )

    try:
        return InvitationService.accept_invitation(
            db,
            invitation,
            current_user,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

@router.delete(
    "/{invitation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def cancel_invitation(
    invitation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invitation = InvitationRepository.get_by_public_id(
        db,
        invitation_id,
    )

    if invitation is None:
        raise HTTPException(
            status_code=404,
            detail="Invitation not found",
        )

    organization = OrganizationRepository.get_by_public_id(
        db,
        invitation.organization_id,
    )

    require_owner(
        organization,
        current_user,
    )

    InvitationService.cancel(
        db,
        invitation,
        current_user,
    )

@router.post(
    "/{invitation_id}/resend",
    response_model=InvitationResponse,
)
def resend_invitation(
    invitation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    invitation = InvitationRepository.get_by_public_id(
        db,
        invitation_id,
    )

    if invitation is None:
        raise HTTPException(
            status_code=404,
            detail="Invitation not found",
        )

    organization = OrganizationRepository.get_by_public_id(
       db,
        invitation.organization_id,
    )

    require_owner(
        organization,
        current_user,
    )

    try:
        return InvitationService.resend(
            db,
            invitation,
            current_user,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )