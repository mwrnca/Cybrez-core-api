from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ActivityLogResponse(BaseModel):
    public_id: UUID

    organization_public_id: UUID

    user_public_id: UUID | None

    action: str

    target_type: str

    # Internal integer id of the target (comment/task/project/membership/
    # organization row) -- left as-is, see note in the ActivityLog model.
    target_id: int | None

    description: str

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )