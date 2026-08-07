from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
)
from app.services.organization_service import OrganizationService

from app.schemas.organization_overview import (
    OrganizationOverviewResponse,
)
from app.services.organization_overview_service import (
    OrganizationOverviewService,
)

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"],
)


@router.post(
    "/",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_organization(
    organization: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return OrganizationService.create(
            db,
            current_user,
            organization,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

@router.get(
    "/",
    response_model=list[OrganizationResponse],
)
def list_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return OrganizationService.get_all(db)

@router.get(
    "/{organization_public_id}",
    response_model=OrganizationResponse,
)
def get_organization(
    organization_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:
        return OrganizationService.get_by_public_id(
            db,
            organization_public_id,
        )   

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

@router.put(
    "/{organization_public_id}",
    response_model=OrganizationResponse,
)
def update_organization(
    organization_public_id: UUID,
    data: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:
        return OrganizationService.update(
            db,
            organization_public_id,
            current_user,
            data,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except PermissionError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e),
        )

@router.delete(
"/{organization_public_id}",
status_code=204,
)
def delete_organization(
    organization_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:
        OrganizationService.delete(
            db,
            organization_public_id,
            current_user,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except PermissionError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e),
        )

@router.post(
    "/{organization_public_id}/restore",
    response_model=OrganizationResponse,
)
def restore_organization(
    organization_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    try:
        return OrganizationService.restore(
            db,
            organization_public_id,
            current_user,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )

    except PermissionError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e),
        )

@router.get(
    "/{organization_public_id}/overview",
    response_model=OrganizationOverviewResponse,
)
def get_organization_overview(
    organization_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return OrganizationOverviewService.get_overview(
        db,
        organization_public_id,
        current_user,
    )