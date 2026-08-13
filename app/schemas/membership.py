from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
)

from app.core.roles import Roles


class MembershipBase(BaseModel):
    role: str = Roles.VIEWER


class MembershipCreate(MembershipBase):
    user_id: UUID


class MembershipRoleUpdate(BaseModel):
    role: str


class MembershipResponse(BaseModel):
    public_id: UUID
    organization_id: UUID
    user_id: UUID
    role: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )