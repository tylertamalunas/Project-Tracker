"""Tests for the dashboard page."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import (
    Project, Material, Tool, MaterialCategory, ToolCategory,
    ProjectMaterial, ProjectTool,
)


def setup_app():
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

    return app, ctx, mat, tool


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def test_dashboard_renders():
    app, ctx, mat, tool = setup_app()
    try:
        client = app.test_client()
        r = client.get("/")
        html = r.data.decode()
        assert r.status_code == 200
        assert "Dashboard" in html
        assert "Total Projects" in html
        assert "Spend Breakdown" in html
        print("PASS: test_dashboard_renders")
    finally:
        teardown(ctx)


def test_dashboard_shows_recent_projects():
    app, ctx, mat, tool = setup_app()
    try:
        p = Project(name="Active Test", status="active")
        db.session.add(p)
        db.session.commit()

        client = app.test_client()
        r = client.get("/")
        html = r.data.decode()
        assert "Active Test" in html
        assert "Recent Projects" in html
        print("PASS: test_dashboard_shows_recent_projects")
    finally:
        teardown(ctx)


def test_dashboard_shows_spend_totals():
    app, ctx, mat, tool = setup_app()
    try:
        p = Project(name="Spend Test", status="active")
        db.session.add(p)
        db.session.commit()
        pm = ProjectMaterial(project_id=p.id, material_id=mat.id,
                             quantity=10, estimated_unit_price=4.00, actual_unit_price=3.50)
        db.session.add(pm)
        db.session.commit()

        client = app.test_client()
        r = client.get("/")
        html = r.data.decode()
        # Global material spend should show $35.00 (10 * 3.50)
        assert "$35.00" in html
        print("PASS: test_dashboard_shows_spend_totals")
    finally:
        teardown(ctx)


def test_dashboard_shows_over_budget():
    app, ctx, mat, tool = setup_app()
    try:
        p = Project(name="Over Budget Project", status="active")
        db.session.add(p)
        db.session.commit()
        # Estimated $40, actual $50 — over by $10
        pm = ProjectMaterial(project_id=p.id, material_id=mat.id,
                             quantity=10, estimated_unit_price=4.00, actual_unit_price=5.00)
        db.session.add(pm)
        db.session.commit()

        client = app.test_client()
        r = client.get("/")
        html = r.data.decode()
        assert "Over Budget" in html
        assert "Over Budget Project" in html
        assert "+$10.00" in html
        print("PASS: test_dashboard_shows_over_budget")
    finally:
        teardown(ctx)


def test_dashboard_no_over_budget_when_under():
    app, ctx, mat, tool = setup_app()
    try:
        p = Project(name="Under Budget", status="active")
        db.session.add(p)
        db.session.commit()
        # Estimated $50, actual $30 — under budget
        pm = ProjectMaterial(project_id=p.id, material_id=mat.id,
                             quantity=10, estimated_unit_price=5.00, actual_unit_price=3.00)
        db.session.add(pm)
        db.session.commit()

        client = app.test_client()
        r = client.get("/")
        html = r.data.decode()
        # The over budget table rows should not appear
        assert "table-danger" not in html
        print("PASS: test_dashboard_no_over_budget_when_under")
    finally:
        teardown(ctx)


def test_dashboard_shows_variance_in_recent():
    app, ctx, mat, tool = setup_app()
    try:
        p = Project(name="Variance Project", status="active")
        db.session.add(p)
        db.session.commit()
        pm = ProjectMaterial(project_id=p.id, material_id=mat.id,
                             quantity=5, estimated_unit_price=10.00, actual_unit_price=8.00)
        db.session.add(pm)
        db.session.commit()

        client = app.test_client()
        r = client.get("/")
        html = r.data.decode()
        assert "Variance" in html
        # Under budget by $10 (estimated $50, actual $40)
        assert "-$10.00" in html
        print("PASS: test_dashboard_shows_variance_in_recent")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_dashboard_renders()
    test_dashboard_shows_recent_projects()
    test_dashboard_shows_spend_totals()
    test_dashboard_shows_over_budget()
    test_dashboard_no_over_budget_when_under()
    test_dashboard_shows_variance_in_recent()
    print("\nAll tests passed!")
