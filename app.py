import streamlit as st
import requests
from datetime import date, timedelta

API = "http://localhost:8000/api"

st.set_page_config(page_title="🏨 Hotel Booking System", layout="wide", page_icon="🏨")

# ─── Sidebar Navigation ───────────────────────────────────────────────────────
st.sidebar.title("🏨 Hotel Booking")
page = st.sidebar.radio("Navigate", [
    "🏠 Home & Search",
    "📅 Make a Booking",
    "📋 My Bookings",
    "📊 Admin Dashboard"
])

# ─── Helper Functions ─────────────────────────────────────────────────────────

def get(endpoint):
    try:
        r = requests.get(f"{API}{endpoint}", timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        st.error("❌ Cannot connect to API. Make sure the backend is running!")
        return []

def post(endpoint, data):
    try:
        r = requests.post(f"{API}{endpoint}", json=data, timeout=10)
        r.raise_for_status()
        return r.json()
    except requests.RequestException:
        st.error("❌ API Error")
        return None

def delete(endpoint):
    try:
        r = requests.delete(f"{API}{endpoint}", timeout=10)
        r.raise_for_status()
        return True
    except requests.RequestException:
        st.error("❌ Could not cancel booking right now. Please try again.")
        return False

# ─── Page: Home & Search ──────────────────────────────────────────────────────

if page == "🏠 Home & Search":
    st.title("🏨 Find Your Perfect Hotel")

    col1, col2 = st.columns([3, 1])
    with col1:
        city_search = st.text_input("🔍 Search by city (e.g. Goa, Mumbai, Jaipur)", "")
    with col2:
        st.write("")
        st.write("")
        search_btn = st.button("Search Hotels", use_container_width=True)

    hotels = get(f"/hotels?city={city_search}" if city_search else "/hotels")

    if hotels:
        st.markdown(f"### Found **{len(hotels)}** hotels")
        for hotel in hotels:
            with st.expander(f"⭐ {'★' * hotel['stars']} — {hotel['name']} ({hotel['city']})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"📍 **City:** {hotel['city']}")
                    st.write(f"⭐ **Stars:** {hotel['stars']}")
                    st.write(f"🛎️ **Amenities:** {hotel['amenities'].replace(',', ' | ')}")
                with col2:
                    st.info(hotel['description'])

                rooms = get(f"/rooms?hotel_id={hotel['id']}")
                if rooms:
                    st.write("**Available Rooms:**")
                    for room in rooms:
                        st.write(f"  🛏️ {room['room_type']} | 👥 {room['capacity']} guests | ₹{room['price_per_night']}/night")
    else:
        st.warning("No hotels found. Try a different city!")

# ─── Page: Make a Booking ─────────────────────────────────────────────────────

elif page == "📅 Make a Booking":
    st.title("📅 Make a Booking")

    st.subheader("Step 1: Your Details")
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Full Name")
    with col2:
        email = st.text_input("Email")
    with col3:
        phone = st.text_input("Phone")

    st.subheader("Step 2: Choose Hotel & Room")
    hotels = get("/hotels")
    hotel_names = {h['name']: h['id'] for h in hotels} if hotels else {}
    if not hotel_names:
        st.warning("No hotels are available right now.")
        st.stop()

    selected_hotel_name = st.selectbox("Select Hotel", list(hotel_names.keys()))

    rooms = []
    if selected_hotel_name:
        hotel_id = hotel_names[selected_hotel_name]
        rooms = get(f"/rooms?hotel_id={hotel_id}")

    room_options = {f"{r['room_type']} — ₹{r['price_per_night']}/night": r['id'] for r in rooms}
    if not room_options:
        st.warning("No rooms are available for this hotel.")
        st.stop()

    selected_room_name = st.selectbox("Select Room Type", list(room_options.keys()))

    st.subheader("Step 3: Choose Dates")
    col1, col2 = st.columns(2)
    with col1:
        check_in = st.date_input("Check-in Date", min_value=date.today())
    with col2:
        check_out = st.date_input("Check-out Date", min_value=date.today() + timedelta(days=1))

    if check_in and check_out and check_out > check_in and selected_room_name:
        nights = (check_out - check_in).days
        selected_room_id = room_options[selected_room_name]
        price_per_night = next(r['price_per_night'] for r in rooms if r['id'] == selected_room_id)
        total = nights * price_per_night

        st.success(f"🧾 **{nights} nights × ₹{price_per_night} = ₹{total:.2f} total**")

    if st.button("✅ Confirm Booking", type="primary"):
        if not name or not email or not phone:
            st.error("Please fill in all your details!")
        elif check_out <= check_in:
            st.error("Check-out must be after check-in!")
        else:
            with st.spinner("Creating your booking..."):
                user = post("/users", {"name": name, "email": email, "phone": phone})
                if user:
                    booking = post("/bookings", {
                        "user_id": user['id'],
                        "room_id": room_options[selected_room_name],
                        "check_in": str(check_in),
                        "check_out": str(check_out)
                    })
                    if booking:
                        st.balloons()
                        st.success(f"🎉 Booking Confirmed! Booking ID: **{booking['id']}**")
                        st.info(f"Total: ₹{booking['total_price']} | Status: {booking['status']}")

# ─── Page: My Bookings ────────────────────────────────────────────────────────

elif page == "📋 My Bookings":
    st.title("📋 My Bookings")

    email_search = st.text_input("Enter your email to find bookings")
    if email_search and st.button("Find Bookings"):
        users = get("/users")
        user = next((u for u in users if u['email'] == email_search), None)
        if user:
            bookings = get(f"/bookings/user/{user['id']}")
            if bookings:
                st.success(f"Found {len(bookings)} booking(s) for {user['name']}")
                for b in bookings:
                    status_color = {"CONFIRMED": "🟢", "CANCELLED": "🔴", "COMPLETED": "🔵"}.get(b['status'], "⚪")
                    with st.expander(f"{status_color} Booking #{b['id']} — ₹{b['total_price']}"):
                        st.write(f"📅 **Check-in:** {b['check_in']}")
                        st.write(f"📅 **Check-out:** {b['check_out']}")
                        st.write(f"🏷️ **Status:** {b['status']}")
                        st.write(f"🕐 **Booked on:** {b['created_at']}")
                        if b['status'] == "CONFIRMED":
                            if st.button(f"Cancel Booking #{b['id']}"):
                                if delete(f"/bookings/{b['id']}"):
                                    st.rerun()
            else:
                st.warning("No bookings found for this email.")
        else:
            st.error("No user found with this email.")

# ─── Page: Admin Dashboard ────────────────────────────────────────────────────

elif page == "📊 Admin Dashboard":
    st.title("📊 Admin Dashboard")

    stats = get("/stats")
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🏨 Hotels", stats['total_hotels'])
        col2.metric("🛏️ Rooms", stats['total_rooms'])
        col3.metric("👥 Users", stats['total_users'])
        col4.metric("📋 Bookings", stats['total_bookings'])

        col1, col2, col3 = st.columns(3)
        col1.metric("✅ Confirmed", stats['confirmed'])
        col2.metric("❌ Cancelled", stats['cancelled'])
        col3.metric("✔️ Completed", stats['completed'])

    st.subheader("All Bookings")
    status_filter = st.selectbox("Filter by Status", ["ALL", "CONFIRMED", "CANCELLED", "COMPLETED"])

    endpoint = "/bookings" if status_filter == "ALL" else f"/bookings?status={status_filter}"
    bookings = get(endpoint)

    if bookings:
        import pandas as pd
        df = pd.DataFrame(bookings)
        df = df[['id', 'user_id', 'room_id', 'check_in', 'check_out', 'total_price', 'status', 'created_at']]
        df.columns = ['ID', 'User ID', 'Room ID', 'Check-in', 'Check-out', 'Total (₹)', 'Status', 'Created']
        st.dataframe(df, use_container_width=True)
        st.caption(f"Showing {len(bookings)} bookings")
    else:
        st.info("No bookings found.")
