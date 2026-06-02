"""Tests for merchant and category management pages."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import Merchant, MaterialCategory, ToolCategory


def setup_app():
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    return app, ctx


def teardown(ctx):
    db.session.remove()
    ctx.pop()


# --- Merchants ---

def test_merchant_list():
    app, ctx = setup_app()
    try:
        db.session.add(Merchant(name="Home Depot"))
        db.session.commit()
        client = app.test_client()
        r = client.get("/merchants")
        assert r.status_code == 200
        assert "Home Depot" in r.data.decode()
        print("PASS: test_merchant_list")
    finally:
        teardown(ctx)


def test_merchant_create():
    app, ctx = setup_app()
    try:
        client = app.test_client()
        r = client.post("/merchants/new", data={"name": "Lowe's", "website": "https://lowes.com"}, follow_redirects=False)
        assert r.status_code == 302
        assert Merchant.query.filter_by(name="Lowe's").first() is not None
        print("PASS: test_merchant_create")
    finally:
        teardown(ctx)


def test_merchant_edit():
    app, ctx = setup_app()
    try:
        m = Merchant(name="Old Name")
        db.session.add(m)
        db.session.commit()
        client = app.test_client()
        r = client.post(f"/merchants/{m.id}/edit", data={"name": "New Name"}, follow_redirects=False)
        assert r.status_code == 302
        db.session.refresh(m)
        assert m.name == "New Name"
        print("PASS: test_merchant_edit")
    finally:
        teardown(ctx)


def test_merchant_delete():
    app, ctx = setup_app()
    try:
        m = Merchant(name="To Delete")
        db.session.add(m)
        db.session.commit()
        mid = m.id
        client = app.test_client()
        r = client.post(f"/merchants/{mid}/delete", follow_redirects=False)
        assert r.status_code == 302
        assert Merchant.query.get(mid) is None
        print("PASS: test_merchant_delete")
    finally:
        teardown(ctx)


# --- Material Categories ---

def test_material_category_list():
    app, ctx = setup_app()
    try:
        db.session.add(MaterialCategory(name="Lumber"))
        db.session.commit()
        client = app.test_client()
        r = client.get("/categories/materials")
        assert r.status_code == 200
        assert "Lumber" in r.data.decode()
        print("PASS: test_material_category_list")
    finally:
        teardown(ctx)


def test_material_category_create():
    app, ctx = setup_app()
    try:
        client = app.test_client()
        r = client.post("/categories/materials/new", data={"name": "Paint"}, follow_redirects=False)
        assert r.status_code == 302
        assert MaterialCategory.query.filter_by(name="Paint").first() is not None
        print("PASS: test_material_category_create")
    finally:
        teardown(ctx)


def test_material_category_delete():
    app, ctx = setup_app()
    try:
        cat = MaterialCategory(name="To Delete")
        db.session.add(cat)
        db.session.commit()
        cid = cat.id
        client = app.test_client()
        r = client.post(f"/categories/materials/{cid}/delete", follow_redirects=False)
        assert r.status_code == 302
        assert MaterialCategory.query.get(cid) is None
        print("PASS: test_material_category_delete")
    finally:
        teardown(ctx)


# --- Tool Categories ---

def test_tool_category_list():
    app, ctx = setup_app()
    try:
        db.session.add(ToolCategory(name="Power Tools"))
        db.session.commit()
        client = app.test_client()
        r = client.get("/categories/tools")
        assert r.status_code == 200
        assert "Power Tools" in r.data.decode()
        print("PASS: test_tool_category_list")
    finally:
        teardown(ctx)


def test_tool_category_create():
    app, ctx = setup_app()
    try:
        client = app.test_client()
        r = client.post("/categories/tools/new", data={"name": "Hand Tools"}, follow_redirects=False)
        assert r.status_code == 302
        assert ToolCategory.query.filter_by(name="Hand Tools").first() is not None
        print("PASS: test_tool_category_create")
    finally:
        teardown(ctx)


def test_tool_category_delete():
    app, ctx = setup_app()
    try:
        cat = ToolCategory(name="To Delete")
        db.session.add(cat)
        db.session.commit()
        cid = cat.id
        client = app.test_client()
        r = client.post(f"/categories/tools/{cid}/delete", follow_redirects=False)
        assert r.status_code == 302
        assert ToolCategory.query.get(cid) is None
        print("PASS: test_tool_category_delete")
    finally:
        teardown(ctx)


# --- Navigation ---

def test_nav_has_manage_dropdown():
    app, ctx = setup_app()
    try:
        client = app.test_client()
        r = client.get("/")
        html = r.data.decode()
        assert "Manage" in html
        assert "/merchants" in html
        assert "/categories/materials" in html
        assert "/categories/tools" in html
        print("PASS: test_nav_has_manage_dropdown")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_merchant_list()
    test_merchant_create()
    test_merchant_edit()
    test_merchant_delete()
    test_material_category_list()
    test_material_category_create()
    test_material_category_delete()
    test_tool_category_list()
    test_tool_category_create()
    test_tool_category_delete()
    test_nav_has_manage_dropdown()
    print("\nAll tests passed!")
