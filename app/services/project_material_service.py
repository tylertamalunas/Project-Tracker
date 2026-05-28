"""Service layer for Project-Material association operations."""
from datetime import date
from app import db
from app.models import ProjectMaterial, Project, Material, Merchant


def list_project_materials(project_id):
    """Return all materials attached to a specific project.

    Args:
        project_id: Integer FK referencing the project.

    Returns:
        List of ProjectMaterial instances for the given project,
        ordered by created_at descending (most recent first).

    Raises:
        ValueError: If project_id is None or the project does not exist.
    """
    if project_id is None:
        raise ValueError("project_id is required.")

    project = Project.query.get(project_id)
    if not project:
        raise ValueError(f"Project with id {project_id} not found.")

    return ProjectMaterial.query.filter_by(
        project_id=project_id
    ).order_by(ProjectMaterial.created_at.desc()).all()


def get_project_material(project_material_id):
    """Get a single project-material record by ID.

    Args:
        project_material_id: Integer primary key.

    Returns:
        ProjectMaterial instance or None if not found.
    """
    return ProjectMaterial.query.get(project_material_id)


def add_material_to_project(project_id, material_id, quantity,
                            estimated_unit_price=0, actual_unit_price=None,
                            unit_of_measure="", merchant_id=None,
                            purchased_on=None, notes=""):
    """Attach a material to a project with project-specific pricing.

    Args:
        project_id: Required FK to projects.
        material_id: Required FK to materials catalog.
        quantity: Required integer > 0.
        estimated_unit_price: Price estimate per unit (>= 0).
        actual_unit_price: Actual price paid per unit (>= 0 or None if unknown).
        unit_of_measure: Unit at time of purchase (e.g. 'each', 'sqft').
        merchant_id: Optional FK to merchants (where it was purchased).
        purchased_on: Optional date or ISO string (YYYY-MM-DD).
        notes: Optional free-text notes.

    Returns:
        Newly created ProjectMaterial instance.

    Raises:
        ValueError: If validation fails (missing fields, bad values, completed project).
    """
    # Validate project exists and is editable
    project = Project.query.get(project_id)
    if not project:
        raise ValueError(f"Project with id {project_id} not found.")
    if project.status == "completed":
        raise ValueError("Cannot add materials to a completed project.")

    # Validate material exists
    material = Material.query.get(material_id)
    if not material:
        raise ValueError(f"Material with id {material_id} not found.")

    # Validate quantity
    if quantity is None or int(quantity) <= 0:
        raise ValueError("Quantity must be greater than 0.")

    # Validate prices
    if estimated_unit_price is not None and float(estimated_unit_price) < 0:
        raise ValueError("Estimated unit price must be >= 0.")
    if actual_unit_price is not None and float(actual_unit_price) < 0:
        raise ValueError("Actual unit price must be >= 0.")

    # Validate merchant if provided
    if merchant_id is not None:
        if not Merchant.query.get(merchant_id):
            raise ValueError(f"Merchant with id {merchant_id} not found.")

    project_material = ProjectMaterial(
        project_id=project_id,
        material_id=material_id,
        merchant_id=merchant_id,
        quantity=int(quantity),
        estimated_unit_price=estimated_unit_price or 0,
        actual_unit_price=actual_unit_price,
        unit_of_measure=unit_of_measure or "",
        purchased_on=_parse_date(purchased_on),
        notes=notes or "",
    )

    db.session.add(project_material)
    db.session.commit()
    return project_material


def update_project_material(project_material_id, **kwargs):
    """Update a project-material record.

    Args:
        project_material_id: Integer primary key.
        **kwargs: Fields to update. Supported: quantity, estimated_unit_price,
                  actual_unit_price, unit_of_measure, merchant_id, purchased_on, notes.

    Returns:
        Updated ProjectMaterial instance.

    Raises:
        ValueError: If record not found, project is completed, or values are invalid.
    """
    pm = ProjectMaterial.query.get(project_material_id)
    if not pm:
        raise ValueError(f"ProjectMaterial with id {project_material_id} not found.")

    # Check project is editable
    if pm.project.status == "completed":
        raise ValueError("Cannot modify materials on a completed project.")

    if "quantity" in kwargs:
        if kwargs["quantity"] is None or int(kwargs["quantity"]) <= 0:
            raise ValueError("Quantity must be greater than 0.")
        pm.quantity = int(kwargs["quantity"])

    if "estimated_unit_price" in kwargs:
        price = kwargs["estimated_unit_price"]
        if price is not None and float(price) < 0:
            raise ValueError("Estimated unit price must be >= 0.")
        pm.estimated_unit_price = price or 0

    if "actual_unit_price" in kwargs:
        price = kwargs["actual_unit_price"]
        if price is not None and float(price) < 0:
            raise ValueError("Actual unit price must be >= 0.")
        pm.actual_unit_price = price

    if "unit_of_measure" in kwargs:
        pm.unit_of_measure = kwargs["unit_of_measure"] or ""

    if "merchant_id" in kwargs:
        merch_id = kwargs["merchant_id"]
        if merch_id is not None and not Merchant.query.get(merch_id):
            raise ValueError(f"Merchant with id {merch_id} not found.")
        pm.merchant_id = merch_id

    if "purchased_on" in kwargs:
        pm.purchased_on = _parse_date(kwargs["purchased_on"])

    if "notes" in kwargs:
        pm.notes = kwargs["notes"] or ""

    db.session.commit()
    return pm


def remove_material_from_project(project_material_id):
    """Remove a material from a project.

    Args:
        project_material_id: Integer primary key.

    Returns:
        True if removed successfully.

    Raises:
        ValueError: If record not found or project is completed.
    """
    pm = ProjectMaterial.query.get(project_material_id)
    if not pm:
        raise ValueError(f"ProjectMaterial with id {project_material_id} not found.")

    if pm.project.status == "completed":
        raise ValueError("Cannot remove materials from a completed project.")

    db.session.delete(pm)
    db.session.commit()
    return True


def _parse_date(value):
    """Convert a value to a date object, or None.

    Accepts: None, date instance, or ISO format string (YYYY-MM-DD).
    """
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    return None
