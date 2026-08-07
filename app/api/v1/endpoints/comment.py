from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.core.permissions import require_role
from app.core.roles import Roles
from app.database.session import get_db
from app.models.user import User
from app.repositories.comment_repository import CommentRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.comment import (
    CommentCreate,
    CommentResponse,
    CommentUpdate,
)
from app.services.comment_service import CommentService

router = APIRouter(
    prefix="/comments",
    tags=["Comments"],
)


@router.post(
    "/task/{task_public_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    task_public_id: UUID,
    data: CommentCreate,
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
        Roles.EMPLOYEE,
    )

    return CommentService.create(
        db,
        task,
        current_user,
        data,
    )


@router.get(
    "/task/{task_public_id}",
    response_model=list[CommentResponse],
)
def list_comments(
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
        Roles.EMPLOYEE,
    )

    return CommentService.get_all(
        db,
        task.id,
    )


@router.put(
    "/{comment_public_id}",
    response_model=CommentResponse,
)
def update_comment(
    comment_public_id: UUID,
    data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = CommentRepository.get_by_public_id(
        db,
        comment_public_id,
    )

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed",
        )

    return CommentService.update(
        db,
        comment,
        current_user,
        data,
    )


@router.delete(
    "/{comment_public_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_comment(
    comment_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = CommentRepository.get_by_public_id(
        db,
        comment_public_id,
    )

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed",
        )

    CommentService.delete(
        db,
        comment,
        current_user,
    )


@router.post(
    "/{comment_public_id}/restore",
    response_model=CommentResponse,
)
def restore_comment(
    comment_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = CommentRepository.get_by_public_id(
        db,
        comment_public_id,
        include_deleted=True,
    )

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed",
        )

    try:
        return CommentService.restore(
            db,
            comment,
            current_user,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

@router.get(
    "/{comment_public_id}",
    response_model=CommentResponse,
)
def get_comment(
    comment_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = CommentRepository.get_by_public_id(
        db,
        comment_public_id,
    )

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    require_role(
        db,
        comment.task.project.organization_id,
        current_user,
        Roles.EMPLOYEE,
    )

    return comment

@router.get(
    "/{comment_public_id}",
    response_model=CommentResponse,
)
def get_comment(
    comment_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = CommentRepository.get_by_public_id(
        db,
        comment_public_id,
    )

    if comment is None:
        raise HTTPException(
            status_code=404,
            detail="Comment not found",
        )

    require_role(
        db,
        comment.task.project.organization_id,
        current_user,
        Roles.EMPLOYEE,
    )

    return comment