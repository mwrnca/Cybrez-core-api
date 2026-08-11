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

class TasksByStatus(BaseModel):
    status: str
    count: int


class ProjectCount(BaseModel):
    status: str
    count: int


class TasksPerMonth(BaseModel):
    month: str
    count: int