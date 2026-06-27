from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import UserRole, get_current_user, require_role
from app.database import get_db
from app.models.booking import Booking
from app.models.hiking_event import HikingEvent

from app.models.review import Review
from app.models.user import User
from app.schemas.event import EventRead
from app.schemas.user import UserRead


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db), _current_admin=Depends(require_role(UserRole.admin))):
    return db.query(User).order_by(User.created_at.desc()).all()


@router.patch("/users/{user_id}/ban", response_model=UserRead)
def ban_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role(UserRole.admin)),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_banned = True
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}/verify", response_model=UserRead)
def verify_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_role(UserRole.admin)),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_verified = True
    user.verified_by = current_admin.id
    db.commit()
    db.refresh(user)
    return user


@router.get("/pending-events", response_model=list[EventRead])
def list_pending_events(db: Session = Depends(get_db), _current_admin=Depends(require_role(UserRole.admin))):
    return db.query(HikingEvent).filter(HikingEvent.is_approved.is_(False)).order_by(HikingEvent.created_at.desc()).all()


@router.patch("/events/{event_id}/approve", response_model=EventRead)
def approve_event(
    event_id: int,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_role(UserRole.admin)),
):
    event = db.query(HikingEvent).filter(HikingEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    event.is_approved = True
    db.commit()
    db.refresh(event)
    return event


@router.patch("/events/{event_id}/reject", response_model=EventRead)
def reject_event(
    event_id: int,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_role(UserRole.admin)),
):
    event = db.query(HikingEvent).filter(HikingEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    db.delete(event)
    db.commit()
    return event


@router.get("/reports/summary")
def report_summary(db: Session = Depends(get_db), _current_admin=Depends(require_role(UserRole.admin))):
    return {
        "users": db.query(func.count(User.id)).scalar() or 0,
        "owners": db.query(func.count(User.id)).filter(User.role == UserRole.owner.value).scalar() or 0,
        "visitors": db.query(func.count(User.id)).filter(User.role == UserRole.visitor.value).scalar() or 0,
        "events": db.query(func.count(HikingEvent.id)).scalar() or 0,
        "approved_events": db.query(func.count(HikingEvent.id)).filter(HikingEvent.is_approved.is_(True)).scalar() or 0,
        "bookings": db.query(func.count(Booking.id)).scalar() or 0,
        "reviews": db.query(func.count(Review.id)).scalar() or 0,
        "mountains": db.query(func.count(Mountain.id)).scalar() or 0,
    }