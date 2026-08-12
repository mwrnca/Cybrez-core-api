from sqlalchemy.orm import Session
from app.models.membership import Membership
from app.repositories.membership_repository import MembershipRepository
from app.core.roles import Roles
from app.models.organization import Organization
from app.models.user import User
from app.repositories.organization_repository import (
    OrganizationRepository,
)
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
)
from app.services.activity_log_service import ActivityLogService
from uuid import UUID
import re

class OrganizationService:

    @staticmethod
    def generate_slug(name: str) -> str:
        slug = name.lower()

        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"\s+", "-", slug)
        slug = re.sub(r"-+", "-", slug)

        return slug.strip("-")

    @staticmethod
    def create(
        db: Session,
        current_user: User,
        data: OrganizationCreate,
    ):

        slug = OrganizationService.generate_slug(data.name)

        existing = OrganizationRepository.get_by_slug(
            db,
            slug,
        )

        if existing:
            raise ValueError(
                "Slug already exists"
            )

        organization = Organization(
            name=data.name,
            slug=slug,
            description=data.description,
            logo_url=data.logo_url,
            owner_id=current_user.public_id,
        )

        organization = OrganizationRepository.create(
            db,
            organization,
        )

        membership = Membership(
            organization_id=organization.public_id,
            user_id=current_user.public_id,
            role=Roles.OWNER,
        )

        MembershipRepository.create(
            db,
            membership,
        )

        ActivityLogService.log(
            db=db,
            organization_id=organization.id,
            user_id=current_user.id,
            action="organization_created",
            target_type="organization",
            target_id=organization.id,
            description=f"Created organization '{organization.name}'",
        )

        return organization

    @staticmethod
    def get_all(
        db: Session
    ):
        return OrganizationRepository.get_all(db)

    @staticmethod
    def get_by_public_id(
        db: Session,
        public_id: UUID,
    ):
        organization = OrganizationRepository.get_by_public_id(
            db,
            public_id,
        )

        if organization is None:
            raise ValueError("Organization not found")

        return organization

    @staticmethod
    def update(
        db: Session,
        organization_id: UUID,
        current_user: User,
        data: OrganizationUpdate,
    ):
        organization = OrganizationRepository.get_by_public_id(
            db, 
            organization_id
        )

        if organization is None:
            raise ValueError("Organization not found")

        if organization.owner_id != current_user.public_id:
            raise PermissionError("You are not the owner")

        if data.name is not None:
            slug = OrganizationService.generate_slug(data.name)

            existing = OrganizationRepository.get_by_slug(
                db,
                slug,
            )

            if (
                existing
                and existing.id != organization.id
            ):
                raise ValueError(
                    "Organization name already exists."
                )

            organization.name = data.name
            organization.slug = slug

        if data.description is not None:
            organization.description = data.description

        if data.logo_url is not None:
            organization.logo_url = data.logo_url

        organization = OrganizationRepository.update(
            db,
            organization,
        )

        ActivityLogService.log(
            db=db,
            organization_id=organization.id,
            user_id=current_user.id,
            action="organization_updated",
            target_type="organization",
            target_id=organization.id,
            description=f"Updated organization '{organization.name}'",
        )

        return organization

    @staticmethod
    def delete(
        db: Session,
        organization_id: UUID,
        current_user: User,
    ):
        organization = OrganizationRepository.get_by_public_id(
            db, 
            organization_id
        )

        if organization is None:
            raise ValueError("Organization not found")

        if organization.owner_id != current_user.public_id:
            raise PermissionError("You are not the owner")

        OrganizationRepository.delete(
            db,
            organization,
        )

        ActivityLogService.log(
            db=db,
            organization_id=organization.id,
            user_id=current_user.id,
            action="organization_deleted",
            target_type="organization",
            target_id=organization.id,
            description=f"Deleted organization '{organization.name}'",
        )

    @staticmethod
    def restore(
        db: Session,
        organization_id: UUID,
        current_user: User,
    ):
        organization = OrganizationRepository.get_by_public_id(
            db,
            organization_id,
            include_deleted=True,
        )

        if organization is None:
            raise ValueError("Organization not found")

        if organization.deleted_at is None:
            raise ValueError("Organization is not deleted")

        if organization.owner_id != current_user.public_id:
            raise PermissionError("You are not the owner")

        organization = OrganizationRepository.restore(
            db,
            organization,
        )

        ActivityLogService.log(
            db=db,
            organization_id=organization.id,
            user_id=current_user.id,
            action="organization_restored",
            target_type="organization",
            target_id=organization.id,
            description=f"Restored organization '{organization.name}'",
        )

        return organization