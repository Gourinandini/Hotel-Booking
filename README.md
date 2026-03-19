# 🏨 Hotel Booking System — Setup Guide

## Prerequisites (Install these first)
- Python 3.10+ → https://python.org
- VS Code → https://code.visualstudio.com

---

## Step 1 — Install all Python packages
Open a terminal in VS Code and run:
```bash
pip install fastapi uvicorn streamlit sqlalchemy pymongo faker requests anthropic
```

---

## Step 2 — Sign up for free cloud services

### MongoDB Atlas (NoSQL Database)
1. Go to https://mongodb.com/atlas
2. Sign up free → Create a project → Build a free cluster (M0)
3. Create a database user (username + password)
4. Click "Connect" → "Drivers" → copy the connection string
5. Paste it in `migration/migrate.py` where it says `YOUR_MONGODB_ATLAS_CONNECTION_STRING`
   - Replace `<password>` in the string with your actual password

### Upstash Kafka (Message Broker) — Do this on Day 3
1. Go to https://upstash.com
2. Sign up free → Create Kafka → Single Region
3. Copy the bootstrap server, username, password

---

## Step 3 — Run the Backend API
```bash
cd api
python main.py
```
✅ API is running at: http://localhost:8000
✅ API docs at:       http://localhost:8000/docs

---

## Step 4 — Run the Frontend
Open a NEW terminal window:
```bash
cd hotel-booking
streamlit run app.py
```
✅ Frontend opens automatically in your browser

---

## Step 5 — Generate Bookings (Run the Bot)
Open another NEW terminal window:
```bash
cd automation
python booking_bot.py
```
This will create 2000 bookings automatically!

---

## Step 6 — Run Migration to MongoDB
```bash
cd migration
python migrate.py
```
This migrates all bookings from SQLite to MongoDB Atlas.

---

## Folder Structure
```
hotel-booking/
  api/
    main.py        ← Start the backend here
    models.py      ← Database tables
    routes.py      ← All API endpoints
  migration/
    migrate.py     ← SQLite → MongoDB migration
  automation/
    booking_bot.py ← Auto-generate thousands of bookings
  app.py           ← Streamlit frontend (run this)
  README.md        ← This file
```

---

## Troubleshooting
- "Cannot connect to API" → Make sure `python main.py` is running in a separate terminal
- "MongoDB connection error" → Check your Atlas connection string, make sure IP whitelist is set to 0.0.0.0/0
- "Module not found" → Run `pip install <module_name>`
=======
# Hotel-Booking
