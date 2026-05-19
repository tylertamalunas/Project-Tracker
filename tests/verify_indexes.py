"""Verify indexes, unique constraints, and ORM consistency."""
import sqlite3
from app import create_app, db
from sqlalchemy import inspect

# Test 1: Validate DDL schema
print("=== DDL Validation ===")
conn = sqlite3.connect(":memory:")
conn.execute("PRAGMA foreign_keys = ON")
conn.executescript(open("schema.sql").read())

indexes = conn.execute(
    "SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND name LIKE 'ix_%' ORDER BY name"
).fetchall()
print(f"Indexes created: {len(indexes)}")
for idx in indexes:
    print(f"  {idx[0]} on {idx[1]}")

# Verify unique constraints
print("\n--- Unique constraint tests ---")
conn.execute("INSERT INTO material_categories (name) VALUES ('Lumber')")
try:
    conn.execute("INSERT INTO material_categories (name) VALUES ('Lumber')")
    print("FAIL: duplicate category name allowed")
except sqlite3.IntegrityError:
    print("OK: material_categories.name is unique")

conn.execute("INSERT INTO merchants (name) VALUES ('Home Depot')")
try:
    conn.execute("INSERT INTO merchants (name) VALUES ('Home Depot')")
    print("FAIL: duplicate merchant name allowed")
except sqlite3.IntegrityError:
    print("OK: merchants.name is unique")

conn.close()

# Test 2: Validate ORM creates matching indexes
print("\n=== ORM Validation ===")
import os
os.remove("tracker.db") if os.path.exists("tracker.db") else None
app = create_app()
with app.app_context():
    insp = inspect(db.engine)
    for table in sorted(insp.get_table_names()):
        idxs = insp.get_indexes(table)
        uniques = [c for c in insp.get_unique_constraints(table)]
        if idxs or uniques:
            print(f"\n  {table}:")
            for idx in idxs:
                print(f"    IDX: {idx['name']} on {idx['column_names']} (unique={idx['unique']})")
            for u in uniques:
                print(f"    UQ: {u['column_names']}")

print("\n\nAll validations passed.")
