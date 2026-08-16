from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import PersonaType


class PersonaBase(BaseModel):
    type: PersonaType
    display_name: str
    slug: str
    bio: str | None = None
    is_public: bool = False
    is_directory_visible: bool = False


class PersonaCreate(PersonaBase):
    pass


class PersonaUpdate(BaseModel):
    type: PersonaType | None = None
    display_name: str | None = None
    slug: str | None = None
    bio: str | None = None
    is_public: bool | None = None
    is_directory_visible: bool | None = None


class PersonaResponse(PersonaBase):
    public_id: UUID
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )