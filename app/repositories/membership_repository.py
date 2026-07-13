from sqlalchemy.orm import Session

from app.models.membership import Membership


class MembershipRepository:

    @staticmethod
    def create(
        db: Session,
        membership: Membership,
    ):
        db.add(membership)
        db.commit()
        db.refresh(membership)
        return membership

    @staticmethod
    def get_member(
        db: Session,
        organization_id: int,
        user_id: int,
    ):
        return (
            db.query(Membership)
            .filter(
                Membership.organization_id == organization_id,
                Membership.user_id == user_id,
            )
            .first()
        )

    @staticmethod
    def get_members(
        db: Session,
        organization_id: int,
    ):
        return (
            db.query(Membership)
            .filter(
                Membership.organization_id == organization_id
            )
            .all()
        )

    @staticmethod
    def delete(
        db: Session,
        membership: Membership,
    ):
        db.delete(membership)
        db.commit()

    @staticmethod
    def get_by_user_and_organization(
        db: Session,
        user_id: int,
        organization_id: int,
    ):
        return (
            db.query(Membership)
            .filter(
                Membership.user_id == user_id,
                Membership.organization_id == organization_id,
            )
            .first()
        )

        