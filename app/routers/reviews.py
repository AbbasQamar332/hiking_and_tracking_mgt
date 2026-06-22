from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import UserRole, require_role
from app.database import get_db
from app.models.booking import Booking
from app.models.hiking_event import HikingEvent
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewRead, ReviewReply


router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("", response_model=list[ReviewRead])
def list_reviews(db: Session = Depends(get_db)):
    return db.query(Review).order_by(Review.created_at.desc()).all()


@router.post("", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
def create_review(
    review_in: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.visitor)),
):
    event = db.query(HikingEvent).filter(HikingEvent.id == review_in.event_id).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    if not event.is_approved:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event is not approved yet")

    attended_booking = db.query(Booking).filter(
        Booking.event_id == review_in.event_id,
        Booking.user_id == current_user.id,
        Booking.status == "confirmed",
    ).first()
    if not attended_booking:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You must book the event before reviewing it")

    review = Review(user_id=current_user.id, **review_in.model_dump())
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.patch("/{review_id}/reply", response_model=ReviewRead)
def reply_to_review(
    review_id: int,
    reply_in: ReviewReply,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.owner)),
):
    review = db.query(Review).join(HikingEvent).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    if review.event.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only reply to reviews for your own events")

    review.owner_reply = reply_in.reply
    db.commit()
    db.refresh(review)
    return review