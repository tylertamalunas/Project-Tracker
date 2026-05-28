"""Tests for the cost calculation service."""
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
    """Create app and seed a project with materials and tools."""
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

    project = Project(name="Test Project", status="active")
    db.session.add(project)
    db.session.commit()

    return app, ctx, project, mat, tool


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def test_empty_project_totals():
    """Project with no materials or tools should have zero totals."""
    app, ctx, project, mat, tool = setup_app()
    try:
        summary = cost_service.get_project_cost_summary(project.id)
        assert summary["estimated_total"] == 0
        assert summary["actual_total"] == 0
        assert summary["variance"] == 0
        print("PASS: test_empty_project_totals")
    finally:
        teardown(ctx)


def test_material_totals():
    """Material total = sum(quantity * unit_price)."""
    app, ctx, project, mat, tool = setup_app()
    try:
        # 10 units at $5.00 estimated, $4.50 actual
        pm = ProjectMaterial(
            project_id=project.id, material_id=mat.id,
            quantity=10, estimated_unit_price=5.00, actual_unit_price=4.50)
        db.session.add(pm)
        db.session.commit()

        summary = cost_service.get_project_cost_summary(project.id)
        assert summary["material_estimated"] == 50.00
        assert summary["material_actual"] == 45.00
        assert summary["estimated_total"] == 50.00
        assert summary["actual_total"] == 45.00
        assert summary["variance"] == -5.00  # under budget
        print("PASS: test_material_totals")
    finally:
        teardown(ctx)


def test_tool_purchased_counts():
    """Purchased tools contribute to totals."""
    app, ctx, project, mat, tool = setup_app()
    try:
        pt = ProjectTool(
            project_id=project.id, tool_id=tool.id,
            quantity=1, already_owned=False,
            estimated_unit_price=100.00, actual_unit_price=89.00)
        db.session.add(pt)
        db.session.commit()

        summary = cost_service.get_project_cost_summary(project.id)
        assert summary["tool_estimated"] == 100.00
        assert summary["tool_actual"] == 89.00
        print("PASS: test_tool_purchased_counts")
    finally:
        teardown(ctx)


def test_tool_owned_excluded():
    """Already-owned tools contribute $0 to totals."""
    app, ctx, project, mat, tool = setup_app()
    try:
        pt = ProjectTool(
            project_id=project.id, tool_id=tool.id,
            quantity=1, already_owned=True,
            estimated_unit_price=100.00, actual_unit_price=100.00)
        db.session.add(pt)
        db.session.commit()

        summary = cost_service.get_project_cost_summary(project.id)
        assert summary["tool_estimated"] == 0
        assert summary["tool_actual"] == 0
        assert summary["estimated_total"] == 0
        assert summary["actual_total"] == 0
        print("PASS: test_tool_owned_excluded")
    finally:
        teardown(ctx)


def test_null_actual_contributes_zero():
    """NULL actual_unit_price contributes $0 to actual total."""
    app, ctx, project, mat, tool = setup_app()
    try:
        pm = ProjectMaterial(
            project_id=project.id, material_id=mat.id,
            quantity=5, estimated_unit_price=10.00, actual_unit_price=None)
        db.session.add(pm)
        db.session.commit()

        summary = cost_service.get_project_cost_summary(project.id)
        assert summary["material_estimated"] == 50.00
        assert summary["material_actual"] == 0
        assert summary["variance"] == -50.00
        print("PASS: test_null_actual_contributes_zero")
    finally:
        teardown(ctx)


def test_combined_materials_and_tools():
    """Full project with both materials and tools."""
    app, ctx, project, mat, tool = setup_app()
    try:
        pm = ProjectMaterial(
            project_id=project.id, material_id=mat.id,
            quantity=20, estimated_unit_price=4.00, actual_unit_price=3.80)
        pt_purchased = ProjectTool(
            project_id=project.id, tool_id=tool.id,
            quantity=1, already_owned=False,
            estimated_unit_price=99.00, actual_unit_price=85.00)
        pt_owned = ProjectTool(
            project_id=project.id, tool_id=tool.id,
            quantity=1, already_owned=True,
            estimated_unit_price=50.00, actual_unit_price=50.00)
        db.session.add_all([pm, pt_purchased, pt_owned])
        db.session.commit()

        summary = cost_service.get_project_cost_summary(project.id)

        # Materials: 20 * 4.00 = 80 est, 20 * 3.80 = 76 act
        assert summary["material_estimated"] == 80.00
        assert summary["material_actual"] == 76.00

        # Tools: only purchased counts: 1 * 99 = 99 est, 1 * 85 = 85 act
        assert summary["tool_estimated"] == 99.00
        assert summary["tool_actual"] == 85.00

        # Totals
        assert summary["estimated_total"] == 179.00  # 80 + 99
        assert summary["actual_total"] == 161.00     # 76 + 85
        assert summary["variance"] == -18.00         # under budget

        print("PASS: test_combined_materials_and_tools")
    finally:
        teardown(ctx)


def test_model_properties_match_service():
    """Verify model .estimated_total/.actual_total/.variance match service."""
    app, ctx, project, mat, tool = setup_app()
    try:
        pm = ProjectMaterial(
            project_id=project.id, material_id=mat.id,
            quantity=5, estimated_unit_price=10.00, actual_unit_price=12.00)
        db.session.add(pm)
        db.session.commit()

        db.session.refresh(project)
        summary = cost_service.get_project_cost_summary(project.id)

        assert float(project.estimated_total) == summary["estimated_total"]
        assert float(project.actual_total) == summary["actual_total"]
        assert float(project.variance) == summary["variance"]
        print("PASS: test_model_properties_match_service")
    finally:
        teardown(ctx)


def test_nonexistent_project_raises():
    """Service raises ValueError for non-existent project."""
    app, ctx, project, mat, tool = setup_app()
    try:
        try:
            cost_service.get_project_cost_summary(9999)
            assert False
        except ValueError as e:
            assert "not found" in str(e)
        print("PASS: test_nonexistent_project_raises")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_empty_project_totals()
    test_material_totals()
    test_tool_purchased_counts()
    test_tool_owned_excluded()
    test_null_actual_contributes_zero()
    test_combined_materials_and_tools()
    test_model_properties_match_service()
    test_nonexistent_project_raises()
    print("\nAll tests passed!")
