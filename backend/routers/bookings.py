from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from database import get_db
from models import Booking, BookingStatus, Property, RentalType

router = APIRouter(prefix="/bookings", tags=["bookings"])


class BookingCreate(BaseModel):
    property_id: int
    renter_name: str = Field(..., min_length=2)
    renter_phone: str = Field(..., min_length=11)
    renter_email: Optional[str] = None
    check_in: datetime
    check_out: datetime
    rental_type: RentalType
    note: Optional[str] = None


class BookingOut(BaseModel):
    id: int
    property_id: int
    renter_name: str
    renter_phone: str
    renter_email: Optional[str]
    check_in: datetime
    check_out: datetime
    rental_type: RentalType
    total_price: float
    status: BookingStatus
    note: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


def compute_price(prop: Property, check_in: datetime, check_out: datetime, rental_type: RentalType) -> float:
    delta = check_out - check_in
    if rental_type == RentalType.hourly:
        hours = max(delta.total_seconds() / 3600, 1)
        return round(prop.price * hours, 2)
    if rental_type == RentalType.daily:
        days = max(delta.days, 1)
        return round(prop.price * days, 2)
    # monthly — count started months
    months = max(round(delta.days / 30), 1)
    return round(prop.price * months, 2)


def has_overlap(db: Session, property_id: int, check_in: datetime, check_out: datetime, exclude_id: int = None):
    q = db.query(Booking).filter(
        Booking.property_id == property_id,
        Booking.status != BookingStatus.cancelled,
        Booking.check_in < check_out,
        Booking.check_out > check_in,
    )
    if exclude_id:
        q = q.filter(Booking.id != exclude_id)
    return q.first() is not None


@router.post("/", response_model=BookingOut, status_code=201)
def create_booking(payload: BookingCreate, db: Session = Depends(get_db)):
    if payload.check_out <= payload.check_in:
        raise HTTPException(status_code=400, detail="check_out must be after check_in")

    prop = db.query(Property).filter(Property.id == payload.property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    if has_overlap(db, payload.property_id, payload.check_in, payload.check_out):
        raise HTTPException(status_code=409, detail="Property is already booked for the selected dates")

    total = compute_price(prop, payload.check_in, payload.check_out, payload.rental_type)

    booking = Booking(
        **payload.model_dump(),
        total_price=total,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/property/{property_id}", response_model=list[BookingOut])
def get_property_bookings(property_id: int, db: Session = Depends(get_db)):
    return (
        db.query(Booking)
        .filter(
            Booking.property_id == property_id,
            Booking.status != BookingStatus.cancelled,
        )
        .order_by(Booking.check_in)
        .all()
    )


@router.get("/property/{property_id}/availability")
def get_availability(property_id: int, db: Session = Depends(get_db)):
    bookings = (
        db.query(Booking)
        .filter(
            Booking.property_id == property_id,
            Booking.status != BookingStatus.cancelled,
            Booking.check_out >= datetime.utcnow(),
        )
        .order_by(Booking.check_in)
        .all()
    )
    return [
        {"check_in": b.check_in.isoformat(), "check_out": b.check_out.isoformat(), "status": b.status}
        for b in bookings
    ]


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    b = db.query(Booking).filter(Booking.id == booking_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    return b


@router.patch("/{booking_id}/cancel", response_model=BookingOut)
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    b = db.query(Booking).filter(Booking.id == booking_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Booking not found")
    if b.status == BookingStatus.cancelled:
        raise HTTPException(status_code=400, detail="Booking is already cancelled")
    b.status = BookingStatus.cancelled
    db.commit()
    db.refresh(b)
    return b
