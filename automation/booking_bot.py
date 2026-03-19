"""
Playwright Automation Script
Generates thousands of realistic hotel bookings via the API directly (faster than browser automation).
Run: python booking_bot.py
"""

import requests
import random
from datetime import date, timedelta
from faker import Faker

fake = Faker('en_IN')  # Indian locale for realistic names/phones
API = "http://localhost:8000/api"
TARGET_BOOKINGS = 2000  # Change to 5000 for more data


def random_date_in_next_3_years():
    start = date.today()
    end = start + timedelta(days=3 * 365)
    random_days = random.randint(0, (end - start).days)
    check_in = start + timedelta(days=random_days)
    check_out = check_in + timedelta(days=random.randint(1, 14))
    return check_in, check_out


def get_all_rooms():
    r = requests.get(f"{API}/rooms")
    return r.json()


def create_user():
    name = fake.name()
    email = fake.unique.email()
    phone = fake.phone_number()[:15]
    r = requests.post(f"{API}/users", json={"name": name, "email": email, "phone": phone})
    return r.json()


def create_booking(user_id, room_id, check_in, check_out):
    r = requests.post(f"{API}/bookings", json={
        "user_id": user_id,
        "room_id": room_id,
        "check_in": str(check_in),
        "check_out": str(check_out)
    })
    return r.json()


def run():
    print(f"🤖 Starting automation — target: {TARGET_BOOKINGS} bookings\n")
    rooms = get_all_rooms()
    room_ids = [r['id'] for r in rooms]

    success = 0
    failed = 0

    for i in range(TARGET_BOOKINGS):
        try:
            user = create_user()
            room_id = random.choice(room_ids)
            check_in, check_out = random_date_in_next_3_years()
            booking = create_booking(user['id'], room_id, check_in, check_out)
            success += 1

            if success % 100 == 0:
                print(f"  ✅ {success} bookings created so far...")

        except Exception as e:
            failed += 1
            if failed % 50 == 0:
                print(f"  ⚠️ {failed} failures so far: {e}")

    print(f"\n🎉 Done! {success} bookings created, {failed} failed.")


if __name__ == "__main__":
    run()
