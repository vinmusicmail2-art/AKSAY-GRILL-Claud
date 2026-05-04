"""Generic CSV export utility for admin views."""
import io
import csv
from datetime import datetime
from typing import Type, List, Callable, Any
from flask import Response
from sqlalchemy.orm import Session


def export_to_csv(
    session: Session,
    model: Type,
    filename_prefix: str,
    headers: List[str],
    row_mapper: Callable[[Any], List[Any]],
    show: str = "all"
) -> Response:
    """Export model data to CSV with filtering.

    Args:
        session: Database session
        model: SQLAlchemy model class
        filename_prefix: Prefix for generated filename (e.g., "dostavka")
        headers: List of column headers for CSV
        row_mapper: Function that takes a model instance and returns list of values
        show: Filter by status ("pending", "processed", "all")

    Returns:
        Flask Response with CSV file

    Example:
        >>> def map_order(o):
        ...     return [o.id, o.contact_name, o.phone, o.total_amount]
        >>> return export_to_csv(
        ...     session, DeliveryOrder, "dostavka",
        ...     ["#", "Имя", "Телефон", "Сумма"],
        ...     map_order, show="pending"
        ... )
    """
    q = session.query(model)
    if show == "pending":
        q = q.filter(model.is_processed.is_(False))
    elif show == "processed":
        q = q.filter(model.is_processed.is_(True))

    items = q.order_by(model.is_processed.asc(), model.created_at.desc()).all()

    buf = io.StringIO()
    buf.write("﻿")
    w = csv.writer(buf)
    w.writerow(headers)

    for item in items:
        w.writerow(row_mapper(item))

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M")
    filename = f"{filename_prefix}_{ts}.csv"

    return Response(
        buf.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
