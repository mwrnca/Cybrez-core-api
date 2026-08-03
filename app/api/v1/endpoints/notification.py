from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.repositories.notification_repository import NotificationRepository
from app.schemas.notification import NotificationResponse
from app.services.notification_service import NotificationService

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.get("/", response_model=list[NotificationResponse])
def list_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return NotificationService.get_for_user(db, current_user.id)


@router.post("/{notification_public_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = NotificationRepository.get_by_public_id(db, notification_public_id)

    if notification is None or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")

    return NotificationService.mark_as_read(db, notification)


@router.post("/read-all", response_model=list[NotificationResponse])
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return NotificationService.mark_all_as_read(db, current_user.id)


@router.delete("/{notification_public_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_public_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    notification = NotificationRepository.get_by_public_id(db, notification_public_id)

    if notification is None or notification.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Notification not found")

    NotificationService.delete(db, notification)
