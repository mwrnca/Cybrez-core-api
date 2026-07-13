from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class InvitationCreate(BaseModel):
    email: EmailStr
    role: str


class InvitationResponse(BaseModel):
    id: int
    organization_id: int
    email: EmailStr
    role: str
    token: str
    accepted: bool
    expires_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    