"""
migrate_sqlite_to_postgres.py — ek baar chalao

Purani dukaan.db (SQLite) ka saara data naye PostgreSQL (Supabase) mein copy karta hai.
Chalane se pehle:
  1. .env mein DATABASE_URL sahi hona chahiye (real password ke saath)
  2. naya database.py (PostgreSQL wala) already daal diya ho
  3. dukaan.db isi folder mein honi chahiye (purani SQLite file)

Chalao:
  python migrate_sqlite_to_postgres.py
"""
import sqlite3
from sqlalchemy import text
from database import setup_database, get_connection

OLD_DB = "dukaan.db"

def migrate():
    # Step 1: naye Postgres mein tables bana lo
    setup_database()

    sqlite_conn = sqlite3.connect(OLD_DB)
    sqlite_conn.row_factory = sqlite3.Row
    cur = sqlite_conn.cursor()

    with get_connection() as pg:
        # ---- shops ----
        shop_id_map = {}
        for row in cur.execute("SELECT * FROM shops"):
            existing = pg.execute(
                text("SELECT shop_id FROM shops WHERE username = :u"),
                {"u": row["username"]}
            ).fetchone()
            if existing:
                shop_id_map[row["shop_id"]] = existing[0]
                continue
            result = pg.execute(
                text("""
                    INSERT INTO shops (username, password, shop_name)
                    VALUES (:u, :p, :s) RETURNING shop_id
                """),
                {"u": row["username"], "p": row["password"], "s": row["shop_name"]}
            )
            new_id = result.fetchone()[0]
            shop_id_map[row["shop_id"]] = new_id
        pg.commit()
        print(f"Shops migrated: {len(shop_id_map)}")

        # ---- customers ----
        customer_id_map = {}
        for row in cur.execute("SELECT * FROM customers"):
            new_shop_id = shop_id_map.get(row["shop_id"])
            if not new_shop_id:
                continue
            result = pg.execute(
                text("""
                    INSERT INTO customers (shop_id, name, phone)
                    VALUES (:shop_id, :name, :phone) RETURNING customer_id
                """),
                {"shop_id": new_shop_id, "name": row["name"], "phone": row["phone"]}
            )
            customer_id_map[row["customer_id"]] = result.fetchone()[0]
        pg.commit()
        print(f"Customers migrated: {len(customer_id_map)}")

        # ---- khaata ----
        count = 0
        for row in cur.execute("SELECT * FROM khaata"):
            new_cid = customer_id_map.get(row["customer_id"])
            if not new_cid:
                continue
            pg.execute(
                text("""
                    INSERT INTO khaata (customer_id, item_name, quantity, price_per_item, total, date)
                    VALUES (:cid, :item, :qty, :price, :total, :date)
                """),
                {"cid": new_cid, "item": row["item_name"], "qty": row["quantity"],
                 "price": row["price_per_item"], "total": row["total"], "date": row["date"]}
            )
            count += 1
        pg.commit()
        print(f"Khaata entries migrated: {count}")

        # ---- purchases ----
        count = 0
        for row in cur.execute("SELECT * FROM purchases"):
            new_shop_id = shop_id_map.get(row["shop_id"])
            if not new_shop_id:
                continue
            pg.execute(
                text("""
                    INSERT INTO purchases (shop_id, supplier_name, item_name, quantity, purchase_rate, total_cost, date)
                    VALUES (:shop_id, :supplier, :item, :qty, :rate, :total, :date)
                """),
                {"shop_id": new_shop_id, "supplier": row["supplier_name"], "item": row["item_name"],
                 "qty": row["quantity"], "rate": row["purchase_rate"], "total": row["total_cost"], "date": row["date"]}
            )
            count += 1
        pg.commit()
        print(f"Purchases migrated: {count}")

        # ---- inventory ----
        count = 0
        for row in cur.execute("SELECT * FROM inventory"):
            new_shop_id = shop_id_map.get(row["shop_id"])
            if not new_shop_id:
                continue
            pg.execute(
                text("""
                    INSERT INTO inventory (shop_id, item_name, category, sale_price, purchase_rate, stock, reorder_level)
                    VALUES (:shop_id, :item, :category, :price, :purchase_rate, :stock, :reorder)
                """),
                {"shop_id": new_shop_id, "item": row["item_name"], "category": row["category"],
                 "price": row["sale_price"], "purchase_rate": row["purchase_rate"],
                 "stock": row["stock"], "reorder": row["reorder_level"]}
            )
            count += 1
        pg.commit()
        print(f"Inventory items migrated: {count}")

    sqlite_conn.close()
    print("\nMigration complete! Ab Supabase mein saara data hai.")
    print("Shop ID mapping (purana -> naya):", shop_id_map)

if __name__ == "__main__":
    migrate()
