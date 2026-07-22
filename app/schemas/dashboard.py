from pydantic import BaseModel


class DashboardStats(BaseModel):
    organizations: int
    projects: int
    active_projects: int
    archived_projects: int
    tasks: int
    completed_tasks: int
    pending_tasks: int
    members: int

    