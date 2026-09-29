from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class WorkspaceOrganization(BaseModel):
    public_id: UUID
    name: str
    description: str | None = None
    logo_url: str | None = None


class WorkspaceProject(BaseModel):
    public_id: UUID
    name: str
    description: str | None = None


class WorkspaceUnit(BaseModel):
    public_id: UUID
    name: str
    description: str | None = None
    parent_unit_id: UUID | None = None


class WorkspacePerson(BaseModel):
    public_id: UUID
    full_name: str


class TaskWorkspaceResponse(BaseModel):
    task_public_id: UUID
    title: str
    description: str | None
    status: str
    priority: str
    due_date: datetime | None
    is_archived: bool

    project: WorkspaceProject
    organization: WorkspaceOrganization

    organization_unit: WorkspaceUnit | None
    organization_units: list[WorkspaceUnit]

    assignee: WorkspacePerson | None

    tools: list[dict]
    activity: list[dict]