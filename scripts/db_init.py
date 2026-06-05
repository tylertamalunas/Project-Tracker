"""Initialize the database (create tables without seed data).

Usage:
    python scripts/db_init.py

Creates tracker.db with all tables if it doesn't exist.
Safe to run multiple times — only creates missing tables.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

app = create_app()
print("Database initialized at:", app.config["SQLALCHEMY_DATABASE_URI"])
print("Tables created successfully.")
