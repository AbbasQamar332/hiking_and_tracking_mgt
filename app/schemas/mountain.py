from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MountainBase(BaseModel):
    name: str
    altitude_m: int | None = None
    best_season: str | None = None
    weather: str | None = None
    description: str | None = None
    region: str | None = None
    cover_image: str | None = None


class MountainCreate(MountainBase):
    pass


class MountainUpdate(BaseModel):
    name: str | None = None
    altitude_m: int | None = None
    best_season: str | None = None
    weather: str | None = None
    description: str | None = None
    region: str | None = None
    cover_image: str | None = None


class MountainRead(MountainBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime