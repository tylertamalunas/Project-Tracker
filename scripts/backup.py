"""Back up the database and uploaded files.

Usage:
    python scripts/backup.py                # Backup to backups/<timestamp>/
    python scripts/backup.py --dir /path    # Backup to custom directory

Creates a timestamped folder containing:
    - tracker.db (copy of database)
    - uploads/   (copy of all uploaded files)
"""
import sys
import os
import shutil
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, "tracker.db")
uploads_path = os.path.join(base_dir, "uploads")

# Determine backup directory
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
default_backup_dir = os.path.join(base_dir, "backups", timestamp)

backup_dir = default_backup_dir
if "--dir" in sys.argv:
    idx = sys.argv.index("--dir")
    if idx + 1 < len(sys.argv):
        backup_dir = os.path.join(sys.argv[idx + 1], timestamp)

os.makedirs(backup_dir, exist_ok=True)

print(f"Backing up to: {backup_dir}")

# Backup database
if os.path.exists(db_path):
    shutil.copy2(db_path, os.path.join(backup_dir, "tracker.db"))
    size_mb = os.path.getsize(db_path) / (1024 * 1024)
    print(f"  ✓ Database ({size_mb:.2f} MB)")
else:
    print("  ⚠ No database found (tracker.db missing)")

# Backup uploads
if os.path.exists(uploads_path) and os.listdir(uploads_path):
    dest = os.path.join(backup_dir, "uploads")
    shutil.copytree(uploads_path, dest)
    file_count = sum(len(files) for _, _, files in os.walk(dest))
    print(f"  ✓ Uploads ({file_count} files)")
else:
    print("  ⚠ No uploaded files found")

print(f"\n✓ Backup complete: {backup_dir}")
