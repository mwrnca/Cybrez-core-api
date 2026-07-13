from fastapi import HTTPException, status

from app.models.organization import Organization
from app.models.user import User


def require_owner(
    organization: Organization,
    current_user: User,
):
    if organization.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can perform this action.",
        )