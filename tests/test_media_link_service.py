"""Tests for media link service."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import (
    Project, Material, Tool, MaterialCategory, ToolCategory,
    ProjectMaterial, ProjectTool, Media, MediaLink,
)
from app.services import media_link_service


def setup_app():
    app = create_app()
    ctx = app.app_context()
    ctx.push()

    cat = MaterialCategory(name="Lumber")
    tcat = ToolCategory(name="Power Tools")
    db.session.add_all([cat, tcat])
    db.session.commit()

    mat = Material(name="2x4", default_price=4.00, category_id=cat.id)
    tool = Tool(name="Drill", default_price=99.00, category_id=tcat.id)
    db.session.add_all([mat, tool])
    db.session.commit()

    project = Project(name="Test", status="active")
    db.session.add(project)
    db.session.commit()

    pm = ProjectMaterial(project_id=project.id, material_id=mat.id, quantity=5, estimated_unit_price=4.00)
    pt = ProjectTool(project_id=project.id, tool_id=tool.id, quantity=1, already_owned=False, estimated_unit_price=99.00)
    media = Media(project_id=project.id, file_path=f"{project.id}/receipt.pdf", file_name="receipt.pdf", media_type="receipt")
    db.session.add_all([pm, pt, media])
    db.session.commit()

    return app, ctx, project, pm, pt, media


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def test_create_link_to_material():
    app, ctx, project, pm, pt, media = setup_app()
    try:
        link = media_link_service.create_link(media.id, "project_material", pm.id)
        assert link.id is not None
        assert link.media_id == media.id
        assert link.linked_entity_type == "project_material"
        assert link.linked_entity_id == pm.id
        print("PASS: test_create_link_to_material")
    finally:
        teardown(ctx)


def test_create_link_to_tool():
    app, ctx, project, pm, pt, media = setup_app()
    try:
        link = media_link_service.create_link(media.id, "project_tool", pt.id)
        assert link.linked_entity_type == "project_tool"
        assert link.linked_entity_id == pt.id
        print("PASS: test_create_link_to_tool")
    finally:
        teardown(ctx)


def test_prevent_duplicate_link():
    app, ctx, project, pm, pt, media = setup_app()
    try:
        media_link_service.create_link(media.id, "project_material", pm.id)
        try:
            media_link_service.create_link(media.id, "project_material", pm.id)
            assert False
        except ValueError as e:
            assert "already linked" in str(e).lower()
        print("PASS: test_prevent_duplicate_link")
    finally:
        teardown(ctx)


def test_invalid_entity_type():
    app, ctx, project, pm, pt, media = setup_app()
    try:
        try:
            media_link_service.create_link(media.id, "invalid_type", pm.id)
            assert False
        except ValueError as e:
            assert "invalid entity type" in str(e).lower()
        print("PASS: test_invalid_entity_type")
    finally:
        teardown(ctx)


def test_cross_project_rejected():
    app, ctx, project, pm, pt, media = setup_app()
    try:
        # Create a second project with its own material
        other_project = Project(name="Other", status="active")
        db.session.add(other_project)
        db.session.commit()
        other_pm = ProjectMaterial(project_id=other_project.id, material_id=pm.material_id,
                                   quantity=1, estimated_unit_price=4.00)
        db.session.add(other_pm)
        db.session.commit()

        # Try to link media from project 1 to a line item on project 2
        try:
            media_link_service.create_link(media.id, "project_material", other_pm.id)
            assert False
        except ValueError as e:
            assert "same project" in str(e).lower()
        print("PASS: test_cross_project_rejected")
    finally:
        teardown(ctx)


def test_get_media_for_entity():
    app, ctx, project, pm, pt, media = setup_app()
    try:
        media_link_service.create_link(media.id, "project_material", pm.id)

        results = media_link_service.get_media_for_entity("project_material", pm.id)
        assert len(results) == 1
        assert results[0].file_name == "receipt.pdf"

        # No links for tool
        assert media_link_service.get_media_for_entity("project_tool", pt.id) == []
        print("PASS: test_get_media_for_entity")
    finally:
        teardown(ctx)


def test_delete_link():
    app, ctx, project, pm, pt, media = setup_app()
    try:
        link = media_link_service.create_link(media.id, "project_material", pm.id)
        lid = link.id

        result = media_link_service.delete_link(lid)
        assert result is True
        assert MediaLink.query.get(lid) is None

        # Non-existent
        try:
            media_link_service.delete_link(9999)
            assert False
        except ValueError as e:
            assert "not found" in str(e)
        print("PASS: test_delete_link")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_create_link_to_material()
    test_create_link_to_tool()
    test_prevent_duplicate_link()
    test_invalid_entity_type()
    test_cross_project_rejected()
    test_get_media_for_entity()
    test_delete_link()
    print("\nAll tests passed!")
