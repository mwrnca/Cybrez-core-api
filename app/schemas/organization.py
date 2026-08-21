from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class OrganizationBase(BaseModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    logo_url: str | None = Field(default=None, max_length=500)


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    logo_url: str | None = Field(default=None, max_length=500)


class OrganizationResponse(OrganizationBase):
    public_id: UUID
    owner_id: UUID

    slug: str

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)