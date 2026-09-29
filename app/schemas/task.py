from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import TaskPriority, TaskStatus


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    status: TaskStatus
    priority: TaskPriority
    assignee_id: UUID | None = None
    organization_unit_id: UUID | None = None
    due_date: datetime | None = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class TaskResponse(TaskBase):
    public_id: UUID
    project_public_id: UUID

    organization_unit_id: UUID | None = Field(
        default=None,
        validation_alias="organization_unit_public_id",
        serialization_alias="organization_unit_id",
    )

    created_at: datetime
    updated_at: datetime
    is_archived: bool

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )