"""Routes for the global tools catalog."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import ToolCategory, Merchant
from app.services import tool_service

tools_bp = Blueprint("tools", __name__)


@tools_bp.route("/tools")
def tool_list():
    """List all tools with optional filters and sorting."""
    from app.models import Tool
    active_filter = request.args.get("active")
    category_id = request.args.get("category_id", type=int)
    sort_by = request.args.get("sort", "name")
    sort_dir = request.args.get("dir", "asc")

    active_only = None
    if active_filter == "true":
        active_only = True
    elif active_filter == "false":
        active_only = False

    # Build query
    query = Tool.query
    if active_only is True:
        query = query.filter_by(is_active=True)
    elif active_only is False:
        query = query.filter_by(is_active=False)
    if category_id:
        query = query.filter_by(category_id=category_id)

    # Apply sort
    sort_columns = {
        "name": Tool.name,
        "default_price": Tool.default_price,
        "brand": Tool.brand,
        "created_at": Tool.created_at,
    }
    sort_col = sort_columns.get(sort_by, Tool.name)
    if sort_dir == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    tools = query.all()
    categories = ToolCategory.query.order_by(ToolCategory.name).all()

    return render_template(
        "tools/list.html",
        tools=tools,
        categories=categories,
        current_active_filter=active_filter or "all",
        current_category_id=category_id,
        current_sort=sort_by,
        current_dir=sort_dir,
    )


@tools_bp.route("/tools/new", methods=["GET", "POST"])
def tool_create():
    """Create a new tool."""
    errors = []
    categories = ToolCategory.query.order_by(ToolCategory.name).all()
    merchants = Merchant.query.order_by(Merchant.name).all()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        default_price = request.form.get("default_price") or 0
        brand = request.form.get("brand", "").strip()
        model_number = request.form.get("model_number", "").strip()
        category_id = request.form.get("category_id", type=int) or None
        merchant_id = request.form.get("merchant_id", type=int) or None
        notes = request.form.get("notes", "").strip()

        try:
            default_price = float(default_price)
        except (ValueError, TypeError):
            errors.append("Default price must be a number.")
            default_price = 0

        if not errors:
            try:
                tool = tool_service.create_tool(
                    name=name,
                    default_price=default_price,
                    brand=brand,
                    model_number=model_number,
                    category_id=category_id,
                    merchant_id=merchant_id,
                    notes=notes,
                )
                flash("Tool created successfully.", "success")
                return redirect(url_for("tools.tool_list"))
            except ValueError as e:
                errors.append(str(e))

        return render_template(
            "tools/form.html",
            action="Create",
            errors=errors,
            tool={
                "name": name, "default_price": default_price,
                "brand": brand, "model_number": model_number,
                "category_id": category_id, "merchant_id": merchant_id,
                "notes": notes,
            },
            categories=categories,
            merchants=merchants,
        )

    return render_template(
        "tools/form.html",
        action="Create",
        errors=[],
        tool={},
        categories=categories,
        merchants=merchants,
    )


@tools_bp.route("/tools/<int:tool_id>/edit", methods=["GET", "POST"])
def tool_edit(tool_id):
    """Edit an existing tool."""
    tool = tool_service.get_tool(tool_id)
    if not tool:
        flash("Tool not found.", "danger")
        return redirect(url_for("tools.tool_list"))

    errors = []
    categories = ToolCategory.query.order_by(ToolCategory.name).all()
    merchants = Merchant.query.order_by(Merchant.name).all()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        default_price = request.form.get("default_price") or 0
        brand = request.form.get("brand", "").strip()
        model_number = request.form.get("model_number", "").strip()
        category_id = request.form.get("category_id", type=int) or None
        merchant_id = request.form.get("merchant_id", type=int) or None
        notes = request.form.get("notes", "").strip()
        is_active = request.form.get("is_active") == "on"

        try:
            default_price = float(default_price)
        except (ValueError, TypeError):
            errors.append("Default price must be a number.")
            default_price = 0

        if not errors:
            try:
                tool_service.update_tool(
                    tool_id,
                    name=name,
                    default_price=default_price,
                    brand=brand,
                    model_number=model_number,
                    category_id=category_id,
                    merchant_id=merchant_id,
                    notes=notes,
                    is_active=is_active,
                )
                flash("Tool updated successfully.", "success")
                return redirect(url_for("tools.tool_list"))
            except ValueError as e:
                errors.append(str(e))

        return render_template(
            "tools/form.html",
            action="Edit",
            errors=errors,
            tool={
                "name": name, "default_price": default_price,
                "brand": brand, "model_number": model_number,
                "category_id": category_id, "merchant_id": merchant_id,
                "notes": notes, "is_active": is_active,
            },
            categories=categories,
            merchants=merchants,
            tool_id=tool_id,
        )

    return render_template(
        "tools/form.html",
        action="Edit",
        errors=[],
        tool={
            "name": tool.name,
            "default_price": str(tool.default_price),
            "brand": tool.brand,
            "model_number": tool.model_number,
            "category_id": tool.category_id,
            "merchant_id": tool.merchant_id,
            "notes": tool.notes,
            "is_active": tool.is_active,
        },
        categories=categories,
        merchants=merchants,
        tool_id=tool_id,
    )


@tools_bp.route("/tools/<int:tool_id>/delete", methods=["POST"])
def tool_delete(tool_id):
    """Delete a tool from the catalog."""
    from app.models import ProjectTool
    # Check if tool is used in any project
    in_use = ProjectTool.query.filter_by(tool_id=tool_id).count()
    if in_use > 0:
        flash(f"Cannot delete: this tool is used in {in_use} project(s). Remove it from projects first.", "danger")
        return redirect(url_for("tools.tool_list"))

    try:
        tool_service.delete_tool(tool_id)
        flash("Tool deleted.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("tools.tool_list"))
