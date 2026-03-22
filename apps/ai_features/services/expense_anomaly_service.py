"""
Expense Anomaly Detection Service
Detects abnormal spending by category using statistical analysis (mean + std dev).
Flags expenses that deviate significantly from historical norms.
"""
import logging
from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from apps.finance.models import ExpenseItem

logger = logging.getLogger(__name__)


def get_expense_anomalies(period_days=365, threshold=2.0, from_date=None, to_date=None):
    """
    Detect expense anomalies by ledger account category.

    Groups expenses by ledger_account (category) and month, calculates
    mean + std dev per category, and flags months where spending exceeds
    mean + threshold * std_dev.

    Returns: (anomalies_list, summary_dict)
    """
    cutoff = from_date or (timezone.now().date() - timedelta(days=period_days))
    end_cutoff = to_date

    # Get all non-deleted expenses in the period, grouped by ledger account + month
    qs_filter = dict(is_deleted=False, expense_date__gte=cutoff)
    if end_cutoff:
        qs_filter['expense_date__lte'] = end_cutoff
    expenses = (
        ExpenseItem.objects
        .filter(**qs_filter)
        .exclude(ledger_account_id__isnull=True)
        .select_related('ledger_account_id', 'vendor_id')
        .order_by('expense_date')
    )

    if not expenses.exists():
        return [], _build_summary([])

    # Group by ledger account → monthly totals
    monthly_by_category = {}
    expense_details = {}  # Store individual expenses for detail

    for exp in expenses:
        ledger = exp.ledger_account_id
        cat_id = str(ledger.ledger_account_id)
        cat_name = ledger.name
        month_key = exp.expense_date.replace(day=1)

        if cat_id not in monthly_by_category:
            monthly_by_category[cat_id] = {
                'name': cat_name,
                'months': {},
                'ledger': ledger,
            }
            expense_details[cat_id] = []

        if month_key not in monthly_by_category[cat_id]['months']:
            monthly_by_category[cat_id]['months'][month_key] = Decimal('0')

        monthly_by_category[cat_id]['months'][month_key] += (exp.amount or Decimal('0'))
        expense_details[cat_id].append(exp)

    anomalies = []

    for cat_id, cat_data in monthly_by_category.items():
        monthly_totals = list(cat_data['months'].values())

        # Need at least 3 months of data to establish a pattern
        if len(monthly_totals) < 3:
            continue

        # Calculate mean and std dev
        mean_val = sum(monthly_totals) / len(monthly_totals)
        variance = sum((x - mean_val) ** 2 for x in monthly_totals) / len(monthly_totals)
        std_dev = float(variance) ** 0.5
        mean_float = float(mean_val)

        if std_dev == 0:
            # No variance — perfectly consistent spending, skip
            continue

        # Check each month for anomalies
        for month_date, month_total in cat_data['months'].items():
            month_float = float(month_total)
            deviation = (month_float - mean_float) / std_dev if std_dev > 0 else 0

            if deviation >= threshold:
                # This month is anomalous
                severity = 'CRITICAL' if deviation >= 3.0 else 'WARNING'
                excess = month_float - mean_float

                # Find top expenses in this anomalous month
                top_expenses = []
                for exp in expense_details[cat_id]:
                    if exp.expense_date.replace(day=1) == month_date:
                        top_expenses.append({
                            'date': str(exp.expense_date),
                            'description': exp.description or '',
                            'amount': float(exp.amount),
                            'vendor': exp.vendor_id.name if exp.vendor_id else None,
                            'status': exp.status,
                        })

                # Sort by amount descending, keep top 5
                top_expenses.sort(key=lambda x: x['amount'], reverse=True)
                top_expenses = top_expenses[:5]

                anomalies.append({
                    'category_id': cat_id,
                    'category_name': cat_data['name'],
                    'month': str(month_date),
                    'month_total': round(month_float, 2),
                    'category_mean': round(mean_float, 2),
                    'category_std_dev': round(std_dev, 2),
                    'deviation_score': round(deviation, 2),
                    'excess_amount': round(excess, 2),
                    'severity': severity,
                    'top_expenses': top_expenses,
                })

    # Sort by deviation score descending (worst anomalies first)
    anomalies.sort(key=lambda x: x['deviation_score'], reverse=True)

    return anomalies, _build_summary(anomalies)


def _build_summary(anomalies):
    """Build summary statistics for the anomaly results."""
    critical = sum(1 for a in anomalies if a['severity'] == 'CRITICAL')
    warning = sum(1 for a in anomalies if a['severity'] == 'WARNING')
    total_excess = sum(a['excess_amount'] for a in anomalies)
    categories_affected = len(set(a['category_id'] for a in anomalies))

    return {
        'total_anomalies': len(anomalies),
        'critical': critical,
        'warning': warning,
        'total_excess_amount': round(total_excess, 2),
        'categories_affected': categories_affected,
    }
