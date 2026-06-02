"""Tests for tool catalog pages and forms."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import Tool, ToolCategory, Merchant


def setup_app():
    """Create app with sample data."""
    app = create_app()
    ctx = app.app_context()
    ctx.push()

    cat = ToolCategory(name="Power Tools")
    merchant = Merchant(name="Home Depot")
    db.session.add_all([cat, merchant])
    db.session.commit()

    tool = Tool(name="Drill", default_price=99.00, brand="DeWalt",
                model_number="DCD771", category_id=cat.id, merchant_id=merchant.id, is_active=True)
    inactive = Tool(name="Old Sander", default_price=40.00, is_active=False)
    db.session.add_all([tool, inactive])
    db.session.commit()

    return app, ctx, cat, merchant, tool


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def test_tool_list_page():
    app, ctx, cat, merchant, tool = setup_app()
    try:
        client = app.test_client()
        r = client.get("/tools")
        html = r.data.decode()

        assert r.status_code == 200
        assert "Drill" in html
        assert "Old Sander" in html
        assert "Power Tools" in html
        assert "DeWalt" in html
        print("PASS: test_tool_list_page")
    finally:
        teardown(ctx)


def test_tool_list_filter_active():
    app, ctx, cat, merchant, tool = setup_app()
    try:
        client = app.test_client()
        r = client.get("/tools?active=true")
        html = r.data.decode()

        assert "Drill" in html
        assert "Old Sander" not in html
        print("PASS: test_tool_list_filter_active")
    finally:
        teardown(ctx)


def test_tool_list_filter_category():
    app, ctx, cat, merchant, tool = setup_app()
    try:
        client = app.test_client()
        r = client.get(f"/tools?category_id={cat.id}")
        html = r.data.decode()

        assert "Drill" in html
        assert "Old Sander" not in html
        print("PASS: test_tool_list_filter_category")
    finally:
        teardown(ctx)


def test_create_tool_form():
    app, ctx, cat, merchant, tool = setup_app()
    try:
        client = app.test_client()
        r = client.get("/tools/new")
        html = r.data.decode()

        assert r.status_code == 200
        assert "Create Tool" in html
        assert "Power Tools" in html
        assert "Home Depot" in html
        print("PASS: test_create_tool_form")
    finally:
        teardown(ctx)


def test_create_tool_success():
    app, ctx, cat, merchant, tool = setup_app()
    try:
        client = app.test_client()
        r = client.post("/tools/new", data={
            "name": "Circular Saw",
            "default_price": "129.00",
            "brand": "Milwaukee",
            "model_number": "2631-20",
            "category_id": str(cat.id),
            "merchant_id": str(merchant.id),
            "notes": "Brushless motor",
        }, follow_redirects=False)

        assert r.status_code == 302
        t = Tool.query.filter_by(name="Circular Saw").first()
        assert t is not None
        assert float(t.default_price) == 129.00
        assert t.brand == "Milwaukee"
        assert t.model_number == "2631-20"
        print("PASS: test_create_tool_success")
    finally:
        teardown(ctx)


def test_create_tool_validation():
    app, ctx, cat, merchant, tool = setup_app()
    try:
        client = app.test_client()
        r = client.post("/tools/new", data={"name": ""})
        html = r.data.decode()

        assert r.status_code == 200
        assert "error" in html.lower() or "name" in html.lower()
        print("PASS: test_create_tool_validation")
    finally:
        teardown(ctx)


def test_edit_tool_form():
    app, ctx, cat, merchant, tool = setup_app()
    try:
        client = app.test_client()
        r = client.get(f"/tools/{tool.id}/edit")
        html = r.data.decode()

        assert r.status_code == 200
        assert "Edit" in html
        assert "Drill" in html
        assert "DeWalt" in html
        print("PASS: test_edit_tool_form")
    finally:
        teardown(ctx)


def test_edit_tool_success():
    app, ctx, cat, merchant, tool = setup_app()
    try:
        client = app.test_client()
        r = client.post(f"/tools/{tool.id}/edit", data={
            "name": "Updated Drill",
            "default_price": "109.00",
            "brand": "DeWalt",
            "model_number": "DCD771C2",
            "is_active": "on",
        }, follow_redirects=False)

        assert r.status_code == 302
        db.session.refresh(tool)
        assert tool.name == "Updated Drill"
        assert float(tool.default_price) == 109.00
        assert tool.model_number == "DCD771C2"
        print("PASS: test_edit_tool_success")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_tool_list_page()
    test_tool_list_filter_active()
    test_tool_list_filter_category()
    test_create_tool_form()
    test_create_tool_success()
    test_create_tool_validation()
    test_edit_tool_form()
    test_edit_tool_success()
    print("\nAll tests passed!")
