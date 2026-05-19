# Task Summary — 2026-05-19

## Task 1: SQLite Connection Management & App Configuration

### Summary
Set up SQLite connection management and app configuration.

### What Was Done

**`config.py` — Rewritten**
- Converted from flat variables to class-based configuration
- `Config` base class with environment-variable overrides:
  - `DATABASE_URL` — configurable DB path (defaults to `tracker.db` in project root)
  - `UPLOAD_FOLDER` — configurable upload directory (defaults to `./uploads`)
  - `SECRET_KEY` — overridable via env var
  - `MAX_CONTENT_LENGTH` — 16 MB upload limit
- `DevelopmentConfig` — enables `DEBUG = True`
- `ProductionConfig` — sets `DEBUG = False` (future use)
- `config_by_name` dictionary maps environment names to config classes

**`app/__init__.py` — Updated**
- App factory now accepts optional `config_name` parameter
- Defaults to `FLASK_ENV` environment variable, falling back to `"development"`
- Added `_enable_sqlite_foreign_keys` event listener that executes `PRAGMA foreign_keys = ON` on every new SQLite connection
- Loads config via class-based objects instead of flat file

### Acceptance Criteria — All Met
- ✓ Database path is configurable (via `DATABASE_URL` env var)
- ✓ Connection lifecycle handled cleanly (Flask-SQLAlchemy manages sessions per-request)
- ✓ Foreign keys enabled in SQLite (PRAGMA listener on every connection)
- ✓ Development config supports local file uploads and debug mode

---

## Task 2: Create Initial SQL Schema from Approved Mermaid Model

### Summary
Translate the approved ER diagram into SQLite DDL and sync ORM models.

### What Was Done

**`schema.sql` — Created**
- Standalone DDL file with CREATE TABLE statements for all 12 required tables
- Tables from approved ER diagram:
  - `projects`
  - `material_categories`
  - `tool_categories`
  - `merchants`
  - `materials`
  - `tools`
  - `project_materials`
  - `project_tools`
  - `media`
- Tables reserved for future use:
  - `media_links` — polymorphic media associations
  - `project_hierarchy` — sub-project relationships
  - `project_relationships` — linked/related projects
- Includes CHECK constraints (quantity > 0, prices >= 0, status IN list, media_type IN list)
- Foreign keys with ON DELETE CASCADE/RESTRICT/SET NULL as appropriate
- Timestamp defaults using `datetime('now')` (UTC)

**`app/models.py` — Updated**
- Added 3 new SQLAlchemy models: `MediaLink`, `ProjectHierarchy`, `ProjectRelationship`
- ORM now matches DDL 1:1 for all 12 tables

### Acceptance Criteria — All Met
- ✓ CREATE TABLE scripts exist for all 12 tables
- ✓ Data types are SQLite-appropriate (INTEGER, TEXT, REAL)
- ✓ Foreign keys declared with ON DELETE behavior
- ✓ Timestamp defaults handled consistently (UTC throughout)

### Verification
- All 12 tables created successfully via both raw DDL and ORM
- FK enforcement confirmed active (`PRAGMA foreign_keys` = 1)
- CHECK constraints validated (quantity=0 rejected, invalid FK rejected)
- Timestamps auto-populate on insert
