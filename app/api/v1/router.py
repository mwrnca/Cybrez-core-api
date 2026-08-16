from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    organization,
    membership,
    invitation,
    project,
    task,
    comment,
    activity_log,
    dashboard,
    notification,
    persona,
    directory,
)

from app.api.v1.endpoints import search


api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(organization.router)
api_router.include_router(membership.router)
api_router.include_router(invitation.router)
api_router.include_router(project.router)
api_router.include_router(task.router)
api_router.include_router(comment.router)
api_router.include_router(activity_log.router)
api_router.include_router(dashboard.router)
api_router.include_router(notification.router)
api_router.include_router(persona.router)
api_router.include_router(directory.router)
api_router.include_router(search.router)