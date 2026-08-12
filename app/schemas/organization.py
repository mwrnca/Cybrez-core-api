from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class OrganizationBase(BaseModel):
    name: str
    description: str | None = None
    logo_url: str | None = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    logo_url: str | None = None


class OrganizationResponse(OrganizationBase):
    public_id: UUID
    owner_id: UUID

    slug: str

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
    