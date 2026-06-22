from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EventBase(BaseModel):
    title: str
    description: str | None = None
    location: str
    price: float = Field(ge=0)
    event_date: datetime
    capacity: int = Field(ge=1)
    difficulty: str = Field(pattern="^(Easy|Moderate|Hard|Extreme)$")
    mountain_id: int | None = None
    duration_days: int = Field(default=1, ge=1)
    gear_required: str | None = None
    cover_image: str | None = None


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    location: str | None = None
    price: float | None = Field(default=None, ge=0)
    event_date: datetime | None = None
    capacity: int | None = Field(default=None, ge=1)
    difficulty: str | None = Field(default=None, pattern="^(Easy|Moderate|Hard|Extreme)$")
    mountain_id: int | None = None
    duration_days: int | None = Field(default=None, ge=1)
    gear_required: str | None = None
    cover_image: str | None = None


class EventRead(EventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    is_approved: bool
    created_at: datetime