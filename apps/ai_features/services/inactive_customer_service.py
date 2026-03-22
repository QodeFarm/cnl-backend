from datetime import date, timedelta
from django.db.models import Max
from apps.customer.models import Customer
from apps.sales.models import SaleInvoiceOrders, SaleOrder
import logging

logger = logging.getLogger(__name__)

DEFAULT_INACTIVE_DAYS = 180


def get_inactive_customers(inactive_days=None, limit=500, from_date=None, to_date=None):
    if inactive_days is None:
        inactive_days = DEFAULT_INACTIVE_DAYS

    cutoff_date = date.today() - timedelta(days=inactive_days)

    customers = list(Customer.objects.filter(is_deleted=False))

    # Latest invoice date per customer
    inv_filter = dict(is_deleted=False)
    if from_date:
        inv_filter['invoice_date__gte'] = from_date
    if to_date:
        inv_filter['invoice_date__lte'] = to_date
    invoice_activity = dict(
        SaleInvoiceOrders.objects
        .filter(**inv_filter)
        .values_list('customer_id')
        .annotate(last_date=Max('invoice_date'))
        .values_list('customer_id', 'last_date')
    )

    # Latest order date per customer
    ord_filter = dict(is_deleted=False)
    if from_date:
        ord_filter['order_date__gte'] = from_date
    if to_date:
        ord_filter['order_date__lte'] = to_date
    order_activity = dict(
        SaleOrder.objects
        .filter(**ord_filter)
        .values_list('customer_id')
        .annotate(last_date=Max('order_date'))
        .values_list('customer_id', 'last_date')
    )

    results = []
    today = date.today()

    for customer in customers:
        cid = customer.customer_id
        last_invoice = invoice_activity.get(cid)
        last_order = order_activity.get(cid)

        # Pick the most recent activity
        dates = [d for d in [last_invoice, last_order] if d is not None]
        if not dates:
            last_activity = None
            inactive_since = customer.created_at.date() if customer.created_at else None
            days_inactive = (today - inactive_since).days if inactive_since else None
        else:
            last_activity = max(dates)
            if last_activity >= cutoff_date:
                continue  # Customer is active
            inactive_since = last_activity
            days_inactive = (today - last_activity).days

        if days_inactive is None:
            continue

        # Risk level based on inactivity duration
        if days_inactive >= 365:
            risk_level = 'LOST'
        elif days_inactive >= 270:
            risk_level = 'CRITICAL'
        elif days_inactive >= 180:
            risk_level = 'WARNING'
        else:
            # Customer registered recently but never ordered — only flag if old enough
            if last_activity is None and days_inactive < inactive_days:
                continue
            risk_level = 'AT_RISK'

        results.append({
            'customer': customer,
            'last_activity_date': last_activity,
            'days_inactive': days_inactive,
            'risk_level': risk_level,
            'total_invoices': 0,  # Will be enriched below
        })

    # Enrich with total invoice count for context
    from django.db.models import Count
    invoice_counts = dict(
        SaleInvoiceOrders.objects
        .filter(is_deleted=False)
        .values('customer_id')
        .annotate(count=Count('sale_invoice_id'))
        .values_list('customer_id', 'count')
    )
    for r in results:
        r['total_invoices'] = invoice_counts.get(r['customer'].customer_id, 0)

    risk_order = {'LOST': 0, 'CRITICAL': 1, 'WARNING': 2, 'AT_RISK': 3}
    results.sort(key=lambda x: (risk_order.get(x['risk_level'], 99), -x['days_inactive']))

    return results
