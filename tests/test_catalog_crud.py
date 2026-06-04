"""Tests for material and tool catalog CRUD including delete."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import (
    Material, Tool, MaterialCategory, ToolCategory, Merchant,
    Project, ProjectMaterial, ProjectTool,
)


def setup_app():
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    cat = MaterialCategory(name="Lumber")
    tcat = ToolCategory(name="Power Tools")
    merchant = Merchant(name="Home Depot")
    db.session.add_all([cat, tcat, merchant])
    db.session.commit()
    return app, ctx, cat, tcat, merchant


def teardown(ctx):
    db.session.remove()
    ctx.pop()


# --- Material delete ---

def test_delete_material_success():
    """Material not used in any project can be deleted."""
    app, ctx, cat, tcat, merchant = setup_app()
    try:
        mat = Material(name="Unused Material", default_price=5.00, category_id=cat.id)
        db.session.add(mat)
        db.session.commit()
        mid = mat.id

        client = app.test_client()
        r = client.post(f"/materials/{mid}/delete", follow_redirects=False)
        assert r.status_code == 302
        assert Material.query.get(mid) is None
        print("PASS: test_delete_material_success")
    finally:
        teardown(ctx)


def test_delete_material_in_use_blocked():
    """Material used in a project cannot be deleted."""
    app, ctx, cat, tcat, merchant = setup_app()
    try:
        mat = Material(name="Used Material", default_price=5.00, category_id=cat.id)
        db.session.add(mat)
        db.session.commit()

        p = Project(name="Test", status="active")
        db.session.add(p)
        db.session.commit()

        pm = ProjectMaterial(project_id=p.id, material_id=mat.id,
                             quantity=1, estimated_unit_price=5.00)
        db.session.add(pm)
        db.session.commit()
        mid = mat.id

        client = app.test_client()
        r = client.post(f"/materials/{mid}/delete", follow_redirects=True)
        assert r.status_code == 200
        html = r.data.decode()
        assert "cannot delete" in html.lower()
        assert Material.query.get(mid) is not None  # Not deleted
        print("PASS: test_delete_material_in_use_blocked")
    finally:
        teardown(ctx)


# --- Tool delete ---

def test_delete_tool_success():
    """Tool not used in any project can be deleted."""
    app, ctx, cat, tcat, merchant = setup_app()
    try:
        tool = Tool(name="Unused Tool", default_price=50.00, category_id=tcat.id)
        db.session.add(tool)
        db.session.commit()
        tid = tool.id

        client = app.test_client()
        r = client.post(f"/tools/{tid}/delete", follow_redirects=False)
        assert r.status_code == 302
        assert Tool.query.get(tid) is None
        print("PASS: test_delete_tool_success")
    finally:
        teardown(ctx)


def test_delete_tool_in_use_blocked():
    """Tool used in a project cannot be deleted."""
    app, ctx, cat, tcat, merchant = setup_app()
    try:
        tool = Tool(name="Used Tool", default_price=50.00, category_id=tcat.id)
        db.session.add(tool)
        db.session.commit()

        p = Project(name="Test", status="active")
        db.session.add(p)
        db.session.commit()

        pt = ProjectTool(project_id=p.id, tool_id=tool.id,
                         quantity=1, already_owned=False, estimated_unit_price=50.00)
        db.session.add(pt)
        db.session.commit()
        tid = tool.id

        client = app.test_client()
        r = client.post(f"/tools/{tid}/delete", follow_redirects=True)
        assert r.status_code == 200
        html = r.data.decode()
        assert "cannot delete" in html.lower()
        assert Tool.query.get(tid) is not None
        print("PASS: test_delete_tool_in_use_blocked")
    finally:
        teardown(ctx)


# --- Category/merchant references ---

def test_material_saves_category_and_merchant():
    """Material form correctly saves category and merchant references."""
    app, ctx, cat, tcat, merchant = setup_app()
    try:
        client = app.test_client()
        r = client.post("/materials/new", data={
            "name": "Test Material",
            "default_price": "10.00",
            "category_id": str(cat.id),
            "merchant_id": str(merchant.id),
        }, follow_redirects=False)
        assert r.status_code == 302

        mat = Material.query.filter_by(name="Test Material").first()
        assert mat is not None
        assert mat.category_id == cat.id
        assert mat.merchant_id == merchant.id
        print("PASS: test_material_saves_category_and_merchant")
    finally:
        teardown(ctx)


def test_tool_saves_category_and_merchant():
    """Tool form correctly saves category and merchant references."""
    app, ctx, cat, tcat, merchant = setup_app()
    try:
        client = app.test_client()
        r = client.post("/tools/new", data={
            "name": "Test Tool",
            "default_price": "50.00",
            "category_id": str(tcat.id),
            "merchant_id": str(merchant.id),
        }, follow_redirects=False)
        assert r.status_code == 302

        tool = Tool.query.filter_by(name="Test Tool").first()
        assert tool is not None
        assert tool.category_id == tcat.id
        assert tool.merchant_id == merchant.id
        print("PASS: test_tool_saves_category_and_merchant")
    finally:
        teardown(ctx)


# --- Inactive items ---

def test_inactive_material_hidden_from_project_form():
    """Inactive materials don't appear in project add-material dropdown."""
    app, ctx, cat, tcat, merchant = setup_app()
    try:
        active = Material(name="Active Mat", default_price=5.00, is_active=True)
        inactive = Material(name="Inactive Mat", default_price=5.00, is_active=False)
        db.session.add_all([active, inactive])
        db.session.commit()

        p = Project(name="Test", status="active")
        db.session.add(p)
        db.session.commit()

        client = app.test_client()
        r = client.get(f"/projects/{p.id}/materials/new")
        html = r.data.decode()
        assert "Active Mat" in html
        assert "Inactive Mat" not in html
        print("PASS: test_inactive_material_hidden_from_project_form")
    finally:
        teardown(ctx)


def test_inactive_tool_hidden_from_project_form():
    """Inactive tools don't appear in project add-tool dropdown."""
    app, ctx, cat, tcat, merchant = setup_app()
    try:
        active = Tool(name="Active Tool", default_price=50.00, is_active=True)
        inactive = Tool(name="Inactive Tool", default_price=50.00, is_active=False)
        db.session.add_all([active, inactive])
        db.session.commit()

        p = Project(name="Test", status="active")
        db.session.add(p)
        db.session.commit()

        client = app.test_client()
        r = client.get(f"/projects/{p.id}/tools/new")
        html = r.data.decode()
        assert "Active Tool" in html
        assert "Inactive Tool" not in html
        print("PASS: test_inactive_tool_hidden_from_project_form")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_delete_material_success()
    test_delete_material_in_use_blocked()
    test_delete_tool_success()
    test_delete_tool_in_use_blocked()
    test_material_saves_category_and_merchant()
    test_tool_saves_category_and_merchant()
    test_inactive_material_hidden_from_project_form()
    test_inactive_tool_hidden_from_project_form()
    print("\nAll tests passed!")
