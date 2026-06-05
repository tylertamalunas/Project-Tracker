"""Edge case tests for project hierarchy and related-project links."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import Project
from app.services import project_hierarchy_service, project_relationship_service


def setup_app():
    app = create_app()
    ctx = app.app_context()
    ctx.push()

    p1 = Project(name="Project A", status="active")
    p2 = Project(name="Project B", status="active")
    p3 = Project(name="Project C", status="planned")
    p4 = Project(name="Project D", status="completed")
    db.session.add_all([p1, p2, p3, p4])
    db.session.commit()

    return app, ctx, p1, p2, p3, p4


def teardown(ctx):
    db.session.remove()
    ctx.pop()


# === Hierarchy edge cases ===

def test_hierarchy_self_link_rejected():
    """A project cannot be its own parent."""
    app, ctx, p1, p2, p3, p4 = setup_app()
    try:
        try:
            project_hierarchy_service.link_child_to_parent(p1.id, p1.id)
            assert False
        except ValueError as e:
            assert "own parent" in str(e).lower()
        print("PASS: test_hierarchy_self_link_rejected")
    finally:
        teardown(ctx)


def test_hierarchy_direct_circular():
    """A->B then B->A is rejected (direct circle)."""
    app, ctx, p1, p2, p3, p4 = setup_app()
    try:
        project_hierarchy_service.link_child_to_parent(p1.id, p2.id)  # A is parent of B
        try:
            project_hierarchy_service.link_child_to_parent(p2.id, p1.id)  # B tries to parent A
            assert False
        except ValueError as e:
            assert "circular" in str(e).lower()
        print("PASS: test_hierarchy_direct_circular")
    finally:
        teardown(ctx)


def test_hierarchy_indirect_circular():
    """A->B->C then C->A is rejected (3-level circle)."""
    app, ctx, p1, p2, p3, p4 = setup_app()
    try:
        project_hierarchy_service.link_child_to_parent(p1.id, p2.id)  # A parent of B
        project_hierarchy_service.link_child_to_parent(p2.id, p3.id)  # B parent of C
        try:
            project_hierarchy_service.link_child_to_parent(p3.id, p1.id)  # C tries to parent A
            assert False
        except ValueError as e:
            assert "circular" in str(e).lower()
        print("PASS: test_hierarchy_indirect_circular")
    finally:
        teardown(ctx)


def test_hierarchy_sibling_allowed():
    """Two children under the same parent is valid (siblings)."""
    app, ctx, p1, p2, p3, p4 = setup_app()
    try:
        project_hierarchy_service.link_child_to_parent(p1.id, p2.id)  # A parent of B
        project_hierarchy_service.link_child_to_parent(p1.id, p3.id)  # A parent of C
        children = project_hierarchy_service.get_child_projects(p1.id)
        assert len(children) == 2
        print("PASS: test_hierarchy_sibling_allowed")
    finally:
        teardown(ctx)


def test_hierarchy_child_cannot_have_two_parents():
    """A child can only have one parent."""
    app, ctx, p1, p2, p3, p4 = setup_app()
    try:
        project_hierarchy_service.link_child_to_parent(p1.id, p3.id)  # A parent of C
        try:
            project_hierarchy_service.link_child_to_parent(p2.id, p3.id)  # B also tries to parent C
            assert False
        except ValueError as e:
            assert "already has a parent" in str(e).lower()
        print("PASS: test_hierarchy_child_cannot_have_two_parents")
    finally:
        teardown(ctx)


def test_hierarchy_unlink_then_relink():
    """After unlinking, the child can be linked to a new parent."""
    app, ctx, p1, p2, p3, p4 = setup_app()
    try:
        project_hierarchy_service.link_child_to_parent(p1.id, p3.id)
        project_hierarchy_service.unlink_child_from_parent(p1.id, p3.id)

        # Now C is free — can link to B
        project_hierarchy_service.link_child_to_parent(p2.id, p3.id)
        parent = project_hierarchy_service.get_parent_project(p3.id)
        assert parent.id == p2.id
        print("PASS: test_hierarchy_unlink_then_relink")
    finally:
        teardown(ctx)


# === Related project edge cases ===

def test_relationship_self_link_rejected():
    """A project cannot be related to itself."""
    app, ctx, p1, p2, p3, p4 = setup_app()
    try:
        try:
            project_relationship_service.create_relationship(p1.id, p1.id, "related")
            assert False
        except ValueError as e:
            assert "itself" in str(e).lower()
        print("PASS: test_relationship_self_link_rejected")
    finally:
        teardown(ctx)


def test_relationship_bidirectional_display():
    """A relationship shows on both projects (outgoing and incoming)."""
    app, ctx, p1, p2, p3, p4 = setup_app()
    try:
        project_relationship_service.create_relationship(
            p1.id, p2.id, "depends_on", "A depends on B")

        # From A's perspective: outgoing to B
        a_related = project_relationship_service.get_related_projects(p1.id)
        assert len(a_related) == 1
        assert a_related[0]["project"].id == p2.id
        assert a_related[0]["direction"] == "outgoing"
        assert a_related[0]["relationship_type"] == "depends_on"

        # From B's perspective: incoming from A
        b_related = project_relationship_service.get_related_projects(p2.id)
        assert len(b_related) == 1
        assert b_related[0]["project"].id == p1.id
        assert b_related[0]["direction"] == "incoming"
        assert b_related[0]["relationship_type"] == "depends_on"

        print("PASS: test_relationship_bidirectional_display")
    finally:
        teardown(ctx)


def test_relationship_duplicate_both_directions():
    """Same type between A->B prevents B->A (checked both directions)."""
    app, ctx, p1, p2, p3, p4 = setup_app()
    try:
        project_relationship_service.create_relationship(p1.id, p2.id, "similar_to")
        try:
            project_relationship_service.create_relationship(p2.id, p1.id, "similar_to")
            assert False
        except ValueError as e:
            assert "already exists" in str(e).lower()
        print("PASS: test_relationship_duplicate_both_directions")
    finally:
        teardown(ctx)


def test_relationship_different_types_allowed():
    """Same pair can have multiple relationships of different types."""
    app, ctx, p1, p2, p3, p4 = setup_app()
    try:
        project_relationship_service.create_relationship(p1.id, p2.id, "similar_to")
        project_relationship_service.create_relationship(p1.id, p2.id, "depends_on")

        related = project_relationship_service.get_related_projects(p1.id)
        assert len(related) == 2
        types = {r["relationship_type"] for r in related}
        assert types == {"similar_to", "depends_on"}
        print("PASS: test_relationship_different_types_allowed")
    finally:
        teardown(ctx)


def test_relationship_renders_on_detail_page():
    """Both sides of a relationship render on project detail pages."""
    app, ctx, p1, p2, p3, p4 = setup_app()
    try:
        project_relationship_service.create_relationship(
            p1.id, p2.id, "blocks", "A blocks B")

        client = app.test_client()

        # Project A detail
        r1 = client.get(f"/projects/{p1.id}")
        html1 = r1.data.decode()
        assert "Related Projects" in html1
        assert "Project B" in html1
        assert "blocks" in html1

        # Project B detail
        r2 = client.get(f"/projects/{p2.id}")
        html2 = r2.data.decode()
        assert "Related Projects" in html2
        assert "Project A" in html2
        assert "blocks" in html2

        print("PASS: test_relationship_renders_on_detail_page")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    # Hierarchy
    test_hierarchy_self_link_rejected()
    test_hierarchy_direct_circular()
    test_hierarchy_indirect_circular()
    test_hierarchy_sibling_allowed()
    test_hierarchy_child_cannot_have_two_parents()
    test_hierarchy_unlink_then_relink()
    # Relationships
    test_relationship_self_link_rejected()
    test_relationship_bidirectional_display()
    test_relationship_duplicate_both_directions()
    test_relationship_different_types_allowed()
    test_relationship_renders_on_detail_page()
    print("\nAll tests passed!")
