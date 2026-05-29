"""Service layer for Project Hierarchy (parent-child) relationships."""
from app import db
from app.models import Project, ProjectHierarchy


def get_parent_project(project_id):
    """Get the parent project of a given project, if any.

    Args:
        project_id: Integer FK of the child project.

    Returns:
        Parent Project instance, or None if no parent.
    """
    link = ProjectHierarchy.query.filter_by(child_project_id=project_id).first()
    if link:
        return Project.query.get(link.parent_project_id)
    return None


def get_child_projects(project_id):
    """Get all child (sub) projects of a given project.

    Args:
        project_id: Integer FK of the parent project.

    Returns:
        List of child Project instances.
    """
    links = ProjectHierarchy.query.filter_by(parent_project_id=project_id).all()
    child_ids = [link.child_project_id for link in links]
    if not child_ids:
        return []
    return Project.query.filter(Project.id.in_(child_ids)).all()


def link_child_to_parent(parent_project_id, child_project_id):
    """Create a parent-child relationship between two projects.

    Args:
        parent_project_id: Integer ID of the parent project.
        child_project_id: Integer ID of the child project.

    Returns:
        The newly created ProjectHierarchy instance.

    Raises:
        ValueError: If either project doesn't exist, self-link attempted,
                    child already has a parent, or circular reference detected.
    """
    # Validate both projects exist
    parent = Project.query.get(parent_project_id)
    if not parent:
        raise ValueError(f"Parent project with id {parent_project_id} not found.")

    child = Project.query.get(child_project_id)
    if not child:
        raise ValueError(f"Child project with id {child_project_id} not found.")

    # Prevent self-linking
    if parent_project_id == child_project_id:
        raise ValueError("A project cannot be its own parent.")

    # Prevent child from having multiple parents
    existing = ProjectHierarchy.query.filter_by(child_project_id=child_project_id).first()
    if existing:
        raise ValueError(
            f"Project '{child.name}' already has a parent (project id {existing.parent_project_id})."
        )

    # Prevent circular references: parent cannot be a descendant of child
    if _is_descendant_of(parent_project_id, child_project_id):
        raise ValueError(
            "Circular reference detected: the parent is already a descendant of the child."
        )

    link = ProjectHierarchy(
        parent_project_id=parent_project_id,
        child_project_id=child_project_id,
    )
    db.session.add(link)
    db.session.commit()
    return link


def unlink_child_from_parent(parent_project_id, child_project_id):
    """Remove a parent-child relationship.

    Args:
        parent_project_id: Integer ID of the parent.
        child_project_id: Integer ID of the child.

    Returns:
        True if removed successfully.

    Raises:
        ValueError: If the relationship doesn't exist.
    """
    link = ProjectHierarchy.query.filter_by(
        parent_project_id=parent_project_id,
        child_project_id=child_project_id,
    ).first()

    if not link:
        raise ValueError("No parent-child relationship found between these projects.")

    db.session.delete(link)
    db.session.commit()
    return True


def _is_descendant_of(project_id, potential_ancestor_id):
    """Check if project_id is a descendant of potential_ancestor_id.

    Walks up the hierarchy from project_id looking for potential_ancestor_id.
    Prevents circular references by detecting if linking would create a loop.

    Returns:
        True if project_id is a descendant of potential_ancestor_id.
    """
    visited = set()
    current_id = project_id

    while current_id is not None:
        if current_id in visited:
            break  # Already visited, prevent infinite loop in corrupted data
        visited.add(current_id)

        link = ProjectHierarchy.query.filter_by(child_project_id=current_id).first()
        if link is None:
            return False
        if link.parent_project_id == potential_ancestor_id:
            return True
        current_id = link.parent_project_id

    return False
