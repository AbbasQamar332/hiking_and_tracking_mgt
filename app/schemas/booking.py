from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BookingBase(BaseModel):
    event_id: int


class BookingCreate(BookingBase):
    pass


class BookingRead(BookingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: str
    booked_at: datetime