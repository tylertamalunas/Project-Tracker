"""Tests for server-side validation across forms."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import Project, Material, MaterialCategory, Tool, ToolCategory
from app.services.validators import (
    validate_required, validate_positive_int, validate_price,
    validate_date, validate_choice,
)


# --- Unit tests for validator functions ---

def test_validate_required():
    errors = []
    assert validate_required("hello", "Name", errors) == "hello"
    assert errors == []

    assert validate_required("", "Name", errors) is None
    assert "Name is required" in errors[0]

    errors2 = []
    assert validate_required("  ", "Name", errors2) is None
    assert len(errors2) == 1
    print("PASS: test_validate_required")


def test_validate_positive_int():
    errors = []
    assert validate_positive_int("5", "Qty", errors) == 5
    assert errors == []

    errors2 = []
    assert validate_positive_int("0", "Qty", errors2) is None
    assert "greater than 0" in errors2[0]

    errors3 = []
    assert validate_positive_int("abc", "Qty", errors3) is None
    assert "whole number" in errors3[0]

    errors4 = []
    assert validate_positive_int("-1", "Qty", errors4) is None
    print("PASS: test_validate_positive_int")


def test_validate_price():
    errors = []
    assert validate_price("9.99", "Price", errors) == 9.99
    assert errors == []

    errors2 = []
    assert validate_price("-5", "Price", errors2) is None
    assert "$0.00 or greater" in errors2[0]

    errors3 = []
    assert validate_price("abc", "Price", errors3) is None
    assert "valid number" in errors3[0]

    errors4 = []
    assert validate_price("", "Price", errors4) is None  # allowed None
    assert errors4 == []

    errors5 = []
    assert validate_price("", "Price", errors5, allow_none=False) is None
    assert "required" in errors5[0]
    print("PASS: test_validate_price")


def test_validate_date():
    errors = []
    d = validate_date("2026-06-01", "Start", errors)
    assert d is not None
    assert str(d) == "2026-06-01"
    assert errors == []

    errors2 = []
    assert validate_date("not-a-date", "Start", errors2) is None
    assert "valid date" in errors2[0]

    errors3 = []
    assert validate_date("", "Start", errors3) is None  # allowed None
    assert errors3 == []
    print("PASS: test_validate_date")


def test_validate_choice():
    errors = []
    assert validate_choice("active", "Status", ("planned", "active", "completed"), errors) == "active"
    assert errors == []

    errors2 = []
    assert validate_choice("invalid", "Status", ("planned", "active"), errors2) is None
    assert "must be one of" in errors2[0]
    print("PASS: test_validate_choice")


# --- Integration tests: form validation in routes ---

def setup_app():
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    cat = MaterialCategory(name="Lumber")
    tcat = ToolCategory(name="Power")
    db.session.add_all([cat, tcat])
    db.session.commit()
    mat = Material(name="2x4", default_price=4.00, category_id=cat.id, is_active=True)
    tool = Tool(name="Drill", default_price=99.00, category_id=tcat.id, is_active=True)
    db.session.add_all([mat, tool])
    db.session.commit()
    project = Project(name="Test", status="active")
    db.session.add(project)
    db.session.commit()
    return app, ctx, project, mat, tool


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def test_project_form_rejects_empty_name():
    app, ctx, project, mat, tool = setup_app()
    try:
        client = app.test_client()
        r = client.post("/projects/new", data={"name": "", "status": "planned"})
        assert r.status_code == 200
        assert "required" in r.data.decode().lower()
        assert Project.query.filter_by(name="").count() == 0
        print("PASS: test_project_form_rejects_empty_name")
    finally:
        teardown(ctx)


def test_project_form_rejects_invalid_status():
    app, ctx, project, mat, tool = setup_app()
    try:
        client = app.test_client()
        r = client.post("/projects/new", data={"name": "Test", "status": "invalid"})
        assert r.status_code == 200
        assert "must be one of" in r.data.decode().lower()
        print("PASS: test_project_form_rejects_invalid_status")
    finally:
        teardown(ctx)


def test_project_form_rejects_bad_date():
    app, ctx, project, mat, tool = setup_app()
    try:
        client = app.test_client()
        r = client.post("/projects/new", data={
            "name": "Test", "status": "planned", "start_date": "not-a-date"})
        assert r.status_code == 200
        assert "valid date" in r.data.decode().lower()
        print("PASS: test_project_form_rejects_bad_date")
    finally:
        teardown(ctx)


def test_material_form_rejects_zero_quantity():
    app, ctx, project, mat, tool = setup_app()
    try:
        client = app.test_client()
        r = client.post(f"/projects/{project.id}/materials/new", data={
            "material_id": str(mat.id),
            "quantity": "0",
            "estimated_unit_price": "4.00",
        })
        assert r.status_code == 200
        assert "greater than 0" in r.data.decode().lower()
        print("PASS: test_material_form_rejects_zero_quantity")
    finally:
        teardown(ctx)


def test_material_form_rejects_negative_price():
    app, ctx, project, mat, tool = setup_app()
    try:
        client = app.test_client()
        r = client.post(f"/projects/{project.id}/materials/new", data={
            "material_id": str(mat.id),
            "quantity": "5",
            "estimated_unit_price": "-10",
        })
        assert r.status_code == 200
        assert "$0.00 or greater" in r.data.decode().lower()
        print("PASS: test_material_form_rejects_negative_price")
    finally:
        teardown(ctx)


def test_material_form_rejects_no_material():
    app, ctx, project, mat, tool = setup_app()
    try:
        client = app.test_client()
        r = client.post(f"/projects/{project.id}/materials/new", data={
            "quantity": "5",
            "estimated_unit_price": "4.00",
        })
        assert r.status_code == 200
        assert "select a material" in r.data.decode().lower()
        print("PASS: test_material_form_rejects_no_material")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    # Unit tests
    test_validate_required()
    test_validate_positive_int()
    test_validate_price()
    test_validate_date()
    test_validate_choice()
    # Integration tests
    test_project_form_rejects_empty_name()
    test_project_form_rejects_invalid_status()
    test_project_form_rejects_bad_date()
    test_material_form_rejects_zero_quantity()
    test_material_form_rejects_negative_price()
    test_material_form_rejects_no_material()
    print("\nAll tests passed!")
