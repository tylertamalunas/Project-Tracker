"""Tests for the project hierarchy (parent-child) service."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import Project
from app.services import project_hierarchy_service


def setup_app():
    """Create app with in-memory DB and sample projects."""
    app = create_app()
    ctx = app.app_context()
    ctx.push()

    parent = Project(name="House Renovation", status="active")
    child1 = Project(name="Kitchen Remodel", status="active")
    child2 = Project(name="Bathroom Remodel", status="planned")
    standalone = Project(name="Deck Build", status="planned")
    db.session.add_all([parent, child1, child2, standalone])
    db.session.commit()

    return app, ctx, parent, child1, child2, standalone


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def test_link_child_to_parent():
    app, ctx, parent, child1, child2, standalone = setup_app()
    try:
        link = project_hierarchy_service.link_child_to_parent(parent.id, child1.id)
        assert link.parent_project_id == parent.id
        assert link.child_project_id == child1.id
        assert link.created_at is not None
        print("PASS: test_link_child_to_parent")
    finally:
        teardown(ctx)


def test_get_parent_project():
    app, ctx, parent, child1, child2, standalone = setup_app()
    try:
        project_hierarchy_service.link_child_to_parent(parent.id, child1.id)

        result = project_hierarchy_service.get_parent_project(child1.id)
        assert result is not None
        assert result.id == parent.id
        assert result.name == "House Renovation"

        # Project with no parent
        assert project_hierarchy_service.get_parent_project(standalone.id) is None
        print("PASS: test_get_parent_project")
    finally:
        teardown(ctx)


def test_get_child_projects():
    app, ctx, parent, child1, child2, standalone = setup_app()
    try:
        project_hierarchy_service.link_child_to_parent(parent.id, child1.id)
        project_hierarchy_service.link_child_to_parent(parent.id, child2.id)

        children = project_hierarchy_service.get_child_projects(parent.id)
        assert len(children) == 2
        child_names = {c.name for c in children}
        assert "Kitchen Remodel" in child_names
        assert "Bathroom Remodel" in child_names

        # Project with no children
        assert project_hierarchy_service.get_child_projects(standalone.id) == []
        print("PASS: test_get_child_projects")
    finally:
        teardown(ctx)


def test_prevent_self_link():
    app, ctx, parent, child1, child2, standalone = setup_app()
    try:
        try:
            project_hierarchy_service.link_child_to_parent(parent.id, parent.id)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "own parent" in str(e).lower()
        print("PASS: test_prevent_self_link")
    finally:
        teardown(ctx)


def test_prevent_duplicate_parent():
    app, ctx, parent, child1, child2, standalone = setup_app()
    try:
        project_hierarchy_service.link_child_to_parent(parent.id, child1.id)

        # Try to give child1 a second parent
        try:
            project_hierarchy_service.link_child_to_parent(standalone.id, child1.id)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "already has a parent" in str(e).lower()
        print("PASS: test_prevent_duplicate_parent")
    finally:
        teardown(ctx)


def test_prevent_circular_reference():
    app, ctx, parent, child1, child2, standalone = setup_app()
    try:
        # Create: parent -> child1
        project_hierarchy_service.link_child_to_parent(parent.id, child1.id)

        # Try to make parent a child of child1 (circular)
        try:
            project_hierarchy_service.link_child_to_parent(child1.id, parent.id)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "circular" in str(e).lower()
        print("PASS: test_prevent_circular_reference")
    finally:
        teardown(ctx)


def test_prevent_deep_circular_reference():
    app, ctx, parent, child1, child2, standalone = setup_app()
    try:
        # Create chain: parent -> child1 -> child2
        project_hierarchy_service.link_child_to_parent(parent.id, child1.id)
        project_hierarchy_service.link_child_to_parent(child1.id, child2.id)

        # Try to make parent a child of child2 (deep circular)
        try:
            project_hierarchy_service.link_child_to_parent(child2.id, parent.id)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "circular" in str(e).lower()
        print("PASS: test_prevent_deep_circular_reference")
    finally:
        teardown(ctx)


def test_unlink_child():
    app, ctx, parent, child1, child2, standalone = setup_app()
    try:
        project_hierarchy_service.link_child_to_parent(parent.id, child1.id)

        result = project_hierarchy_service.unlink_child_from_parent(parent.id, child1.id)
        assert result is True

        # Verify child no longer has parent
        assert project_hierarchy_service.get_parent_project(child1.id) is None

        # Non-existent link
        try:
            project_hierarchy_service.unlink_child_from_parent(parent.id, standalone.id)
            assert False
        except ValueError as e:
            assert "no parent-child" in str(e).lower()
        print("PASS: test_unlink_child")
    finally:
        teardown(ctx)


def test_nonexistent_project_raises():
    app, ctx, parent, child1, child2, standalone = setup_app()
    try:
        try:
            project_hierarchy_service.link_child_to_parent(9999, child1.id)
            assert False
        except ValueError as e:
            assert "not found" in str(e)

        try:
            project_hierarchy_service.link_child_to_parent(parent.id, 9999)
            assert False
        except ValueError as e:
            assert "not found" in str(e)
        print("PASS: test_nonexistent_project_raises")
    finally:
        teardown(ctx)


def test_detail_page_shows_hierarchy():
    """Verify the project detail page renders hierarchy info."""
    app, ctx, parent, child1, child2, standalone = setup_app()
    try:
        project_hierarchy_service.link_child_to_parent(parent.id, child1.id)
        project_hierarchy_service.link_child_to_parent(parent.id, child2.id)

        client = app.test_client()

        # Parent should show children
        r = client.get(f"/projects/{parent.id}")
        html = r.data.decode()
        assert "Sub-Projects" in html
        assert "Kitchen Remodel" in html
        assert "Bathroom Remodel" in html

        # Child should show parent
        r2 = client.get(f"/projects/{child1.id}")
        html2 = r2.data.decode()
        assert "Parent Project" in html2
        assert "House Renovation" in html2

        print("PASS: test_detail_page_shows_hierarchy")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_link_child_to_parent()
    test_get_parent_project()
    test_get_child_projects()
    test_prevent_self_link()
    test_prevent_duplicate_parent()
    test_prevent_circular_reference()
    test_prevent_deep_circular_reference()
    test_unlink_child()
    test_nonexistent_project_raises()
    test_detail_page_shows_hierarchy()
    print("\nAll tests passed!")
