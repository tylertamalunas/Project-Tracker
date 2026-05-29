from flask import Blueprint, render_template, request
from app.models import Project
from app.services import project_material_service, project_tool_service, project_hierarchy_service

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


@projects_bp.route("/projects/<int:project_id>")
def project_detail(project_id):
    """Show a full view of one project with attached materials and tools."""
    project = Project.query.get_or_404(project_id)
    materials = project_material_service.list_project_materials(project_id)
    tools = project_tool_service.list_project_tools(project_id)
    parent_project = project_hierarchy_service.get_parent_project(project_id)
    child_projects = project_hierarchy_service.get_child_projects(project_id)

    return render_template(
        "projects/detail.html",
        project=project,
        materials=materials,
        tools=tools,
        parent_project=parent_project,
        child_projects=child_projects,
    )
