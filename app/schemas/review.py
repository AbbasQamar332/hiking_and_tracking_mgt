from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewBase(BaseModel):
    event_id: int
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class ReviewCreate(ReviewBase):
    pass


class ReviewRead(ReviewBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    owner_reply: str | None
    created_at: datetime


class ReviewReply(BaseModel):
    reply: str = Field(min_length=1, max_length=500)