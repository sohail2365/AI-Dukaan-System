# database.py — PostgreSQL (Supabase) version
import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL missing — .env file check karo")

# Supabase/Postgres needs sslmode + NullPool works best on serverless (Vercel)
if "sslmode" not in DATABASE_URL:
    DATABASE_URL += "?sslmode=require" if "?" not in DATABASE_URL else "&sslmode=require"

engine = create_engine(DATABASE_URL, poolclass=NullPool)

def get_connection():
    """Returns a SQLAlchemy connection. Use like:
        with get_connection() as conn:
            conn.execute(text("..."), {...})
            conn.commit()
    """
    return engine.connect()

def setup_database():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS shops (
                shop_id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                shop_name TEXT NOT NULL,
                created_at DATE DEFAULT CURRENT_DATE
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id SERIAL PRIMARY KEY,
                shop_id INTEGER NOT NULL REFERENCES shops(shop_id),
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                created_at DATE DEFAULT CURRENT_DATE
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS khaata (
                id SERIAL PRIMARY KEY,
                customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
                item_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                price_per_item REAL NOT NULL,
                total REAL NOT NULL,
                date DATE DEFAULT CURRENT_DATE
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS purchases (
                id SERIAL PRIMARY KEY,
                shop_id INTEGER NOT NULL REFERENCES shops(shop_id),
                supplier_name TEXT NOT NULL,
                item_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                purchase_rate REAL NOT NULL,
                total_cost REAL NOT NULL,
                date DATE DEFAULT CURRENT_DATE
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS inventory (
                id SERIAL PRIMARY KEY,
                shop_id INTEGER NOT NULL REFERENCES shops(shop_id),
                item_name TEXT NOT NULL,
                category TEXT DEFAULT '',
                sale_price REAL NOT NULL,
                purchase_rate REAL DEFAULT 0,
                stock REAL DEFAULT 0,
                reorder_level INTEGER DEFAULT 5,
                created_at DATE DEFAULT CURRENT_DATE
            )
        """))
        # ---- Non-destructive migrations (safe on existing DBs) ----
        # Soft delete: khaata + purchases par deleted_at column
        conn.execute(text("ALTER TABLE khaata ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP DEFAULT NULL"))
        conn.execute(text("ALTER TABLE purchases ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP DEFAULT NULL"))
        # Indexes for faster search + filtering
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_khaata_customer_deleted ON khaata(customer_id, deleted_at)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_customers_shop_name ON customers(shop_id, LOWER(name))"))
        conn.commit()
    print("Database ready! (PostgreSQL)")
