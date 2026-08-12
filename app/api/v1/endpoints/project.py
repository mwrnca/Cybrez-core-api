from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_user
from app.core.permissions import (
    require_role,
)
from app.core.roles import Roles
from app.database.session import get_db
from app.models.user import User
from app.repositories.organization_repository import OrganizationRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project_service import ProjectService

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post(
    "/{organization_public_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    organization_public_id: UUID,
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    organization = OrganizationRepository.get_by_public_id(
        db,
        organization_public_id,
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found",
        )

    require_role(
        db,
        organization.public_id,
        current_user,
        Roles.MANAGER,
    )

    return ProjectService.create(
        db,
        organization,
        current_user,
        data,
    )


@router.get(
    "/organization/{organization_public_id}",
    response_model=list[ProjectResponse],
)
def list_projects(
    organization_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    organization = OrganizationRepository.get_by_public_id(
        db,
        organization_public_id,
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found",
        )

    return ProjectService.get_all(
        db,
        organization.public_id,
    )


@router.put(
    "/{project_public_id}",
    response_model=ProjectResponse,
)
def update_project(
    project_public_id: UUID,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = ProjectRepository.get_by_public_id(
        db,
        project_public_id,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    require_role(
        db,
        project.organization_id,
        current_user,
        Roles.MANAGER,
    )

    return ProjectService.update(
        db,
        project,
        current_user,
        data,
    )

@router.get(
    "/{project_public_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = ProjectRepository.get_by_public_id(
        db,
        project_public_id,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return project


@router.delete(
    "/{project_public_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    project_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = ProjectRepository.get_by_public_id(
        db,
        project_public_id,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    require_role(
        db,
        project.organization_id,
        current_user,
        Roles.ADMIN,
    )

    ProjectService.delete(
        db,
        project,
        current_user,
    )


@router.post(
    "/{project_public_id}/restore",
    response_model=ProjectResponse,
)
def restore_project(
    project_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = ProjectRepository.get_by_public_id(
        db,
        project_public_id,
        include_deleted=True,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    organization = project.organization

    require_role(
        db,
        organization.public_id,
        current_user,
        Roles.MANAGER,
    )

    try:
        return ProjectService.restore(
            db,
            project,
            current_user,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post(
    "/{project_public_id}/archive",
    response_model=ProjectResponse,
)
def archive_project(
    project_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = ProjectRepository.get_by_public_id(
        db,
        project_public_id,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    require_role(
        db,
        project.organization_id,
        current_user,
        Roles.MANAGER,
    )

    try:
        return ProjectService.archive(
            db,
            project,
            current_user,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post(
    "/{project_public_id}/unarchive",
    response_model=ProjectResponse,
)
def unarchive_project(
    project_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = ProjectRepository.get_by_public_id(
        db,
        project_public_id,
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    require_role(
        db,
        project.organization_id,
        current_user,
        Roles.MANAGER,
    )

    try:
        return ProjectService.unarchive(
            db,
            project,
            current_user,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

        