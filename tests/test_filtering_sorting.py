"""Tests for filtering and sorting on list pages."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import Project, Material, Tool, MaterialCategory, ToolCategory


def setup_app():
    app = create_app()
    ctx = app.app_context()
    ctx.push()

    cat = MaterialCategory(name="Lumber")
    tcat = ToolCategory(name="Power Tools")
    db.session.add_all([cat, tcat])
    db.session.commit()

    # Projects with different statuses
    db.session.add_all([
        Project(name="Alpha Project", status="active"),
        Project(name="Beta Project", status="planned"),
        Project(name="Gamma Project", status="completed"),
    ])
    db.session.commit()

    # Materials
    db.session.add_all([
        Material(name="Zebra Wood", default_price=50.00, brand="Premium", category_id=cat.id, is_active=True),
        Material(name="Alder Board", default_price=10.00, brand="Basic", category_id=cat.id, is_active=True),
        Material(name="Inactive Mat", default_price=5.00, is_active=False),
    ])
    db.session.commit()

    # Tools
    db.session.add_all([
        Tool(name="Zsaw", default_price=200.00, brand="ZBrand", category_id=tcat.id, is_active=True),
        Tool(name="Adrill", default_price=50.00, brand="ABrand", category_id=tcat.id, is_active=True),
    ])
    db.session.commit()

    return app, ctx


def teardown(ctx):
    db.session.remove()
    ctx.pop()


# --- Project filtering ---

def test_project_filter_active():
    app, ctx = setup_app()
    try:
        client = app.test_client()
        r = client.get("/projects?status=active")
        html = r.data.decode()
        assert "Alpha Project" in html
        assert "Beta Project" not in html
        assert "Gamma Project" not in html
        print("PASS: test_project_filter_active")
    finally:
        teardown(ctx)


def test_project_filter_all():
    app, ctx = setup_app()
    try:
        client = app.test_client()
        r = client.get("/projects")
        html = r.data.decode()
        assert "Alpha Project" in html
        assert "Beta Project" in html
        assert "Gamma Project" in html
        print("PASS: test_project_filter_all")
    finally:
        teardown(ctx)


# --- Project sorting ---

def test_project_sort_name_asc():
    app, ctx = setup_app()
    try:
        client = app.test_client()
        r = client.get("/projects?sort=name&dir=asc")
        html = r.data.decode()
        alpha_pos = html.index("Alpha Project")
        beta_pos = html.index("Beta Project")
        gamma_pos = html.index("Gamma Project")
        assert alpha_pos < beta_pos < gamma_pos
        print("PASS: test_project_sort_name_asc")
    finally:
        teardown(ctx)


def test_project_sort_name_desc():
    app, ctx = setup_app()
    try:
        client = app.test_client()
        r = client.get("/projects?sort=name&dir=desc")
        html = r.data.decode()
        alpha_pos = html.index("Alpha Project")
        gamma_pos = html.index("Gamma Project")
        assert gamma_pos < alpha_pos
        print("PASS: test_project_sort_name_desc")
    finally:
        teardown(ctx)


# --- Material sorting ---

def test_material_sort_price_desc():
    app, ctx = setup_app()
    try:
        client = app.test_client()
        r = client.get("/materials?sort=default_price&dir=desc")
        html = r.data.decode()
        zebra_pos = html.index("Zebra Wood")
        alder_pos = html.index("Alder Board")
        assert zebra_pos < alder_pos  # $50 before $10
        print("PASS: test_material_sort_price_desc")
    finally:
        teardown(ctx)


def test_material_sort_name_asc():
    app, ctx = setup_app()
    try:
        client = app.test_client()
        r = client.get("/materials?sort=name&dir=asc")
        html = r.data.decode()
        alder_pos = html.index("Alder Board")
        zebra_pos = html.index("Zebra Wood")
        assert alder_pos < zebra_pos
        print("PASS: test_material_sort_name_asc")
    finally:
        teardown(ctx)


# --- Tool sorting ---

def test_tool_sort_name_asc():
    app, ctx = setup_app()
    try:
        client = app.test_client()
        r = client.get("/tools?sort=name&dir=asc")
        html = r.data.decode()
        adrill_pos = html.index("Adrill")
        zsaw_pos = html.index("Zsaw")
        assert adrill_pos < zsaw_pos
        print("PASS: test_tool_sort_name_asc")
    finally:
        teardown(ctx)


def test_tool_sort_price_desc():
    app, ctx = setup_app()
    try:
        client = app.test_client()
        r = client.get("/tools?sort=default_price&dir=desc")
        html = r.data.decode()
        zsaw_pos = html.index("Zsaw")
        adrill_pos = html.index("Adrill")
        assert zsaw_pos < adrill_pos  # $200 before $50
        print("PASS: test_tool_sort_price_desc")
    finally:
        teardown(ctx)


# --- Sort controls visible ---

def test_sort_controls_visible():
    app, ctx = setup_app()
    try:
        client = app.test_client()
        r1 = client.get("/projects")
        assert "Sort by:" in r1.data.decode()

        r2 = client.get("/materials")
        assert "Sort:" in r2.data.decode()

        r3 = client.get("/tools")
        assert "Sort:" in r3.data.decode()
        print("PASS: test_sort_controls_visible")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_project_filter_active()
    test_project_filter_all()
    test_project_sort_name_asc()
    test_project_sort_name_desc()
    test_material_sort_price_desc()
    test_material_sort_name_asc()
    test_tool_sort_name_asc()
    test_tool_sort_price_desc()
    test_sort_controls_visible()
    print("\nAll tests passed!")
