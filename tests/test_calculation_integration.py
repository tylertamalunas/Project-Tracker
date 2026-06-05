"""Integration tests for project-material and project-tool calculations.

Tests the full pipeline: line-item math, total rollups, owned-tool exclusion,
and variance for representative cases.
"""
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
    app = create_app()
    ctx = app.app_context()
    ctx.push()

    cat = MaterialCategory(name="Lumber")
    tcat = ToolCategory(name="Power Tools")
    db.session.add_all([cat, tcat])
    db.session.commit()

    mat1 = Material(name="2x4", default_price=4.00, category_id=cat.id)
    mat2 = Material(name="Plywood", default_price=45.00, category_id=cat.id)
    tool1 = Tool(name="Drill", default_price=99.00, category_id=tcat.id)
    tool2 = Tool(name="Saw", default_price=129.00, category_id=tcat.id)
    tool3 = Tool(name="Tape", default_price=12.00, category_id=tcat.id)
    db.session.add_all([mat1, mat2, tool1, tool2, tool3])
    db.session.commit()

    return app, ctx, mat1, mat2, tool1, tool2, tool3


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def test_quantity_times_unit_price():
    """Verify quantity * unit_price math for individual line items."""
    app, ctx, mat1, mat2, tool1, tool2, tool3 = setup_app()
    try:
        p = Project(name="Math Test", status="active")
        db.session.add(p)
        db.session.commit()

        # 10 studs at $3.98 = $39.80 estimated, 10 * $4.20 = $42.00 actual
        pm = ProjectMaterial(project_id=p.id, material_id=mat1.id,
                             quantity=10, estimated_unit_price=3.98, actual_unit_price=4.20)
        db.session.add(pm)
        db.session.commit()

        summary = cost_service.get_project_cost_summary(p.id)
        assert abs(summary["material_estimated"] - 39.80) < 0.01
        assert abs(summary["material_actual"] - 42.00) < 0.01
        print("PASS: test_quantity_times_unit_price")
    finally:
        teardown(ctx)


def test_multiple_materials_sum():
    """Multiple materials on one project sum correctly."""
    app, ctx, mat1, mat2, tool1, tool2, tool3 = setup_app()
    try:
        p = Project(name="Sum Test", status="active")
        db.session.add(p)
        db.session.commit()

        # 20 studs * $4.00 = $80
        pm1 = ProjectMaterial(project_id=p.id, material_id=mat1.id,
                              quantity=20, estimated_unit_price=4.00, actual_unit_price=3.80)
        # 3 plywood * $45.00 = $135
        pm2 = ProjectMaterial(project_id=p.id, material_id=mat2.id,
                              quantity=3, estimated_unit_price=45.00, actual_unit_price=48.00)
        db.session.add_all([pm1, pm2])
        db.session.commit()

        summary = cost_service.get_project_cost_summary(p.id)
        # Estimated: 80 + 135 = $215
        assert abs(summary["material_estimated"] - 215.00) < 0.01
        # Actual: (20*3.80) + (3*48.00) = 76 + 144 = $220
        assert abs(summary["material_actual"] - 220.00) < 0.01
        print("PASS: test_multiple_materials_sum")
    finally:
        teardown(ctx)


def test_estimated_and_actual_totals():
    """Project totals combine materials and purchased tools."""
    app, ctx, mat1, mat2, tool1, tool2, tool3 = setup_app()
    try:
        p = Project(name="Total Test", status="active")
        db.session.add(p)
        db.session.commit()

        # Material: 5 * $10 estimated, 5 * $9 actual
        pm = ProjectMaterial(project_id=p.id, material_id=mat1.id,
                             quantity=5, estimated_unit_price=10.00, actual_unit_price=9.00)
        # Tool (purchased): 1 * $100 estimated, 1 * $95 actual
        pt = ProjectTool(project_id=p.id, tool_id=tool1.id,
                         quantity=1, already_owned=False,
                         estimated_unit_price=100.00, actual_unit_price=95.00)
        db.session.add_all([pm, pt])
        db.session.commit()

        summary = cost_service.get_project_cost_summary(p.id)
        # Estimated: 50 + 100 = $150
        assert abs(summary["estimated_total"] - 150.00) < 0.01
        # Actual: 45 + 95 = $140
        assert abs(summary["actual_total"] - 140.00) < 0.01
        print("PASS: test_estimated_and_actual_totals")
    finally:
        teardown(ctx)


def test_already_owned_tools_excluded():
    """Owned tools contribute $0 to both estimated and actual totals."""
    app, ctx, mat1, mat2, tool1, tool2, tool3 = setup_app()
    try:
        p = Project(name="Owned Test", status="active")
        db.session.add(p)
        db.session.commit()

        # Purchased tool: $99 est, $89 act — counts
        pt1 = ProjectTool(project_id=p.id, tool_id=tool1.id,
                          quantity=1, already_owned=False,
                          estimated_unit_price=99.00, actual_unit_price=89.00)
        # Owned tool: $129 est, $129 act — excluded
        pt2 = ProjectTool(project_id=p.id, tool_id=tool2.id,
                          quantity=1, already_owned=True,
                          estimated_unit_price=129.00, actual_unit_price=129.00)
        # Owned tool: $12 — excluded
        pt3 = ProjectTool(project_id=p.id, tool_id=tool3.id,
                          quantity=1, already_owned=True,
                          estimated_unit_price=12.00, actual_unit_price=12.00)
        db.session.add_all([pt1, pt2, pt3])
        db.session.commit()

        summary = cost_service.get_project_cost_summary(p.id)
        # Only purchased tool counts
        assert abs(summary["tool_estimated"] - 99.00) < 0.01
        assert abs(summary["tool_actual"] - 89.00) < 0.01
        assert abs(summary["estimated_total"] - 99.00) < 0.01
        assert abs(summary["actual_total"] - 89.00) < 0.01
        print("PASS: test_already_owned_tools_excluded")
    finally:
        teardown(ctx)


