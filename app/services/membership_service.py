from uuid import UUID

from sqlalchemy.orm import Session

from app.core.roles import Roles
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User
from app.repositories.membership_repository import MembershipRepository
from app.services.activity_log_service import ActivityLogService


class MembershipService:

    @staticmethod
    def add_member(
        db: Session,
        organization_id: UUID,
        user_id: UUID,
        role: str = Roles.VIEWER,
    ):
        existing = MembershipRepository.get_member(
            db,
            organization_id,
            user_id,
        )

        if existing:
            raise ValueError(
                "User is already a member"
            )

        valid_roles = {
            Roles.VIEWER,
            Roles.EMPLOYEE,
            Roles.MANAGER,
            Roles.ADMIN,
        }

        if role not in valid_roles:
            raise ValueError(
                "Invalid role"
            )

        organization = (
            db.query(Organization)
            .filter(
                Organization.public_id == organization_id,
            )
            .first()
        )

        if organization is None:
            raise ValueError(
                "Organization not found"
            )

        user = (
            db.query(User)
            .filter(
                User.public_id == user_id,
            )
            .first()
        )

        if user is None:
            raise ValueError(
                "User not found"
            )

        membership = Membership(
            organization_id=organization.public_id,
            user_id=user.public_id,
            role=role,
        )

        membership = MembershipRepository.create(
            db,
            membership,
        )

        ActivityLogService.log(
            db=db,
            organization_id=organization.id,
            user_id=user.id,
            action="member_added",
            target_type="membership",
            target_id=membership.id,
            description=(
                f"Added user {user.public_id} as {role}"
            ),
        )

        return membership

    @staticmethod
    def get_members(
        db: Session,
        organization_id: UUID,
    ):
        return MembershipRepository.get_members(
            db,
            organization_id,
        )

    @staticmethod
    def update_role(
        db: Session,
        membership: Membership,
        role: str,
    ):
        valid_roles = {
            Roles.VIEWER,
            Roles.EMPLOYEE,
            Roles.MANAGER,
            Roles.ADMIN,
        }

        if role not in valid_roles:
            raise ValueError(
                "Invalid role"
            )

        membership.role = role

        membership = MembershipRepository.update(
            db,
            membership,
        )

        organization = (
            db.query(Organization)
            .filter(
                Organization.public_id
                == membership.organization_id,
            )
            .first()
        )

        user = (
            db.query(User)
            .filter(
                User.public_id == membership.user_id,
            )
            .first()
        )

        if organization is None:
            raise ValueError(
                "Organization not found"
            )

        if user is None:
            raise ValueError(
                "User not found"
            )

        ActivityLogService.log(
            db=db,
            organization_id=organization.id,
            user_id=user.id,
            action="member_role_updated",
            target_type="membership",
            target_id=membership.id,
            description=(
                f"Changed role to {membership.role}"
            ),
        )

        return membership

    @staticmethod
    def remove_member(
        db: Session,
        membership: Membership,
    ):
        if membership.role == Roles.OWNER:
            raise ValueError(
                "The owner cannot be removed"
            )

        organization = (
            db.query(Organization)
            .filter(
                Organization.public_id
                == membership.organization_id,
            )
            .first()
        )

        user = (
            db.query(User)
            .filter(
                User.public_id == membership.user_id,
            )
            .first()
        )

        if organization is None:
            raise ValueError(
                "Organization not found"
            )

        if user is None:
            raise ValueError(
                "User not found"
            )

        ActivityLogService.log(
            db=db,
            organization_id=organization.id,
            user_id=user.id,
            action="member_removed",
            target_type="membership",
            target_id=membership.id,
            description=(
                f"Removed user {user.public_id}"
            ),
        )

        MembershipRepository.delete(
            db,
            membership,
        )

    @staticmethod
    def leave_organization(
        db: Session,
        membership: Membership,
    ):
        if membership.role == Roles.OWNER:
            raise ValueError(
                "The organization owner "
                "cannot leave the organization."
            )

        organization = (
            db.query(Organization)
            .filter(
                Organization.public_id
                == membership.organization_id,
            )
            .first()
        )

        user = (
            db.query(User)
            .filter(
                User.public_id == membership.user_id,
            )
            .first()
        )

        if organization is None:
            raise ValueError(
                "Organization not found"
            )

        if user is None:
            raise ValueError(
                "User not found"
            )

        ActivityLogService.log(
            db=db,
            organization_id=organization.id,
            user_id=user.id,
            action="member_left",
            target_type="membership",
            target_id=membership.id,
            description=(
                f"User {user.public_id} "
                "left the organization"
            ),
        )

        MembershipRepository.delete(
            db,
            membership,
        )