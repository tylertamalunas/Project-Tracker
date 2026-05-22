"""Service layer for Tool CRUD operations."""
from app import db
from app.models import Tool, ToolCategory, Merchant


def list_tools(active_only=None, category_id=None):
    """Returns tools with optional filters. 

    Args:
        active_only: True for active items, False for inactive, None for all.__annotations__
        category_id: Filter by category FK.

    Returns:
        List of Tool instances ordered by name.
    """

    query = Tool.query.order_by(Tool.name)

    if active_only is True:
        query = query.filter_by(is_active=True)
    elif active_only is False:
        query = query.filter_by(is_active=False)

    if category_id is not None:
        query = query.filter_by(category_id=category_id)

    return query.all()


def get_tool(tool_id):
    """Get a single tool by ID.

    Returns:
        Tool instance or None.
    """
    return Tool.query.get(tool_id)


def create_tool(name, default_price=0, brand="", model_number="",
                category_id=None, merchant_id=None, notes="", is_active=True):
    """Create a new tool in the global catalog.

    Args:
        name: required tool name
        default_price: Default price of the tool (must be >=0)
        brand: Optional brand name of the tool
        model_number: Optional model number of the tool
        category_id: Optional FK of tool category
        merchant_id: Optional FK of the merchant tool was purchased from
        notes: Optional any notes about the tool
        is_active: If the tool is active in the catalog. Defaults True.

    Returns: 
        Newly created Tool instance.

    Raises:
        ValueError: If name is empty or default_price is negative. 
    """
    if not name or not name.strip():
        raise ValueError("Tool needs a name.")
    
    if default_price is not None and float(default_price) < 0:
        raise ValueError("Default Price needs to be >= 0.")
    
    if category_id is not None:
        if not ToolCategory.query.get(category_id):
            raise ValueError(f"Tool category with id {category_id} not found.")
    
    if merchant_id is not None:
        if not Merchant.query.get(merchant_id):
            raise ValueError(f"Merchant with id {merchant_id} not found.")

    tool = Tool(
        name=name.strip(),
        default_price=default_price or 0,
        brand=brand or "",
        model_number=model_number or "",
        category_id=category_id,
        merchant_id=merchant_id,
        notes=notes or "",
        is_active=is_active,
    )
    db.session.add(tool)
    db.session.commit()
    return tool


def update_tool(tool_id, **kwargs):
    """Update an existing tool.

    Args:
        tool_id: int primary key
        **kwargs: Fields to update. 
        name: tool name
        default_price: price of the tool (must be >=0)
        brand: brand name of the tool
        model_number: model number of the tool
        category_id: FK of tool category
        merchant_id: FK of the merchant tool was purchased from
        notes: notes about the tool
        is_active: If the tool is active in the catalog.

    Returns:
        Updated Tool instance.

    Raises:
        ValueError: if tool not found, value is empty, int is negative.
    """
    tool = Tool.query.get(tool_id)
    if not tool:
        raise ValueError(f"Tool with id {tool_id} not found.")
    
    if "name" in kwargs:
        if not kwargs["name"] or not kwargs["name"].strip():
            raise ValueError("Tool name is required.")
        tool.name = kwargs["name"].strip()

    if "default_price" in kwargs:
        price = kwargs["default_price"]
        if price is not None and float(price) < 0:
            raise ValueError(f"Default price must be >= 0.")
        tool.default_price = price or 0

    if "brand" in kwargs:
        tool.brand = kwargs["brand"] or ""

    if "model_number" in kwargs:
        tool.model_number = kwargs["model_number"] or ""

    if "category_id" in kwargs:
        cat_id = kwargs["category_id"]
        if cat_id is not None and not ToolCategory.query.get(cat_id):
            raise ValueError(f"Tool category with id {cat_id} not found.")
        tool.category_id  = cat_id
    
    if "merchant_id" in kwargs:
        merch_id = kwargs["merchant_id"]
        if merch_id is not None and not Merchant.query.get(merch_id):
            raise ValueError(f"Merchant with id {merch_id} not found.")
        tool.merchant_id = merch_id

    if "notes" in kwargs:
        tool.notes = kwargs["notes"] or ""
    
    if "is_active" in kwargs:
        tool.is_active = bool(kwargs["is_active"])

    db.session.commit()
    return tool


def delete_tool(tool_id):
    """Delete a tool by ID.

    Args:
        tool_id: Int primary key.

    Raises:
        ValueError if tool not found.

    Returns:
        True if deleted successfully. 
    """
    tool = Tool.query.get(tool_id)
    if not tool:
        raise ValueError(f"Tool with id {tool_id} not found.")
    
    db.session.delete(tool)
    db.session.commit()
    return True