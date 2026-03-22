"""
Shared utilities for AI Features module.
"""
import datetime
import logging

logger = logging.getLogger(__name__)


def parse_date_params(request):
    """
    Extract from_date and to_date from query params.
    Returns (from_date, to_date) as date objects, or (None, None) if not provided.
    Supports format: YYYY-MM-DD
    """
    from_date_str = request.query_params.get('from_date')
    to_date_str = request.query_params.get('to_date')

    from_date = None
    to_date = None

    if from_date_str:
        try:
            from_date = datetime.datetime.strptime(from_date_str, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Invalid from_date format: {from_date_str}")

    if to_date_str:
        try:
            to_date = datetime.datetime.strptime(to_date_str, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Invalid to_date format: {to_date_str}")

    return from_date, to_date
