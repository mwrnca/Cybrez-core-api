from uuid import UUID

from pydantic import BaseModel


class DirectoryOrganization(BaseModel):
    public_id: UUID
    name: str
    description: str | None = None
    logo_url: str | None = None
    role: str


class DirectoryPerson(BaseModel):
    public_id: UUID
    full_name: str
    organizations: list[DirectoryOrganization]