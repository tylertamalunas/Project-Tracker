from flask import Blueprint, render_template, request
from app.models import Project

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/projects")
def project_list():
    """Show all projects in a table with optional status filter."""
    status_filter = request.args.get("status", "all")

    if status_filter in ("planned", "active", "completed"):
        projects = Project.query.filter_by(status=status_filter).order_by(Project.created_at.desc()).all()
    else:
        projects = Project.query.order_by(Project.created_at.desc()).all()

    return render_template(
        "projects/list.html",
        projects=projects,
        current_filter=status_filter,
    )
