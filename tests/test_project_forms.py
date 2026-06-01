"""Tests for project create/edit forms."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import Project


def setup_app():
    """Create app with in-memory DB."""
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    return app, ctx


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def test_create_form_renders():
    app, ctx = setup_app()
    try:
        client = app.test_client()
        r = client.get("/projects/new")
        html = r.data.decode()

        assert r.status_code == 200
        assert "Create Project" in html
        assert 'name="name"' in html
        assert 'name="description"' in html
        assert 'name="status"' in html
        assert 'name="start_date"' in html
        assert 'name="end_date"' in html
        assert 'name="budget_estimate"' in html
        assert 'name="notes"' in html
        print("PASS: test_create_form_renders")
    finally:
        teardown(ctx)


def test_create_project_success():
    app, ctx = setup_app()
    try:
        client = app.test_client()
        r = client.post("/projects/new", data={
            "name": "New Project",
            "description": "A test project",
            "status": "planned",
            "start_date": "2026-07-01",
            "budget_estimate": "1500.00",
            "notes": "Some notes",
        }, follow_redirects=False)

        # Should redirect to project detail
        assert r.status_code == 302
        assert "/projects/" in r.headers["Location"]

        # Verify project was created
        p = Project.query.filter_by(name="New Project").first()
        assert p is not None
        assert p.description == "A test project"
        assert p.status == "planned"
        assert str(p.start_date) == "2026-07-01"
        assert float(p.budget_estimate) == 1500.00
        assert p.notes == "Some notes"
        print("PASS: test_create_project_success")
    finally:
        teardown(ctx)


def test_create_project_validation_error():
    app, ctx = setup_app()
    try:
        client = app.test_client()
        # Submit with empty name
        r = client.post("/projects/new", data={
            "name": "",
            "status": "planned",
        })

        assert r.status_code == 200
        html = r.data.decode()
        assert "error" in html.lower() or "required" in html.lower()
        # Should not have created a project
        assert Project.query.count() == 0
        print("PASS: test_create_project_validation_error")
    finally:
        teardown(ctx)


def test_edit_form_renders():
    app, ctx = setup_app()
    try:
        p = Project(name="Existing", description="Desc", status="active",
                    notes="Old notes")
        db.session.add(p)
        db.session.commit()

        client = app.test_client()
        r = client.get(f"/projects/{p.id}/edit")
        html = r.data.decode()

        assert r.status_code == 200
        assert "Edit" in html
        assert "Existing" in html  # pre-filled name
        assert "Desc" in html      # pre-filled description
        assert "Old notes" in html  # pre-filled notes
        print("PASS: test_edit_form_renders")
    finally:
        teardown(ctx)


def test_edit_project_success():
    app, ctx = setup_app()
    try:
        p = Project(name="Original", status="active")
        db.session.add(p)
        db.session.commit()
        pid = p.id

        client = app.test_client()
        r = client.post(f"/projects/{pid}/edit", data={
            "name": "Updated Name",
            "description": "Updated desc",
            "status": "active",
            "notes": "Updated notes",
        }, follow_redirects=False)

        assert r.status_code == 302
        assert f"/projects/{pid}" in r.headers["Location"]

        db.session.refresh(p)
        assert p.name == "Updated Name"
        assert p.description == "Updated desc"
        assert p.notes == "Updated notes"
        print("PASS: test_edit_project_success")
    finally:
        teardown(ctx)


def test_edit_completed_project_redirects():
    app, ctx = setup_app()
    try:
        p = Project(name="Done", status="completed")
        db.session.add(p)
        db.session.commit()

        client = app.test_client()
        r = client.get(f"/projects/{p.id}/edit", follow_redirects=False)

        # Should redirect back to detail (completed = read-only)
        assert r.status_code == 302
        print("PASS: test_edit_completed_project_redirects")
    finally:
        teardown(ctx)


def test_edit_validation_error():
    app, ctx = setup_app()
    try:
        p = Project(name="Test", status="active")
        db.session.add(p)
        db.session.commit()

        client = app.test_client()
        r = client.post(f"/projects/{p.id}/edit", data={
            "name": "",
            "status": "active",
        })

        assert r.status_code == 200
        html = r.data.decode()
        assert "error" in html.lower() or "required" in html.lower()
        # Name should not have changed
        db.session.refresh(p)
        assert p.name == "Test"
        print("PASS: test_edit_validation_error")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_create_form_renders()
    test_create_project_success()
    test_create_project_validation_error()
    test_edit_form_renders()
    test_edit_project_success()
    test_edit_completed_project_redirects()
    test_edit_validation_error()
    print("\nAll tests passed!")
