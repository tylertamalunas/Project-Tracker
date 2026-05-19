import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event

db = SQLAlchemy()


def _enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    """Enable foreign key enforcement for every SQLite connection."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()


def create_app(config_name=None):
    """Application factory.

    Args:
        config_name: 'development' or 'production'. Defaults to FLASK_ENV
                     environment variable, falling back to 'development'.
    """
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    from config import config_by_name
    app.config.from_object(config_by_name.get(config_name, config_by_name["development"]))

    # Ensure upload folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize database
    db.init_app(app)

    # Enable SQLite foreign keys on every connection
    with app.app_context():
        event.listen(db.engine, "connect", _enable_sqlite_foreign_keys)

    # Register blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    # Create tables
    with app.app_context():
        from app import models  # noqa: F401
        db.create_all()

    return app
