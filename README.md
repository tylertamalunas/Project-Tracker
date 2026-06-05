# Home Improvement Project Tracker

A local web application for homeowners to track home improvement projects, materials, tools, costs, and receipts.

## Tech Stack

- **Backend:** Python / Flask
- **Frontend:** Jinja2 templates with Bootstrap 5
- **Database:** SQLite (via SQLAlchemy)
- **File Storage:** Local filesystem

## Local Development Setup

### Prerequisites

- **Python 3.10+** (check with `python --version`)
- **pip** (comes with Python)
- **Git** (for cloning)

### 1. Clone the Repository

```bash
git clone https://github.com/tylertamalunas/Project-Tracker.git
cd Project-Tracker
```

### 2. Create a Virtual Environment

Using a virtual environment keeps dependencies isolated from your system Python.

```bash
# Create the virtual environment
python -m venv .venv

# Activate it
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (CMD):
.venv\Scripts\activate.bat
# macOS/Linux:
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt when activated.

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs Flask, Flask-SQLAlchemy, and SQLAlchemy.

### 4. Initialize the Database

The SQLite database (`tracker.db`) is created automatically on first run — no manual setup required. The app factory calls `db.create_all()` which creates all tables if they don't exist.

To start with sample data:

```bash
python seed.py          # Load base catalog (categories, merchants, materials, tools, sample projects)
python seed.py --reset  # Clear everything and re-seed from scratch
python seed_qa.py       # (Optional) Add QA edge-case scenarios for testing
```

**Note:** If you see `OperationalError: no such column`, delete `tracker.db` and re-run. This happens when new columns are added to models without a migration tool (SQLAlchemy doesn't alter existing tables).

### 5. Upload Directory

Media files (receipts, photos, documents) are stored locally in the `uploads/` directory.

- The directory is created automatically on app startup
- Files are organized into project-specific subdirectories: `uploads/<project_id>/<filename>`
- The `uploads/` directory is git-ignored (user content is not committed)
- Max upload size: 16 MB (configurable in `config.py`)
- Accepted file types: PNG, JPG, JPEG, GIF, PDF, DOC, DOCX, TXT

### 6. Run the Application

```bash
python run.py
```

The app starts at **http://localhost:5000** with debug mode enabled.

### Environment Variables (Optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///tracker.db` | Database connection string |
| `UPLOAD_FOLDER` | `./uploads` | Local directory for file uploads |
| `SECRET_KEY` | `dev-secret-key...` | Flask session secret (change for production) |
| `FLASK_ENV` | `development` | `development` or `production` |

## Project Structure

```
Project-Tracker/
├── app/
│   ├── __init__.py          # App factory, DB init, FK enforcement
│   ├── models.py            # SQLAlchemy models (12 tables)
│   ├── routes/              # Flask blueprints (7 route files)
│   ├── services/            # Business logic layer (12 service files)
│   ├── templates/           # Jinja2 HTML templates
│   └── static/css/          # Custom stylesheets
├── tests/                   # All test files
├── uploads/                 # Media file storage (git-ignored)
├── config.py                # App configuration (class-based)
├── run.py                   # Entry point
├── seed.py                  # Base seed data script
├── seed_qa.py              # QA fixture data script
├── schema.sql              # Standalone DDL (reference)
├── requirements.txt         # Python dependencies
├── Instructions/            # Project specs and planning docs
├── memory/                  # Task completion logs
└── tasks/                   # Current task definition
```

## Features (MVP)

- Create, edit, and delete projects
- Track project status (planned → active → completed → reopen)
- Add materials and tools to projects with project-specific pricing
- Compare estimated vs actual costs with variance tracking
- Upload receipts and reference photos (linked to line items)
- Dashboard with global spend summaries and over-budget alerts
- Material and tool catalogs with categories and merchants
- Project hierarchy (parent/child) and related-project links
- Filtering and sorting on all list pages

## Running Tests

Tests are in the `tests/` directory and can be run individually:

```bash
python tests/test_cost_service.py
python tests/test_project_forms.py
python tests/test_media_lifecycle.py
# ... or run all:
python -m pytest tests/ -v  # (if pytest installed)
```