def test_variance_under_budget():
    """Variance is negative when actual < estimated (under budget)."""
    app, ctx, mat1, mat2, tool1, tool2, tool3 = setup_app()
    try:
        p = Project(name="Under Budget", status="active")
        db.session.add(p)
        db.session.commit()

        pm = ProjectMaterial(project_id=p.id, material_id=mat1.id,
                             quantity=10, estimated_unit_price=5.00, actual_unit_price=4.00)
        db.session.add(pm)
        db.session.commit()

        summary = cost_service.get_project_cost_summary(p.id)
        # Estimated: $50, Actual: $40, Variance: -$10
        assert abs(summary["variance"] - (-10.00)) < 0.01
        print("PASS: test_variance_under_budget")
    finally:
        teardown(ctx)


def test_variance_over_budget():
    """Variance is positive when actual > estimated (over budget)."""
    app, ctx, mat1, mat2, tool1, tool2, tool3 = setup_app()
    try:
        p = Project(name="Over Budget", status="active")
        db.session.add(p)
        db.session.commit()

        pm = ProjectMaterial(project_id=p.id, material_id=mat1.id,
                             quantity=10, estimated_unit_price=4.00, actual_unit_price=6.00)
        pt = ProjectTool(project_id=p.id, tool_id=tool1.id,
                         quantity=1, already_owned=False,
                         estimated_unit_price=99.00, actual_unit_price=120.00)
        db.session.add_all([pm, pt])
        db.session.commit()

        summary = cost_service.get_project_cost_summary(p.id)
        # Estimated: 40 + 99 = $139, Actual: 60 + 120 = $180, Variance: +$41
        assert abs(summary["variance"] - 41.00) < 0.01
        print("PASS: test_variance_over_budget")
    finally:
        teardown(ctx)


def test_variance_exactly_zero():
    """Variance is $0 when estimated equals actual."""
    app, ctx, mat1, mat2, tool1, tool2, tool3 = setup_app()
    try:
        p = Project(name="On Budget", status="active")
        db.session.add(p)
        db.session.commit()

        pm = ProjectMaterial(project_id=p.id, material_id=mat1.id,
                             quantity=10, estimated_unit_price=4.00, actual_unit_price=4.00)
        db.session.add(pm)
        db.session.commit()

        summary = cost_service.get_project_cost_summary(p.id)
        assert summary["variance"] == 0
        print("PASS: test_variance_exactly_zero")
    finally:
        teardown(ctx)


def test_null_actuals_contribute_zero():
    """Materials with NULL actual_unit_price contribute $0 to actual total."""
    app, ctx, mat1, mat2, tool1, tool2, tool3 = setup_app()
    try:
        p = Project(name="Null Test", status="planned")
        db.session.add(p)
        db.session.commit()

        pm = ProjectMaterial(project_id=p.id, material_id=mat1.id,
                             quantity=10, estimated_unit_price=5.00, actual_unit_price=None)
        pt = ProjectTool(project_id=p.id, tool_id=tool1.id,
                         quantity=1, already_owned=False,
                         estimated_unit_price=99.00, actual_unit_price=None)
        db.session.add_all([pm, pt])
        db.session.commit()

        summary = cost_service.get_project_cost_summary(p.id)
        assert abs(summary["estimated_total"] - 149.00) < 0.01
        assert summary["actual_total"] == 0
        assert abs(summary["variance"] - (-149.00)) < 0.01
        print("PASS: test_null_actuals_contribute_zero")
    finally:
        teardown(ctx)


def test_model_properties_consistent():
    """Project model properties match cost_service calculations."""
    app, ctx, mat1, mat2, tool1, tool2, tool3 = setup_app()
    try:
        p = Project(name="Consistency", status="active")
        db.session.add(p)
        db.session.commit()

        pm = ProjectMaterial(project_id=p.id, material_id=mat1.id,
                             quantity=8, estimated_unit_price=4.50, actual_unit_price=4.25)
        pt = ProjectTool(project_id=p.id, tool_id=tool1.id,
                         quantity=1, already_owned=False,
                         estimated_unit_price=99.00, actual_unit_price=92.00)
        db.session.add_all([pm, pt])
        db.session.commit()

        db.session.refresh(p)
        summary = cost_service.get_project_cost_summary(p.id)

        assert abs(float(p.estimated_total) - summary["estimated_total"]) < 0.01
        assert abs(float(p.actual_total) - summary["actual_total"]) < 0.01
        assert abs(float(p.variance) - summary["variance"]) < 0.01
        print("PASS: test_model_properties_consistent")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_quantity_times_unit_price()
    test_multiple_materials_sum()
    test_estimated_and_actual_totals()
    test_already_owned_tools_excluded()
    test_variance_under_budget()
    test_variance_over_budget()
    test_variance_exactly_zero()
    test_null_actuals_contribute_zero()
    test_model_properties_consistent()
    print("\nAll tests passed!")
