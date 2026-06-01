from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Project
from app.services import project_service, project_material_service, project_tool_service, project_hierarchy_service, project_relationship_service

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
    related_projects = project_relationship_service.get_related_projects(project_id)

    return render_template(
        "projects/detail.html",
        project=project,
        materials=materials,
        tools=tools,
        parent_project=parent_project,
        child_projects=child_projects,
        related_projects=related_projects,
    )


@projects_bp.route("/projects/new", methods=["GET", "POST"])
def project_create():
    """Create a new project."""
    errors = []

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "planned")
        start_date = request.form.get("start_date") or None
        end_date = request.form.get("end_date") or None
        budget_estimate = request.form.get("budget_estimate") or None
        notes = request.form.get("notes", "").strip()

        # Convert budget to float if provided
        if budget_estimate:
            try:
                budget_estimate = float(budget_estimate)
            except ValueError:
                errors.append("Budget estimate must be a number.")
                budget_estimate = None

        if not errors:
            try:
                project = project_service.create_project(
                    name=name,
                    description=description,
                    status=status,
                    start_date=start_date,
                    end_date=end_date,
                    budget_estimate=budget_estimate,
                    notes=notes,
                )
                flash("Project created successfully.", "success")
                return redirect(url_for("projects.project_detail", project_id=project.id))
            except ValueError as e:
                errors.append(str(e))

        # Re-render form with errors and submitted values
        return render_template(
            "projects/form.html",
            action="Create",
            errors=errors,
            project={
                "name": name,
                "description": description,
                "status": status,
                "start_date": start_date,
                "end_date": end_date,
                "budget_estimate": budget_estimate,
                "notes": notes,
            },
        )

    # GET — empty form
    return render_template(
        "projects/form.html",
        action="Create",
        errors=[],
        project={},
    )


@projects_bp.route("/projects/<int:project_id>/edit", methods=["GET", "POST"])
def project_edit(project_id):
    """Edit an existing project."""
    project = Project.query.get_or_404(project_id)
    errors = []

    # Completed projects cannot be edited (domain rule)
    if project.status == "completed":
        flash("Completed projects are read-only. Change status to 'active' to edit.", "warning")
        return redirect(url_for("projects.project_detail", project_id=project.id))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        status = request.form.get("status", project.status)
        start_date = request.form.get("start_date") or None
        end_date = request.form.get("end_date") or None
        budget_estimate = request.form.get("budget_estimate") or None
        notes = request.form.get("notes", "").strip()

        # Convert budget to float if provided
        if budget_estimate:
            try:
                budget_estimate = float(budget_estimate)
            except ValueError:
                errors.append("Budget estimate must be a number.")
                budget_estimate = None

        if not errors:
            try:
                project_service.update_project(
                    project_id,
                    name=name,
                    description=description,
                    status=status,
                    start_date=start_date,
                    end_date=end_date,
                    budget_estimate=budget_estimate,
                    notes=notes,
                )
                flash("Project updated successfully.", "success")
                return redirect(url_for("projects.project_detail", project_id=project.id))
            except ValueError as e:
                errors.append(str(e))

        # Re-render form with errors
        return render_template(
            "projects/form.html",
            action="Edit",
            errors=errors,
            project={
                "name": name,
                "description": description,
                "status": status,
                "start_date": start_date,
                "end_date": end_date,
                "budget_estimate": budget_estimate,
                "notes": notes,
            },
            project_id=project_id,
        )

    # GET — pre-fill form with existing data
    return render_template(
        "projects/form.html",
        action="Edit",
        errors=[],
        project={
            "name": project.name,
            "description": project.description,
            "status": project.status,
            "start_date": str(project.start_date) if project.start_date else "",
            "end_date": str(project.end_date) if project.end_date else "",
            "budget_estimate": str(project.budget_estimate) if project.budget_estimate else "",
            "notes": project.notes,
        },
        project_id=project_id,
    )
