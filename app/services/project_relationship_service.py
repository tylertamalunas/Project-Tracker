"""Service layer for non-hierarchical project relationships (related, depends_on, etc.)."""
from app import db
from app.models import Project, ProjectRelationship

ALLOWED_TYPES = ("related", "depends_on", "similar_to", "blocks", "follow_up")


def get_related_projects(project_id):
    """Get all projects related to a given project (both directions).

    Returns relationships where this project is either the source or target,
    so relationships are effectively bidirectional for display purposes.

    Args:
        project_id: Integer project primary key.

    Returns:
        List of dicts with keys: relationship_id, project (the *other* project),
        relationship_type, notes, direction ('outgoing' or 'incoming').
    """
    outgoing = ProjectRelationship.query.filter_by(project_id=project_id).all()
    incoming = ProjectRelationship.query.filter_by(related_project_id=project_id).all()

    results = []
    for rel in outgoing:
        other = Project.query.get(rel.related_project_id)
        results.append({
            "relationship_id": rel.id,
            "project": other,
            "relationship_type": rel.relationship_type,
            "notes": rel.notes,
            "direction": "outgoing",
        })
    for rel in incoming:
        other = Project.query.get(rel.project_id)
        results.append({
            "relationship_id": rel.id,
            "project": other,
            "relationship_type": rel.relationship_type,
            "notes": rel.notes,
            "direction": "incoming",
        })

    return results


def create_relationship(project_id, related_project_id, relationship_type="related", notes=""):
    """Create a relationship between two projects.

    Args:
        project_id: Source project ID.
        related_project_id: Target project ID.
        relationship_type: One of: related, depends_on, similar_to, blocks, follow_up.
        notes: Optional description of the relationship.

    Returns:
        Newly created ProjectRelationship instance.

    Raises:
        ValueError: If projects don't exist, self-link, invalid type, or duplicate.
    """
    # Validate projects exist
    project = Project.query.get(project_id)
    if not project:
        raise ValueError(f"Project with id {project_id} not found.")

    related = Project.query.get(related_project_id)
    if not related:
        raise ValueError(f"Related project with id {related_project_id} not found.")

    # Prevent self-link
    if project_id == related_project_id:
        raise ValueError("A project cannot be related to itself.")

    # Validate relationship type
    if relationship_type not in ALLOWED_TYPES:
        raise ValueError(
            f"Invalid relationship type '{relationship_type}'. "
            f"Must be one of: {', '.join(ALLOWED_TYPES)}"
        )

    # Prevent duplicate (same pair + same type, either direction)
    existing = ProjectRelationship.query.filter(
        db.or_(
            db.and_(
                ProjectRelationship.project_id == project_id,
                ProjectRelationship.related_project_id == related_project_id,
                ProjectRelationship.relationship_type == relationship_type,
            ),
            db.and_(
                ProjectRelationship.project_id == related_project_id,
                ProjectRelationship.related_project_id == project_id,
                ProjectRelationship.relationship_type == relationship_type,
            ),
        )
    ).first()
    if existing:
        raise ValueError(
            f"A '{relationship_type}' relationship already exists between these projects."
        )

    rel = ProjectRelationship(
        project_id=project_id,
        related_project_id=related_project_id,
        relationship_type=relationship_type,
        notes=notes or "",
    )
    db.session.add(rel)
    db.session.commit()
    return rel


def delete_relationship(relationship_id):
    """Remove a project relationship.

    Args:
        relationship_id: Integer primary key of the relationship.

    Returns:
        True if deleted.

    Raises:
        ValueError: If relationship not found.
    """
    rel = ProjectRelationship.query.get(relationship_id)
    if not rel:
        raise ValueError(f"Relationship with id {relationship_id} not found.")

    db.session.delete(rel)
    db.session.commit()
    return True
