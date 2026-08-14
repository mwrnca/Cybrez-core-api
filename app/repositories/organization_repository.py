from sqlalchemy.orm import Session
from uuid import UUID
from app.models.membership import Membership
from app.core.soft_delete import soft_delete
from app.models.organization import Organization


class OrganizationRepository:

    @staticmethod
    def create(
        db: Session,
        organization: Organization,
    ):
        db.add(organization)
        db.commit()
        db.refresh(organization)
        return organization

    @staticmethod
    def get_by_id(
        db: Session,
        organization_id: int,
    ):
        return (
            db.query(Organization)
            .filter(
                Organization.id == organization_id,
                Organization.deleted_at.is_(None),
            )
            .first()
        )

    @staticmethod
    def get_by_public_id(
        db: Session,
        public_id,
        include_deleted: bool = False,
    ):
        query = db.query(Organization).filter(
            Organization.public_id == public_id,
        )

        if not include_deleted:
            query = query.filter(Organization.deleted_at.is_(None))

        return query.first()

    @staticmethod
    def get_by_slug(
        db: Session,
        slug: str,
    ):
        return (
            db.query(Organization)
            .filter(
                Organization.slug == slug,
                Organization.deleted_at.is_(None),
            )
            .first()
        )

    @staticmethod
    def get_all_for_user(
        db: Session,
        user_id: UUID,
    ):
        return (
            db.query(Organization)
            .join(
                Membership,
                Membership.organization_id == Organization.public_id,
            )
            .filter(
                Membership.user_id == user_id,
                Organization.deleted_at.is_(None),
            )
            .all()
        )

    @staticmethod
    def update(
        db: Session,
        organization: Organization,
    ):
        db.commit()
        db.refresh(organization)
        return organization

    @staticmethod
    def delete(
        db: Session,
        organization: Organization,
        user_id: int | None = None,
    ):
        soft_delete(
            organization,
            user_id,
        )

        db.commit()
        db.refresh(organization)

        return organization

    @staticmethod
    def restore(
        db: Session,
        organization: Organization,
    ):
        organization.deleted_at = None
        organization.deleted_by = None

        db.commit()
        db.refresh(organization)

        return organization

    