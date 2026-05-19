"""Quick ORM index check using in-memory DB."""
import os
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from sqlalchemy import text

app = create_app()
with app.app_context():
    rows = db.session.execute(
        text("SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite%' ORDER BY name")
    ).fetchall()
    print(f"Indexes: {len(rows)}")
    for r in rows:
        print(f"  {r[0]} on {r[1]}")
