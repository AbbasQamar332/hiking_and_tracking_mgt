from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.auth import UserRole


class UserBase(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.visitor


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_verified: bool
    is_banned: bool
    verified_by: int | None
    created_at: datetime