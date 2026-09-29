from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.session import get_db

from app.models.membership import Membership
from app.models.task import Task
from app.models.user import User

from app.repositories.organization_unit_repository import (
    OrganizationUnitRepository,
)

from app.schemas.task_workspace import (
    TaskWorkspaceResponse,
    WorkspaceOrganization,
    WorkspacePerson,
    WorkspaceProject,
    WorkspaceUnit,
)


router = APIRouter(
    prefix="/tasks",
    tags=["Task Workspace"],
)


def _get_task_for_user(
    db: Session,
    task_public_id: UUID,
    current_user: User,
) -> Task:

    task = (
        db.query(Task)
        .filter(
            Task.public_id == task_public_id,
            Task.deleted_at.is_(None),
        )
        .first()
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )

    organization_id = task.project.organization_id

    membership = (
        db.query(Membership)
        .filter(
            Membership.organization_id == organization_id,
            Membership.user_id == current_user.public_id,
        )
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this task.",
        )

    return task


@router.get(
    "/{task_public_id}/workspace",
    response_model=TaskWorkspaceResponse,
)
def get_task_workspace(
    task_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = _get_task_for_user(
        db,
        task_public_id,
        current_user,
    )

    organization = task.project.organization

    units = OrganizationUnitRepository.get_for_organization(
        db,
        organization.public_id,
    )

    unit_map = {
        unit.id: unit
        for unit in units
    }

    def serialize_unit(unit):
        if unit is None:
            return None

        parent_public_id = None

        if unit.parent_unit_id:
            parent = unit_map.get(unit.parent_unit_id)

            if parent:
                parent_public_id = parent.public_id

        return WorkspaceUnit(
            public_id=unit.public_id,
            name=unit.name,
            description=unit.description,
            parent_unit_id=parent_public_id,
        )

    current_unit = None

    if task.organization_unit_id:
        current_unit = unit_map.get(
            task.organization_unit_id
        )

    return TaskWorkspaceResponse(
        task_public_id=task.public_id,
        title=task.title,
        description=task.description,
        status=(
            task.status.value
            if hasattr(task.status, "value")
            else str(task.status)
        ),
        priority=(
            task.priority.value
            if hasattr(task.priority, "value")
            else str(task.priority)
        ),
        due_date=task.due_date,
        is_archived=task.is_archived,

        project=WorkspaceProject(
            public_id=task.project.public_id,
            name=task.project.name,
            description=task.project.description,
        ),

        organization=WorkspaceOrganization(
            public_id=organization.public_id,
            name=organization.name,
            description=organization.description,
            logo_url=organization.logo_url,
        ),

        organization_unit=serialize_unit(
            current_unit
        ),

        organization_units=[
            serialize_unit(unit)
            for unit in units
        ],

        assignee=(
            WorkspacePerson(
                public_id=task.assignee.public_id,
                full_name=task.assignee.full_name,
            )
            if task.assignee
            else None
        ),

        tools=[],
        activity=[],
    )