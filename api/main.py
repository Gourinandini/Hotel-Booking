from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import init_db, SessionLocal, Hotel, Room, User
from routes import router

app = FastAPI(title="Hotel Booking API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


def seed_data():
    """Insert sample hotels and rooms if DB is empty."""
    db = SessionLocal()
    if db.query(Hotel).count() > 0:
        db.close()
        return

    hotels_data = [
        {"name": "The Grand Palace", "city": "Mumbai", "stars": 5, "amenities": "wifi,pool,gym,spa,restaurant", "description": "A luxurious 5-star hotel in the heart of Mumbai with world-class amenities."},
        {"name": "Sea Breeze Resort", "city": "Goa", "stars": 4, "amenities": "wifi,pool,beach,restaurant,bar", "description": "Beachfront resort with stunning Arabian Sea views and tropical vibes."},
        {"name": "Heritage Haveli", "city": "Jaipur", "stars": 4, "amenities": "wifi,pool,spa,restaurant,heritage-tour", "description": "Stay in a restored royal haveli with authentic Rajasthani hospitality."},
        {"name": "Backwater Bliss", "city": "Kerala", "stars": 3, "amenities": "wifi,houseboat,spa,ayurveda", "description": "Serene Kerala backwater retreat with Ayurvedic treatments."},
        {"name": "City Comfort Inn", "city": "Bengaluru", "stars": 3, "amenities": "wifi,gym,restaurant,parking", "description": "Modern business hotel in the tech hub of India."},
        {"name": "Himalayan Retreat", "city": "Manali", "stars": 4, "amenities": "wifi,fireplace,trekking,restaurant", "description": "Cosy mountain retreat with breathtaking Himalayan views."},
        {"name": "Pearl of the East", "city": "Kolkata", "stars": 5, "amenities": "wifi,pool,gym,spa,restaurant,rooftop-bar", "description": "Colonial-era grandeur meets modern luxury in the City of Joy."},
        {"name": "Desert Dunes Camp", "city": "Jaisalmer", "stars": 3, "amenities": "wifi,desert-safari,bonfire,folk-music", "description": "Authentic desert camp experience under a canopy of stars."},
        {"name": "Marina Bay Hotel", "city": "Chennai", "stars": 4, "amenities": "wifi,pool,beach,gym,restaurant", "description": "Premium beachside hotel near Chennai's famous Marina Beach."},
        {"name": "Valley View Lodge", "city": "Ooty", "stars": 3, "amenities": "wifi,garden,restaurant,trekking", "description": "Charming hill-station lodge surrounded by tea gardens."},
    ]

    room_types = [
        {"room_type": "Single", "capacity": 1, "price_per_night": 1500.0},
        {"room_type": "Double", "capacity": 2, "price_per_night": 2500.0},
        {"room_type": "Suite",  "capacity": 4, "price_per_night": 5000.0},
    ]

    for h_data in hotels_data:
        hotel = Hotel(**h_data)
        db.add(hotel)
        db.flush()
        for r_data in room_types:
            room = Room(hotel_id=hotel.id, **r_data)
            db.add(room)

    db.commit()
    db.close()
    print("✅ Seed data inserted: 10 hotels, 30 rooms")


@app.on_event("startup")
def startup():
    init_db()
    seed_data()
    print("🚀 Hotel Booking API is running!")
    print("📖 Docs at: http://localhost:8000/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
