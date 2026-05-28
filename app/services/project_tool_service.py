"""Service layer for Project-Tool association operations."""
from datetime import date
from app import db
from app.models import ProjectTool, Project, Tool, Merchant


def list_project_tools(project_id):
    """Return all tools attached to a specific project.

    Args:
        project_id: Integer FK referencing the project.

    Returns:
        List of ProjectTool instances ordered by created_at descending.

    Raises:
        ValueError: If project does not exist.
    """
    if project_id is None:
        raise ValueError("project_id is required.")

    project = Project.query.get(project_id)
    if not project:
        raise ValueError(f"Project with id {project_id} not found.")

    return ProjectTool.query.filter_by(
        project_id=project_id
    ).order_by(ProjectTool.created_at.desc()).all()


def get_project_tool(project_tool_id):
    """Get a single project-tool record by ID.

    Returns:
        ProjectTool instance or None.
    """
    return ProjectTool.query.get(project_tool_id)


def add_tool_to_project(project_id, tool_id, quantity=1, already_owned=False,
                        estimated_unit_price=0, actual_unit_price=None,
                        merchant_id=None, purchased_on=None, notes=""):
    """Attach a tool to a project with project-specific pricing.

    Args:
        project_id: Required FK to projects.
        tool_id: Required FK to tools catalog.
        quantity: Integer > 0 (default 1).
        already_owned: Boolean. If True, cost contribution is $0.
        estimated_unit_price: Price estimate per unit (>= 0).
        actual_unit_price: Actual price paid (>= 0 or None).
        merchant_id: Optional FK to merchants.
        purchased_on: Optional date or ISO string (YYYY-MM-DD).
        notes: Optional free-text.

    Returns:
        Newly created ProjectTool instance.

    Raises:
        ValueError: If validation fails.
    """
    # Validate project exists and is editable
    project = Project.query.get(project_id)
    if not project:
        raise ValueError(f"Project with id {project_id} not found.")
    if project.status == "completed":
        raise ValueError("Cannot add tools to a completed project.")

    # Validate tool exists
    tool = Tool.query.get(tool_id)
    if not tool:
        raise ValueError(f"Tool with id {tool_id} not found.")

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

    project_tool = ProjectTool(
        project_id=project_id,
        tool_id=tool_id,
        merchant_id=merchant_id,
        quantity=int(quantity),
        already_owned=bool(already_owned),
        estimated_unit_price=estimated_unit_price or 0,
        actual_unit_price=actual_unit_price,
        purchased_on=_parse_date(purchased_on),
        notes=notes or "",
    )

    db.session.add(project_tool)
    db.session.commit()
    return project_tool


def update_project_tool(project_tool_id, **kwargs):
    """Update a project-tool record.

    Args:
        project_tool_id: Integer primary key.
        **kwargs: Fields to update. Supported: quantity, already_owned,
                  estimated_unit_price, actual_unit_price, merchant_id,
                  purchased_on, notes.

    Returns:
        Updated ProjectTool instance.

    Raises:
        ValueError: If record not found, project is completed, or values invalid.
    """
    pt = ProjectTool.query.get(project_tool_id)
    if not pt:
        raise ValueError(f"ProjectTool with id {project_tool_id} not found.")

    if pt.project.status == "completed":
        raise ValueError("Cannot modify tools on a completed project.")

    if "quantity" in kwargs:
        if kwargs["quantity"] is None or int(kwargs["quantity"]) <= 0:
            raise ValueError("Quantity must be greater than 0.")
        pt.quantity = int(kwargs["quantity"])

    if "already_owned" in kwargs:
        pt.already_owned = bool(kwargs["already_owned"])

    if "estimated_unit_price" in kwargs:
        price = kwargs["estimated_unit_price"]
        if price is not None and float(price) < 0:
            raise ValueError("Estimated unit price must be >= 0.")
        pt.estimated_unit_price = price or 0

    if "actual_unit_price" in kwargs:
        price = kwargs["actual_unit_price"]
        if price is not None and float(price) < 0:
            raise ValueError("Actual unit price must be >= 0.")
        pt.actual_unit_price = price

    if "merchant_id" in kwargs:
        merch_id = kwargs["merchant_id"]
        if merch_id is not None and not Merchant.query.get(merch_id):
            raise ValueError(f"Merchant with id {merch_id} not found.")
        pt.merchant_id = merch_id

    if "purchased_on" in kwargs:
        pt.purchased_on = _parse_date(kwargs["purchased_on"])

    if "notes" in kwargs:
        pt.notes = kwargs["notes"] or ""

    db.session.commit()
    return pt


def remove_tool_from_project(project_tool_id):
    """Remove a tool from a project.

    Args:
        project_tool_id: Integer primary key.

    Returns:
        True if removed successfully.

    Raises:
        ValueError: If record not found or project is completed.
    """
    pt = ProjectTool.query.get(project_tool_id)
    if not pt:
        raise ValueError(f"ProjectTool with id {project_tool_id} not found.")

    if pt.project.status == "completed":
        raise ValueError("Cannot remove tools from a completed project.")

    db.session.delete(pt)
    db.session.commit()
    return True


def _parse_date(value):
    """Convert a value to a date object, or None."""
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return date.fromisoformat(value)
    return None
