"""Tests for the tool service layer."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import ToolCategory, Merchant
from app.services import tool_service


def setup_app():
    """Create app with in-memory DB and seed lookup data."""
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    cat = ToolCategory(name="Power Tools", description="Drills, saws, etc.")
    merchant = Merchant(name="Home Depot", website="https://homedepot.com")
    db.session.add_all([cat, merchant])
    db.session.commit()
    return app, ctx, cat, merchant


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def test_create_tool():
    app, ctx, cat, merchant = setup_app()
    try:
        t = tool_service.create_tool(
            name="Cordless Drill",
            default_price=99.00,
            brand="DeWalt",
            model_number="DCD771",
            category_id=cat.id,
            merchant_id=merchant.id,
            notes="20V MAX",
        )
        assert t.id is not None
        assert t.name == "Cordless Drill"
        assert float(t.default_price) == 99.00
        assert t.brand == "DeWalt"
        assert t.model_number == "DCD771"
        assert t.category_id == cat.id
        assert t.merchant_id == merchant.id
        assert t.notes == "20V MAX"
        assert t.is_active is True
        assert t.created_at is not None
        print("PASS: test_create_tool")
    finally:
        teardown(ctx)


def test_create_tool_validation():
    app, ctx, cat, merchant = setup_app()
    try:
        # Empty name
        try:
            tool_service.create_tool(name="")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "name" in str(e).lower()

        # Negative price
        try:
            tool_service.create_tool(name="Test", default_price=-1)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert ">= 0" in str(e)

        # Invalid category
        try:
            tool_service.create_tool(name="Test", category_id=9999)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "not found" in str(e)

        # Invalid merchant
        try:
            tool_service.create_tool(name="Test", merchant_id=9999)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "not found" in str(e)

        print("PASS: test_create_tool_validation")
    finally:
        teardown(ctx)


def test_list_tools():
    app, ctx, cat, merchant = setup_app()
    try:
        tool_service.create_tool(name="Active Tool 1", is_active=True)
        tool_service.create_tool(name="Active Tool 2", is_active=True)
        tool_service.create_tool(name="Inactive Tool", is_active=False)

        # All
        all_tools = tool_service.list_tools()
        assert len(all_tools) == 3

        # Active only
        active = tool_service.list_tools(active_only=True)
        assert len(active) == 2
        assert all(t.is_active for t in active)

        # Inactive only
        inactive = tool_service.list_tools(active_only=False)
        assert len(inactive) == 1
        assert not inactive[0].is_active

        print("PASS: test_list_tools")
    finally:
        teardown(ctx)


def test_list_tools_by_category():
    app, ctx, cat, merchant = setup_app()
    try:
        tool_service.create_tool(name="In Category", category_id=cat.id)
        tool_service.create_tool(name="No Category")

        filtered = tool_service.list_tools(category_id=cat.id)
        assert len(filtered) == 1
        assert filtered[0].name == "In Category"

        print("PASS: test_list_tools_by_category")
    finally:
        teardown(ctx)


def test_get_tool():
    app, ctx, cat, merchant = setup_app()
    try:
        t = tool_service.create_tool(name="Circular Saw")
        fetched = tool_service.get_tool(t.id)
        assert fetched is not None
        assert fetched.name == "Circular Saw"

        assert tool_service.get_tool(9999) is None
        print("PASS: test_get_tool")
    finally:
        teardown(ctx)


def test_update_tool():
    app, ctx, cat, merchant = setup_app()
    try:
        t = tool_service.create_tool(name="Old Name", default_price=50.00)

        updated = tool_service.update_tool(
            t.id,
            name="New Name",
            default_price=75.00,
            brand="Milwaukee",
            model_number="M18",
            is_active=False,
        )
        assert updated.name == "New Name"
        assert float(updated.default_price) == 75.00
        assert updated.brand == "Milwaukee"
        assert updated.model_number == "M18"
        assert updated.is_active is False

        print("PASS: test_update_tool")
    finally:
        teardown(ctx)


def test_update_tool_validation():
    app, ctx, cat, merchant = setup_app()
    try:
        t = tool_service.create_tool(name="Test")

        # Empty name
        try:
            tool_service.update_tool(t.id, name="")
            assert False
        except ValueError:
            pass

        # Negative price
        try:
            tool_service.update_tool(t.id, default_price=-5)
            assert False
        except ValueError:
            pass

        # Non-existent tool
        try:
            tool_service.update_tool(9999, name="Nope")
            assert False
        except ValueError as e:
            assert "not found" in str(e)

        print("PASS: test_update_tool_validation")
    finally:
        teardown(ctx)


def test_delete_tool():
    app, ctx, cat, merchant = setup_app()
    try:
        t = tool_service.create_tool(name="To Delete")
        tid = t.id

        result = tool_service.delete_tool(tid)
        assert result is True
        assert tool_service.get_tool(tid) is None

        # Non-existent
        try:
            tool_service.delete_tool(9999)
            assert False
        except ValueError as e:
            assert "not found" in str(e)

        print("PASS: test_delete_tool")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_create_tool()
    test_create_tool_validation()
    test_list_tools()
    test_list_tools_by_category()
    test_get_tool()
    test_update_tool()
    test_update_tool_validation()
    test_delete_tool()
    print("\nAll tests passed!")
