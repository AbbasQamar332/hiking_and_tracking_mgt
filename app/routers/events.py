from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import UserRole, require_role
from app.database import get_db
from app.models.hiking_event import HikingEvent

from app.models.user import User
from app.schemas.event import EventCreate, EventRead, EventUpdate


router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventRead])
def list_events(
    db: Session = Depends(get_db),
    mountain_id: int | None = None,
    difficulty: str | None = None,
    is_approved: bool | None = True,
    q: str | None = Query(default=None, description="Search title, location, and description"),
):
    query = db.query(HikingEvent)
    if mountain_id is not None:
        query = query.filter(HikingEvent.mountain_id == mountain_id)
    if difficulty is not None:
        query = query.filter(HikingEvent.difficulty == difficulty)
    if is_approved is not None:
        query = query.filter(HikingEvent.is_approved == is_approved)
    if q:
        term = f"%{q}%"
        query = query.filter(
            (HikingEvent.title.ilike(term))
            | (HikingEvent.location.ilike(term))
            | (HikingEvent.description.ilike(term))
        )
    return query.order_by(HikingEvent.event_date.asc()).all()


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(
    event_in: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.owner)),
):
    event = HikingEvent(**event_in.model_dump(), owner_id=current_user.id)
    event.is_approved = current_user.role == UserRole.admin.value
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(HikingEvent).filter(HikingEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.put("/{event_id}", response_model=EventRead)
def update_event(
    event_id: int,
    event_in: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.owner)),
):
    event = db.query(HikingEvent).filter(HikingEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if event.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own events")

    for field, value in event_in.model_dump(exclude_unset=True).items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)
    return event


@router.get("/approved", response_model=list[EventRead])
def list_approved_events(db: Session = Depends(get_db)):
    return db.query(HikingEvent).filter(HikingEvent.is_approved.is_(True)).order_by(HikingEvent.event_date.asc()).all()


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.owner)),
):
    event = db.query(HikingEvent).filter(HikingEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if event.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own events")

    db.delete(event)
    db.commit()