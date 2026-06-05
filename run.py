"""Entry point for the Project Tracker application.

Usage:
    python run.py                    # Start with default settings (localhost:5000, debug on)
    FLASK_ENV=production python run.py  # Start in production mode (debug off)
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=app.config.get("DEBUG", False),
    )
