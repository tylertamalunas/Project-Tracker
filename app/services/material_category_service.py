"""Service layer for Material Category CRUD operations."""
from app import db
from app.models import MaterialCategory


def list_material_categories():
    """Return all material categories ordered by name.

    Returns:
        List of MaterialCategory instances.
    """
    query = MaterialCategory.query.order_by(MaterialCategory.name)
    return query.all()


def get_material_category(material_category_id):
    """Get a single material category by ID.

    Args:
        material_category_id: Integer primary key.

    Returns:
        MaterialCategory instance or None if not found.
    """
    return MaterialCategory.query.get(material_category_id)


def create_material_category(name, description=""):
    """Create a new material category.

    Args:
        name: Required category name. Must be unique.
        description: Optional description text.

    Returns:
        Newly created MaterialCategory instance.

    Raises:
        ValueError: If name is empty or already exists.
    """
    if not name or not name.strip():
        raise ValueError("Name is required.")

    # Check uniqueness before insert for a clean error message
    existing = MaterialCategory.query.filter(
        MaterialCategory.name.ilike(name.strip())
    ).first()
    if existing:
        raise ValueError(f"Material category '{name.strip()}' already exists.")

    material_category = MaterialCategory(
        name=name.strip(),
        description=description or "",
    )

    db.session.add(material_category)
    db.session.commit()
    return material_category


def update_material_category(material_category_id, **kwargs):
    """Update an existing material category.

    Args:
        material_category_id: Integer primary key.
        **kwargs: Fields to update. Supported: name, description.

    Returns:
        Updated MaterialCategory instance.

    Raises:
        ValueError: If category not found, name is empty, or name already exists.
    """
    material_category = MaterialCategory.query.get(material_category_id)
    if not material_category:
        raise ValueError(f"Material category with id {material_category_id} not found.")

    if "name" in kwargs:
        if not kwargs["name"] or not kwargs["name"].strip():
            raise ValueError("Name is required.")
        new_name = kwargs["name"].strip()
        # Check uniqueness if name is changing
        if new_name.lower() != material_category.name.lower():
            existing = MaterialCategory.query.filter(
                MaterialCategory.name.ilike(new_name)
            ).first()
            if existing:
                raise ValueError(f"Material category '{new_name}' already exists.")
        material_category.name = new_name

    if "description" in kwargs:
        material_category.description = kwargs["description"] or ""

    db.session.commit()
    return material_category


def delete_material_category(material_category_id):
    """Delete a material category by ID.

    Materials referencing this category will have their category_id set to NULL
    (per ON DELETE SET NULL FK behavior).

    Args:
        material_category_id: Integer primary key.

    Returns:
        True if deleted successfully.

    Raises:
        ValueError: If category not found.
    """
    material_category = MaterialCategory.query.get(material_category_id)
    if not material_category:
        raise ValueError(f"Material category with id {material_category_id} not found.")

    db.session.delete(material_category)
    db.session.commit()
    return True
