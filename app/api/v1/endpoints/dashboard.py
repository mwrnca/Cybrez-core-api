from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DashboardService.get_dashboard_stats(
        db,
        current_user,
    )


@router.get("/tasks-by-status")
def tasks_by_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DashboardService.get_tasks_by_status(
        db,
        current_user,
    )


@router.get("/project-counts")
def project_counts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DashboardService.get_project_counts(
        db,
        current_user,
    )


@router.get("/tasks-per-month")
def tasks_per_month(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return DashboardService.get_tasks_per_month(
        db,
        current_user,
    )