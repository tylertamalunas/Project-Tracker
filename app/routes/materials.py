"""Routes for the global materials catalog."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models import MaterialCategory, Merchant
from app.services import material_service

materials_bp = Blueprint("materials", __name__)


@materials_bp.route("/materials")
def material_list():
    """List all materials with optional filters."""
    active_filter = request.args.get("active")
    category_id = request.args.get("category_id", type=int)

    # Convert active filter
    active_only = None
    if active_filter == "true":
        active_only = True
    elif active_filter == "false":
        active_only = False

    materials = material_service.list_materials(active_only=active_only, category_id=category_id)
    categories = MaterialCategory.query.order_by(MaterialCategory.name).all()

    return render_template(
        "materials/list.html",
        materials=materials,
        categories=categories,
        current_active_filter=active_filter or "all",
        current_category_id=category_id,
    )


@materials_bp.route("/materials/new", methods=["GET", "POST"])
def material_create():
    """Create a new material."""
    errors = []
    categories = MaterialCategory.query.order_by(MaterialCategory.name).all()
    merchants = Merchant.query.order_by(Merchant.name).all()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        default_price = request.form.get("default_price") or 0
        unit_of_measure = request.form.get("unit_of_measure", "").strip()
        sku = request.form.get("sku", "").strip()
        brand = request.form.get("brand", "").strip()
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
                material = material_service.create_material(
                    name=name,
                    default_price=default_price,
                    unit_of_measure=unit_of_measure,
                    sku=sku,
                    brand=brand,
                    category_id=category_id,
                    merchant_id=merchant_id,
                    notes=notes,
                )
                flash("Material created successfully.", "success")
                return redirect(url_for("materials.material_list"))
            except ValueError as e:
                errors.append(str(e))

        return render_template(
            "materials/form.html",
            action="Create",
            errors=errors,
            material={
                "name": name, "default_price": default_price,
                "unit_of_measure": unit_of_measure, "sku": sku,
                "brand": brand, "category_id": category_id,
                "merchant_id": merchant_id, "notes": notes,
            },
            categories=categories,
            merchants=merchants,
        )

    return render_template(
        "materials/form.html",
        action="Create",
        errors=[],
        material={},
        categories=categories,
        merchants=merchants,
    )


@materials_bp.route("/materials/<int:material_id>/edit", methods=["GET", "POST"])
def material_edit(material_id):
    """Edit an existing material."""
    material = material_service.get_material(material_id)
    if not material:
        flash("Material not found.", "danger")
        return redirect(url_for("materials.material_list"))

    errors = []
    categories = MaterialCategory.query.order_by(MaterialCategory.name).all()
    merchants = Merchant.query.order_by(Merchant.name).all()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        default_price = request.form.get("default_price") or 0
        unit_of_measure = request.form.get("unit_of_measure", "").strip()
        sku = request.form.get("sku", "").strip()
        brand = request.form.get("brand", "").strip()
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
                material_service.update_material(
                    material_id,
                    name=name,
                    default_price=default_price,
                    unit_of_measure=unit_of_measure,
                    sku=sku,
                    brand=brand,
                    category_id=category_id,
                    merchant_id=merchant_id,
                    notes=notes,
                    is_active=is_active,
                )
                flash("Material updated successfully.", "success")
                return redirect(url_for("materials.material_list"))
            except ValueError as e:
                errors.append(str(e))

        return render_template(
            "materials/form.html",
            action="Edit",
            errors=errors,
            material={
                "name": name, "default_price": default_price,
                "unit_of_measure": unit_of_measure, "sku": sku,
                "brand": brand, "category_id": category_id,
                "merchant_id": merchant_id, "notes": notes,
                "is_active": is_active,
            },
            categories=categories,
            merchants=merchants,
            material_id=material_id,
        )

    return render_template(
        "materials/form.html",
        action="Edit",
        errors=[],
        material={
            "name": material.name,
            "default_price": str(material.default_price),
            "unit_of_measure": material.unit_of_measure,
            "sku": material.sku,
            "brand": material.brand,
            "category_id": material.category_id,
            "merchant_id": material.merchant_id,
            "notes": material.notes,
            "is_active": material.is_active,
        },
        categories=categories,
        merchants=merchants,
        material_id=material_id,
    )
