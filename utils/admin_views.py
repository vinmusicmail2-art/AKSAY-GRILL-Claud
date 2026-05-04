"""Admin list view utilities for filtering and sorting."""
from datetime import datetime, timedelta
from typing import Type, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_


def build_admin_list_query(
    session: Session,
    model: Type,
    show: str,
    admin_filter: str,
    period: str,
    search_q: str,
    search_fields: List[str],
    sort_config: Dict[str, Any],
    sort: str,
    limit: int = 200
):
    """Build filtered and sorted query for admin list views.

    Args:
        session: Database session
        model: SQLAlchemy model class
        show: Filter by status ("pending", "processed", "all")
        admin_filter: Filter by admin username
        period: Time period filter ("today", "week", "month", "all")
        search_q: Search query string
        search_fields: List of field names to search in
        sort_config: Dictionary mapping sort keys to SQLAlchemy order_by clauses
        sort: Sort key from sort_config
        limit: Maximum number of results (default 200)

    Returns:
        List of model instances matching the filters

    Example:
        >>> sort_config = {
        ...     "date_desc": [BusinessLunchOrder.created_at.desc()],
        ...     "date_asc": [BusinessLunchOrder.created_at.asc()],
        ... }
        >>> results = build_admin_list_query(
        ...     session, BusinessLunchOrder, "pending", "", "today", "",
        ...     ["contact_name", "phone"], sort_config, "date_desc"
        ... )
    """
    q = session.query(model)

    # Status filter
    if show == "pending":
        q = q.filter(model.is_processed.is_(False))
    elif show == "processed":
        q = q.filter(model.is_processed.is_(True))
    # "all" - no filter

    # Admin filter
    if admin_filter:
        q = q.filter(model.processed_by == admin_filter)

    # Period filter
    if period and period != "all":
        now = datetime.utcnow()
        if period == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            q = q.filter(model.created_at >= start)
        elif period == "week":
            start = now - timedelta(days=7)
            q = q.filter(model.created_at >= start)
        elif period == "month":
            start = now - timedelta(days=30)
            q = q.filter(model.created_at >= start)

    # Search filter
    if search_q:
        like = f"%{search_q}%"
        conditions = [getattr(model, field).like(like) for field in search_fields]
        q = q.filter(or_(*conditions))

    # Apply sorting
    sort_clauses = sort_config.get(sort, sort_config.get("date_desc", []))
    for clause in sort_clauses:
        q = q.order_by(clause)

    return q.limit(limit).all()


def get_admin_list(
    session: Session,
    model: Type
) -> List[str]:
    """Get list of unique admin usernames who processed items.

    Args:
        session: Database session
        model: SQLAlchemy model class with processed_by field

    Returns:
        Sorted list of admin usernames

    Example:
        >>> admins = get_admin_list(session, BusinessLunchOrder)
        >>> print(admins)
        ['admin1', 'admin2']
    """
    admins = session.query(model.processed_by).filter(
        model.is_processed.is_(True),
        model.processed_by.isnot(None)
    ).distinct().all()

    return sorted({row[0] for row in admins})
