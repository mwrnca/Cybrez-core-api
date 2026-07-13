import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.invitation import Invitation
from app.models.organization import Organization
from app.models.user import User
from app.repositories.invitation_repository import InvitationRepository
from app.schemas.invitation import InvitationCreate
from app.services.membership_service import MembershipService


class InvitationService:

    @staticmethod
    def create_invitation(
        db: Session,
        organization: Organization,
        data: InvitationCreate,
    ):
        invitation = Invitation(
            organization_id=organization.id,
            email=data.email,
            role=data.role,
            token=secrets.token_urlsafe(32),
            expires_at=datetime.now(timezone.utc)
            + timedelta(days=7),
        )

        return InvitationRepository.create(
            db,
            invitation,
        )

    @staticmethod
    def accept_invitation(
        db: Session,
        invitation: Invitation,
        current_user: User,
    ):

        if invitation.accepted:
            raise ValueError("Invitation already accepted")

        if invitation.expires_at < datetime.now(timezone.utc):
            raise ValueError("Invitation has expired")

        MembershipService.add_member(
            db=db,
            organization_id=invitation.organization_id,
            user_id=current_user.id,
            role=invitation.role,
        )

        invitation.accepted = True

        db.commit()
        db.refresh(invitation)

        return invitation

        