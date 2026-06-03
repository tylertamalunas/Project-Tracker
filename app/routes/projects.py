from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import Project
from app.services import project_service, project_material_service, project_tool_service, project_hierarchy_service, project_relationship_service

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/projects")
def project_list():
    """Show all projects with optional status filter and sorting."""
    status_filter = request.args.get("status", "all")
    sort_by = request.args.get("sort", "updated_at")
    sort_dir = request.args.get("dir", "desc")

    # Build query
    query = Project.query
    if status_filter in ("planned", "active", "completed"):
        query = query.filter_by(status=status_filter)

    # Apply sort
    sort_columns = {
        "name": Project.name,
        "status": Project.status,
        "start_date": Project.start_date,
        "created_at": Project.created_at,
        "updated_at": Project.updated_at,
    }
    sort_col = sort_columns.get(sort_by, Project.updated_at)
    if sort_dir == "asc":
        query = query.order_by(sort_col.asc())
    else:
        query = query.order_by(sort_col.desc())

    projects = query.all()

    return render_template(
        "projects/list.html",
        projects=projects,
        current_filter=status_filter,
        current_sort=sort_by,
        current_dir=sort_dir,
    )


@projects_bp.route("/projects/<int:project_id>")
def project_detail(project_id):
    """Show a full view of one project with attached materials and tools."""
    from app.services import media_link_service

    project = Project.query.get_or_404(project_id)
    materials = project_material_service.list_project_materials(project_id)
    tools = project_tool_service.list_project_tools(project_id)
    parent_project = project_hierarchy_service.get_parent_project(project_id)
    child_projects = project_hierarchy_service.get_child_projects(project_id)
    related_projects = project_relationship_service.get_related_projects(project_id)

    # Build media links lookup: {entity_type}_{entity_id} -> [Media]
    material_media = {}
    for pm in materials:
        material_media[pm.id] = media_link_service.get_media_for_entity("project_material", pm.id)
    tool_media = {}
    for pt in tools:
        tool_media[pt.id] = media_link_service.get_media_for_entity("project_tool", pt.id)

    return render_template(
        "projects/detail.html",
        project=project,
        materials=materials,
        tools=tools,
        parent_project=parent_project,
        child_projects=child_projects,
        related_projects=related_projects,
        material_media=material_media,
        tool_media=tool_media,
    )


@projects_bp.route("/projects/new", methods=["GET", "POST"])
def project_create():
    """Create a new project."""
    from app.services.validators import validate_required, validate_price, validate_date, validate_choice
    errors = []

    if request.method == "POST":
        name = request.form.get("name", "")
        description = request.form.get("description", "").strip()
        status = request.form.get("status", "planned")
        start_date_raw = request.form.get("start_date") or None
        end_date_raw = request.form.get("end_date") or None
        budget_raw = request.form.get("budget_estimate") or None
        notes = request.form.get("notes", "").strip()

        # Validate
        name = validate_required(name, "Project name", errors)
        status = validate_choice(status, "Status", ("planned", "active", "completed"), errors)
        start_date = validate_date(start_date_raw, "Start date", errors)
        end_date = validate_date(end_date_raw, "End date", errors)
        budget_estimate = validate_price(budget_raw, "Budget estimate", errors)

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

        return render_template(
            "projects/form.html",
            action="Create",
            errors=errors,
            project={
                "name": name or "",
                "description": description,
                "status": status or "planned",
                "start_date": start_date_raw,
                "end_date": end_date_raw,
                "budget_estimate": budget_raw,
                "notes": notes,
            },
        )

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


# ============================================================
# Project-Material Forms
# ============================================================

@projects_bp.route("/projects/<int:project_id>/materials/new", methods=["GET", "POST"])
def project_material_add(project_id):
    """Add a material to a project."""
    from app.models import Material, Merchant
    project = Project.query.get_or_404(project_id)

    if project.status == "completed":
        flash("Cannot add materials to a completed project.", "warning")
        return redirect(url_for("projects.project_detail", project_id=project_id))

    errors = []
    materials = Material.query.filter_by(is_active=True).order_by(Material.name).all()
    merchants = Merchant.query.order_by(Merchant.name).all()

    if request.method == "POST":
        from app.services.validators import validate_required, validate_positive_int, validate_price, validate_date

        material_id = request.form.get("material_id", type=int)
        quantity_raw = request.form.get("quantity", "")
        unit_of_measure = request.form.get("unit_of_measure", "").strip()
        est_raw = request.form.get("estimated_unit_price", "")
        act_raw = request.form.get("actual_unit_price", "")
        merchant_id = request.form.get("merchant_id", type=int) or None
        purchased_on_raw = request.form.get("purchased_on", "")
        notes = request.form.get("notes", "").strip()

        if not material_id:
            errors.append("Please select a material.")
        quantity = validate_positive_int(quantity_raw, "Quantity", errors)
        estimated_unit_price = validate_price(est_raw, "Estimated unit price", errors, allow_none=False)
        actual_unit_price = validate_price(act_raw, "Actual unit price", errors, allow_none=True)
        purchased_on = validate_date(purchased_on_raw, "Purchase date", errors)

        if not errors:
            try:
                project_material_service.add_material_to_project(
                    project_id=project_id,
                    material_id=material_id,
                    quantity=quantity,
                    unit_of_measure=unit_of_measure,
                    estimated_unit_price=estimated_unit_price,
                    actual_unit_price=actual_unit_price,
                    merchant_id=merchant_id,
                    purchased_on=purchased_on,
                    notes=notes,
                )
                flash("Material added to project.", "success")
                return redirect(url_for("projects.project_detail", project_id=project_id))
            except ValueError as e:
                errors.append(str(e))

        return render_template("projects/material_form.html", action="Add",
                               project=project, errors=errors, materials=materials, merchants=merchants,
                               form_data=request.form)

    return render_template("projects/material_form.html", action="Add",
                           project=project, errors=[], materials=materials, merchants=merchants,
                           form_data={})


