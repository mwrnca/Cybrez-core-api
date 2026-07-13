from pydantic import BaseModel, ConfigDict


class UserUpdate(BaseModel):
    full_name: str | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class Message(BaseModel):
    message: str

    model_config = ConfigDict(from_attributes=True)