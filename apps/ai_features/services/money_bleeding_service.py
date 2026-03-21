"""
Money Bleeding Summary Service
Aggregates all sources of financial leakage across 6 modules:
  Inventory, Sales, Purchase, Production, HRMS, Finance
"""
import logging
from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum, Q, F
from django.utils import timezone

from apps.products.models import Products
from apps.sales.models import (
    SaleInvoiceOrders, SaleReturnOrders, SaleCreditNotes,
)
from apps.purchase.models import PurchaseInvoiceOrders
from apps.production.models import WorkOrder
from apps.finance.models import ExpenseItem, ExpenseClaim
from apps.hrms.models import EmployeeSalary

logger = logging.getLogger(__name__)


def get_money_bleeding_summary(period_days=365, from_date=None, to_date=None):
    """
    Analyze all money bleeding sources across modules.

    Categories:
    1. Dead Stock           — Inventory sitting idle (capital locked)
    2. Unpaid Receivables   — Customers not paying (cash stuck)
    3. Pending Payables     — Money owed to vendors (liability risk)
    4. Sales Returns        — Revenue given back
    5. Credit Notes         — Adjustments/refunds issued
    6. Discounts Given      — Revenue reduced via discounts
    7. Production Wastage   — Material/product wasted in manufacturing
    8. Pending Expense Claims — Employee reimbursements pending
    9. Salary Costs         — Monthly payroll expense
    10. Operating Expenses  — Business running costs

    Returns: (categories_list, summary_dict)
    """
    cutoff = from_date or (timezone.now().date() - timedelta(days=period_days))
    end_cutoff = to_date
    categories = []

    # ============================================================
    # 1. DEAD STOCK (Inventory Module)
    # ============================================================
    try:
        from apps.ai_features.services.dead_stock_service import get_dead_stock
        dead = get_dead_stock()
        dead_items = []
        dead_total = 0
        for d in dead:
            p = d['product']
            cost = float(p.purchase_rate or p.sales_rate or 0)
            value = float(p.balance) * cost
            dead_total += value
            dead_items.append({
                'name': p.name,
                'detail': '%d units x Rs.%.0f' % (int(p.balance), cost),
                'amount': round(value, 2),
            })
        dead_items.sort(key=lambda x: x['amount'], reverse=True)
        categories.append({
            'category': 'dead_stock',
            'label': 'Idle Inventory',
            'module': 'Inventory',
            'amount': round(dead_total, 2),
            'item_count': len(dead_items),
            'severity': _severity(dead_total, 100000),
            'top_items': dead_items[:5],
        })
    except Exception as e:
        logger.warning('Dead stock calculation failed: %s', e)

    # ============================================================
    # 2. UNPAID RECEIVABLES (Sales Module)
    # ============================================================
    try:
        receivable_invoices = SaleInvoiceOrders.objects.filter(
            is_deleted=False,
            pending_amount__gt=0,
        ).select_related('customer_id').order_by('-pending_amount')

        recv_total = float(receivable_invoices.aggregate(
            total=Sum('pending_amount'))['total'] or 0)
        recv_items = []
        for inv in receivable_invoices[:10]:
            cust = inv.customer_id
            cname = cust.name if cust else 'Unknown'
            days_overdue = (timezone.now().date() - inv.invoice_date).days if inv.invoice_date else 0
            recv_items.append({
                'name': cname,
                'detail': 'Invoice %s (%d days)' % (
                    inv.invoice_date.strftime('%d-%b-%Y') if inv.invoice_date else '?',
                    days_overdue),
                'amount': float(inv.pending_amount),
            })
        categories.append({
            'category': 'unpaid_receivables',
            'label': 'Uncollected Revenue',
            'module': 'Sales',
            'amount': round(recv_total, 2),
            'item_count': receivable_invoices.count(),
            'severity': _severity(recv_total, 50000),
            'top_items': recv_items[:5],
        })
    except Exception as e:
        logger.warning('Unpaid receivables calculation failed: %s', e)

    # ============================================================
    # 3. PENDING PAYABLES (Purchase Module)
    # ============================================================
    try:
        payable_invoices = PurchaseInvoiceOrders.objects.filter(
            is_deleted=False,
            pending_amount__gt=0,
        ).select_related('vendor_id').order_by('-pending_amount')

        payb_total = float(payable_invoices.aggregate(
            total=Sum('pending_amount'))['total'] or 0)
        payb_items = []
        for inv in payable_invoices[:10]:
            vendor = inv.vendor_id
            vname = vendor.name if vendor else 'Unknown'
            payb_items.append({
                'name': vname,
                'detail': 'Invoice %s' % (
                    inv.invoice_date.strftime('%d-%b-%Y') if inv.invoice_date else '?'),
                'amount': float(inv.pending_amount),
            })
        categories.append({
            'category': 'pending_payables',
            'label': 'Vendor Dues',
            'module': 'Purchase',
            'amount': round(payb_total, 2),
            'item_count': payable_invoices.count(),
            'severity': _severity(payb_total, 25000),
            'top_items': payb_items[:5],
        })
    except Exception as e:
        logger.warning('Pending payables calculation failed: %s', e)

    # ============================================================
    # 4. SALES RETURNS (Sales Module)
    # ============================================================
    try:
        returns_filter = dict(is_deleted=False, return_date__gte=cutoff)
        if end_cutoff:
            returns_filter['return_date__lte'] = end_cutoff
        returns = SaleReturnOrders.objects.filter(**returns_filter)
        returns_total = float(returns.aggregate(
            total=Sum('total_amount'))['total'] or 0)
        returns_count = returns.count()
        categories.append({
            'category': 'sales_returns',
            'label': 'Sales Returns',
            'module': 'Sales',
            'amount': round(returns_total, 2),
            'item_count': returns_count,
            'severity': _severity(returns_total, 10000),
            'top_items': [],
        })
    except Exception as e:
        logger.warning('Sales returns calculation failed: %s', e)

    # ============================================================
    # 5. CREDIT NOTES (Sales Module)
    # ============================================================
    try:
        cn_filter = dict(is_deleted=False, created_at__date__gte=cutoff)
        if end_cutoff:
            cn_filter['created_at__date__lte'] = end_cutoff
        credit_notes = SaleCreditNotes.objects.filter(**cn_filter)
        cn_total = float(credit_notes.aggregate(
            total=Sum('total_amount'))['total'] or 0)
        cn_count = credit_notes.count()
        categories.append({
            'category': 'credit_notes',
            'label': 'Credit Notes Issued',
            'module': 'Sales',
            'amount': round(cn_total, 2),
            'item_count': cn_count,
            'severity': _severity(cn_total, 10000),
            'top_items': [],
        })
    except Exception as e:
        logger.warning('Credit notes calculation failed: %s', e)

    # ============================================================
    # 6. DISCOUNTS GIVEN (Sales Module)
    # ============================================================
    try:
        disc_filter = dict(
            is_deleted=False,
            invoice_date__gte=cutoff,
            dis_amt__gt=0,
        )
        if end_cutoff:
            disc_filter['invoice_date__lte'] = end_cutoff
        discounted = SaleInvoiceOrders.objects.filter(**disc_filter)
        disc_total = float(discounted.aggregate(
            total=Sum('dis_amt'))['total'] or 0)
        disc_count = discounted.count()
        categories.append({
            'category': 'discounts_given',
            'label': 'Discounts Given',
            'module': 'Sales',
            'amount': round(disc_total, 2),
            'item_count': disc_count,
            'severity': _severity(disc_total, 5000),
            'top_items': [],
        })
    except Exception as e:
        logger.warning('Discounts calculation failed: %s', e)

    # ============================================================
    # 7. PRODUCTION WASTAGE (Production Module)
    # ============================================================
    try:
        work_orders = WorkOrder.objects.filter(
            completed_qty__gt=0,
        ).select_related('product_id')

        waste_total = 0
        waste_count = 0
        waste_items = []
        for wo in work_orders:
            product = wo.product_id
            if not product:
                continue
            wasted_qty = int(wo.quantity) - int(wo.completed_qty)
            if wasted_qty > 0:
                cost = float(product.purchase_rate or product.sales_rate or 0)
                value = wasted_qty * cost
                waste_total += value
                waste_count += 1
                waste_items.append({
                    'name': product.name,
                    'detail': 'Ordered %d, Completed %d, Wasted %d' % (
                        wo.quantity, wo.completed_qty, wasted_qty),
                    'amount': round(value, 2),
                })
        waste_items.sort(key=lambda x: x['amount'], reverse=True)
        categories.append({
            'category': 'production_wastage',
            'label': 'Production Wastage',
            'module': 'Production',
            'amount': round(waste_total, 2),
            'item_count': waste_count,
            'severity': _severity(waste_total, 25000),
            'top_items': waste_items[:5],
        })
    except Exception as e:
        logger.warning('Production wastage calculation failed: %s', e)

    # ============================================================
    # 8. PENDING EXPENSE CLAIMS (HRMS Module)
    # ============================================================
    try:
        pending_claims = ExpenseClaim.objects.filter(
            is_deleted=False,
            status='Pending',
        ).select_related('employee_id')

        claims_total = float(pending_claims.aggregate(
            total=Sum('total_amount'))['total'] or 0)
        claims_items = []
        for claim in pending_claims[:10]:
            emp = claim.employee_id
            ename = '%s %s' % (emp.first_name, emp.last_name or '') if emp else 'Unknown'
            claims_items.append({
                'name': ename.strip(),
                'detail': 'Claimed on %s' % (
                    claim.claim_date.strftime('%d-%b-%Y') if claim.claim_date else '?'),
                'amount': float(claim.total_amount),
            })
        categories.append({
            'category': 'pending_expense_claims',
            'label': 'Pending Employee Claims',
            'module': 'HRMS',
            'amount': round(claims_total, 2),
            'item_count': pending_claims.count(),
            'severity': _severity(claims_total, 10000),
            'top_items': claims_items[:5],
        })
    except Exception as e:
        logger.warning('Expense claims calculation failed: %s', e)

    # ============================================================
    # 9. SALARY COSTS (HRMS Module)
    # ============================================================
    try:
        today = timezone.now().date()
        active_salaries = EmployeeSalary.objects.filter(
            is_deleted=False,
        ).filter(
            Q(salary_end_date__isnull=True) | Q(salary_end_date__gte=today)
        ).select_related('employee_id')

        salary_total = float(active_salaries.aggregate(
            total=Sum('salary_amount'))['total'] or 0)
        salary_items = []
        for sal in active_salaries[:10]:
            emp = sal.employee_id
            ename = '%s %s' % (emp.first_name, emp.last_name or '') if emp else 'Unknown'
            salary_items.append({
                'name': ename.strip(),
                'detail': 'Monthly salary',
                'amount': round(sal.salary_amount or 0, 2),
            })
        salary_items.sort(key=lambda x: x['amount'], reverse=True)
        categories.append({
            'category': 'salary_costs',
            'label': 'Monthly Payroll',
            'module': 'HRMS',
            'amount': round(salary_total, 2),
            'item_count': active_salaries.count(),
            'severity': _severity(salary_total, 50000),
            'top_items': salary_items[:5],
        })
    except Exception as e:
        logger.warning('Salary costs calculation failed: %s', e)

    # ============================================================
    # 10. OPERATING EXPENSES (Finance Module)
    # ============================================================
    try:
        exp_filter = dict(expense_date__gte=cutoff)
        if end_cutoff:
            exp_filter['expense_date__lte'] = end_cutoff
        expenses = ExpenseItem.objects.filter(**exp_filter)
        exp_total = float(expenses.aggregate(
            total=Sum('amount'))['total'] or 0)
        exp_items = []
        for exp in expenses.order_by('-amount')[:10]:
            exp_items.append({
                'name': exp.description or 'Expense',
                'detail': exp.expense_date.strftime('%d-%b-%Y') if exp.expense_date else '?',
                'amount': float(exp.amount),
            })
        categories.append({
            'category': 'operating_expenses',
            'label': 'Operating Expenses',
            'module': 'Finance',
            'amount': round(exp_total, 2),
            'item_count': expenses.count(),
            'severity': _severity(exp_total, 25000),
            'top_items': exp_items[:5],
        })
    except Exception as e:
        logger.warning('Operating expenses calculation failed: %s', e)

    # Sort categories by amount descending
    categories.sort(key=lambda x: x['amount'], reverse=True)

    # Calculate percentages
    grand_total = sum(c['amount'] for c in categories)
    for cat in categories:
        cat['percentage'] = round(
            (cat['amount'] / grand_total * 100) if grand_total > 0 else 0, 1)

    return categories, _build_summary(categories, grand_total)


def _severity(amount, threshold):
    if amount >= threshold * 2:
        return 'CRITICAL'
    elif amount >= threshold:
        return 'HIGH'
    elif amount >= threshold * 0.5:
        return 'MEDIUM'
    return 'LOW'


def _build_summary(categories, grand_total):
    modules = {}
    for cat in categories:
        mod = cat['module']
        if mod not in modules:
            modules[mod] = 0
        modules[mod] += cat['amount']

    module_breakdown = [
        {'module': mod, 'amount': round(amt, 2),
         'percentage': round(amt / grand_total * 100, 1) if grand_total > 0 else 0}
        for mod, amt in sorted(modules.items(), key=lambda x: x[1], reverse=True)
    ]

    critical = sum(1 for c in categories if c['severity'] == 'CRITICAL')
    high = sum(1 for c in categories if c['severity'] == 'HIGH')

    return {
        'total_bleeding': round(grand_total, 2),
        'total_categories': len(categories),
        'critical_count': critical,
        'high_count': high,
        'modules_affected': len(modules),
        'module_breakdown': module_breakdown,
    }
