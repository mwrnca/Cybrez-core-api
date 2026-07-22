from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProjectBase(BaseModel):
    name: str
    description: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    public_id: UUID
    organization_public_id: UUID
    created_at: datetime
    updated_at: datetime
    is_archived: bool

    model_config = ConfigDict(
        from_attributes=True,
    )