"""Tests for project list and detail pages."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from datetime import date
from app import create_app, db
from app.models import (
    Project, Material, Tool, MaterialCategory, ToolCategory,
    ProjectMaterial, ProjectTool, Media,
)


def setup_app():
    """Create app with sample data."""
    app = create_app()
    ctx = app.app_context()
    ctx.push()

    cat = MaterialCategory(name="Lumber")
    tcat = ToolCategory(name="Power Tools")
    db.session.add_all([cat, tcat])
    db.session.commit()

    mat = Material(name="2x4", default_price=4.00, category_id=cat.id)
    tool = Tool(name="Drill", default_price=99.00, category_id=tcat.id)
    db.session.add_all([mat, tool])
    db.session.commit()

    project = Project(
        name="Test Project", status="active",
        description="A test project", notes="Important notes here",
        start_date=date(2026, 6, 1), end_date=date(2026, 7, 1),
    )
    db.session.add(project)
    db.session.commit()

    pm = ProjectMaterial(project_id=project.id, material_id=mat.id,
                         quantity=5, estimated_unit_price=4.00, actual_unit_price=3.50)
    pt = ProjectTool(project_id=project.id, tool_id=tool.id,
                     quantity=1, already_owned=False,
                     estimated_unit_price=99.00, actual_unit_price=89.00)
    media = Media(project_id=project.id, file_path="/uploads/receipt.pdf",
                  file_name="receipt.pdf", media_type="receipt", notes="Store receipt")
    db.session.add_all([pm, pt, media])
    db.session.commit()

    return app, ctx, project


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def test_project_list_page():
    app, ctx, project = setup_app()
    try:
        client = app.test_client()
        r = client.get("/projects")
        html = r.data.decode()

        assert r.status_code == 200
        assert "Test Project" in html
        assert "Start Date" in html
        assert "End Date" in html
        assert "2026-06-01" in html
        assert "2026-07-01" in html
        assert "Estimated Total" in html
        assert "Actual Total" in html
        assert "Variance" in html
        print("PASS: test_project_list_page")
    finally:
        teardown(ctx)


def test_project_detail_page():
    app, ctx, project = setup_app()
    try:
        client = app.test_client()
        r = client.get(f"/projects/{project.id}")
        html = r.data.decode()

        assert r.status_code == 200
        # Metadata
        assert "Test Project" in html
        assert "A test project" in html
        assert "Important notes here" in html
        assert "2026-06-01" in html
        # Totals
        assert "Estimated Total" in html
        assert "Actual Total" in html
        # Materials
        assert "2x4" in html
        # Tools
        assert "Drill" in html
        # Media
        assert "receipt.pdf" in html
        assert "Store receipt" in html
        print("PASS: test_project_detail_page")
    finally:
        teardown(ctx)


def test_project_list_uses_base_layout():
    app, ctx, project = setup_app()
    try:
        client = app.test_client()
        r = client.get("/projects")
        html = r.data.decode()

        assert "Project Tracker" in html  # navbar brand
        assert "Dashboard" in html        # nav link
        assert "Projects" in html         # nav link
        print("PASS: test_project_list_uses_base_layout")
    finally:
        teardown(ctx)


def test_project_detail_uses_base_layout():
    app, ctx, project = setup_app()
    try:
        client = app.test_client()
        r = client.get(f"/projects/{project.id}")
        html = r.data.decode()

        assert "Project Tracker" in html
        assert "navbar" in html
        print("PASS: test_project_detail_uses_base_layout")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_project_list_page()
    test_project_detail_page()
    test_project_list_uses_base_layout()
    test_project_detail_uses_base_layout()
    print("\nAll tests passed!")
