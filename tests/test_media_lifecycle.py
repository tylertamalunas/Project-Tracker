"""End-to-end tests for media upload, retrieval, deletion, and link lifecycle."""
import os
import sys
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from werkzeug.datastructures import FileStorage
from app import create_app, db
from app.models import (
    Project, Material, MaterialCategory, ProjectMaterial, Media, MediaLink,
)
from app.services import media_service, media_link_service


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
    project = Project(name="Media Test", status="active")
    db.session.add(project)
    db.session.commit()

    return app, ctx, project, mat


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def _file(name="test.pdf", content=b"fake content", size=None):
    if size:
        content = b"x" * size
    return FileStorage(stream=io.BytesIO(content), filename=name, content_type="application/octet-stream")


# --- Allowed types ---

def test_upload_pdf():
    app, ctx, project, mat = setup_app()
    try:
        m = media_service.upload_file(project.id, _file("receipt.pdf"), "receipt")
        assert m.file_name == "receipt.pdf"
        assert m.media_type == "receipt"
        print("PASS: test_upload_pdf")
    finally:
        teardown(ctx)


def test_upload_jpg():
    app, ctx, project, mat = setup_app()
    try:
        m = media_service.upload_file(project.id, _file("photo.jpg"), "progress")
        assert m.file_name == "photo.jpg"
        print("PASS: test_upload_jpg")
    finally:
        teardown(ctx)


def test_upload_png():
    app, ctx, project, mat = setup_app()
    try:
        m = media_service.upload_file(project.id, _file("diagram.png"), "document")
        assert m.file_name == "diagram.png"
        print("PASS: test_upload_png")
    finally:
        teardown(ctx)


def test_upload_txt():
    app, ctx, project, mat = setup_app()
    try:
        m = media_service.upload_file(project.id, _file("notes.txt"), "other")
        assert m.file_name == "notes.txt"
        print("PASS: test_upload_txt")
    finally:
        teardown(ctx)


# --- Invalid types ---

def test_reject_exe():
    app, ctx, project, mat = setup_app()
    try:
        try:
            media_service.upload_file(project.id, _file("virus.exe"))
            assert False
        except ValueError as e:
            assert "not allowed" in str(e).lower()
        print("PASS: test_reject_exe")
    finally:
        teardown(ctx)


def test_reject_bat():
    app, ctx, project, mat = setup_app()
    try:
        try:
            media_service.upload_file(project.id, _file("script.bat"))
            assert False
        except ValueError as e:
            assert "not allowed" in str(e).lower()
        print("PASS: test_reject_bat")
    finally:
        teardown(ctx)


def test_reject_no_extension():
    app, ctx, project, mat = setup_app()
    try:
        try:
            media_service.upload_file(project.id, _file("noextension"))
            assert False
        except ValueError as e:
            assert "not allowed" in str(e).lower()
        print("PASS: test_reject_no_extension")
    finally:
        teardown(ctx)


# --- Oversize file (via route, since Flask enforces MAX_CONTENT_LENGTH) ---

def test_oversize_rejected_by_flask():
    """Flask rejects requests exceeding MAX_CONTENT_LENGTH."""
    app, ctx, project, mat = setup_app()
    try:
        # Set a tiny limit for testing
        app.config["MAX_CONTENT_LENGTH"] = 100  # 100 bytes

        client = app.test_client()
        # Send file larger than limit
        data = {"file": (io.BytesIO(b"x" * 200), "big.pdf"), "media_type": "document"}
        r = client.post(f"/projects/{project.id}/media/new",
                        data=data, content_type="multipart/form-data")
        # Flask returns 413 Request Entity Too Large
        assert r.status_code == 413
        print("PASS: test_oversize_rejected_by_flask")
    finally:
        teardown(ctx)


# --- Delete handles metadata + file ---

def test_delete_removes_file_and_metadata():
    app, ctx, project, mat = setup_app()
    try:
        m = media_service.upload_file(project.id, _file("to_delete.pdf"), "receipt")
        mid = m.id
        full_path = media_service.get_media_full_path(m)

        # File exists
        assert os.path.exists(full_path)

        # Delete
        media_service.delete_media(mid)

        # File gone
        assert not os.path.exists(full_path)
        # DB record gone
        assert Media.query.get(mid) is None
        print("PASS: test_delete_removes_file_and_metadata")
    finally:
        teardown(ctx)


def test_delete_handles_missing_file():
    """Delete succeeds even if file is already gone from disk."""
    app, ctx, project, mat = setup_app()
    try:
        m = media_service.upload_file(project.id, _file("will_vanish.pdf"), "receipt")
        mid = m.id
        full_path = media_service.get_media_full_path(m)

        # Manually remove file
        os.remove(full_path)
        assert not os.path.exists(full_path)

        # Delete should still succeed (removes DB record)
        media_service.delete_media(mid)
        assert Media.query.get(mid) is None
        print("PASS: test_delete_handles_missing_file")
    finally:
        teardown(ctx)


# --- Media links lifecycle ---

def test_full_media_link_lifecycle():
    """Upload -> link to line item -> verify link -> delete link -> delete media."""
    app, ctx, project, mat = setup_app()
    try:
        # Add a material to project
        pm = ProjectMaterial(project_id=project.id, material_id=mat.id,
                             quantity=5, estimated_unit_price=4.00)
        db.session.add(pm)
        db.session.commit()

        # Upload media
        m = media_service.upload_file(project.id, _file("receipt.pdf"), "receipt", "Paint receipt")
        assert m.id is not None

        # Link to material
        link = media_link_service.create_link(m.id, "project_material", pm.id)
        assert link.id is not None

        # Verify link
        linked_media = media_link_service.get_media_for_entity("project_material", pm.id)
        assert len(linked_media) == 1
        assert linked_media[0].id == m.id

        # Delete link
        media_link_service.delete_link(link.id)
        assert media_link_service.get_media_for_entity("project_material", pm.id) == []

        # Media still exists after link removal
        assert Media.query.get(m.id) is not None

        # Delete media
        media_service.delete_media(m.id)
        assert Media.query.get(m.id) is None

        print("PASS: test_full_media_link_lifecycle")
    finally:
        teardown(ctx)


def test_delete_media_cascades_links():
    """Deleting media removes associated media_links via FK cascade."""
    app, ctx, project, mat = setup_app()
    try:
        pm = ProjectMaterial(project_id=project.id, material_id=mat.id,
                             quantity=1, estimated_unit_price=4.00)
        db.session.add(pm)
        db.session.commit()

        m = media_service.upload_file(project.id, _file("cascade_test.pdf"), "receipt")
        link = media_link_service.create_link(m.id, "project_material", pm.id)
        link_id = link.id

        # Delete media — should cascade to link
        media_service.delete_media(m.id)
        assert MediaLink.query.get(link_id) is None
        print("PASS: test_delete_media_cascades_links")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_upload_pdf()
    test_upload_jpg()
    test_upload_png()
    test_upload_txt()
    test_reject_exe()
    test_reject_bat()
    test_reject_no_extension()
    test_oversize_rejected_by_flask()
    test_delete_removes_file_and_metadata()
    test_delete_handles_missing_file()
    test_full_media_link_lifecycle()
    test_delete_media_cascades_links()
    print("\nAll tests passed!")
