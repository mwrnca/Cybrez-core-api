from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    organization,
    membership,
    invitation,
    project,
    task,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(organization.router)
api_router.include_router(membership.router)
api_router.include_router(invitation.router)
api_router.include_router(project.router)
api_router.include_router(task.router)