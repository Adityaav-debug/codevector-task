ProductVault — CodeVector Backend Task

A backend service to browse 200,000 products with category filtering and stable cursor-based pagination.

Stack
Backend: FastAPI + asyncpg
Database: PostgreSQL (Neon)
Frontend: Vanilla HTML/CSS/JS served by FastAPI
Deployment: Render

Why I chose this stack

I chose FastAPI because it's lightweight and asynchronous, making it a good fit for database-heavy APIs. PostgreSQL was chosen because cursor pagination relies heavily on ordered queries and indexes, which PostgreSQL handles efficiently. Neon provided a free hosted database and Render made deployment simple.

Key Design Decision — Cursor Pagination

Traditional OFFSET pagination becomes unstable when data changes while users are browsing. New products inserted at the top can shift rows, causing duplicates or skipped records.

I used a composite cursor (created_at, id) with:

WHERE (created_at, id) < (cursor_created_at, cursor_id)
ORDER BY created_at DESC, id DESC

This guarantees stable pagination even if products are inserted while users are browsing.

Performance

To efficiently seed 200,000 products, I used PostgreSQL's COPY protocol via asyncpg.copy_records_to_table(), which is much faster than inserting rows individually.

Indexes:

(created_at DESC, id DESC)

(category, created_at DESC, id DESC)

allow efficient filtering and pagination using index scans.

Setup

Install dependencies:

pip install -r requirements.txt

Add your Neon connection string to .env:

DATABASE_URL=postgresql://...

Seed the database:

python seed.py

Start the server:

uvicorn main:app --reload

Open:

http://127.0.0.1:8000
What I'd improve with more time
Price range filters.
Search by product name.
Cursor signing to prevent tampering.
Rate limiting.
Unit tests.
Better UI.
Caching categories.
How I used AI

I used AI tools to discuss approaches and accelerate implementation.

AI helped with:

Structuring the FastAPI application.
Designing cursor-based pagination.
Suggesting PostgreSQL COPY for efficient seeding.

Things I caught and corrected:

Fixed cursor formatting issues.
Cleaned Git history after accidentally tracking .env.
Verified pagination logic and indexes instead of blindly using generated code.
Live Demo

Render URL:
https://codevector-task-dcxt.onrender.com

Repository

GitHub:
https://github.com/Adityaav-debug/codevector-task