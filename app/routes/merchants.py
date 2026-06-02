"""Routes for merchant management."""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services import merchant_service

merchants_bp = Blueprint("merchants", __name__)


@merchants_bp.route("/merchants")
def merchant_list():
    """List all merchants."""
    name_filter = request.args.get("q")
    merchants = merchant_service.list_merchants(name_filter=name_filter)
    return render_template("merchants/list.html", merchants=merchants, query=name_filter or "")


@merchants_bp.route("/merchants/new", methods=["GET", "POST"])
def merchant_create():
    """Create a new merchant."""
    errors = []
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        website = request.form.get("website", "").strip()
        notes = request.form.get("notes", "").strip()

        try:
            merchant_service.create_merchant(name=name, website=website, notes=notes)
            flash("Merchant created.", "success")
            return redirect(url_for("merchants.merchant_list"))
        except ValueError as e:
            errors.append(str(e))

        return render_template("merchants/form.html", action="Create", errors=errors,
                               merchant={"name": name, "website": website, "notes": notes})

    return render_template("merchants/form.html", action="Create", errors=[], merchant={})


@merchants_bp.route("/merchants/<int:merchant_id>/edit", methods=["GET", "POST"])
def merchant_edit(merchant_id):
    """Edit a merchant."""
    merchant = merchant_service.get_merchant(merchant_id)
    if not merchant:
        flash("Merchant not found.", "danger")
        return redirect(url_for("merchants.merchant_list"))

    errors = []
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        website = request.form.get("website", "").strip()
        notes = request.form.get("notes", "").strip()

        try:
            merchant_service.update_merchant(merchant_id, name=name, website=website, notes=notes)
            flash("Merchant updated.", "success")
            return redirect(url_for("merchants.merchant_list"))
        except ValueError as e:
            errors.append(str(e))

        return render_template("merchants/form.html", action="Edit", errors=errors,
                               merchant={"name": name, "website": website, "notes": notes},
                               merchant_id=merchant_id)

    return render_template("merchants/form.html", action="Edit", errors=[],
                           merchant={"name": merchant.name, "website": merchant.website, "notes": merchant.notes},
                           merchant_id=merchant_id)


@merchants_bp.route("/merchants/<int:merchant_id>/delete", methods=["POST"])
def merchant_delete(merchant_id):
    """Delete a merchant."""
    try:
        merchant_service.delete_merchant(merchant_id)
        flash("Merchant deleted.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("merchants.merchant_list"))
