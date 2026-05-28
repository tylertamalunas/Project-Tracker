"""Tests for the project-tool association service."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import Project, Tool, ToolCategory, Merchant
from app.services import project_tool_service


def setup_app():
    """Create app with in-memory DB and seed required reference data."""
    app = create_app()
    ctx = app.app_context()
    ctx.push()

    cat = ToolCategory(name="Power Tools")
    merchant = Merchant(name="Home Depot")
    db.session.add_all([cat, merchant])
    db.session.commit()

    tool = Tool(name="Cordless Drill", default_price=99.00, category_id=cat.id)
    db.session.add(tool)
    db.session.commit()

    project = Project(name="Kitchen Remodel", status="active")
    db.session.add(project)
    db.session.commit()

    return app, ctx, project, tool, merchant


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def test_add_tool_to_project():
    app, ctx, project, tool, merchant = setup_app()
    try:
        pt = project_tool_service.add_tool_to_project(
            project_id=project.id,
            tool_id=tool.id,
            quantity=1,
            already_owned=False,
            estimated_unit_price=99.00,
            actual_unit_price=89.00,
            merchant_id=merchant.id,
            purchased_on="2026-05-20",
            notes="On sale",
        )
        assert pt.id is not None
        assert pt.project_id == project.id
        assert pt.tool_id == tool.id
        assert pt.quantity == 1
        assert pt.already_owned is False
        assert float(pt.estimated_unit_price) == 99.00
        assert float(pt.actual_unit_price) == 89.00
        assert pt.merchant_id == merchant.id
        assert pt.purchased_on.strftime("%Y-%m-%d") == "2026-05-20"
        assert pt.notes == "On sale"
        print("PASS: test_add_tool_to_project")
    finally:
        teardown(ctx)


def test_add_tool_validation():
    app, ctx, project, tool, merchant = setup_app()
    try:
        # Quantity <= 0
        try:
            project_tool_service.add_tool_to_project(
                project_id=project.id, tool_id=tool.id, quantity=0)
            assert False
        except ValueError as e:
            assert "greater than 0" in str(e)

        # Negative price
        try:
            project_tool_service.add_tool_to_project(
                project_id=project.id, tool_id=tool.id,
                quantity=1, estimated_unit_price=-5)
            assert False
        except ValueError as e:
            assert ">= 0" in str(e)

        # Non-existent project
        try:
            project_tool_service.add_tool_to_project(
                project_id=9999, tool_id=tool.id, quantity=1)
            assert False
        except ValueError as e:
            assert "not found" in str(e)

        # Completed project
        project.status = "completed"
        db.session.commit()
        try:
            project_tool_service.add_tool_to_project(
                project_id=project.id, tool_id=tool.id, quantity=1)
            assert False
        except ValueError as e:
            assert "completed" in str(e).lower()

        print("PASS: test_add_tool_validation")
    finally:
        teardown(ctx)


def test_list_project_tools():
    app, ctx, project, tool, merchant = setup_app()
    try:
        project_tool_service.add_tool_to_project(
            project_id=project.id, tool_id=tool.id, quantity=1)
        project_tool_service.add_tool_to_project(
            project_id=project.id, tool_id=tool.id, quantity=2, already_owned=True)

        results = project_tool_service.list_project_tools(project.id)
        assert len(results) == 2

        print("PASS: test_list_project_tools")
    finally:
        teardown(ctx)


def test_update_project_tool():
    app, ctx, project, tool, merchant = setup_app()
    try:
        pt = project_tool_service.add_tool_to_project(
            project_id=project.id, tool_id=tool.id, quantity=1)

        updated = project_tool_service.update_project_tool(
            pt.id,
            quantity=2,
            already_owned=True,
            notes="Already had this",
        )
        assert updated.quantity == 2
        assert updated.already_owned is True
        assert updated.notes == "Already had this"

        print("PASS: test_update_project_tool")
    finally:
        teardown(ctx)


def test_remove_tool_from_project():
    app, ctx, project, tool, merchant = setup_app()
    try:
        pt = project_tool_service.add_tool_to_project(
            project_id=project.id, tool_id=tool.id, quantity=1)
        pt_id = pt.id

        result = project_tool_service.remove_tool_from_project(pt_id)
        assert result is True
        assert project_tool_service.get_project_tool(pt_id) is None

        print("PASS: test_remove_tool_from_project")
    finally:
        teardown(ctx)


def test_already_owned_excludes_from_totals():
    """Verify already_owned tools contribute $0 to project totals."""
    app, ctx, project, tool, merchant = setup_app()
    try:
        # Purchased tool: should count
        project_tool_service.add_tool_to_project(
            project_id=project.id, tool_id=tool.id,
            quantity=1, already_owned=False,
            estimated_unit_price=99.00, actual_unit_price=89.00)

        # Owned tool: should NOT count
        project_tool_service.add_tool_to_project(
            project_id=project.id, tool_id=tool.id,
            quantity=1, already_owned=True,
            estimated_unit_price=50.00, actual_unit_price=50.00)

        db.session.refresh(project)
        # Only the purchased tool counts: 1 * 99 estimated, 1 * 89 actual
        assert float(project.estimated_total) == 99.00
        assert float(project.actual_total) == 89.00

        print("PASS: test_already_owned_excludes_from_totals")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_add_tool_to_project()
    test_add_tool_validation()
    test_list_project_tools()
    test_update_project_tool()
    test_remove_tool_from_project()
    test_already_owned_excludes_from_totals()
    print("\nAll tests passed!")
