from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
)


class InvitationCreate(BaseModel):
    email: EmailStr
    role: str


class InvitationResponse(BaseModel):
    public_id: UUID
    organization_id: UUID
    email: EmailStr
    role: str
    token: str
    accepted: bool
    expires_at: datetime
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )