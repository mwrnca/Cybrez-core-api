from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.role_hierarchy import ROLE_HIERARCHY
from app.core.roles import Roles
from app.models.organization import Organization
from app.models.user import User
from app.repositories.membership_repository import MembershipRepository

def require_role(
    db: Session,
    organization_public_id: UUID,
    current_user: User,
    minimum_role: str,
):
    membership = MembershipRepository.get_by_user_and_organization(
        db,
        current_user.public_id,
        organization_public_id,
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization.",
        )

    if ROLE_HIERARCHY[membership.role] < ROLE_HIERARCHY[minimum_role]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission.",
        )

    return membership

def require_owner(
    organization: Organization,
    current_user: User,
):
    if organization.owner_id != current_user.public_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can perform this action.",
        )