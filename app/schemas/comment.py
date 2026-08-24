from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class CommentBase(BaseModel):
    content: str = Field(max_length=5000)


class CommentCreate(CommentBase):
    pass


class CommentUpdate(CommentBase):
    pass


class CommentResponse(CommentBase):
    public_id: UUID
    task_public_id: UUID
    user_public_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )