"""Service layer for Material catalog CRUD operations."""
from app import db
from app.models import Material, MaterialCategory, Merchant


def list_materials(active_only=None, category_id=None):
    """Return materials with optional filters.

    Args:
        active_only: True for active items, False for inactive, None for all.
        category_id: Filter by category FK.

    Returns:
        List of Material instances ordered by name.
    """
    query = Material.query.order_by(Material.name)

    if active_only is True:
        query = query.filter_by(is_active=True)
    elif active_only is False:
        query = query.filter_by(is_active=False)

    if category_id is not None:
        query = query.filter_by(category_id=category_id)

    return query.all()


def get_material(material_id):
    """Get a single material by ID.

    Returns:
        Material instance or None.
    """
    return Material.query.get(material_id)


def create_material(name, default_price=0, unit_of_measure="", sku="",
                    brand="", category_id=None, merchant_id=None,
                    notes="", is_active=True):
    """Create a new material in the global catalog.

    Args:
        name: Required material name.
        default_price: Default price (must be >= 0).
        unit_of_measure: e.g. 'each', 'sqft', 'gallon'.
        sku: Optional SKU/part number.
        brand: Optional brand name.
        category_id: FK to material_categories (optional).
        merchant_id: FK to merchants (optional).
        notes: Optional free-text notes.
        is_active: Whether material is active in catalog. Defaults True.

    Returns:
        The newly created Material instance.

    Raises:
        ValueError: If name is empty or default_price is negative.
    """
    if not name or not name.strip():
        raise ValueError("Material name is required.")

    if default_price is not None and float(default_price) < 0:
        raise ValueError("Default price must be >= 0.")

    # Validate FK references if provided
    if category_id is not None:
        if not MaterialCategory.query.get(category_id):
            raise ValueError(f"Material category with id {category_id} not found.")

    if merchant_id is not None:
        if not Merchant.query.get(merchant_id):
            raise ValueError(f"Merchant with id {merchant_id} not found.")

    material = Material(
        name=name.strip(),
        default_price=default_price or 0,
        unit_of_measure=unit_of_measure or "",
        sku=sku or "",
        brand=brand or "",
        category_id=category_id,
        merchant_id=merchant_id,
        notes=notes or "",
        is_active=is_active,
    )
    db.session.add(material)
    db.session.commit()
    return material


def update_material(material_id, **kwargs):
    """Update an existing material.

    Args:
        material_id: Integer primary key.
        **kwargs: Fields to update. Supported: name, default_price,
                  unit_of_measure, sku, brand, category_id, merchant_id,
                  notes, is_active.

    Returns:
        The updated Material instance.

    Raises:
        ValueError: If material not found, name is empty, or price is negative.
    """
    material = Material.query.get(material_id)
    if not material:
        raise ValueError(f"Material with id {material_id} not found.")

    if "name" in kwargs:
        if not kwargs["name"] or not kwargs["name"].strip():
            raise ValueError("Material name is required.")
        material.name = kwargs["name"].strip()

    if "default_price" in kwargs:
        price = kwargs["default_price"]
        if price is not None and float(price) < 0:
            raise ValueError("Default price must be >= 0.")
        material.default_price = price or 0

    if "unit_of_measure" in kwargs:
        material.unit_of_measure = kwargs["unit_of_measure"] or ""

    if "sku" in kwargs:
        material.sku = kwargs["sku"] or ""

    if "brand" in kwargs:
        material.brand = kwargs["brand"] or ""

    if "category_id" in kwargs:
        cat_id = kwargs["category_id"]
        if cat_id is not None and not MaterialCategory.query.get(cat_id):
            raise ValueError(f"Material category with id {cat_id} not found.")
        material.category_id = cat_id

    if "merchant_id" in kwargs:
        merch_id = kwargs["merchant_id"]
        if merch_id is not None and not Merchant.query.get(merch_id):
            raise ValueError(f"Merchant with id {merch_id} not found.")
        material.merchant_id = merch_id

    if "notes" in kwargs:
        material.notes = kwargs["notes"] or ""

    if "is_active" in kwargs:
        material.is_active = bool(kwargs["is_active"])

    db.session.commit()
    return material


def delete_material(material_id):
    """Delete a material by ID.

    Args:
        material_id: Integer primary key.

    Returns:
        True if deleted successfully.

    Raises:
        ValueError: If material not found.
    """
    material = Material.query.get(material_id)
    if not material:
        raise ValueError(f"Material with id {material_id} not found.")

    db.session.delete(material)
    db.session.commit()
    return True
