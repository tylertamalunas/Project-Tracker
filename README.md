# Home Improvement Project Tracker

A local web application for homeowners to track home improvement projects, materials, tools, costs, and receipts.

## Features

- Create and manage projects with status tracking (planned → active → completed)
- Add materials and tools with estimated and actual costs
- Compare budgets with variance highlighting (over/under budget)
- Upload receipts and reference photos linked to specific purchases
- Dashboard with global spend summaries and over-budget alerts
- Organize with categories, merchants, project hierarchies, and related projects
- Filter and sort all lists

---

## For Users (Self-Hosting)

Everything you need to run the app on your own computer.

### Requirements

- Python 3.10 or newer ([download here](https://www.python.org/downloads/))

### Setup (One Time)

```bash
# 1. Download the project
git clone https://github.com/tylertamalunas/Project-Tracker.git
cd Project-Tracker

# 2. Install dependencies
pip install -r requirements.txt

# 3. Load sample data (optional, gives you something to explore)
python seed.py
```

### Run the App

```bash
python run.py
```

Open your browser to **http://localhost:5000** — that's it.

### What You Should Know

- **Your data** is stored in `tracker.db` (SQLite file in the project folder). Back this up if you care about your data.
- **Uploaded files** (receipts, photos) are saved in the `uploads/` folder.
- **Accepted file types:** PNG, JPG, GIF, PDF, DOC, DOCX, TXT (max 16 MB each)
- **No account needed** — it's a single-user local app, no login required.
- **To reset everything:** delete `tracker.db` and the `uploads/` folder, then run `python seed.py` if you want sample data again.

---

## For Developers

Technical details for contributing or modifying the app.

### Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python / Flask |
| Frontend | Jinja2 templates, Bootstrap 5 |
| Database | SQLite via SQLAlchemy |
| File Storage | Local filesystem |

### Dev Environment Setup

```bash
# Clone
git clone https://github.com/tylertamalunas/Project-Tracker.git
cd Project-Tracker

# Create virtual environment
python -m venv .venv

# Activate it
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize with seed data
python seed.py --reset
python seed_qa.py        # Optional: adds edge-case test scenarios

# Run
python run.py
```

### Database

- **Auto-created** on first run (`db.create_all()` in the app factory)
- **No migrations tool** — if you add columns to models, delete `tracker.db` and re-seed
- **Foreign keys enforced** via PRAGMA on every connection
- **Schema reference:** see `schema.sql` for the full DDL

### Upload Directory

- Created automatically at startup
- Structure: `uploads/<project_id>/<uuid>_<safe_filename>`
- Git-ignored (user content not committed)
- Configurable via `UPLOAD_FOLDER` environment variable

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///tracker.db` | Database connection string |
| `UPLOAD_FOLDER` | `./uploads` | Local directory for file uploads |
| `SECRET_KEY` | `dev-secret-key...` | Flask session secret |
| `FLASK_ENV` | `development` | `development` or `production` |

### Project Structure

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
├── config.py                # Class-based configuration
├── run.py                   # Entry point
├── seed.py                  # Base seed data
├── seed_qa.py              # QA fixture data
├── schema.sql              # DDL reference
├── requirements.txt         # Python dependencies
├── Instructions/            # Project specs and decisions
├── memory/                  # Task completion logs
└── tasks/                   # Current task definition
```

### Running Tests

```bash
# Individual test file
python tests/test_cost_service.py

# All tests (if pytest installed)
pip install pytest
python -m pytest tests/ -v
```

### Architecture Notes

- **Service layer pattern** — business logic lives in `app/services/`, routes are thin controllers
- **Computed totals** — project costs are calculated dynamically, never stored
- **Polymorphic media links** — `media_links` table uses `entity_type` + `entity_id` to link files to any line item
- **Soft deactivation** — materials/tools have `is_active` flag (inactive items hidden from project forms but preserved in history)
