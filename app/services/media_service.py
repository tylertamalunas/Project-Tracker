"""Service layer for media file upload and management.

Files are stored locally under the configured UPLOAD_FOLDER in a
project-specific subdirectory: uploads/<project_id>/<filename>
"""
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from app import db
from app.models import Media, Project

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf", "doc", "docx", "txt"}
ALLOWED_MEDIA_TYPES = ("receipt", "progress", "document", "other")


def _allowed_file(filename):
    """Check if file extension is permitted."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _get_upload_path(project_id):
    """Get the upload directory for a project, creating it if needed."""
    base = current_app.config["UPLOAD_FOLDER"]
    project_dir = os.path.join(base, str(project_id))
    os.makedirs(project_dir, exist_ok=True)
    return project_dir


def _safe_filename(filename):
    """Normalize a filename: secure it and prepend a UUID to avoid collisions."""
    safe = secure_filename(filename)
    if not safe:
        safe = "unnamed_file"
    # Prepend short UUID to avoid overwriting files with the same name
    prefix = uuid.uuid4().hex[:8]
    return f"{prefix}_{safe}"


def upload_file(project_id, file, media_type="other", notes=""):
    """Upload a file and attach it to a project.

    Args:
        project_id: Integer project FK.
        file: Werkzeug FileStorage object from the form.
        media_type: One of: receipt, progress, document, other.
        notes: Optional description.

    Returns:
        Newly created Media instance.

    Raises:
        ValueError: If project not found, project completed, no file,
                    invalid extension, or invalid media type.
    """
    # Validate project
    project = Project.query.get(project_id)
    if not project:
        raise ValueError(f"Project with id {project_id} not found.")
    if project.status == "completed":
        raise ValueError("Cannot upload media to a completed project.")

    # Validate file
    if not file or not file.filename:
        raise ValueError("No file selected.")
    if not _allowed_file(file.filename):
        raise ValueError(
            f"File type not allowed. Accepted: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Validate media type
    if media_type not in ALLOWED_MEDIA_TYPES:
        raise ValueError(f"Invalid media type. Must be one of: {', '.join(ALLOWED_MEDIA_TYPES)}")

    # Save file to disk
    safe_name = _safe_filename(file.filename)
    project_dir = _get_upload_path(project_id)
    file_path = os.path.join(project_dir, safe_name)
    file.save(file_path)

    # Store relative path for portability
    relative_path = os.path.join(str(project_id), safe_name)

    # Save metadata to DB
    media = Media(
        project_id=project_id,
        file_path=relative_path,
        file_name=secure_filename(file.filename),
        media_type=media_type,
        notes=notes or "",
    )
    db.session.add(media)
    db.session.commit()
    return media


def list_project_media(project_id):
    """Get all media records for a project.

    Args:
        project_id: Integer project FK.

    Returns:
        List of Media instances ordered by created_at descending.
    """
    return Media.query.filter_by(
        project_id=project_id
    ).order_by(Media.created_at.desc()).all()


def get_media(media_id):
    """Get a single media record by ID."""
    return Media.query.get(media_id)


def get_media_full_path(media):
    """Get the full filesystem path for a media record.

    Args:
        media: Media instance.

    Returns:
        Absolute file path string.
    """
    base = current_app.config["UPLOAD_FOLDER"]
    return os.path.join(base, media.file_path)


def delete_media(media_id):
    """Delete a media record and its file from disk.

    Args:
        media_id: Integer primary key.

    Returns:
        True if deleted.

    Raises:
        ValueError: If media not found or project is completed.
    """
    media = Media.query.get(media_id)
    if not media:
        raise ValueError(f"Media with id {media_id} not found.")

    if media.project.status == "completed":
        raise ValueError("Cannot delete media from a completed project.")

    # Remove file from disk
    full_path = get_media_full_path(media)
    if os.path.exists(full_path):
        os.remove(full_path)

    db.session.delete(media)
    db.session.commit()
    return True
