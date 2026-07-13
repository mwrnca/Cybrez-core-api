from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MembershipBase(BaseModel):
    role: str = "member"


class MembershipCreate(MembershipBase):
    user_id: int


class MembershipResponse(MembershipBase):
    id: int
    organization_id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    