from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List
from models import Hotel, Room, User, Booking, get_db

router = APIRouter()

# ─── Pydantic Schemas ────────────────────────────────────────────────────────

class HotelCreate(BaseModel):
    name: str
    city: str
    stars: int
    amenities: str
    description: str

class RoomCreate(BaseModel):
    hotel_id: int
    room_type: str
    capacity: int
    price_per_night: float

class UserCreate(BaseModel):
    name: str
    email: str
    phone: str

class BookingCreate(BaseModel):
    user_id: int
    room_id: int
    check_in: date
    check_out: date

class BookingStatusUpdate(BaseModel):
    status: str

# ─── Hotel Endpoints ──────────────────────────────────────────────────────────

@router.post("/hotels")
def create_hotel(hotel: HotelCreate, db: Session = Depends(get_db)):
    db_hotel = Hotel(**hotel.dict())
    db.add(db_hotel)
    db.commit()
    db.refresh(db_hotel)
    return db_hotel

@router.get("/hotels")
def get_hotels(city: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Hotel)
    if city:
        query = query.filter(Hotel.city.ilike(f"%{city}%"))
    return query.all()

@router.get("/hotels/{hotel_id}")
def get_hotel(hotel_id: int, db: Session = Depends(get_db)):
    hotel = db.query(Hotel).filter(Hotel.id == hotel_id).first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel

# ─── Room Endpoints ───────────────────────────────────────────────────────────

@router.post("/rooms")
def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    db_room = Room(**room.dict())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

@router.get("/rooms")
def get_rooms(hotel_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Room)
    if hotel_id:
        query = query.filter(Room.hotel_id == hotel_id)
    return query.all()

# ─── User Endpoints ───────────────────────────────────────────────────────────

@router.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        return existing  # return existing user instead of error (for automation)
    db_user = User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ─── Booking Endpoints ────────────────────────────────────────────────────────

@router.post("/bookings")
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == booking.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    nights = (booking.check_out - booking.check_in).days
    if nights <= 0:
        raise HTTPException(status_code=400, detail="Check-out must be after check-in")

    total_price = nights * room.price_per_night

    db_booking = Booking(
        user_id=booking.user_id,
        room_id=booking.room_id,
        check_in=booking.check_in,
        check_out=booking.check_out,
        total_price=total_price,
        status="CONFIRMED"
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

@router.get("/bookings")
def get_bookings(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Booking)
    if status:
        query = query.filter(Booking.status == status)
    return query.all()

@router.get("/bookings/{booking_id}")
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.get("/bookings/user/{user_id}")
def get_user_bookings(user_id: int, db: Session = Depends(get_db)):
    return db.query(Booking).filter(Booking.user_id == user_id).all()

@router.patch("/bookings/{booking_id}/status")
def update_booking_status(booking_id: int, update: BookingStatusUpdate, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = update.status
    db.commit()
    return booking

@router.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = "CANCELLED"
    db.commit()
    return {"message": "Booking cancelled", "id": booking_id}

# ─── Stats Endpoint (for dashboard) ──────────────────────────────────────────

@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return {
        "total_hotels": db.query(Hotel).count(),
        "total_rooms": db.query(Room).count(),
        "total_users": db.query(User).count(),
        "total_bookings": db.query(Booking).count(),
        "confirmed": db.query(Booking).filter(Booking.status == "CONFIRMED").count(),
        "cancelled": db.query(Booking).filter(Booking.status == "CANCELLED").count(),
        "completed": db.query(Booking).filter(Booking.status == "COMPLETED").count(),
    }
