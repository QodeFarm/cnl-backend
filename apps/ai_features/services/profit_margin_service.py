"""
Profit Margin Analysis Service
Shows Revenue, Cost, Profit, Margin for every product with sales data.
Cost = actual purchase invoice rate OR catalog purchase_rate as fallback.
Simple table: Product | Revenue | Cost | Profit | Margin% | Status
"""
import logging
from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone

from apps.sales.models import SaleInvoiceItems
from apps.purchase.models import PurchaseInvoiceItem
from apps.products.models import Products

logger = logging.getLogger(__name__)


def get_profit_margin_analysis(period_days=365, from_date=None, to_date=None):
    """
    Calculate Revenue, Cost, Profit, Margin for each sold product.

    Revenue = SUM(SaleInvoiceItems.amount) per product
    Cost    = avg_purchase_rate × sold_qty (from purchase invoices or catalog)
    Profit  = Revenue - Cost
    Margin  = (Profit / Revenue) × 100

    Returns: (results_list, summary_dict)
    """
    cutoff = from_date or (timezone.now().date() - timedelta(days=period_days))
    end_cutoff = to_date

    # Step 1: Aggregate sales per product (only products with actual sales)
    sale_filter = dict(
        sale_invoice_id__is_deleted=False,
        sale_invoice_id__invoice_date__gte=cutoff,
        quantity__gt=0,
    )
    if end_cutoff:
        sale_filter['sale_invoice_id__invoice_date__lte'] = end_cutoff
    sale_rows = (
        SaleInvoiceItems.objects
        .filter(**sale_filter)
        .values('product_id_id')
        .annotate(
            total_qty=Sum('quantity'),
            total_amount=Sum('amount'),
        )
    )

    if not sale_rows:
        return [], _build_summary([])

    sale_map = {}
    product_ids = set()
    for row in sale_rows:
        pid = str(row['product_id_id'])
        product_ids.add(pid)
        sale_map[pid] = {
            'sold_qty': float(row['total_qty'] or 0),
            'revenue': float(row['total_amount'] or 0),
        }

    # Step 2: Aggregate purchases per product (for cost calculation)
    purchase_filter = dict(
        purchase_invoice_id__is_deleted=False,
        purchase_invoice_id__invoice_date__gte=cutoff,
        quantity__gt=0,
    )
    if end_cutoff:
        purchase_filter['purchase_invoice_id__invoice_date__lte'] = end_cutoff
    purchase_rows = (
        PurchaseInvoiceItem.objects
        .filter(**purchase_filter)
        .values('product_id_id')
        .annotate(
            total_qty=Sum('quantity'),
            total_amount=Sum('amount'),
        )
    )

    purchase_map = {}
    for row in purchase_rows:
        pid = str(row['product_id_id'])
        qty = float(row['total_qty'] or 0)
        amt = float(row['total_amount'] or 0)
        purchase_map[pid] = {
            'bought_qty': qty,
            'bought_amount': amt,
            'avg_buy_rate': round(amt / qty, 2) if qty > 0 else 0,
        }

    # Step 3: Load products
    products = Products.objects.filter(
        product_id__in=product_ids,
    ).select_related('product_group_id', 'category_id', 'unit_options_id')

    results = []

    for product in products:
        pid = str(product.product_id)
        sale = sale_map.get(pid)
        if not sale:
            continue

        revenue = sale['revenue']
        sold_qty = sale['sold_qty']

        # Cost: prefer actual purchase invoice rate, fallback to catalog
        purch = purchase_map.get(pid)
        if purch and purch['avg_buy_rate'] > 0:
            cost_per_unit = purch['avg_buy_rate']
            cost_source = 'invoice'
        elif product.purchase_rate and float(product.purchase_rate) > 0:
            cost_per_unit = float(product.purchase_rate)
            cost_source = 'catalog'
        else:
            cost_per_unit = 0
            cost_source = 'unknown'

        total_cost = round(cost_per_unit * sold_qty, 2)
        profit = round(revenue - total_cost, 2)
        margin_pct = round((profit / revenue) * 100, 1) if revenue > 0 else 0

        # Status based on margin percentage
        if margin_pct < 10:
            margin_status = 'RED'
        elif margin_pct < 20:
            margin_status = 'YELLOW'
        else:
            margin_status = 'GREEN'

        results.append({
            'product': product,
            'revenue': round(revenue, 2),
            'cost': total_cost,
            'profit': profit,
            'margin_pct': margin_pct,
            'status': margin_status,
            'sold_qty': round(sold_qty, 2),
            'cost_per_unit': round(cost_per_unit, 2),
            'sell_per_unit': round(revenue / sold_qty, 2) if sold_qty > 0 else 0,
            'cost_source': cost_source,
        })

    # Sort: RED first, then YELLOW, then GREEN; within same status by margin ascending
    status_order = {'RED': 0, 'YELLOW': 1, 'GREEN': 2}
    results.sort(key=lambda x: (status_order.get(x['status'], 3), x['margin_pct']))

    return results, _build_summary(results)


def _build_summary(results):
    red = sum(1 for r in results if r['status'] == 'RED')
    yellow = sum(1 for r in results if r['status'] == 'YELLOW')
    green = sum(1 for r in results if r['status'] == 'GREEN')
    total_revenue = sum(r['revenue'] for r in results)
    total_cost = sum(r['cost'] for r in results)
    total_profit = sum(r['profit'] for r in results)
    overall_margin = round((total_profit / total_revenue) * 100, 1) if total_revenue > 0 else 0

    return {
        'total_products': len(results),
        'red_count': red,
        'yellow_count': yellow,
        'green_count': green,
        'total_revenue': round(total_revenue, 2),
        'total_cost': round(total_cost, 2),
        'total_profit': round(total_profit, 2),
        'overall_margin': overall_margin,
    }
