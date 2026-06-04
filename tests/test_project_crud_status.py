"""Tests for project CRUD and status transitions."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import Project, Material, MaterialCategory, ProjectMaterial


def setup_app():
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    cat = MaterialCategory(name="Lumber")
    db.session.add(cat)
    db.session.commit()
    mat = Material(name="2x4", default_price=4.00, category_id=cat.id, is_active=True)
    db.session.add(mat)
    db.session.commit()
    return app, ctx, mat


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def test_completed_project_can_be_edited():
    """Completed projects should be editable (to change status back)."""
    app, ctx, mat = setup_app()
    try:
        p = Project(name="Done Project", status="completed")
        db.session.add(p)
        db.session.commit()

        client = app.test_client()
        # GET the edit form — should not redirect
        r = client.get(f"/projects/{p.id}/edit")
        assert r.status_code == 200
        assert "Done Project" in r.data.decode()

        # POST to change status back to active
        r2 = client.post(f"/projects/{p.id}/edit", data={
            "name": "Done Project",
            "status": "active",
        }, follow_redirects=False)
        assert r2.status_code == 302

        db.session.refresh(p)
        assert p.status == "active"
        print("PASS: test_completed_project_can_be_edited")
    finally:
        teardown(ctx)


def test_completed_project_can_reopen_to_planned():
    """A completed project can be set back to planned."""
    app, ctx, mat = setup_app()
    try:
        p = Project(name="Reopen Test", status="completed")
        db.session.add(p)
        db.session.commit()

        client = app.test_client()
        r = client.post(f"/projects/{p.id}/edit", data={
            "name": "Reopen Test",
            "status": "planned",
        }, follow_redirects=False)
        assert r.status_code == 302

        db.session.refresh(p)
        assert p.status == "planned"
        print("PASS: test_completed_project_can_reopen_to_planned")
    finally:
        teardown(ctx)


def test_delete_project_any_status():
    """Projects in any status can be deleted."""
    app, ctx, mat = setup_app()
    try:
        client = app.test_client()
        for status in ("planned", "active", "completed"):
            p = Project(name=f"Del {status}", status=status)
            db.session.add(p)
            db.session.commit()
            pid = p.id

            r = client.post(f"/projects/{pid}/delete", follow_redirects=False)
            assert r.status_code == 302
            assert Project.query.get(pid) is None

        print("PASS: test_delete_project_any_status")
    finally:
        teardown(ctx)


def test_delete_cascades_attachments():
    """Deleting a project removes its materials, tools, and media."""
    app, ctx, mat = setup_app()
    try:
        p = Project(name="Cascade Test", status="active")
        db.session.add(p)
        db.session.commit()

        pm = ProjectMaterial(project_id=p.id, material_id=mat.id,
                             quantity=5, estimated_unit_price=4.00)
        db.session.add(pm)
        db.session.commit()
        pm_id = pm.id
        pid = p.id

        client = app.test_client()
        r = client.post(f"/projects/{pid}/delete", follow_redirects=False)
        assert r.status_code == 302
        assert Project.query.get(pid) is None
        assert ProjectMaterial.query.get(pm_id) is None
        print("PASS: test_delete_cascades_attachments")
    finally:
        teardown(ctx)


def test_delete_nonexistent_project():
    """Deleting a non-existent project shows error flash."""
    app, ctx, mat = setup_app()
    try:
        client = app.test_client()
        r = client.post("/projects/9999/delete", follow_redirects=True)
        assert r.status_code == 200
        assert "not found" in r.data.decode().lower() or "danger" in r.data.decode().lower()
        print("PASS: test_delete_nonexistent_project")
    finally:
        teardown(ctx)


def test_edit_button_visible_for_completed():
    """The Edit button shows on project list for completed projects."""
    app, ctx, mat = setup_app()
    try:
        p = Project(name="Completed Visible", status="completed")
        db.session.add(p)
        db.session.commit()

        client = app.test_client()
        r = client.get("/projects")
        html = r.data.decode()
        assert f"/projects/{p.id}/edit" in html
        print("PASS: test_edit_button_visible_for_completed")
    finally:
        teardown(ctx)


def test_delete_button_on_detail_page():
    """Detail page shows Delete button for all statuses."""
    app, ctx, mat = setup_app()
    try:
        p = Project(name="Has Delete", status="completed")
        db.session.add(p)
        db.session.commit()

        client = app.test_client()
        r = client.get(f"/projects/{p.id}")
        html = r.data.decode()
        assert f"/projects/{p.id}/delete" in html
        assert "Delete Project" in html
        print("PASS: test_delete_button_on_detail_page")
    finally:
        teardown(ctx)


def test_dates_and_budget_persist():
    """Dates and budget fields save correctly through edit."""
    app, ctx, mat = setup_app()
    try:
        p = Project(name="Date Test", status="planned")
        db.session.add(p)
        db.session.commit()

        client = app.test_client()
        r = client.post(f"/projects/{p.id}/edit", data={
            "name": "Date Test",
            "status": "active",
            "start_date": "2026-07-01",
            "end_date": "2026-08-15",
            "budget_estimate": "2500.50",
        }, follow_redirects=False)
        assert r.status_code == 302

        db.session.refresh(p)
        assert str(p.start_date) == "2026-07-01"
        assert str(p.end_date) == "2026-08-15"
        assert float(p.budget_estimate) == 2500.50
        print("PASS: test_dates_and_budget_persist")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_completed_project_can_be_edited()
    test_completed_project_can_reopen_to_planned()
    test_delete_project_any_status()
    test_delete_cascades_attachments()
    test_delete_nonexistent_project()
    test_edit_button_visible_for_completed()
    test_delete_button_on_detail_page()
    test_dates_and_budget_persist()
    print("\nAll tests passed!")
