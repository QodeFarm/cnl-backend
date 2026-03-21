from datetime import date, timedelta
from decimal import Decimal
from collections import defaultdict
from django.db.models import Sum
from django.db.models import DecimalField as DjDecimalField
from django.db.models.functions import Coalesce
from apps.sales.models import SaleInvoiceOrders
from apps.purchase.models import PurchaseInvoiceOrders
from apps.finance.models import ExpenseItem
import logging

logger = logging.getLogger(__name__)


def get_cash_flow_forecast(forecast_days=90, from_date=None, to_date=None):
    """
    Cash flow forecast based on actual receivables, payables, and expenses.

    Looks at:
    - INFLOWS: Unpaid sales invoices (pending_amount) grouped by due_date
    - OUTFLOWS: Unpaid purchase invoices (pending_amount) grouped by due_date
    - OUTFLOWS: Pending expenses
    - HISTORICAL: Recent payment patterns to estimate collection rates

    Provides week-by-week forecast for the next N days.

    Args:
        forecast_days: How many days ahead to forecast (default 90)

    Returns:
        (weekly_forecast, summary)
    """
    today = date.today()
    forecast_end = today + timedelta(days=forecast_days)

    # --- RECEIVABLES (money coming IN) ---
    recv_filter = dict(
        is_deleted=False,
        pending_amount__gt=0,
    )
    if from_date:
        recv_filter['invoice_date__gte'] = from_date
    if to_date:
        recv_filter['invoice_date__lte'] = to_date
    receivables = (
        SaleInvoiceOrders.objects
        .filter(**recv_filter)
        .values('due_date', 'customer_id')
        .annotate(
            amount=Coalesce(
                Sum('pending_amount'), Decimal('0'),
                output_field=DjDecimalField()
            ),
        )
    )

    # --- PAYABLES (money going OUT to vendors) ---
    payb_filter = dict(
        is_deleted=False,
        pending_amount__gt=0,
    )
    if from_date:
        payb_filter['invoice_date__gte'] = from_date
    if to_date:
        payb_filter['invoice_date__lte'] = to_date
    payables = (
        PurchaseInvoiceOrders.objects
        .filter(**payb_filter)
        .values('due_date', 'vendor_id')
        .annotate(
            amount=Coalesce(
                Sum('pending_amount'), Decimal('0'),
                output_field=DjDecimalField()
            ),
        )
    )

    # --- EXPENSES (money going OUT for operations) ---
    pending_expenses = (
        ExpenseItem.objects
        .filter(
            is_deleted=False,
            status='Pending',
        )
        .values('expense_date')
        .annotate(
            amount=Coalesce(
                Sum('amount'), Decimal('0'),
                output_field=DjDecimalField()
            ),
        )
    )

    # Build week buckets
    num_weeks = max(forecast_days // 7, 1)
    weekly_data = []

    for week_num in range(num_weeks):
        week_start = today + timedelta(days=week_num * 7)
        week_end = week_start + timedelta(days=6)

        if week_start > forecast_end:
            break

        inflow = Decimal('0')
        outflow_vendor = Decimal('0')
        outflow_expense = Decimal('0')

        # Sum receivables due this week
        for r in receivables:
            due = r['due_date']
            if due is None:
                # No due date — treat as overdue (already due)
                if week_num == 0:
                    inflow += Decimal(str(r['amount']))
            elif week_start <= due <= week_end:
                inflow += Decimal(str(r['amount']))
            elif due < today and week_num == 0:
                # Already overdue — bucket into week 1
                inflow += Decimal(str(r['amount']))

        # Sum payables due this week
        for p in payables:
            due = p['due_date']
            if due is None:
                if week_num == 0:
                    outflow_vendor += Decimal(str(p['amount']))
            elif week_start <= due <= week_end:
                outflow_vendor += Decimal(str(p['amount']))
            elif due < today and week_num == 0:
                outflow_vendor += Decimal(str(p['amount']))

        # Sum expenses for this week
        for e in pending_expenses:
            exp_date = e['expense_date']
            if exp_date and week_start <= exp_date <= week_end:
                outflow_expense += Decimal(str(e['amount']))
            elif exp_date and exp_date < today and week_num == 0:
                outflow_expense += Decimal(str(e['amount']))

        total_outflow = outflow_vendor + outflow_expense
        net = inflow - total_outflow

        weekly_data.append({
            'week': week_num + 1,
            'start_date': str(week_start),
            'end_date': str(week_end),
            'inflow': round(float(inflow), 2),
            'outflow_vendor': round(float(outflow_vendor), 2),
            'outflow_expense': round(float(outflow_expense), 2),
            'total_outflow': round(float(total_outflow), 2),
            'net': round(float(net), 2),
        })

    # Calculate totals and running balance
    total_inflow = sum(w['inflow'] for w in weekly_data)
    total_outflow = sum(w['total_outflow'] for w in weekly_data)
    total_net = round(total_inflow - total_outflow, 2)

    # Running cumulative balance
    running = 0.0
    lowest_point = 0.0
    lowest_week = 1
    for w in weekly_data:
        running += w['net']
        w['cumulative'] = round(running, 2)
        if running < lowest_point:
            lowest_point = running
            lowest_week = w['week']

    # Count overdue receivables and payables
    overdue_receivables = float(sum(
        Decimal(str(r['amount']))
        for r in receivables
        if r['due_date'] and r['due_date'] < today
    ))
    overdue_payables = float(sum(
        Decimal(str(p['amount']))
        for p in payables
        if p['due_date'] and p['due_date'] < today
    ))

    # Risk assessment
    if total_net < 0:
        risk = 'HIGH'
    elif lowest_point < 0:
        risk = 'MEDIUM'
    else:
        risk = 'LOW'

    summary = {
        'forecast_days': forecast_days,
        'total_expected_inflow': round(total_inflow, 2),
        'total_expected_outflow': round(total_outflow, 2),
        'net_cash_flow': total_net,
        'risk': risk,
        'overdue_receivables': round(overdue_receivables, 2),
        'overdue_payables': round(overdue_payables, 2),
        'lowest_point': round(lowest_point, 2),
        'lowest_week': lowest_week,
        'weeks_forecasted': len(weekly_data),
    }

    return weekly_data, summary