@projects_bp.route("/projects/<int:project_id>/materials/<int:pm_id>/edit", methods=["GET", "POST"])
def project_material_edit(project_id, pm_id):
    """Edit a project-material record."""
    from app.models import Material, Merchant
    project = Project.query.get_or_404(project_id)
    pm = project_material_service.get_project_material(pm_id)

    if not pm or pm.project_id != project_id:
        flash("Record not found.", "danger")
        return redirect(url_for("projects.project_detail", project_id=project_id))

    if project.status == "completed":
        flash("Cannot edit materials on a completed project.", "warning")
        return redirect(url_for("projects.project_detail", project_id=project_id))

    errors = []
    materials = Material.query.filter_by(is_active=True).order_by(Material.name).all()
    merchants = Merchant.query.order_by(Merchant.name).all()

    if request.method == "POST":
        quantity = request.form.get("quantity", type=int) or 0
        unit_of_measure = request.form.get("unit_of_measure", "").strip()
        estimated_unit_price = request.form.get("estimated_unit_price") or 0
        actual_unit_price = request.form.get("actual_unit_price") or None
        merchant_id = request.form.get("merchant_id", type=int) or None
        purchased_on = request.form.get("purchased_on") or None
        notes = request.form.get("notes", "").strip()

        try:
            estimated_unit_price = float(estimated_unit_price)
        except (ValueError, TypeError):
            errors.append("Estimated price must be a number.")
            estimated_unit_price = 0

        if actual_unit_price:
            try:
                actual_unit_price = float(actual_unit_price)
            except (ValueError, TypeError):
                errors.append("Actual price must be a number.")
                actual_unit_price = None

        if not errors:
            try:
                project_material_service.update_project_material(
                    pm_id,
                    quantity=quantity,
                    unit_of_measure=unit_of_measure,
                    estimated_unit_price=estimated_unit_price,
                    actual_unit_price=actual_unit_price,
                    merchant_id=merchant_id,
                    purchased_on=purchased_on,
                    notes=notes,
                )
                flash("Material updated.", "success")
                return redirect(url_for("projects.project_detail", project_id=project_id))
            except ValueError as e:
                errors.append(str(e))

        return render_template("projects/material_form.html", action="Edit",
                               project=project, errors=errors, materials=materials, merchants=merchants,
                               form_data=request.form, pm=pm)

    return render_template("projects/material_form.html", action="Edit",
                           project=project, errors=[], materials=materials, merchants=merchants,
                           form_data={
                               "material_id": pm.material_id,
                               "quantity": pm.quantity,
                               "unit_of_measure": pm.unit_of_measure,
                               "estimated_unit_price": str(pm.estimated_unit_price),
                               "actual_unit_price": str(pm.actual_unit_price) if pm.actual_unit_price else "",
                               "merchant_id": pm.merchant_id,
                               "purchased_on": pm.purchased_on.strftime("%Y-%m-%d") if pm.purchased_on else "",
                               "notes": pm.notes,
                           }, pm=pm)


