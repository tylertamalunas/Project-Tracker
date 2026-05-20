"""Tests for the project service layer."""
import os
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.services import project_service


def setup_app():
    """Create app and push context for testing."""
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    return app, ctx


def teardown(ctx):
    """Clean up after tests."""
    db.session.remove()
    ctx.pop()


def test_create_project():
    app, ctx = setup_app()
    try:
        p = project_service.create_project(
            name="Kitchen Remodel",
            description="Full kitchen renovation",
            status="planned",
            start_date="2026-06-01",
            budget_estimate=5000.00,
            notes="Phase 1 of home renovation",
        )
        assert p.id is not None
        assert p.name == "Kitchen Remodel"
        assert p.description == "Full kitchen renovation"
        assert p.status == "planned"
        assert str(p.start_date) == "2026-06-01"
        assert p.end_date is None
        assert float(p.budget_estimate) == 5000.00
        assert p.notes == "Phase 1 of home renovation"
        assert p.created_at is not None
        assert p.updated_at is not None
        print("PASS: test_create_project")
    finally:
        teardown(ctx)


def test_create_project_validation():
    app, ctx = setup_app()
    try:
        # Empty name
        try:
            project_service.create_project(name="")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "name is required" in str(e)

        # Invalid status
        try:
            project_service.create_project(name="Test", status="invalid")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Invalid status" in str(e)

        print("PASS: test_create_project_validation")
    finally:
        teardown(ctx)


def test_list_projects():
    app, ctx = setup_app()
    try:
        project_service.create_project(name="Project A", status="active")
        project_service.create_project(name="Project B", status="planned")
        project_service.create_project(name="Project C", status="active")

        # List all
        all_projects = project_service.list_projects()
        assert len(all_projects) == 3

        # Filter by status
        active = project_service.list_projects(status_filter="active")
        assert len(active) == 2
        assert all(p.status == "active" for p in active)

        planned = project_service.list_projects(status_filter="planned")
        assert len(planned) == 1

        print("PASS: test_list_projects")
    finally:
        teardown(ctx)


def test_get_project():
    app, ctx = setup_app()
    try:
        p = project_service.create_project(name="Deck Build")
        fetched = project_service.get_project(p.id)
        assert fetched is not None
        assert fetched.name == "Deck Build"

        # Non-existent
        missing = project_service.get_project(9999)
        assert missing is None

        print("PASS: test_get_project")
    finally:
        teardown(ctx)


def test_update_project():
    app, ctx = setup_app()
    try:
        p = project_service.create_project(name="Bathroom", status="planned")

        updated = project_service.update_project(
            p.id,
            name="Bathroom Remodel",
            status="active",
            start_date="2026-07-01",
            budget_estimate=3000.00,
            notes="Updated scope",
        )
        assert updated.name == "Bathroom Remodel"
        assert updated.status == "active"
        assert str(updated.start_date) == "2026-07-01"
        assert float(updated.budget_estimate) == 3000.00
        assert updated.notes == "Updated scope"

        print("PASS: test_update_project")
    finally:
        teardown(ctx)


def test_update_project_validation():
    app, ctx = setup_app()
    try:
        p = project_service.create_project(name="Test")

        # Empty name
        try:
            project_service.update_project(p.id, name="")
            assert False, "Should have raised ValueError"
        except ValueError:
            pass

        # Non-existent project
        try:
            project_service.update_project(9999, name="Nope")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "not found" in str(e)

        print("PASS: test_update_project_validation")
    finally:
        teardown(ctx)


def test_delete_project():
    app, ctx = setup_app()
    try:
        p = project_service.create_project(name="To Delete")
        project_id = p.id

        result = project_service.delete_project(project_id)
        assert result is True
        assert project_service.get_project(project_id) is None

        # Delete non-existent
        try:
            project_service.delete_project(9999)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "not found" in str(e)

        print("PASS: test_delete_project")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_create_project()
    test_create_project_validation()
    test_list_projects()
    test_get_project()
    test_update_project()
    test_update_project_validation()
    test_delete_project()
    print("\nAll tests passed!")
