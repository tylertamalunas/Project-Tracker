"""Tests for media upload UI on project detail page."""
import os
import sys
import io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app, db
from app.models import Project, Media


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


def test_detail_has_inline_upload_form():
    app, ctx, project = setup_app()
    try:
        client = app.test_client()
        r = client.get(f"/projects/{project.id}")
        html = r.data.decode()

        assert "Upload File" in html
        assert 'enctype="multipart/form-data"' in html
        assert 'name="file"' in html
        assert 'name="media_type"' in html
        assert 'name="notes"' in html
        print("PASS: test_detail_has_inline_upload_form")
    finally:
        teardown(ctx)


def test_completed_project_no_upload_form():
    app, ctx, project = setup_app()
    try:
        project.status = "completed"
        db.session.commit()

        client = app.test_client()
        r = client.get(f"/projects/{project.id}")
        html = r.data.decode()

        assert "Upload File" not in html
        print("PASS: test_completed_project_no_upload_form")
    finally:
        teardown(ctx)


def test_media_gallery_shows_images():
    app, ctx, project = setup_app()
    try:
        # Add an image media record
        media = Media(project_id=project.id, file_path=f"{project.id}/test.jpg",
                      file_name="test.jpg", media_type="progress", notes="Before photo")
        db.session.add(media)
        db.session.commit()

        client = app.test_client()
        r = client.get(f"/projects/{project.id}")
        html = r.data.decode()

        assert "Images" in html
        assert "test.jpg" in html
        assert "Before photo" in html
        assert "card-img-top" in html  # gallery card style
        print("PASS: test_media_gallery_shows_images")
    finally:
        teardown(ctx)


def test_media_list_shows_documents():
    app, ctx, project = setup_app()
    try:
        media = Media(project_id=project.id, file_path=f"{project.id}/receipt.pdf",
                      file_name="receipt.pdf", media_type="receipt", notes="Store receipt")
        db.session.add(media)
        db.session.commit()

        client = app.test_client()
        r = client.get(f"/projects/{project.id}")
        html = r.data.decode()

        assert "Documents" in html
        assert "receipt.pdf" in html
        assert "Store receipt" in html
        assert "Download" in html
        print("PASS: test_media_list_shows_documents")
    finally:
        teardown(ctx)


def test_inline_upload_posts_correctly():
    app, ctx, project = setup_app()
    try:
        client = app.test_client()
        data = {
            "file": (io.BytesIO(b"fake"), "photo.png"),
            "media_type": "progress",
            "notes": "Test caption",
        }
        r = client.post(f"/projects/{project.id}/media/new",
                        data=data, content_type="multipart/form-data",
                        follow_redirects=False)
        assert r.status_code == 302
        m = Media.query.filter_by(project_id=project.id).first()
        assert m is not None
        assert m.media_type == "progress"
        assert m.notes == "Test caption"
        print("PASS: test_inline_upload_posts_correctly")
    finally:
        teardown(ctx)


def test_delete_media_from_detail():
    app, ctx, project = setup_app()
    try:
        media = Media(project_id=project.id, file_path=f"{project.id}/del.pdf",
                      file_name="del.pdf", media_type="document")
        db.session.add(media)
        db.session.commit()
        mid = media.id

        client = app.test_client()
        r = client.post(f"/projects/{project.id}/media/{mid}/delete", follow_redirects=False)
        assert r.status_code == 302
        assert Media.query.get(mid) is None
        print("PASS: test_delete_media_from_detail")
    finally:
        teardown(ctx)


if __name__ == "__main__":
    test_detail_has_inline_upload_form()
    test_completed_project_no_upload_form()
    test_media_gallery_shows_images()
    test_media_list_shows_documents()
    test_inline_upload_posts_correctly()
    test_delete_media_from_detail()
    print("\nAll tests passed!")
