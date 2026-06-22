# ProductVault — CodeVector Backend Task

A backend service to browse 200,000 products with stable cursor-based pagination and category filtering.

## Stack
- **Backend:** FastAPI + asyncpg
- **Database:** PostgreSQL (Neon)
- **Frontend:** Vanilla HTML/CSS/JS (served by FastAPI)

## Key Design Decision — Cursor-based Pagination
Standard `OFFSET` pagination breaks when data changes mid-session — new inserts shift rows and cause duplicates or skips. This uses a composite cursor of `(created_at, id)` so pagination stays stable regardless of inserts or updates.

Indexes on `(created_at DESC, id DESC)` and `(category, created_at DESC, id DESC)` make every page fetch a fast index scan.

## Setup

1. Install dependencies:
```bash
   pip install -r requirements.txt
```

2. Add your Neon connection string to `.env`:
DATABASE_URL=postgresql://...

3. Seed the database (inserts 200k rows using Postgres COPY — takes ~10s):
```bash
   python seed.py
```

4. Run the server:
```bash
   uvicorn main:app --reload
```

5. Open `http://127.0.0.1:8000`

## What I'd improve with more time
- Cursor signing to prevent tampering
- Total count per category in sidebar
- Price range and date filters
- Rate limiting
