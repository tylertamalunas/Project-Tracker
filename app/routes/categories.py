"""Routes for material and tool category management."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services import material_category_service, tool_category_service

categories_bp = Blueprint("categories", __name__)


# ============================================================
# Material Categories
# ============================================================

@categories_bp.route("/categories/materials")
def material_category_list():
    """List all material categories."""
    categories = material_category_service.list_material_categories()
    return render_template("categories/list.html", categories=categories,
                           category_type="Material", base_url="/categories/materials")


@categories_bp.route("/categories/materials/new", methods=["GET", "POST"])
def material_category_create():
    """Create a material category."""
    errors = []
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        try:
            material_category_service.create_material_category(name=name, description=description)
            flash("Material category created.", "success")
            return redirect(url_for("categories.material_category_list"))
        except ValueError as e:
            errors.append(str(e))
        return render_template("categories/form.html", action="Create", category_type="Material",
                               errors=errors, category={"name": name, "description": description},
                               base_url="/categories/materials")

    return render_template("categories/form.html", action="Create", category_type="Material",
                           errors=[], category={}, base_url="/categories/materials")


@categories_bp.route("/categories/materials/<int:cat_id>/edit", methods=["GET", "POST"])
def material_category_edit(cat_id):
    """Edit a material category."""
    cat = material_category_service.get_material_category(cat_id)
    if not cat:
        flash("Category not found.", "danger")
        return redirect(url_for("categories.material_category_list"))

    errors = []
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        try:
            material_category_service.update_material_category(cat_id, name=name, description=description)
            flash("Category updated.", "success")
            return redirect(url_for("categories.material_category_list"))
        except ValueError as e:
            errors.append(str(e))
        return render_template("categories/form.html", action="Edit", category_type="Material",
                               errors=errors, category={"name": name, "description": description},
                               base_url="/categories/materials", cat_id=cat_id)

    return render_template("categories/form.html", action="Edit", category_type="Material",
                           errors=[], category={"name": cat.name, "description": cat.description},
                           base_url="/categories/materials", cat_id=cat_id)


@categories_bp.route("/categories/materials/<int:cat_id>/delete", methods=["POST"])
def material_category_delete(cat_id):
    """Delete a material category."""
    try:
        material_category_service.delete_material_category(cat_id)
        flash("Category deleted.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("categories.material_category_list"))


# ============================================================
# Tool Categories
# ============================================================

@categories_bp.route("/categories/tools")
def tool_category_list():
    """List all tool categories."""
    categories = tool_category_service.list_tool_categories()
    return render_template("categories/list.html", categories=categories,
                           category_type="Tool", base_url="/categories/tools")


@categories_bp.route("/categories/tools/new", methods=["GET", "POST"])
def tool_category_create():
    """Create a tool category."""
    errors = []
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        try:
            tool_category_service.create_tool_category(name=name, description=description)
            flash("Tool category created.", "success")
            return redirect(url_for("categories.tool_category_list"))
        except ValueError as e:
            errors.append(str(e))
        return render_template("categories/form.html", action="Create", category_type="Tool",
                               errors=errors, category={"name": name, "description": description},
                               base_url="/categories/tools")

    return render_template("categories/form.html", action="Create", category_type="Tool",
                           errors=[], category={}, base_url="/categories/tools")


@categories_bp.route("/categories/tools/<int:cat_id>/edit", methods=["GET", "POST"])
def tool_category_edit(cat_id):
    """Edit a tool category."""
    cat = tool_category_service.get_tool_category(cat_id)
    if not cat:
        flash("Category not found.", "danger")
        return redirect(url_for("categories.tool_category_list"))

    errors = []
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        try:
            tool_category_service.update_tool_category(cat_id, name=name, description=description)
            flash("Category updated.", "success")
            return redirect(url_for("categories.tool_category_list"))
        except ValueError as e:
            errors.append(str(e))
        return render_template("categories/form.html", action="Edit", category_type="Tool",
                               errors=errors, category={"name": name, "description": description},
                               base_url="/categories/tools", cat_id=cat_id)

    return render_template("categories/form.html", action="Edit", category_type="Tool",
                           errors=[], category={"name": cat.name, "description": cat.description},
                           base_url="/categories/tools", cat_id=cat_id)


@categories_bp.route("/categories/tools/<int:cat_id>/delete", methods=["POST"])
def tool_category_delete(cat_id):
    """Delete a tool category."""
    try:
        tool_category_service.delete_tool_category(cat_id)
        flash("Category deleted.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("categories.tool_category_list"))
