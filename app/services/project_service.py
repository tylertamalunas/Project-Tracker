"""Service layer for Project CRUD operations."""
from datetime import date
from app import db
from app.models import Project


ALLOWED_STATUSES = ("planned", "active", "completed")


def list_projects(status_filter=None):
    """Return all projects, optionally filtered by status.

    Args:
        status_filter: 'planned', 'active', or 'completed'. None returns all.

    Returns:
        List of Project instances ordered by created_at descending.
    """
    query = Project.query.order_by(Project.created_at.desc())
    if status_filter in ALLOWED_STATUSES:
        query = query.filter_by(status=status_filter)
    return query.all()


def get_project(project_id):
    """Get a single project by ID.

    Args:
        project_id: Integer primary key.

    Returns:
        Project instance or None if not found.
    """
    return Project.query.get(project_id)


def create_project(name, description="", status="planned", start_date=None,
                   end_date=None, budget_estimate=None, notes=""):
    """Create a new project.

    Args:
        name: Required project name.
        description: Optional project description.
        status: One of 'planned', 'active', 'completed'. Defaults to 'planned'.
        start_date: Optional date or ISO date string.
        end_date: Optional date or ISO date string.
        budget_estimate: Optional manual budget estimate (decimal).
        notes: Optional free-text notes.

    Returns:
        The newly created Project instance.

    Raises:
        ValueError: If name is empty or status is invalid.
    """
    if not name or not name.strip():
        raise ValueError("Project name is required.")
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of: {ALLOWED_STATUSES}")

    project = Project(
        name=name.strip(),
        description=description or "",
        status=status,
        start_date=_parse_date(start_date),
        end_date=_parse_date(end_date),
        budget_estimate=budget_estimate,
        notes=notes or "",
    )
    db.session.add(project)
    db.session.commit()
    return project


def update_project(project_id, **kwargs):
    """Update an existing project.

    Args:
        project_id: Integer primary key.
        **kwargs: Fields to update. Supported: name, description, status,
                  start_date, end_date, budget_estimate, notes.

    Returns:
        The updated Project instance.

    Raises:
        ValueError: If project not found, name is empty, or status is invalid.
    """
    project = Project.query.get(project_id)
    if not project:
        raise ValueError(f"Project with id {project_id} not found.")

    if "name" in kwargs:
        if not kwargs["name"] or not kwargs["name"].strip():
            raise ValueError("Project name is required.")
        project.name = kwargs["name"].strip()

    if "description" in kwargs:
        project.description = kwargs["description"] or ""

    if "status" in kwargs:
        if kwargs["status"] not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid status '{kwargs['status']}'. Must be one of: {ALLOWED_STATUSES}")
        project.status = kwargs["status"]

    if "start_date" in kwargs:
        project.start_date = _parse_date(kwargs["start_date"])

    if "end_date" in kwargs:
        project.end_date = _parse_date(kwargs["end_date"])

    if "budget_estimate" in kwargs:
        project.budget_estimate = kwargs["budget_estimate"]

    if "notes" in kwargs:
        project.notes = kwargs["notes"] or ""

    db.session.commit()
    return project


def delete_project(project_id):
    """Delete a project by ID.

    Args:
        project_id: Integer primary key.

    Returns:
        True if deleted successfully.

    Raises:
        ValueError: If project not found.
    """
    project = Project.query.get(project_id)
    if not project:
        raise ValueError(f"Project with id {project_id} not found.")

    db.session.delete(project)
    db.session.commit()
    return True


def _parse_date(value):
    """Convert a value to a date object, or None.

    Accepts: None, date instance, or ISO format string (YYYY-MM-DD).
    """
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    return None
