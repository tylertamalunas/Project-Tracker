"""Tests for the project relationship service."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import Project
from app.services import project_relationship_service


def setup_app():
    """Create app with sample projects."""
    app = create_app()
    ctx = app.app_context()
    ctx.push()

    p1 = Project(name="Kitchen Remodel", status="active")
    p2 = Project(name="Bathroom Remodel", status="planned")
    p3 = Project(name="Deck Build", status="planned")
    db.session.add_all([p1, p2, p3])
    db.session.commit()

    return app, ctx, p1, p2, p3


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def test_create_relationship():
    app, ctx, p1, p2, p3 = setup_app()
    try:
        rel = project_relationship_service.create_relationship(
            project_id=p1.id,
            related_project_id=p2.id,
            relationship_type="similar_to",
            notes="Both involve tile work",
        )
        assert rel.id is not None
        assert rel.project_id == p1.id
        assert rel.related_project_id == p2.id
        assert rel.relationship_type == "similar_to"
        assert rel.notes == "Both involve tile work"
        print("PASS: test_create_relationship")
    finally:
        teardown(ctx)


def test_create_relationship_validation():
    app, ctx, p1, p2, p3 = setup_app()
    try:
        # Self-link
        try:
            project_relationship_service.create_relationship(p1.id, p1.id)
            assert False
        except ValueError as e:
            assert "itself" in str(e).lower()

        # Invalid type
        try:
            project_relationship_service.create_relationship(p1.id, p2.id, relationship_type="invalid")
            assert False
        except ValueError as e:
            assert "invalid relationship type" in str(e).lower()

        # Non-existent project
        try:
            project_relationship_service.create_relationship(9999, p2.id)
            assert False
        except ValueError as e:
            assert "not found" in str(e)

        print("PASS: test_create_relationship_validation")
    finally:
        teardown(ctx)


def test_prevent_duplicate():
    app, ctx, p1, p2, p3 = setup_app()
    try:
        project_relationship_service.create_relationship(p1.id, p2.id, "depends_on")

        # Same direction
        try:
            project_relationship_service.create_relationship(p1.id, p2.id, "depends_on")
            assert False
        except ValueError as e:
            assert "already exists" in str(e).lower()

        # Reverse direction, same type
        try:
            project_relationship_service.create_relationship(p2.id, p1.id, "depends_on")
            assert False
        except ValueError as e:
            assert "already exists" in str(e).lower()

        # Different type is allowed
        rel = project_relationship_service.create_relationship(p1.id, p2.id, "similar_to")
        assert rel.id is not None

        print("PASS: test_prevent_duplicate")
    finally:
        teardown(ctx)


def test_get_related_projects():
    app, ctx, p1, p2, p3 = setup_app()
    try:
        project_relationship_service.create_relationship(p1.id, p2.id, "depends_on", "Bathroom after kitchen")
        project_relationship_service.create_relationship(p3.id, p1.id, "similar_to", "Both outdoor adjacent")

        results = project_relationship_service.get_related_projects(p1.id)
        assert len(results) == 2

        # One outgoing (p1 -> p2), one incoming (p3 -> p1)
        outgoing = [r for r in results if r["direction"] == "outgoing"]
        incoming = [r for r in results if r["direction"] == "incoming"]
        assert len(outgoing) == 1
        assert outgoing[0]["project"].name == "Bathroom Remodel"
        assert outgoing[0]["relationship_type"] == "depends_on"
        assert len(incoming) == 1
        assert incoming[0]["project"].name == "Deck Build"

        # Project with no relationships
        assert project_relationship_service.get_related_projects(p3.id) != []  # p3 has outgoing to p1

        print("PASS: test_get_related_projects")
    finally:
        teardown(ctx)


def test_delete_relationship():
    app, ctx, p1, p2, p3 = setup_app()
    try:
        rel = project_relationship_service.create_relationship(p1.id, p2.id, "related")
        rid = rel.id

        result = project_relationship_service.delete_relationship(rid)
        assert result is True

        # Verify gone
        results = project_relationship_service.get_related_projects(p1.id)
        assert len(results) == 0

        # Non-existent
        try:
            project_relationship_service.delete_relationship(9999)
            assert False
        except ValueError as e:
            assert "not found" in str(e)

        print("PASS: test_delete_relationship")
    finally:
        teardown(ctx)


def test_detail_page_shows_relationships():
    """Verify project detail page renders related projects."""
    app, ctx, p1, p2, p3 = setup_app()
    try:
        project_relationship_service.create_relationship(p1.id, p2.id, "depends_on")

        client = app.test_client()
        r = client.get(f"/projects/{p1.id}")
        html = r.data.decode()

        assert r.status_code == 200
        assert "Related Projects" in html
        assert "Bathroom Remodel" in html
        assert "depends_on" in html

        print("PASS: test_detail_page_shows_relationships")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_create_relationship()
    test_create_relationship_validation()
    test_prevent_duplicate()
    test_get_related_projects()
    test_delete_relationship()
    test_detail_page_shows_relationships()
    print("\nAll tests passed!")
