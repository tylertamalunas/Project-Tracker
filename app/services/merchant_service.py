"""Service layer for Merchant CRUD operations."""
from app import db
from app.models import Merchant


def list_merchants(name_filter=None):
    """Return all Merchants, filtered by name.

    Args: 
        name_filter: user input name, None returns all.

    Returns:
        List of merchants ordered by name descending.
    """
    query = Merchant.query.order_by(Merchant.name)
    if name_filter is not None:
        query = query.filter(Merchant.name.ilike(f"%{name_filter}%"))
    return query.all()


def get_merchant(merchant_id):
    """Get a single merchant by ID.

    Args:
        merchant_id: Integer primary key
    
    Returns:
        Merchant or None if not found.
    """
    return Merchant.query.get(merchant_id)


def create_merchant(name, website="", notes=""):
    """Create a new merchant.

    Args:
        name: name of the merchant. Required.
        website: Optional, 500 character string.
        notes: Optional notes about merchant.

    Returns:
        Newly created Merchant instance.

    Raises:
        ValueError: no name entered.
    """
    if not name or not name.strip():
        raise ValueError(f"Merchant name is required.")
    
    merchant = Merchant(
        name=name.strip(),
        website=website or "",
        notes=notes or "",
    )

    db.session.add(merchant)
    db.session.commit()
    return merchant    


def update_merchant(merchant_id, **kwargs):
    """Update an existing Merchant.

        Args:
            merchant_id: Primary Integer key
            **kwargs: Fields to update. Supported: name, website, notes.
        
        Returns:
            Updated Merchant instance.

        Raises:
            ValueError: merchant not found or name is empty.
    """
    merchant = Merchant.query.get(merchant_id)
    if not merchant:
        raise ValueError(f"Merchant with id {merchant_id} not found.")
    if "name" in kwargs:
        if not kwargs["name"] or not kwargs["name"].strip():
            raise ValueError("Name required.")
        merchant.name = kwargs["name"].strip()
    
    if "website" in kwargs:
        merchant.website = kwargs["website"] or ""
    
    if "notes" in kwargs:
        merchant.notes = kwargs["notes"] or ""

    db.session.commit()
    return merchant


def delete_merchant(merchant_id):
    """Delete a Merchant by ID.

    Args:
        mercchant_id: Integer primary key
    
    Returns:
        True if deleted successfully
    
    Raises:
        ValueError: if merchant not found
    """
    merchant = Merchant.query.get(merchant_id)
    if not merchant:
        raise ValueError(f"Merchant with id {merchant_id} not found.")
    
    db.session.delete(merchant)
    db.session.commit()
    return True

