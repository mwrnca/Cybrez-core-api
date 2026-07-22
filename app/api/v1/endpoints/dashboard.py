from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.repositories.dashboard_repository import DashboardRepository

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DashboardRepository.get_stats(db)


@router.get("/tasks-by-status")
def tasks_by_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DashboardRepository.tasks_by_status(db)


@router.get("/project-counts")
def project_counts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DashboardRepository.project_counts(db)


@router.get("/tasks-per-month")
def tasks_per_month(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DashboardRepository.tasks_per_month(db)