from sqlalchemy.orm import Session
from app.services.activity_log_service import ActivityLogService
from app.core.roles import Roles
from app.models.membership import Membership
from app.models.user import User
from app.models.organization import Organization
from app.repositories.membership_repository import MembershipRepository
from uuid import UUID

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
            raise ValueError("User is already a member")

        valid_roles = {
            Roles.VIEWER,
            Roles.EMPLOYEE,
            Roles.MANAGER,
            Roles.ADMIN,
        }

        if role not in valid_roles:
            raise ValueError("Invalid role")

        membership = Membership(
            organization_id=organization_id,
            user_id=user_id,
            role=role,
        )

        membership = MembershipRepository.create(
            db,
            membership,
        )

        org = db.query(Organization).filter(Organization.public_id == organization_id).first()
        user = db.query(User).filter(User.public_id == user_id).first()

        ActivityLogService.log(
            db=db,
            organization_id=org.id,
            user_id=user.id,
            action="member_added",
            target_type="membership",
            target_id=membership.id,
            description=f"Added user {user_id} as {role}",
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
            raise ValueError("Invalid role")

        membership.role = role

        membership = MembershipRepository.update(
            db,
            membership,
        )

        org = db.query(Organization).filter(Organization.public_id == membership.organization_id).first()
        user = db.query(User).filter(User.public_id == membership.user_id).first()

        ActivityLogService.log(
            db=db,
            organization_id=org.id,
            user_id=user.id,
            action="member_role_updated",
            target_type="membership",
            target_id=membership.id,
            description=f"Changed role to {membership.role}",
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

        org = db.query(Organization).filter(Organization.public_id == membership.organization_id).first()
        user = db.query(User).filter(User.public_id == membership.user_id).first()

        ActivityLogService.log(
            db=db,
            organization_id=org.id,
            user_id=user.id,
            action="member_removed",
            target_type="membership",
            target_id=membership.id,
            description=f"Removed user {membership.user_id}",
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
                "The organization owner cannot leave the organization."
            )

        org = db.query(Organization).filter(Organization.public_id == membership.organization_id).first()
        user = db.query(User).filter(User.public_id == membership.user_id).first()

        ActivityLogService.log(
            db=db,
            organization_id=org.id,
            user_id=user.id,
            action="member_left",
            target_type="membership",
            target_id=membership.id,
            description=f"User {membership.user_id} left the organization",
        )

        MembershipRepository.delete(
            db,
            membership,
        )