"""Form data sanitization utilities."""


def sanitize_optional(value: str | None) -> str | None:
    """Strip whitespace and convert empty strings to None.

    Args:
        value: Input string or None

    Returns:
        Stripped string or None if empty

    Example:
        >>> sanitize_optional("  hello  ")
        "hello"
        >>> sanitize_optional("   ")
        None
        >>> sanitize_optional(None)
        None
    """
    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped else None


def sanitize_required(value: str | None) -> str:
    """Strip whitespace from required field.

    Args:
        value: Input string or None

    Returns:
        Stripped string (empty string if None)

    Example:
        >>> sanitize_required("  hello  ")
        "hello"
        >>> sanitize_required(None)
        ""
    """
    return (value or "").strip()


def sanitize_phone(value: str | None) -> str | None:
    """Strip whitespace and remove non-digit characters from phone.

    Args:
        value: Phone number string or None

    Returns:
        Cleaned phone number or None if empty

    Example:
        >>> sanitize_phone("+7 (123) 456-78-90")
        "+71234567890"
        >>> sanitize_phone("   ")
        None
    """
    if value is None:
        return None
    # Keep only digits, +, and ()
    cleaned = ''.join(c for c in value if c.isdigit() or c in '+-()')
    return cleaned if cleaned else None


def sanitize_email(value: str | None) -> str | None:
    """Strip whitespace and lowercase email.

    Args:
        value: Email string or None

    Returns:
        Cleaned email or None if empty

    Example:
        >>> sanitize_email("  User@Example.COM  ")
        "user@example.com"
    """
    if value is None:
        return None
    stripped = value.strip().lower()
    return stripped if stripped else None
