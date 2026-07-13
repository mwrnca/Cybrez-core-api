from sqlalchemy.orm import Session

from app.models.membership import Membership
from app.repositories.membership_repository import MembershipRepository


class MembershipService:

    @staticmethod
    def add_member(
        db: Session,
        organization_id: int,
        user_id: int,
        role: str = "member",
    ):
        existing = MembershipRepository.get_member(
            db,
            organization_id,
            user_id,
        )

        if existing:
            raise ValueError("User is already a member")

        membership = Membership(
            organization_id=organization_id,
            user_id=user_id,
            role=role,
        )

        return MembershipRepository.create(
            db,
            membership,
        )

    @staticmethod
    def get_members(
        db: Session,
        organization_id: int,
    ):
        return MembershipRepository.get_members(
            db,
            organization_id,
        )

        