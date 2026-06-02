"""Tests for media upload service."""
import os
import sys
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import Project, Media
from app.services import media_service


def setup_app():
    app = create_app()
    ctx = app.app_context()
    ctx.push()

    project = Project(name="Test Project", status="active")
    db.session.add(project)
    db.session.commit()

    return app, ctx, project


def teardown(ctx):
    db.session.remove()
    ctx.pop()


def _make_file(filename="test.pdf", content=b"fake file content"):
    """Create a fake FileStorage for testing."""
    from werkzeug.datastructures import FileStorage
    return FileStorage(
        stream=io.BytesIO(content),
        filename=filename,
        content_type="application/pdf",
    )


def test_upload_file():
    app, ctx, project = setup_app()
    try:
        file = _make_file("receipt.pdf")
        media = media_service.upload_file(
            project_id=project.id,
            file=file,
            media_type="receipt",
            notes="Store receipt",
        )
        assert media.id is not None
        assert media.project_id == project.id
        assert media.file_name == "receipt.pdf"
        assert media.media_type == "receipt"
        assert media.notes == "Store receipt"
        # File should exist on disk
        full_path = media_service.get_media_full_path(media)
        assert os.path.exists(full_path)
        print("PASS: test_upload_file")
    finally:
        teardown(ctx)


def test_unsafe_filename_normalized():
    app, ctx, project = setup_app()
    try:
        file = _make_file("../../etc/passwd.pdf")
        media = media_service.upload_file(project_id=project.id, file=file)
        # Filename should be sanitized
        assert ".." not in media.file_path
        assert "etc" not in media.file_path or "passwd" in media.file_name
        assert media.file_name == "etc_passwd.pdf" or "passwd" in media.file_name
        print("PASS: test_unsafe_filename_normalized")
    finally:
        teardown(ctx)


def test_file_extension_validation():
    app, ctx, project = setup_app()
    try:
        file = _make_file("malware.exe")
        try:
            media_service.upload_file(project_id=project.id, file=file)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "not allowed" in str(e).lower()
        print("PASS: test_file_extension_validation")
    finally:
        teardown(ctx)


def test_no_file_raises():
    app, ctx, project = setup_app()
    try:
        from werkzeug.datastructures import FileStorage
        empty = FileStorage(stream=io.BytesIO(b""), filename="")
        try:
            media_service.upload_file(project_id=project.id, file=empty)
            assert False
        except ValueError as e:
            assert "no file" in str(e).lower()
        print("PASS: test_no_file_raises")
    finally:
        teardown(ctx)


def test_completed_project_rejected():
    app, ctx, project = setup_app()
    try:
        project.status = "completed"
        db.session.commit()

        file = _make_file("test.pdf")
        try:
            media_service.upload_file(project_id=project.id, file=file)
            assert False
        except ValueError as e:
            assert "completed" in str(e).lower()
        print("PASS: test_completed_project_rejected")
    finally:
        teardown(ctx)


def test_list_project_media():
    app, ctx, project = setup_app()
    try:
        media_service.upload_file(project_id=project.id, file=_make_file("a.pdf"))
        media_service.upload_file(project_id=project.id, file=_make_file("b.jpg"))

        results = media_service.list_project_media(project.id)
        assert len(results) == 2
        print("PASS: test_list_project_media")
    finally:
        teardown(ctx)


def test_delete_media():
    app, ctx, project = setup_app()
    try:
        media = media_service.upload_file(project_id=project.id, file=_make_file("to_delete.pdf"))
        full_path = media_service.get_media_full_path(media)
        mid = media.id

        assert os.path.exists(full_path)
        media_service.delete_media(mid)
        assert not os.path.exists(full_path)
        assert Media.query.get(mid) is None
        print("PASS: test_delete_media")
    finally:
        teardown(ctx)


def test_upload_route():
    app, ctx, project = setup_app()
    try:
        client = app.test_client()
        r = client.get(f"/projects/{project.id}/media/new")
        assert r.status_code == 200
        assert "Upload" in r.data.decode()

        # POST with file
        data = {
            "file": (_make_file("test.png").stream, "test.png"),
            "media_type": "progress",
            "notes": "Before photo",
        }
        r2 = client.post(f"/projects/{project.id}/media/new",
                         data=data, content_type="multipart/form-data",
                         follow_redirects=False)
        assert r2.status_code == 302
        assert Media.query.filter_by(project_id=project.id).count() == 1
        print("PASS: test_upload_route")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_upload_file()
    test_unsafe_filename_normalized()
    test_file_extension_validation()
    test_no_file_raises()
    test_completed_project_rejected()
    test_list_project_media()
    test_delete_media()
    test_upload_route()
    print("\nAll tests passed!")
