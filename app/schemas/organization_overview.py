from pydantic import BaseModel

from app.schemas.activity_log import ActivityLogResponse
from app.schemas.organization import OrganizationResponse


class OrganizationStats(BaseModel):
    projects: int
    active_projects: int
    archived_projects: int
    tasks: int
    completed_tasks: int
    pending_tasks: int
    members: int
    invitations: int


class OrganizationOverviewResponse(BaseModel):
    organization: OrganizationResponse
    stats: OrganizationStats
    recent_activity: list[ActivityLogResponse]