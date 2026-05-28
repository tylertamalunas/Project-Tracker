"""Tests for global spend summary functions."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import (
    Project, Material, Tool, MaterialCategory, ToolCategory,
    ProjectMaterial, ProjectTool,
)
from app.services import cost_service


def setup_app():
    """Create app with in-memory DB."""
    app = create_app()
    ctx = app.app_context()
    ctx.push()

    mat_cat = MaterialCategory(name="Lumber")
    tool_cat = ToolCategory(name="Power Tools")
    db.session.add_all([mat_cat, tool_cat])
    db.session.commit()

    mat = Material(name="2x4", default_price=4.00, category_id=mat_cat.id)
    tool = Tool(name="Drill", default_price=99.00, category_id=tool_cat.id)
    db.session.add_all([mat, tool])
    db.session.commit()

    return app, ctx, mat, tool


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def test_empty_global_spend():
    """No data should yield zero spend."""
    app, ctx, mat, tool = setup_app()
    try:
        summary = cost_service.get_global_spend_summary()
        assert summary["material_spend"] == 0
        assert summary["tool_spend"] == 0
        assert summary["total_spend"] == 0
        print("PASS: test_empty_global_spend")
    finally:
        teardown(ctx)


def test_material_global_spend():
    """Material spend sums actual prices across all projects."""
    app, ctx, mat, tool = setup_app()
    try:
        p1 = Project(name="P1", status="active")
        p2 = Project(name="P2", status="completed")
        db.session.add_all([p1, p2])
        db.session.commit()

        # P1: 10 * $3.50 = $35
        pm1 = ProjectMaterial(project_id=p1.id, material_id=mat.id,
                              quantity=10, estimated_unit_price=4.00, actual_unit_price=3.50)
        # P2: 5 * $4.00 = $20
        pm2 = ProjectMaterial(project_id=p2.id, material_id=mat.id,
                              quantity=5, estimated_unit_price=4.00, actual_unit_price=4.00)
        db.session.add_all([pm1, pm2])
        db.session.commit()

        assert cost_service.get_global_material_spend() == 55.00  # 35 + 20
        print("PASS: test_material_global_spend")
    finally:
        teardown(ctx)


def test_tool_global_spend_excludes_owned():
    """Tool spend only counts purchased tools across all projects."""
    app, ctx, mat, tool = setup_app()
    try:
        p1 = Project(name="P1", status="active")
        db.session.add(p1)
        db.session.commit()

        # Purchased: 1 * $89 = $89
        pt1 = ProjectTool(project_id=p1.id, tool_id=tool.id,
                          quantity=1, already_owned=False,
                          estimated_unit_price=99.00, actual_unit_price=89.00)
        # Owned: should NOT count
        pt2 = ProjectTool(project_id=p1.id, tool_id=tool.id,
                          quantity=1, already_owned=True,
                          estimated_unit_price=50.00, actual_unit_price=50.00)
        db.session.add_all([pt1, pt2])
        db.session.commit()

        assert cost_service.get_global_tool_spend() == 89.00
        print("PASS: test_tool_global_spend_excludes_owned")
    finally:
        teardown(ctx)


def test_null_actual_contributes_zero():
    """Rows with NULL actual_unit_price contribute $0 to global spend."""
    app, ctx, mat, tool = setup_app()
    try:
        p = Project(name="P1", status="planned")
        db.session.add(p)
        db.session.commit()

        # actual_unit_price is NULL — should contribute $0
        pm = ProjectMaterial(project_id=p.id, material_id=mat.id,
                             quantity=10, estimated_unit_price=5.00, actual_unit_price=None)
        db.session.add(pm)
        db.session.commit()

        assert cost_service.get_global_material_spend() == 0
        print("PASS: test_null_actual_contributes_zero")
    finally:
        teardown(ctx)


def test_zero_price_contributes_zero():
    """Rows with actual_unit_price = 0 contribute $0 (included but produce no spend)."""
    app, ctx, mat, tool = setup_app()
    try:
        p = Project(name="P1", status="active")
        db.session.add(p)
        db.session.commit()

        pm = ProjectMaterial(project_id=p.id, material_id=mat.id,
                             quantity=10, estimated_unit_price=5.00, actual_unit_price=0)
        db.session.add(pm)
        db.session.commit()

        assert cost_service.get_global_material_spend() == 0
        print("PASS: test_zero_price_contributes_zero")
    finally:
        teardown(ctx)


def test_combined_global_summary():
    """Full summary combines material and tool spend."""
    app, ctx, mat, tool = setup_app()
    try:
        p = Project(name="P1", status="active")
        db.session.add(p)
        db.session.commit()

        pm = ProjectMaterial(project_id=p.id, material_id=mat.id,
                             quantity=10, estimated_unit_price=4.00, actual_unit_price=3.80)
        pt = ProjectTool(project_id=p.id, tool_id=tool.id,
                         quantity=1, already_owned=False,
                         estimated_unit_price=99.00, actual_unit_price=85.00)
        db.session.add_all([pm, pt])
        db.session.commit()

        summary = cost_service.get_global_spend_summary()
        assert summary["material_spend"] == 38.00   # 10 * 3.80
        assert summary["tool_spend"] == 85.00       # 1 * 85
        assert summary["total_spend"] == 123.00     # 38 + 85
        print("PASS: test_combined_global_summary")
    finally:
        teardown(ctx)


def test_dashboard_route():
    """Verify dashboard renders with spend data."""
    app, ctx, mat, tool = setup_app()
    try:
        p = Project(name="Active Project", status="active")
        db.session.add(p)
        db.session.commit()

        pm = ProjectMaterial(project_id=p.id, material_id=mat.id,
                             quantity=5, estimated_unit_price=10.00, actual_unit_price=9.00)
        db.session.add(pm)
        db.session.commit()

        client = app.test_client()
        r = client.get("/")
        html = r.data.decode()

        assert r.status_code == 200
        assert "Dashboard" in html
        assert "Total Actual Spend" in html
        assert "Materials (all-time actual)" in html
        assert "Active Project" in html
        print("PASS: test_dashboard_route")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_empty_global_spend()
    test_material_global_spend()
    test_tool_global_spend_excludes_owned()
    test_null_actual_contributes_zero()
    test_zero_price_contributes_zero()
    test_combined_global_summary()
    test_dashboard_route()
    print("\nAll tests passed!")
