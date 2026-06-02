"""Tests for material catalog pages and forms."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import Material, MaterialCategory, Merchant


def setup_app():
    """Create app with sample data."""
    app = create_app()
    ctx = app.app_context()
    ctx.push()

    cat = MaterialCategory(name="Lumber")
    merchant = Merchant(name="Home Depot")
    db.session.add_all([cat, merchant])
    db.session.commit()

    mat = Material(name="2x4", default_price=4.00, unit_of_measure="each",
                   category_id=cat.id, merchant_id=merchant.id, is_active=True)
    inactive = Material(name="Old Plywood", default_price=30.00, is_active=False)
    db.session.add_all([mat, inactive])
    db.session.commit()

    return app, ctx, cat, merchant, mat


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def test_material_list_page():
    app, ctx, cat, merchant, mat = setup_app()
    try:
        client = app.test_client()
        r = client.get("/materials")
        html = r.data.decode()

        assert r.status_code == 200
        assert "2x4" in html
        assert "Old Plywood" in html
        assert "Lumber" in html
        assert "Home Depot" in html
        print("PASS: test_material_list_page")
    finally:
        teardown(ctx)


def test_material_list_filter_active():
    app, ctx, cat, merchant, mat = setup_app()
    try:
        client = app.test_client()
        r = client.get("/materials?active=true")
        html = r.data.decode()

        assert "2x4" in html
        assert "Old Plywood" not in html
        print("PASS: test_material_list_filter_active")
    finally:
        teardown(ctx)


def test_material_list_filter_category():
    app, ctx, cat, merchant, mat = setup_app()
    try:
        client = app.test_client()
        r = client.get(f"/materials?category_id={cat.id}")
        html = r.data.decode()

        assert "2x4" in html
        assert "Old Plywood" not in html
        print("PASS: test_material_list_filter_category")
    finally:
        teardown(ctx)


def test_create_material_form():
    app, ctx, cat, merchant, mat = setup_app()
    try:
        client = app.test_client()
        r = client.get("/materials/new")
        html = r.data.decode()

        assert r.status_code == 200
        assert "Create Material" in html
        assert "Lumber" in html       # category dropdown
        assert "Home Depot" in html   # merchant dropdown
        print("PASS: test_create_material_form")
    finally:
        teardown(ctx)


def test_create_material_success():
    app, ctx, cat, merchant, mat = setup_app()
    try:
        client = app.test_client()
        r = client.post("/materials/new", data={
            "name": "New Material",
            "default_price": "5.50",
            "unit_of_measure": "sqft",
            "category_id": str(cat.id),
            "merchant_id": str(merchant.id),
            "notes": "Test notes",
        }, follow_redirects=False)

        assert r.status_code == 302
        m = Material.query.filter_by(name="New Material").first()
        assert m is not None
        assert float(m.default_price) == 5.50
        assert m.unit_of_measure == "sqft"
        print("PASS: test_create_material_success")
    finally:
        teardown(ctx)


def test_create_material_validation():
    app, ctx, cat, merchant, mat = setup_app()
    try:
        client = app.test_client()
        r = client.post("/materials/new", data={"name": ""})
        html = r.data.decode()

        assert r.status_code == 200
        assert "error" in html.lower() or "required" in html.lower()
        print("PASS: test_create_material_validation")
    finally:
        teardown(ctx)


def test_edit_material_form():
    app, ctx, cat, merchant, mat = setup_app()
    try:
        client = app.test_client()
        r = client.get(f"/materials/{mat.id}/edit")
        html = r.data.decode()

        assert r.status_code == 200
        assert "Edit" in html
        assert "2x4" in html
        print("PASS: test_edit_material_form")
    finally:
        teardown(ctx)


def test_edit_material_success():
    app, ctx, cat, merchant, mat = setup_app()
    try:
        client = app.test_client()
        r = client.post(f"/materials/{mat.id}/edit", data={
            "name": "Updated 2x4",
            "default_price": "4.50",
            "unit_of_measure": "each",
            "is_active": "on",
        }, follow_redirects=False)

        assert r.status_code == 302
        db.session.refresh(mat)
        assert mat.name == "Updated 2x4"
        assert float(mat.default_price) == 4.50
        print("PASS: test_edit_material_success")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_material_list_page()
    test_material_list_filter_active()
    test_material_list_filter_category()
    test_create_material_form()
    test_create_material_success()
    test_create_material_validation()
    test_edit_material_form()
    test_edit_material_success()
    print("\nAll tests passed!")
