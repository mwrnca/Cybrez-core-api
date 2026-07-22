from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    health,
    invitation,
    membership,
    organization,
    project,
    task,
    comment,
    activity_log,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(health.router)
api_router.include_router(organization.router)
api_router.include_router(membership.router)
api_router.include_router(invitation.router)
api_router.include_router(project.router)
api_router.include_router(task.router)
api_router.include_router(comment.router)
api_router.include_router(activity_log.router,)