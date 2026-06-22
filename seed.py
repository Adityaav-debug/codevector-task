import asyncio
import asyncpg
import random
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

CATEGORIES = ["Electronics", "Clothing", "Books", "Home", "Sports",
              "Toys", "Beauty", "Automotive", "Garden", "Food"]

async def seed():
    conn = await asyncpg.connect(os.environ["DATABASE_URL"])

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id          BIGSERIAL PRIMARY KEY,
            name        TEXT NOT NULL,
            category    TEXT NOT NULL,
            price       NUMERIC(10, 2) NOT NULL,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)

    # Create index for fast cursor pagination
    await conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_products_created_id
        ON products (created_at DESC, id DESC)
    """)
    await conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_products_category_created_id
        ON products (category, created_at DESC, id DESC)
    """)

    print("Generating 200,000 products...")

    # Build rows in Python, insert in one COPY — fast
    base_time = datetime.utcnow()
    rows = []
    for i in range(200_000):
        name = f"Product {i+1}"
        category = random.choice(CATEGORIES)
        price = round(random.uniform(1.0, 9999.0), 2)
        # Spread created_at over the last 2 years so ordering is meaningful
        offset_seconds = random.randint(0, 2 * 365 * 24 * 3600)
        created_at = base_time - timedelta(seconds=offset_seconds)
        updated_at = created_at
        rows.append((name, category, price, created_at, updated_at))

    await conn.copy_records_to_table(
        "products",
        records=rows,
        columns=["name", "category", "price", "created_at", "updated_at"]
    )

    count = await conn.fetchval("SELECT COUNT(*) FROM products")
    print(f"Done. {count} products in DB.")
    await conn.close()

asyncio.run(seed())