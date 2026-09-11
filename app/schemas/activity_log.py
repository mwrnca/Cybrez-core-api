from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ActivityLogResponse(BaseModel):
    public_id: UUID

    organization_public_id: UUID

    user_public_id: UUID | None

    action: str

    target_type: str

    target_public_id: UUID | None

    description: str

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )