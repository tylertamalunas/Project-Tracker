"""Service layer for linking media to specific project line items.

Media can be linked to:
- project_material: a specific material row on a project
- project_tool: a specific tool row on a project
"""
from app import db
from app.models import MediaLink, Media, ProjectMaterial, ProjectTool

ALLOWED_ENTITY_TYPES = ("project_material", "project_tool")


def get_links_for_media(media_id):
    """Get all links for a specific media record.

    Returns:
        List of MediaLink instances.
    """
    return MediaLink.query.filter_by(media_id=media_id).all()


def get_links_for_entity(entity_type, entity_id):
    """Get all media linked to a specific entity.

    Args:
        entity_type: 'project_material' or 'project_tool'.
        entity_id: Integer ID of the entity row.

    Returns:
        List of MediaLink instances (with .media relationship loaded).
    """
    return MediaLink.query.filter_by(
        linked_entity_type=entity_type,
        linked_entity_id=entity_id,
    ).all()


def get_media_for_entity(entity_type, entity_id):
    """Get Media records linked to a specific entity.

    Returns:
        List of Media instances linked to the entity.
    """
    links = get_links_for_entity(entity_type, entity_id)
    return [link.media for link in links if link.media]


def create_link(media_id, entity_type, entity_id):
    """Link a media file to a specific line item.

    Args:
        media_id: Integer FK to media table.
        entity_type: 'project_material' or 'project_tool'.
        entity_id: Integer ID of the target row.

    Returns:
        Newly created MediaLink instance.

    Raises:
        ValueError: If media not found, invalid entity type, entity not found,
                    or duplicate link.
    """
    # Validate media exists
    media = Media.query.get(media_id)
    if not media:
        raise ValueError(f"Media with id {media_id} not found.")

    # Validate entity type
    if entity_type not in ALLOWED_ENTITY_TYPES:
        raise ValueError(
            f"Invalid entity type '{entity_type}'. Must be one of: {', '.join(ALLOWED_ENTITY_TYPES)}"
        )

    # Validate entity exists
    if entity_type == "project_material":
        entity = ProjectMaterial.query.get(entity_id)
        if not entity:
            raise ValueError(f"ProjectMaterial with id {entity_id} not found.")
        # Ensure media belongs to the same project
        if media.project_id != entity.project_id:
            raise ValueError("Media and line item must belong to the same project.")
    elif entity_type == "project_tool":
        entity = ProjectTool.query.get(entity_id)
        if not entity:
            raise ValueError(f"ProjectTool with id {entity_id} not found.")
        if media.project_id != entity.project_id:
            raise ValueError("Media and line item must belong to the same project.")

    # Prevent duplicate links
    existing = MediaLink.query.filter_by(
        media_id=media_id,
        linked_entity_type=entity_type,
        linked_entity_id=entity_id,
    ).first()
    if existing:
        raise ValueError("This media is already linked to this item.")

    link = MediaLink(
        media_id=media_id,
        linked_entity_type=entity_type,
        linked_entity_id=entity_id,
    )
    db.session.add(link)
    db.session.commit()
    return link


def delete_link(link_id):
    """Remove a media link.

    Args:
        link_id: Integer primary key of MediaLink.

    Returns:
        True if deleted.

    Raises:
        ValueError: If link not found.
    """
    link = MediaLink.query.get(link_id)
    if not link:
        raise ValueError(f"MediaLink with id {link_id} not found.")

    db.session.delete(link)
    db.session.commit()
    return True
