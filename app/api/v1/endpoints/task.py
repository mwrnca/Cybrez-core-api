from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.permissions import require_role
from app.core.roles import Roles
from app.database.session import get_db
from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.task import (
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)
from app.services.task_service import TaskService


router = APIRouter(
    prefix="/projects",
    tags=["Tasks"],
)


@router.post(
    "/{project_public_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    project_public_id: UUID,
    data: TaskCreate,
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
        return TaskService.create(
            db,
            project,
            data,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.get(
    "/{project_public_id}/tasks",
    response_model=list[TaskResponse],
)
def list_tasks(
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

    return TaskService.get_all(
        db,
        project.id,
    )


@router.get(
    "/tasks/{task_public_id}",
    response_model=TaskResponse,
)
def get_task(
    task_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = TaskRepository.get_by_public_id(
        db,
        task_public_id,
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    require_role(
        db,
        task.project.organization_id,
        current_user,
        Roles.MANAGER,
    )

    return task


@router.put(
    "/tasks/{task_public_id}",
    response_model=TaskResponse,
)
def update_task(
    task_public_id: UUID,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = TaskRepository.get_by_public_id(
        db,
        task_public_id,
        include_deleted=True,
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    require_role(
        db,
        task.project.organization_id,
        current_user,
        Roles.MANAGER,
    )

    try:
        return TaskService.update(
            db,
            task,
            data,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.delete(
    "/{project_public_id}/tasks/{task_public_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    project_public_id: UUID,
    task_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = TaskRepository.get_by_public_id(
        db,
        task_public_id,
        include_deleted=True,
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    if task.project.public_id != project_public_id:
        raise HTTPException(
            status_code=404,
            detail="Task not found in this project",
        )

    require_role(
        db,
        task.project.organization_id,
        current_user,
        Roles.ADMIN,
    )

    TaskService.delete(
        db,
        task,
        current_user,
    )


@router.post(
    "/tasks/{task_public_id}/restore",
    response_model=TaskResponse,
)
def restore_task(
    task_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = TaskRepository.get_by_public_id(
        db,
        task_public_id,
        include_deleted=True,
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    require_role(
        db,
        task.project.organization_id,
        current_user,
        Roles.MANAGER,
    )

    try:
        return TaskService.restore(
            db,
            task,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post(
    "/tasks/{task_public_id}/archive",
    response_model=TaskResponse,
)
def archive_task(
    task_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = TaskRepository.get_by_public_id(
        db,
        task_public_id,
        include_deleted=True,
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    require_role(
        db,
        task.project.organization_id,
        current_user,
        Roles.MANAGER,
    )

    try:
        return TaskService.archive(
            db,
            task,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post(
    "/tasks/{task_public_id}/unarchive",
    response_model=TaskResponse,
)
def unarchive_task(
    task_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = TaskRepository.get_by_public_id(
        db,
        task_public_id,
        include_deleted=True,
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found",
        )

    require_role(
        db,
        task.project.organization_id,
        current_user,
        Roles.MANAGER,
    )

    try:
        return TaskService.unarchive(
            db,
            task,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )