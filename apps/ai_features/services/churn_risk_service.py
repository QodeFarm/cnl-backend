from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Sum, Count, Max, Min
from django.db.models import DecimalField as DjDecimalField
from django.db.models.functions import Coalesce
from apps.customer.models import Customer
from apps.sales.models import SaleInvoiceOrders, SaleOrder
import logging

logger = logging.getLogger(__name__)


def get_churn_risk(period_days=365, from_date=None, to_date=None):
    """
    Customer Churn Risk scoring using RFM (Recency, Frequency, Monetary) model.

    Each customer gets scored 1-5 on three dimensions:
    - Recency: How recently they purchased (5 = recent, 1 = long ago)
    - Frequency: How often they purchase (5 = very often, 1 = rarely)
    - Monetary: How much they spend (5 = high spender, 1 = low)

    Combined score determines segment:
    - CHAMPION: R>=4, F>=4, M>=4
    - LOYAL: R>=3, F>=3, M>=3
    - AT_RISK: R<=2, F>=3 (used to buy often, stopped)
    - NEEDS_ATTENTION: R=3, F<=2, M>=3 (good spender, irregular)
    - LOST: R<=2, F<=2 (haven't bought recently, rarely bought)
    - NEW: F=1, R>=4 (bought recently but only once)

    Args:
        period_days: How far back to analyze (default 365)

    Returns:
        (customers_scored, summary)
    """
    today = to_date or date.today()
    start_date = from_date or (today - timedelta(days=period_days))

    # Get RFM raw data from SaleInvoiceOrders
    rfm_data = (
        SaleInvoiceOrders.objects
        .filter(
            is_deleted=False,
            invoice_date__gte=start_date,
            invoice_date__lte=today,
        )
        .values('customer_id')
        .annotate(
            last_purchase=Max('invoice_date'),
            purchase_count=Count('sale_invoice_id'),
            total_spent=Coalesce(
                Sum('total_amount'), Decimal('0'),
                output_field=DjDecimalField()
            ),
        )
    )

    # Also check SaleOrder for customers who placed orders but no invoices yet
    order_data = (
        SaleOrder.objects
        .filter(
            is_deleted=False,
            order_date__gte=start_date,
            order_date__lte=today,
        )
        .values('customer_id')
        .annotate(
            last_order=Max('order_date'),
            order_count=Count('sale_order_id'),
            total_ordered=Coalesce(
                Sum('total_amount'), Decimal('0'),
                output_field=DjDecimalField()
            ),
        )
    )

    # Merge invoice + order data per customer
    customer_rfm = {}
    for row in rfm_data:
        cid = row['customer_id']
        customer_rfm[cid] = {
            'last_date': row['last_purchase'],
            'frequency': row['purchase_count'],
            'monetary': float(row['total_spent']),
        }

    for row in order_data:
        cid = row['customer_id']
        if cid in customer_rfm:
            existing = customer_rfm[cid]
            if row['last_order'] and (not existing['last_date'] or row['last_order'] > existing['last_date']):
                existing['last_date'] = row['last_order']
            existing['frequency'] += row['order_count']
            existing['monetary'] += float(row['total_ordered'])
        else:
            customer_rfm[cid] = {
                'last_date': row['last_order'],
                'frequency': row['order_count'],
                'monetary': float(row['total_ordered']),
            }

    if not customer_rfm:
        return [], {
            'total_customers': 0, 'champion': 0, 'loyal': 0,
            'at_risk': 0, 'needs_attention': 0, 'lost': 0, 'new': 0,
        }

    # Calculate recency days for each customer
    for cid, data in customer_rfm.items():
        if data['last_date']:
            data['recency_days'] = (today - data['last_date']).days
        else:
            data['recency_days'] = period_days

    # Score 1-5 using quintiles
    recency_values = sorted([d['recency_days'] for d in customer_rfm.values()])
    frequency_values = sorted([d['frequency'] for d in customer_rfm.values()])
    monetary_values = sorted([d['monetary'] for d in customer_rfm.values()])

    def quintile_score(value, sorted_values, reverse=False):
        """Assign 1-5 score based on quintile position."""
        n = len(sorted_values)
        if n == 0:
            return 3
        # Find position
        position = 0
        for i, v in enumerate(sorted_values):
            if value <= v:
                position = i
                break
        else:
            position = n - 1
        # Convert to 1-5
        score = int((position / n) * 5) + 1
        score = min(score, 5)
        if reverse:
            score = 6 - score  # For recency: fewer days = better = higher score
        return score

    # Load customer objects
    customer_ids = list(customer_rfm.keys())
    customers = {
        c.customer_id: c
        for c in Customer.objects.filter(
            customer_id__in=customer_ids,
            is_deleted=False,
        )
    }

    results = []
    summary = {
        'total_customers': 0,
        'champion': 0,
        'loyal': 0,
        'at_risk': 0,
        'needs_attention': 0,
        'lost': 0,
        'new': 0,
    }

    for cid, data in customer_rfm.items():
        customer = customers.get(cid)
        if not customer:
            continue

        summary['total_customers'] += 1

        r_score = quintile_score(data['recency_days'], recency_values, reverse=True)
        f_score = quintile_score(data['frequency'], frequency_values, reverse=False)
        m_score = quintile_score(data['monetary'], monetary_values, reverse=False)

        # Determine segment
        segment = _classify_segment(r_score, f_score, m_score)
        summary[segment.lower()] = summary.get(segment.lower(), 0) + 1

        results.append({
            'customer': customer,
            'recency_days': data['recency_days'],
            'last_purchase_date': data['last_date'],
            'purchase_count': data['frequency'],
            'total_spent': round(data['monetary'], 2),
            'r_score': r_score,
            'f_score': f_score,
            'm_score': m_score,
            'rfm_score': round((r_score + f_score + m_score) / 3, 1),
            'segment': segment,
        })

    # Sort: AT_RISK first (these need immediate action), then by monetary desc
    segment_order = {'AT_RISK': 0, 'NEEDS_ATTENTION': 1, 'LOST': 2, 'NEW': 3, 'LOYAL': 4, 'CHAMPION': 5}
    results.sort(key=lambda x: (segment_order.get(x['segment'], 99), -x['total_spent']))

    return results, summary


def _classify_segment(r, f, m):
    """Classify customer into segment based on RFM scores."""
    if r >= 4 and f >= 4 and m >= 4:
        return 'CHAMPION'
    elif r >= 3 and f >= 3 and m >= 3:
        return 'LOYAL'
    elif r <= 2 and f >= 3:
        return 'AT_RISK'
    elif r >= 4 and f == 1:
        return 'NEW'
    elif r >= 3 and f <= 2 and m >= 3:
        return 'NEEDS_ATTENTION'
    elif r <= 2 and f <= 2:
        return 'LOST'
    else:
        return 'NEEDS_ATTENTION'
