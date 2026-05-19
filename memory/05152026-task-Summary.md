# Task Complete: Project List Page

## Date
2026-05-15

## Task
Build the project list page (`/projects`).

## What Was Done

Scaffolded the foundational Flask app and implemented the project list page.

### Files Created

| File | Purpose |
|------|---------|
| `requirements.txt` | Python dependencies: flask, flask-sqlalchemy, sqlalchemy |
| `config.py` | App config — SQLite DB path, upload folder, secret key |
| `run.py` | Entry point — `python run.py` starts the dev server on port 5000 |
| `app/__init__.py` | Flask app factory, DB init, blueprint registration |
| `app/models.py` | All 9 SQLAlchemy models matching the ER diagram |
| `app/routes/__init__.py` | Blueprint registration helper |
| `app/routes/projects.py` | `/projects` route with optional status filter |
| `app/templates/base.html` | Bootstrap 5 layout with top nav |
| `app/templates/projects/list.html` | Project list table |

### Models Created

- Project (with computed `estimated_total`, `actual_total`, `variance`)
- MaterialCategory
- ToolCategory
- Merchant
- Material
- Tool
- ProjectMaterial
- ProjectTool
- Media

### Features Implemented

- Project list table showing: name, status badge, created date, estimated total, actual total, variance
- Status filter buttons (All / Planned / Active / Completed)
- "New Project" button linking to `/projects/new`
- "View" link per project to `/projects/<id>`
- "Edit" link per project (hidden for completed projects)
- Empty state message when no projects exist
- Color-coded variance (red = over budget, green = under budget)
- Completed status shows green badge per domain decisions

### Acceptance Criteria — All Met

- ✓ Shows all projects in a table
- ✓ Displays name, status, estimated total, actual total
- ✓ Link to create a new project
- ✓ Link to view each project
- ✓ Uses database models
- ✓ No authentication

## How to Run

```bash
pip install -r requirements.txt
python run.py
```

Visit `http://localhost:5000/projects`

## Lines of Code Written

**284 total lines** across 9 files:

- `requirements.txt` — 3 lines
- `config.py` — 6 lines
- `run.py` — 4 lines
- `app/__init__.py` — 18 lines
- `app/models.py` — 138 lines
- `app/routes/__init__.py` — 3 lines
- `app/routes/projects.py` — 16 lines
- `app/templates/base.html` — 26 lines
- `app/templates/projects/list.html` — 70 lines

## Notes

- Database file (`tracker.db`) is auto-created on first run
- Cost totals are computed dynamically from join tables, not stored
- Tools marked `already_owned` contribute zero to cost calculations
- The `/projects/new` and `/projects/<id>/edit` routes are linked but not yet implemented
