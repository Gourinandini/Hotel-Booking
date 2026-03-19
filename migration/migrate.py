"""
Migration Service: SQLite (PostgreSQL) → MongoDB
Run AFTER the FastAPI backend has data.
Run: python migrate.py
"""

import sqlite3
from pymongo import MongoClient
from datetime import datetime

# ─── Config ───────────────────────────────────────────────────────────────────
SQLITE_PATH = "../api/hotel_booking.db"
MONGO_URI = "YOUR_MONGODB_ATLAS_CONNECTION_STRING"  # Replace this!
MONGO_DB = "hotel_bookings"
BATCH_SIZE = 500


def get_sqlite_data():
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            b.id          AS booking_id,
            b.check_in, b.check_out, b.total_price, b.status, b.created_at,
            u.id          AS user_id,
            u.name        AS user_name,
            u.email       AS user_email,
            u.phone       AS user_phone,
            r.id          AS room_id,
            r.room_type, r.capacity, r.price_per_night,
            h.id          AS hotel_id,
            h.name        AS hotel_name,
            h.city        AS hotel_city,
            h.stars       AS hotel_stars,
            h.amenities   AS hotel_amenities,
            h.description AS hotel_description
        FROM bookings b
        JOIN users u  ON b.user_id = u.id
        JOIN rooms r  ON b.room_id = r.id
        JOIN hotels h ON r.hotel_id = h.id
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows


def transform(row):
    """Transform a flat SQL row into a rich MongoDB document."""
    return {
        "_id": f"BOOKING-{row['booking_id']}",
        "bookingId": row['booking_id'],
        "status": row['status'],
        "checkIn": row['check_in'],
        "checkOut": row['check_out'],
        "totalPrice": row['total_price'],
        "createdAt": row['created_at'],
        "guest": {
            "userId": row['user_id'],
            "name": row['user_name'],
            "email": row['user_email'],
            "phone": row['user_phone'],
        },
        "room": {
            "roomId": row['room_id'],
            "type": row['room_type'],
            "capacity": row['capacity'],
            "pricePerNight": row['price_per_night'],
        },
        "hotel": {
            "hotelId": row['hotel_id'],
            "name": row['hotel_name'],
            "city": row['hotel_city'],
            "stars": row['hotel_stars'],
            "amenities": row['hotel_amenities'].split(',') if row['hotel_amenities'] else [],
            "description": row['hotel_description'],
        },
        "migratedAt": datetime.utcnow().isoformat(),
        "source": "migration-v1"
    }


def run_migration():
    print("🔄 Starting migration: SQLite → MongoDB\n")

    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db["bookings"]

    # Step 1: Clean MongoDB
    print("🗑️  Cleaning MongoDB collection...")
    collection.drop()
    print("   ✅ MongoDB collection cleared\n")

    # Step 2: Extract from SQLite
    print("📤 Extracting data from SQLite...")
    rows = get_sqlite_data()
    print(f"   ✅ Extracted {len(rows)} bookings\n")

    # Step 3: Transform & Load in batches
    print("📥 Loading into MongoDB in batches...")
    total = 0
    batch = []

    for row in rows:
        doc = transform(row)
        batch.append(doc)

        if len(batch) == BATCH_SIZE:
            collection.insert_many(batch)
            total += len(batch)
            batch = []
            print(f"   ✅ {total} records loaded...")

    if batch:
        collection.insert_many(batch)
        total += len(batch)

    # Step 4: Create indexes for fast search
    collection.create_index("guest.email")
    collection.create_index("hotel.city")
    collection.create_index("status")
    collection.create_index("hotel.hotelId")
    print("\n   ✅ Indexes created\n")

    print(f"🎉 Migration complete! {total} bookings migrated to MongoDB.\n")

    # Step 5: Verify
    count = collection.count_documents({})
    print(f"✅ Verification: {count} documents in MongoDB")

    # Sample search demo
    sample = collection.find_one({"hotel.city": "Goa"})
    if sample:
        print(f"\n📋 Sample document from MongoDB (Goa hotel):")
        print(f"   Booking ID : {sample['bookingId']}")
        print(f"   Guest      : {sample['guest']['name']}")
        print(f"   Hotel      : {sample['hotel']['name']}")
        print(f"   Dates      : {sample['checkIn']} → {sample['checkOut']}")
        print(f"   Total      : ₹{sample['totalPrice']}")

    client.close()


if __name__ == "__main__":
    run_migration()
