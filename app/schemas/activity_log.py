from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ActivityLogResponse(BaseModel):
    public_id: UUID

    organization_id: int

    user_id: int | None

    action: str

    target_type: str

    target_id: int | None

    description: str

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )