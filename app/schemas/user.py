from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.auth import UserRole


class UserBase(BaseModel):
    name : str =  Field(min_length=3, max_length=50)
    email: EmailStr
    role: UserRole = UserRole.visitor

    @field_validator("email")
    @classmethod
    def email_validation(cls,value):
        if value.lower().strip().endswith("@gmail.com"):
            return value
        else:
            raise ValueError("Email must be ends with @gmail.com")


    



class UserCreate(UserBase):
    password: str = Field(min_length=8, examples=["12345678"])


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_verified: bool
    is_banned: bool
    verified_by: int | None
    created_at: datetime