"""Shared validation helpers for form data.

All functions append error messages to the provided errors list
and return the cleaned value (or None/default on failure).
"""
from datetime import date


def validate_required(value, field_name, errors):
    """Check that a string field is not empty.

    Returns:
        Stripped string if valid, None if invalid.
    """
    if not value or not str(value).strip():
        errors.append(f"{field_name} is required.")
        return None
    return str(value).strip()


def validate_positive_int(value, field_name, errors, allow_zero=False):
    """Validate an integer field is > 0 (or >= 0 if allow_zero).

    Returns:
        Integer value if valid, None if invalid.
    """
    try:
        val = int(value)
    except (ValueError, TypeError):
        errors.append(f"{field_name} must be a whole number.")
        return None

    if allow_zero and val < 0:
        errors.append(f"{field_name} must be 0 or greater.")
        return None
    elif not allow_zero and val <= 0:
        errors.append(f"{field_name} must be greater than 0.")
        return None

    return val


def validate_price(value, field_name, errors, allow_none=True):
    """Validate a price/decimal field is >= 0.

    Args:
        value: Raw form value (string, None, or empty).
        field_name: Human-readable field name for error messages.
        errors: List to append errors to.
        allow_none: If True, empty/None returns None without error.

    Returns:
        Float value if valid, None if empty (and allowed) or invalid.
    """
    if value is None or str(value).strip() == "":
        if allow_none:
            return None
        else:
            errors.append(f"{field_name} is required.")
            return None

    try:
        val = float(value)
    except (ValueError, TypeError):
        errors.append(f"{field_name} must be a valid number.")
        return None

    if val < 0:
        errors.append(f"{field_name} must be $0.00 or greater.")
        return None

    return val


def validate_date(value, field_name, errors, allow_none=True):
    """Validate a date field in ISO format (YYYY-MM-DD).

    Returns:
        date object if valid, None if empty (and allowed) or invalid.
    """
    if value is None or str(value).strip() == "":
        if allow_none:
            return None
        else:
            errors.append(f"{field_name} is required.")
            return None

    try:
        return date.fromisoformat(str(value).strip())
    except (ValueError, TypeError):
        errors.append(f"{field_name} must be a valid date (YYYY-MM-DD).")
        return None


def validate_choice(value, field_name, choices, errors, allow_none=False):
    """Validate a value is one of the allowed choices.

    Returns:
        The value if valid, None if invalid.
    """
    if value is None or str(value).strip() == "":
        if allow_none:
            return None
        else:
            errors.append(f"{field_name} is required.")
            return None

    val = str(value).strip()
    if val not in choices:
        errors.append(f"{field_name} must be one of: {', '.join(choices)}.")
        return None

    return val
