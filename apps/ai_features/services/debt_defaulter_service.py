from datetime import date
from decimal import Decimal
from django.db.models import Sum, Count, Min, Q, F
from apps.sales.models import SaleInvoiceOrders
from apps.customer.models import Customer
import logging

logger = logging.getLogger(__name__)

RISK_CRITICAL_DAYS = 90
RISK_WARNING_DAYS = 31


def _get_risk_level(overdue_days):
    if overdue_days >= RISK_CRITICAL_DAYS:
        return 'CRITICAL'
    elif overdue_days >= RISK_WARNING_DAYS:
        return 'WARNING'
    return 'MILD'


def get_debt_defaulters(from_date=None, to_date=None):
    today = date.today()

    base_filter = dict(
        bill_type='CREDIT',
        pending_amount__gt=0,
        due_date__lt=today,
        due_date__isnull=False,
        is_deleted=False,
    )
    if from_date:
        base_filter['invoice_date__gte'] = from_date
    if to_date:
        base_filter['invoice_date__lte'] = to_date

    overdue_data = (
        SaleInvoiceOrders.objects
        .filter(**base_filter)
        .values('customer_id')
        .annotate(
            total_overdue_amount=Sum('pending_amount'),
            overdue_invoices_count=Count('sale_invoice_id'),
            oldest_overdue_date=Min('due_date'),
        )
        .order_by('customer_id')
    )

    if not overdue_data:
        return []

    customer_ids = [row['customer_id'] for row in overdue_data]
    customers = {
        str(c.customer_id): c
        for c in Customer.objects.filter(
            customer_id__in=customer_ids,
            is_deleted=False,
        )
    }

    results = []
    for row in overdue_data:
        cid = str(row['customer_id'])
        customer = customers.get(cid)
        if not customer:
            continue

        overdue_days = (today - row['oldest_overdue_date']).days
        total_overdue = row['total_overdue_amount'] or Decimal('0')
        credit_limit = customer.credit_limit

        credit_utilization = None
        if credit_limit and credit_limit > 0:
            credit_utilization = round(
                float(total_overdue / credit_limit) * 100, 2
            )

        results.append({
            'customer': customer,
            'total_overdue_amount': float(total_overdue),
            'overdue_invoices_count': row['overdue_invoices_count'],
            'oldest_overdue_date': row['oldest_overdue_date'],
            'max_overdue_days': overdue_days,
            'risk_level': _get_risk_level(overdue_days),
            'credit_limit': float(credit_limit) if credit_limit else None,
            'credit_utilization': credit_utilization,
        })

    risk_order = {'CRITICAL': 0, 'WARNING': 1, 'MILD': 2}
    results.sort(key=lambda x: (risk_order[x['risk_level']], -x['total_overdue_amount']))

    return results
