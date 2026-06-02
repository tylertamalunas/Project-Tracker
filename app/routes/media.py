"""Routes for media upload and serving."""
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, current_app
from app.models import Project
from app.services import media_service

media_bp = Blueprint("media", __name__)


@media_bp.route("/projects/<int:project_id>/media/new", methods=["GET", "POST"])
def media_upload(project_id):
    """Upload media to a project."""
    project = Project.query.get_or_404(project_id)

    if project.status == "completed":
        flash("Cannot upload media to a completed project.", "warning")
        return redirect(url_for("projects.project_detail", project_id=project_id))

    errors = []

    if request.method == "POST":
        file = request.files.get("file")
        media_type = request.form.get("media_type", "other")
        notes = request.form.get("notes", "").strip()

        try:
            media_service.upload_file(
                project_id=project_id,
                file=file,
                media_type=media_type,
                notes=notes,
            )
            flash("File uploaded successfully.", "success")
            return redirect(url_for("projects.project_detail", project_id=project_id))
        except ValueError as e:
            errors.append(str(e))

        return render_template("media/upload.html", project=project, errors=errors,
                               form_data={"media_type": media_type, "notes": notes})

    return render_template("media/upload.html", project=project, errors=[], form_data={})


@media_bp.route("/uploads/<path:filename>")
def serve_file(filename):
    """Serve uploaded files in development."""
    upload_folder = current_app.config["UPLOAD_FOLDER"]
    directory = os.path.dirname(os.path.join(upload_folder, filename))
    basename = os.path.basename(filename)
    return send_from_directory(directory, basename)


@media_bp.route("/projects/<int:project_id>/media/<int:media_id>/download")
def media_download(project_id, media_id):
    """Download a media file."""
    media = media_service.get_media(media_id)
    if not media or media.project_id != project_id:
        flash("File not found.", "danger")
        return redirect(url_for("projects.project_detail", project_id=project_id))

    upload_folder = current_app.config["UPLOAD_FOLDER"]
    full_path = os.path.join(upload_folder, media.file_path)
    directory = os.path.dirname(full_path)
    basename = os.path.basename(full_path)
    return send_from_directory(directory, basename, as_attachment=True,
                               download_name=media.file_name)


@media_bp.route("/projects/<int:project_id>/media/<int:media_id>/delete", methods=["POST"])
def media_delete(project_id, media_id):
    """Delete a media file."""
    try:
        media_service.delete_media(media_id)
        flash("File deleted.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("projects.project_detail", project_id=project_id))
