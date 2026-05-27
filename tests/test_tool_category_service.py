"""Tests for the tool category service layer."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import Tool
from app.services import tool_category_service


def setup_app():
    """Create app with in-memory DB."""
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    return app, ctx


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def test_create_category():
    app, ctx = setup_app()
    try:
        cat = tool_category_service.create_tool_category(
            name="Power Tools",
            description="Drills, saws, and sanders",
        )
        assert cat.id is not None
        assert cat.name == "Power Tools"
        assert cat.description == "Drills, saws, and sanders"
        assert cat.created_at is not None
        print("PASS: test_create_category")
    finally:
        teardown(ctx)


def test_create_category_validation():
    app, ctx = setup_app()
    try:
        # Empty name
        try:
            tool_category_service.create_tool_category(name="")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "required" in str(e).lower()

        # Duplicate name
        tool_category_service.create_tool_category(name="Hand Tools")
        try:
            tool_category_service.create_tool_category(name="Hand Tools")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "already exists" in str(e).lower()

        # Duplicate name (case-insensitive)
        try:
            tool_category_service.create_tool_category(name="hand tools")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "already exists" in str(e).lower()

        print("PASS: test_create_category_validation")
    finally:
        teardown(ctx)


def test_list_categories():
    app, ctx = setup_app()
    try:
        tool_category_service.create_tool_category(name="Safety")
        tool_category_service.create_tool_category(name="Measuring")
        tool_category_service.create_tool_category(name="Painting")

        categories = tool_category_service.list_tool_categories()
        assert len(categories) == 3
        # Ordered by name
        assert categories[0].name == "Measuring"
        assert categories[1].name == "Painting"
        assert categories[2].name == "Safety"

        print("PASS: test_list_categories")
    finally:
        teardown(ctx)


def test_get_category():
    app, ctx = setup_app()
    try:
        cat = tool_category_service.create_tool_category(name="Power Tools")
        fetched = tool_category_service.get_tool_category(cat.id)
        assert fetched is not None
        assert fetched.name == "Power Tools"

        assert tool_category_service.get_tool_category(9999) is None
        print("PASS: test_get_category")
    finally:
        teardown(ctx)


def test_update_category():
    app, ctx = setup_app()
    try:
        cat = tool_category_service.create_tool_category(name="Old Name")

        updated = tool_category_service.update_tool_category(
            cat.id,
            name="New Name",
            description="Updated description",
        )
        assert updated.name == "New Name"
        assert updated.description == "Updated description"

        print("PASS: test_update_category")
    finally:
        teardown(ctx)


def test_update_category_validation():
    app, ctx = setup_app()
    try:
        cat = tool_category_service.create_tool_category(name="Safety")
        tool_category_service.create_tool_category(name="Power Tools")

        # Empty name
        try:
            tool_category_service.update_tool_category(cat.id, name="")
            assert False
        except ValueError:
            pass

        # Duplicate name
        try:
            tool_category_service.update_tool_category(cat.id, name="Power Tools")
            assert False
        except ValueError as e:
            assert "already exists" in str(e).lower()

        # Non-existent category
        try:
            tool_category_service.update_tool_category(9999, name="Nope")
            assert False
        except ValueError as e:
            assert "not found" in str(e)

        print("PASS: test_update_category_validation")
    finally:
        teardown(ctx)


def test_delete_category():
    app, ctx = setup_app()
    try:
        cat = tool_category_service.create_tool_category(name="To Delete")
        cid = cat.id

        result = tool_category_service.delete_tool_category(cid)
        assert result is True
        assert tool_category_service.get_tool_category(cid) is None

        # Non-existent
        try:
            tool_category_service.delete_tool_category(9999)
            assert False
        except ValueError as e:
            assert "not found" in str(e)

        print("PASS: test_delete_category")
    finally:
        teardown(ctx)


def test_delete_nullifies_tool_reference():
    """Verify deleting a category sets tool.category_id to NULL."""
    app, ctx = setup_app()
    try:
        cat = tool_category_service.create_tool_category(name="Temp Category")
        tool = Tool(name="Test Drill", default_price=50.00, category_id=cat.id)
        db.session.add(tool)
        db.session.commit()

        assert tool.category_id == cat.id

        tool_category_service.delete_tool_category(cat.id)
        db.session.refresh(tool)
        assert tool.category_id is None

        print("PASS: test_delete_nullifies_tool_reference")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_create_category()
    test_create_category_validation()
    test_list_categories()
    test_get_category()
    test_update_category()
    test_update_category_validation()
    test_delete_category()
    test_delete_nullifies_tool_reference()
    print("\nAll tests passed!")
