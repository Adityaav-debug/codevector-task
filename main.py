from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware, allow_origins=["*"],
    allow_methods=["*"], allow_headers=["*"]
)

pool = None

@app.on_event("startup")
async def startup():
    global pool
    pool = await asyncpg.create_pool(os.environ["DATABASE_URL"])

@app.on_event("shutdown")
async def shutdown():
    await pool.close()


@app.get("/products")
async def get_products(
    category: Optional[str] = None,
    limit: int = Query(default=20, le=100),
    cursor: Optional[str] = None,
):
    cursor_created_at = None
    cursor_id = None
    if cursor:
        try:
            ts_part, id_part = cursor.rsplit("__", 1)
            cursor_created_at = ts_part
            cursor_id = int(id_part)
        except Exception:
            pass

    params = []
    conditions = []

    if category:
        params.append(category)
        conditions.append(f"category = ${len(params)}")

    if cursor_created_at and cursor_id is not None:
        from datetime import datetime
        dt = datetime.strptime(cursor_created_at.strip(), '%Y-%m-%d %H:%M:%S.%f')
        params.append(dt)
        params.append(cursor_id)
        conditions.append(
            f"(created_at, id) < (${len(params)-1}, ${len(params)})"
        )

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    params.append(limit + 1)

    query = f"""
        SELECT id, name, category, price, created_at, updated_at
        FROM products
        {where}
        ORDER BY created_at DESC, id DESC
        LIMIT ${len(params)}
    """

    rows = await pool.fetch(query, *params)
    has_next = len(rows) > limit
    rows = rows[:limit]

    next_cursor = None
    if has_next and rows:
        last = rows[-1]
        next_cursor = f"{last['created_at'].strftime('%Y-%m-%d %H:%M:%S.%f')}__{last['id']}"

    return {
        "data": [
            {
                "id": r["id"],
                "name": r["name"],
                "category": r["category"],
                "price": float(r["price"]),
                "created_at": r["created_at"].isoformat(),
                "updated_at": r["updated_at"].isoformat(),
            }
            for r in rows
        ],
        "next_cursor": next_cursor,
        "has_next": has_next,
    }


@app.get("/categories")
async def get_categories():
    rows = await pool.fetch("SELECT DISTINCT category FROM products ORDER BY category")
    return [r["category"] for r in rows]


@app.get("/health")
async def health():
    return {"status": "ok"}


# Serve the frontend — MUST be after all API routes
@app.get("/")
async def serve_frontend():
    return FileResponse("static/index.html")