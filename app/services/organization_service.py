from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.user import User
from app.repositories.organization_repository import (
    OrganizationRepository,
)
from app.schemas.organization import OrganizationCreate


class OrganizationService:

    @staticmethod
    def create(
        db: Session,
        current_user: User,
        data: OrganizationCreate,
    ):

        existing = OrganizationRepository.get_by_slug(
            db,
            data.slug,
        )

        if existing:
            raise ValueError(
                "Slug already exists"
            )

        organization = Organization(
            name=data.name,
            slug=data.slug,
            description=data.description,
            logo_url=data.logo_url,
            owner_id=current_user.id,
        )

        return OrganizationRepository.create(
            db,
            organization,
        )

    @staticmethod
    def get_all(db: Session):
        return OrganizationRepository.get_all(db)

    @staticmethod
    def get_by_id(
        db: Session,
        organization_id: int,
    ):
        organization = OrganizationRepository.get_by_id(
            db,
            organization_id,
        )

        if organization is None:
            raise ValueError("Organization not found")

        return organization

    @staticmethod
    def update(
        db: Session,
        organization_id: int,
        current_user: User,
        data: OrganizationCreate,
    ):
        organization = OrganizationRepository.get_by_id(
            db,
            organization_id,
        )

        if organization is None:
            raise ValueError("Organization not found")

        if organization.owner_id != current_user.id:
            raise PermissionError("You are not the owner")

        organization.name = data.name
        organization.slug = data.slug
        organization.description = data.description
        organization.logo_url = data.logo_url

        return OrganizationRepository.update(
            db,
            organization,
        )

    @staticmethod
    def delete(
        db: Session,
        organization_id: int,
        current_user: User,
    ):
        organization = OrganizationRepository.get_by_id(
            db,
            organization_id,
        )

        if organization is None:
            raise ValueError("Organization not found")

        if organization.owner_id != current_user.id:
            raise PermissionError("You are not the owner")

        OrganizationRepository.delete(
            db,
            organization,
        )