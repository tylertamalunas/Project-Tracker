# Home Improvement Project Tracker

A local web application for homeowners to track home improvement projects, materials, tools, costs, and receipts.

## Tech Stack

- **Backend:** Python / Flask
- **Frontend:** Jinja2 templates with Bootstrap 5
- **Database:** SQLite (via SQLAlchemy)
- **File Storage:** Local filesystem

## Local Setup

### Prerequisites

- Python 3.10+

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
python run.py
```

The app starts at **http://localhost:5000**.

### Project Structure

```
Python-Project-Tracker/
├── app/
│   ├── __init__.py          # App factory, DB init
│   ├── models.py            # SQLAlchemy models
│   ├── routes/              # Flask blueprints
│   ├── services/            # Business logic layer
│   ├── templates/           # Jinja2 HTML templates
│   └── static/css/          # Stylesheets
├── uploads/                 # Media file storage
├── config.py                # App configuration
├── run.py                   # Entry point
├── requirements.txt         # Python dependencies
├── Instructions/            # All project specs, planning docs, and decisions
├── memory/                  # Task logs and decisions
└── tasks/                   # Current task definition
```

### Database

SQLite database (`tracker.db`) is created automatically on first run. No manual setup required.

### Load Seed Data

```bash
python seed.py          # Insert sample categories, merchants, materials, and tools
python seed.py --reset  # Clear catalog data and re-seed from scratch
python seed_qa.py       # Add QA fixture data (run after seed.py)
```

## Features (MVP)

- Create, edit, and delete projects
- Track project status (planned → active → completed)
- Add materials and tools to projects
- Compare estimated vs actual costs
- Upload receipts and reference photos
- Dashboard with spend summaries
