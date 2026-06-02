"""Tests for project material/tool attachment forms."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import (
    Project, Material, Tool, MaterialCategory, ToolCategory,
    Merchant, ProjectMaterial, ProjectTool,
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

    mat = Material(name="2x4", default_price=4.00, category_id=cat.id, is_active=True)
    tool = Tool(name="Drill", default_price=99.00, category_id=tcat.id, is_active=True)
    db.session.add_all([mat, tool])
    db.session.commit()

    project = Project(name="Test Project", status="active")
    db.session.add(project)
    db.session.commit()

    return app, ctx, project, mat, tool, merchant


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def test_add_material_form_renders():
    app, ctx, project, mat, tool, merchant = setup_app()
    try:
        client = app.test_client()
        r = client.get(f"/projects/{project.id}/materials/new")
        html = r.data.decode()
        assert r.status_code == 200
        assert "Add Material" in html
        assert "2x4" in html
        print("PASS: test_add_material_form_renders")
    finally:
        teardown(ctx)


def test_add_material_success():
    app, ctx, project, mat, tool, merchant = setup_app()
    try:
        client = app.test_client()
        r = client.post(f"/projects/{project.id}/materials/new", data={
            "material_id": str(mat.id),
            "quantity": "5",
            "estimated_unit_price": "4.00",
            "actual_unit_price": "3.50",
            "merchant_id": str(merchant.id),
        }, follow_redirects=False)
        assert r.status_code == 302
        assert ProjectMaterial.query.filter_by(project_id=project.id).count() == 1
        print("PASS: test_add_material_success")
    finally:
        teardown(ctx)


def test_edit_material():
    app, ctx, project, mat, tool, merchant = setup_app()
    try:
        pm = ProjectMaterial(project_id=project.id, material_id=mat.id,
                             quantity=5, estimated_unit_price=4.00)
        db.session.add(pm)
        db.session.commit()

        client = app.test_client()
        r = client.post(f"/projects/{project.id}/materials/{pm.id}/edit", data={
            "quantity": "10",
            "estimated_unit_price": "4.50",
            "unit_of_measure": "each",
        }, follow_redirects=False)
        assert r.status_code == 302
        db.session.refresh(pm)
        assert pm.quantity == 10
        print("PASS: test_edit_material")
    finally:
        teardown(ctx)


def test_delete_material():
    app, ctx, project, mat, tool, merchant = setup_app()
    try:
        pm = ProjectMaterial(project_id=project.id, material_id=mat.id,
                             quantity=1, estimated_unit_price=4.00)
        db.session.add(pm)
        db.session.commit()
        pm_id = pm.id

        client = app.test_client()
        r = client.post(f"/projects/{project.id}/materials/{pm_id}/delete", follow_redirects=False)
        assert r.status_code == 302
        assert ProjectMaterial.query.get(pm_id) is None
        print("PASS: test_delete_material")
    finally:
        teardown(ctx)


def test_add_tool_form_renders():
    app, ctx, project, mat, tool, merchant = setup_app()
    try:
        client = app.test_client()
        r = client.get(f"/projects/{project.id}/tools/new")
        html = r.data.decode()
        assert r.status_code == 200
        assert "Add Tool" in html
        assert "Drill" in html
        print("PASS: test_add_tool_form_renders")
    finally:
        teardown(ctx)


def test_add_tool_success():
    app, ctx, project, mat, tool, merchant = setup_app()
    try:
        client = app.test_client()
        r = client.post(f"/projects/{project.id}/tools/new", data={
            "tool_id": str(tool.id),
            "quantity": "1",
            "estimated_unit_price": "99.00",
            "already_owned": "on",
        }, follow_redirects=False)
        assert r.status_code == 302
        pt = ProjectTool.query.filter_by(project_id=project.id).first()
        assert pt is not None
        assert pt.already_owned is True
        print("PASS: test_add_tool_success")
    finally:
        teardown(ctx)


def test_edit_tool():
    app, ctx, project, mat, tool, merchant = setup_app()
    try:
        pt = ProjectTool(project_id=project.id, tool_id=tool.id,
                         quantity=1, already_owned=False, estimated_unit_price=99.00)
        db.session.add(pt)
        db.session.commit()

        client = app.test_client()
        r = client.post(f"/projects/{project.id}/tools/{pt.id}/edit", data={
            "quantity": "2",
            "estimated_unit_price": "99.00",
            "already_owned": "on",
        }, follow_redirects=False)
        assert r.status_code == 302
        db.session.refresh(pt)
        assert pt.quantity == 2
        assert pt.already_owned is True
        print("PASS: test_edit_tool")
    finally:
        teardown(ctx)


def test_delete_tool():
    app, ctx, project, mat, tool, merchant = setup_app()
    try:
        pt = ProjectTool(project_id=project.id, tool_id=tool.id,
                         quantity=1, already_owned=False, estimated_unit_price=99.00)
        db.session.add(pt)
        db.session.commit()
        pt_id = pt.id

        client = app.test_client()
        r = client.post(f"/projects/{project.id}/tools/{pt_id}/delete", follow_redirects=False)
        assert r.status_code == 302
        assert ProjectTool.query.get(pt_id) is None
        print("PASS: test_delete_tool")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_add_material_form_renders()
    test_add_material_success()
    test_edit_material()
    test_delete_material()
    test_add_tool_form_renders()
    test_add_tool_success()
    test_edit_tool()
    test_delete_tool()
    print("\nAll tests passed!")
