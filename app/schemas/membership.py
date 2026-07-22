from datetime import datetime

from pydantic import BaseModel, ConfigDict
from uuid import UUID
from app.core.roles import Roles


class MembershipBase(BaseModel):
    role: str = Roles.VIEWER


class MembershipCreate(MembershipBase):
    user_id: int

class MembershipRoleUpdate(BaseModel):
    role: str
    
class MembershipResponse(MembershipBase):
    public_id: UUID
    organization_id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    