@projects_bp.route("/projects/<int:project_id>/materials/<int:pm_id>/delete", methods=["POST"])
def project_material_delete(project_id, pm_id):
    """Remove a material from a project."""
    try:
        project_material_service.remove_material_from_project(pm_id)
        flash("Material removed.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("projects.project_detail", project_id=project_id))


# ============================================================
# Project-Tool Forms
# ============================================================

@projects_bp.route("/projects/<int:project_id>/tools/new", methods=["GET", "POST"])
def project_tool_add(project_id):
    """Add a tool to a project."""
    from app.models import Tool, Merchant
    project = Project.query.get_or_404(project_id)

    if project.status == "completed":
        flash("Cannot add tools to a completed project.", "warning")
        return redirect(url_for("projects.project_detail", project_id=project_id))

    errors = []
    tools = Tool.query.filter_by(is_active=True).order_by(Tool.name).all()
    merchants = Merchant.query.order_by(Merchant.name).all()

    if request.method == "POST":
        tool_id = request.form.get("tool_id", type=int)
        quantity = request.form.get("quantity", type=int) or 1
        already_owned = request.form.get("already_owned") == "on"
        estimated_unit_price = request.form.get("estimated_unit_price") or 0
        actual_unit_price = request.form.get("actual_unit_price") or None
        merchant_id = request.form.get("merchant_id", type=int) or None
        purchased_on = request.form.get("purchased_on") or None
        notes = request.form.get("notes", "").strip()

        try:
            estimated_unit_price = float(estimated_unit_price)
        except (ValueError, TypeError):
            errors.append("Estimated price must be a number.")
            estimated_unit_price = 0

        if actual_unit_price:
            try:
                actual_unit_price = float(actual_unit_price)
            except (ValueError, TypeError):
                errors.append("Actual price must be a number.")
                actual_unit_price = None

        if not errors:
            try:
                project_tool_service.add_tool_to_project(
                    project_id=project_id,
                    tool_id=tool_id,
                    quantity=quantity,
                    already_owned=already_owned,
                    estimated_unit_price=estimated_unit_price,
                    actual_unit_price=actual_unit_price,
                    merchant_id=merchant_id,
                    purchased_on=purchased_on,
                    notes=notes,
                )
                flash("Tool added to project.", "success")
                return redirect(url_for("projects.project_detail", project_id=project_id))
            except ValueError as e:
                errors.append(str(e))

        return render_template("projects/tool_form.html", action="Add",
                               project=project, errors=errors, tools=tools, merchants=merchants,
                               form_data=request.form)

    return render_template("projects/tool_form.html", action="Add",
                           project=project, errors=[], tools=tools, merchants=merchants,
                           form_data={})


@projects_bp.route("/projects/<int:project_id>/tools/<int:pt_id>/edit", methods=["GET", "POST"])
def project_tool_edit(project_id, pt_id):
    """Edit a project-tool record."""
    from app.models import Tool, Merchant
    project = Project.query.get_or_404(project_id)
    pt = project_tool_service.get_project_tool(pt_id)

    if not pt or pt.project_id != project_id:
        flash("Record not found.", "danger")
        return redirect(url_for("projects.project_detail", project_id=project_id))

    if project.status == "completed":
        flash("Cannot edit tools on a completed project.", "warning")
        return redirect(url_for("projects.project_detail", project_id=project_id))

    errors = []
    tools = Tool.query.filter_by(is_active=True).order_by(Tool.name).all()
    merchants = Merchant.query.order_by(Merchant.name).all()

    if request.method == "POST":
        quantity = request.form.get("quantity", type=int) or 1
        already_owned = request.form.get("already_owned") == "on"
        estimated_unit_price = request.form.get("estimated_unit_price") or 0
        actual_unit_price = request.form.get("actual_unit_price") or None
        merchant_id = request.form.get("merchant_id", type=int) or None
        purchased_on = request.form.get("purchased_on") or None
        notes = request.form.get("notes", "").strip()

        try:
            estimated_unit_price = float(estimated_unit_price)
        except (ValueError, TypeError):
            errors.append("Estimated price must be a number.")
            estimated_unit_price = 0

        if actual_unit_price:
            try:
                actual_unit_price = float(actual_unit_price)
            except (ValueError, TypeError):
                errors.append("Actual price must be a number.")
                actual_unit_price = None

        if not errors:
            try:
                project_tool_service.update_project_tool(
                    pt_id,
                    quantity=quantity,
                    already_owned=already_owned,
                    estimated_unit_price=estimated_unit_price,
                    actual_unit_price=actual_unit_price,
                    merchant_id=merchant_id,
                    purchased_on=purchased_on,
                    notes=notes,
                )
                flash("Tool updated.", "success")
                return redirect(url_for("projects.project_detail", project_id=project_id))
            except ValueError as e:
                errors.append(str(e))

        return render_template("projects/tool_form.html", action="Edit",
                               project=project, errors=errors, tools=tools, merchants=merchants,
                               form_data=request.form, pt=pt)

    return render_template("projects/tool_form.html", action="Edit",
                           project=project, errors=[], tools=tools, merchants=merchants,
                           form_data={
                               "tool_id": pt.tool_id,
                               "quantity": pt.quantity,
                               "already_owned": pt.already_owned,
                               "estimated_unit_price": str(pt.estimated_unit_price),
                               "actual_unit_price": str(pt.actual_unit_price) if pt.actual_unit_price else "",
                               "merchant_id": pt.merchant_id,
                               "purchased_on": pt.purchased_on.strftime("%Y-%m-%d") if pt.purchased_on else "",
                               "notes": pt.notes,
                           }, pt=pt)


@projects_bp.route("/projects/<int:project_id>/tools/<int:pt_id>/delete", methods=["POST"])
def project_tool_delete(project_id, pt_id):
    """Remove a tool from a project."""
    try:
        project_tool_service.remove_tool_from_project(pt_id)
        flash("Tool removed.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("projects.project_detail", project_id=project_id))
