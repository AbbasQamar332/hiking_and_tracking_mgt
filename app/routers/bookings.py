from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import UserRole, get_current_user, require_role
from app.database import get_db
from app.models.booking import Booking
from app.models.hiking_event import HikingEvent
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingRead


router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("", response_model=list[BookingRead])
def list_my_bookings(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Booking).filter(Booking.user_id == current_user.id)
    if current_user.role == UserRole.owner.value:
        query = db.query(Booking)
    return query.order_by(Booking.booked_at.desc()).all()


@router.post("", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.visitor)),
):
    event = db.query(HikingEvent).filter(HikingEvent.id == booking_in.event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if not event.is_approved:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event is not approved yet")

    confirmed_bookings = db.query(Booking).filter(Booking.event_id == event.id, Booking.status == "confirmed").count()
    if confirmed_bookings >= event.capacity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event is fully booked")

    existing_booking = db.query(Booking).filter(
        Booking.user_id == current_user.id,
        Booking.event_id == booking_in.event_id,
    ).first()
    if existing_booking:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already booked this event")

    booking = Booking(user_id=current_user.id, event_id=booking_in.event_id)
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_booking(booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    if current_user.role != UserRole.owner.value and booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only cancel your own bookings")

    db.delete(booking)
    db.commit()