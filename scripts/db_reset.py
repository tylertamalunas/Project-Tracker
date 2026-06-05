"""Reset the database for development.

Usage:
    python scripts/db_reset.py           # Reset and seed with base data
    python scripts/db_reset.py --qa      # Reset, seed, and add QA fixtures

WARNING: This destroys all existing data and uploaded files!
"""
import sys
import os
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

app = create_app()
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, "tracker.db")
uploads_path = app.config["UPLOAD_FOLDER"]

# Confirm
print("⚠️  This will DELETE all data and uploaded files!")
print(f"   Database: {db_path}")
print(f"   Uploads:  {uploads_path}")
confirm = input("Continue? [y/N]: ").strip().lower()
if confirm != "y":
    print("Cancelled.")
    sys.exit(0)

# Remove database
if os.path.exists(db_path):
    os.remove(db_path)
    print("  Deleted tracker.db")

# Remove uploads
if os.path.exists(uploads_path):
    shutil.rmtree(uploads_path)
    print("  Deleted uploads/")

# Recreate
print("  Recreating database...")
app = create_app()

# Seed
print("  Running seed.py...")
os.system(f'"{sys.executable}" seed.py')

if "--qa" in sys.argv:
    print("  Running seed_qa.py...")
    os.system(f'"{sys.executable}" seed_qa.py')

print("\n✓ Reset complete. Run 'python run.py' to start.")
