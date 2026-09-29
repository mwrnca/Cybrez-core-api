from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.session import get_db
from app.models.membership import Membership
from app.models.organization_unit import OrganizationUnit
from app.models.user import User
from app.repositories.organization_unit_repository import (
    OrganizationUnitRepository,
)
from app.schemas.organization_unit import (
    OrganizationUnitCreate,
    OrganizationUnitResponse,
    OrganizationUnitUpdate,
)


router = APIRouter(
    prefix="/organizations/{organization_public_id}/units",
    tags=["Organization Units"],
)


def _require_membership(
    db: Session,
    user: User,
    organization_id: UUID,
) -> Membership:
    membership = (
        db.query(Membership)
        .filter(
            Membership.organization_id == organization_id,
            Membership.user_id == user.public_id,
        )
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this organization.",
        )

    return membership


@router.get(
    "",
    response_model=list[OrganizationUnitResponse],
)
def list_units(
    organization_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_membership(
        db,
        current_user,
        organization_public_id,
    )

    return OrganizationUnitRepository.get_for_organization(
        db,
        organization_public_id,
    )


@router.post(
    "",
    response_model=OrganizationUnitResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_unit(
    organization_public_id: UUID,
    data: OrganizationUnitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    membership = _require_membership(
        db,
        current_user,
        organization_public_id,
    )

    if membership.role not in {
        "OWNER",
        "ADMIN",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage organization units.",
        )

    parent_id = None

    if data.parent_unit_id:
        parent = OrganizationUnitRepository.get_by_public_id(
            db,
            data.parent_unit_id,
        )

        if not parent or parent.organization_id != organization_public_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent unit does not belong to this organization.",
            )

        parent_id = parent.id

    return OrganizationUnitRepository.create(
        db,
        organization_id=organization_public_id,
        name=data.name,
        description=data.description,
        parent_unit_id=parent_id,
    )


@router.put(
    "/{unit_public_id}",
    response_model=OrganizationUnitResponse,
)
def update_unit(
    organization_public_id: UUID,
    unit_public_id: UUID,
    data: OrganizationUnitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    membership = _require_membership(
        db,
        current_user,
        organization_public_id,
    )

    if membership.role not in {
        "OWNER",
        "ADMIN",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage organization units.",
        )

    unit = OrganizationUnitRepository.get_by_public_id(
        db,
        unit_public_id,
    )

    if not unit or unit.organization_id != organization_public_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization unit not found.",
        )

    parent_id = None

    if data.parent_unit_id:
        parent = OrganizationUnitRepository.get_by_public_id(
            db,
            data.parent_unit_id,
        )

        if not parent or parent.organization_id != organization_public_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent unit does not belong to this organization.",
            )

        if parent.id == unit.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A unit cannot be its own parent.",
            )

        parent_id = parent.id

    values = {
        "name": data.name,
        "description": data.description,
        "parent_unit_id": parent_id,
    }

    if data.name is None:
        values.pop("name")

    if data.description is None:
        values.pop("description")

    return OrganizationUnitRepository.update(
        db,
        unit,
        **values,
    )


@router.delete(
    "/{unit_public_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_unit(
    organization_public_id: UUID,
    unit_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    membership = _require_membership(
        db,
        current_user,
        organization_public_id,
    )

    if membership.role not in {
        "OWNER",
        "ADMIN",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to manage organization units.",
        )

    unit = OrganizationUnitRepository.get_by_public_id(
        db,
        unit_public_id,
    )

    if not unit or unit.organization_id != organization_public_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization unit not found.",
        )

    OrganizationUnitRepository.delete(db, unit)