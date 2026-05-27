"""Service layer for Tool Category CRUD operations."""
from app import db
from app.models import ToolCategory


def list_tool_categories():
    """Return all tool categories ordered by name.

    Returns:
        List of ToolCategory instances.
    """
    query = ToolCategory.query.order_by(ToolCategory.name)
    return query.all()


def get_tool_category(tool_category_id):
    """Get a single tool category by ID.

    Args:
        tool_category_id: Integer primary key.

    Returns:
        ToolCategory instance or None if not found.
    """
    return ToolCategory.query.get(tool_category_id)


def create_tool_category(name, description=""):
    """Create a new tool category.

    Args:
        name: Required category name. Must be unique.
        description: Optional description text.

    Returns:
        Newly created ToolCategory instance.

    Raises:
        ValueError: If name is empty or already exists.
    """
    if not name or not name.strip():
        raise ValueError("Name is required.")

    # Check uniqueness before insert for a clean error message
    existing = ToolCategory.query.filter(
        ToolCategory.name.ilike(name.strip())
    ).first()
    if existing:
        raise ValueError(f"Tool category '{name.strip()}' already exists.")

    tool_category = ToolCategory(
        name=name.strip(),
        description=description or "",
    )

    db.session.add(tool_category)
    db.session.commit()
    return tool_category


def update_tool_category(tool_category_id, **kwargs):
    """Update an existing tool category.

    Args:
        tool_category_id: Integer primary key.
        **kwargs: Fields to update. Supported: name, description.

    Returns:
        Updated ToolCategory instance.

    Raises:
        ValueError: If category not found, name is empty, or name already exists.
    """
    tool_category = ToolCategory.query.get(tool_category_id)
    if not tool_category:
        raise ValueError(f"Tool category with id {tool_category_id} not found.")

    if "name" in kwargs:
        if not kwargs["name"] or not kwargs["name"].strip():
            raise ValueError("Name is required.")
        new_name = kwargs["name"].strip()
        # Check uniqueness if name is changing
        if new_name.lower() != tool_category.name.lower():
            existing = ToolCategory.query.filter(
                ToolCategory.name.ilike(new_name)
            ).first()
            if existing:
                raise ValueError(f"Tool category '{new_name}' already exists.")
        tool_category.name = new_name

    if "description" in kwargs:
        tool_category.description = kwargs["description"] or ""

    db.session.commit()
    return tool_category


def delete_tool_category(tool_category_id):
    """Delete a tool category by ID.

    Tools referencing this category will have their category_id set to NULL
    (per ON DELETE SET NULL FK behavior).

    Args:
        tool_category_id: Integer primary key.

    Returns:
        True if deleted successfully.

    Raises:
        ValueError: If category not found.
    """
    tool_category = ToolCategory.query.get(tool_category_id)
    if not tool_category:
        raise ValueError(f"Tool category with id {tool_category_id} not found.")

    db.session.delete(tool_category)
    db.session.commit()
    return True
