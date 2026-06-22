from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import UserRole, require_role
from app.database import get_db
from app.models.mountain import Mountain
from app.schemas.mountain import MountainCreate, MountainRead, MountainUpdate


router = APIRouter(prefix="/mountains", tags=["mountains"])


@router.get("", response_model=list[MountainRead])
def list_mountains(db: Session = Depends(get_db)):
    return db.query(Mountain).order_by(Mountain.name.asc()).all()


@router.get("/{mountain_id}", response_model=MountainRead)
def get_mountain(mountain_id: int, db: Session = Depends(get_db)):
    mountain = db.query(Mountain).filter(Mountain.id == mountain_id).first()
    if not mountain:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mountain not found")
    return mountain


@router.post("", response_model=MountainRead, status_code=status.HTTP_201_CREATED)
def create_mountain(
    mountain_in: MountainCreate,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_role(UserRole.admin)),
):
    mountain = Mountain(**mountain_in.model_dump())
    db.add(mountain)
    db.commit()
    db.refresh(mountain)
    return mountain


@router.put("/{mountain_id}", response_model=MountainRead)
def update_mountain(
    mountain_id: int,
    mountain_in: MountainUpdate,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_role(UserRole.admin)),
):
    mountain = db.query(Mountain).filter(Mountain.id == mountain_id).first()
    if not mountain:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mountain not found")

    for field, value in mountain_in.model_dump(exclude_unset=True).items():
        setattr(mountain, field, value)

    db.commit()
    db.refresh(mountain)
    return mountain


@router.delete("/{mountain_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mountain(
    mountain_id: int,
    db: Session = Depends(get_db),
    _current_admin=Depends(require_role(UserRole.admin)),
):
    mountain = db.query(Mountain).filter(Mountain.id == mountain_id).first()
    if not mountain:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mountain not found")

    db.delete(mountain)
    db.commit()