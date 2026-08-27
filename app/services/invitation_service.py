import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.invitation import Invitation
from app.models.organization import Organization
from app.models.user import User
from app.repositories.invitation_repository import (
    InvitationRepository,
)
from app.repositories.membership_repository import (
    MembershipRepository,
)
from app.repositories.user_repository import UserRepository
from app.schemas.invitation import InvitationCreate
from app.services.activity_log_service import (
    ActivityLogService,
)
from app.services.membership_service import (
    MembershipService,
)
from app.services.notification_service import (
    NotificationService,
)


class InvitationService:

    @staticmethod
    def create_invitation(
        db: Session,
        organization: Organization,
        data: InvitationCreate,
    ):
        invitee = UserRepository.get_by_email(
            db,
            data.email,
        )

        if invitee is None:
            raise ValueError(
                "No CYBREZ account found for that email. "
                "They'll need to register first before you can invite them."
            )

        existing_membership = (
            MembershipRepository.get_by_user_and_organization(
                db,
                invitee.public_id,
                organization.public_id,
            )
        )

        if existing_membership is not None:
            raise ValueError(
                "This person is already a member of the organization."
            )

        invitation = Invitation(
            organization_id=organization.public_id,
            email=data.email,
            role=data.role,
            token=secrets.token_urlsafe(32),
            expires_at=(
                datetime.now(timezone.utc)
                + timedelta(days=7)
            ),
        )

        invitation = InvitationRepository.create(
            db,
            invitation,
        )

        accept_url = (
            f"{settings.FRONTEND_URL}"
            f"/invitations/accept/{invitation.token}"
        )

        NotificationService.create(
            db,
            invitee,
            title="Workspace invitation",
            message=(
                f"You've been invited to join "
                f"'{organization.name}' as {data.role}. "
                f"Accept it here: {accept_url}"
            ),
        )

        return invitation

    @staticmethod
    def list_invitations(
        db: Session,
        organization_id,
    ):
        return InvitationRepository.get_by_organization(
            db,
            organization_id,
        )

    @staticmethod
    def accept_invitation(
        db: Session,
        invitation: Invitation,
        current_user: User,
    ):
        if invitation.accepted:
            raise ValueError(
                "Invitation already accepted"
            )

        if invitation.expires_at < datetime.now(
            timezone.utc
        ):
            raise ValueError(
                "Invitation has expired"
            )

        MembershipService.add_member(
            db=db,
            organization_id=invitation.organization_id,
            user_id=current_user.public_id,
            role=invitation.role,
        )

        invitation.accepted = True

        db.commit()
        db.refresh(invitation)

        return invitation

    @staticmethod
    def cancel(
        db: Session,
        invitation: Invitation,
        current_user: User,
    ):
        organization = (
            db.query(Organization)
            .filter(
                Organization.public_id
                == invitation.organization_id,
            )
            .first()
        )

        if organization is None:
            raise ValueError(
                "Organization not found"
            )

        ActivityLogService.log(
            db=db,
            organization_id=organization.id,
            user_id=current_user.id,
            action="invitation_cancelled",
            target_type="invitation",
            target_id=invitation.id,
            description=(
                f"Cancelled invitation "
                f"for {invitation.email}"
            ),
        )

        InvitationRepository.delete(
            db,
            invitation,
        )

    @staticmethod
    def resend(
        db: Session,
        invitation: Invitation,
        current_user: User,
    ):
        if invitation.accepted:
            raise ValueError(
                "Invitation has already been accepted"
            )

        invitation.token = secrets.token_urlsafe(32)

        invitation.expires_at = (
            datetime.now(timezone.utc)
            + timedelta(days=7)
        )

        invitation = InvitationRepository.update(
            db,
            invitation,
        )

        organization = (
            db.query(Organization)
            .filter(
                Organization.public_id
                == invitation.organization_id,
            )
            .first()
        )

        if organization is None:
            raise ValueError(
                "Organization not found"
            )

        ActivityLogService.log(
            db=db,
            organization_id=organization.id,
            user_id=current_user.id,
            action="invitation_resent",
            target_type="invitation",
            target_id=invitation.id,
            description=(
                f"Resent invitation "
                f"to {invitation.email}"
            ),
        )

        # The invitee is guaranteed to have existed at invite-creation
        # time (create_invitation requires it), but re-check here in
        # case their account was removed in the meantime.
        existing_user = UserRepository.get_by_email(
            db,
            invitation.email,
        )

        if existing_user is not None:
            accept_url = (
                f"{settings.FRONTEND_URL}"
                f"/invitations/accept/{invitation.token}"
            )

            NotificationService.create(
                db,
                existing_user,
                title="Workspace invitation (resent)",
                message=(
                    f"Your invitation to join "
                    f"'{organization.name}' as {invitation.role} "
                    f"was resent. Accept it here: {accept_url}"
                ),
            )

        return invitation