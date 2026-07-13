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


def resolve_unit_cost(invoice_avg_rate, catalog_rate):
    """
    SINGLE SOURCE OF TRUTH for a product's unit cost (CLAUDE.md §4B / flow.md).

    Used by BOTH the Profit Margin insight (this service) and the Profit Margin
    report (apps/reports/sales) so the two can never disagree on a product's cost.

    Preference: actual purchase-invoice average rate → catalog purchase_rate →
    unknown. Never assume 0 — that would fabricate a 100% margin (a hallucination).

    Returns (cost_per_unit: float | None, cost_source: 'invoice' | 'catalog' | 'unknown').
    """
    if invoice_avg_rate and float(invoice_avg_rate) > 0:
        return float(invoice_avg_rate), 'invoice'
    if catalog_rate and float(catalog_rate) > 0:
        return float(catalog_rate), 'catalog'
    return None, 'unknown'


def get_product_cost_map(product_ids, db_alias='default'):
    """
    SINGLE SOURCE OF TRUTH for per-product unit cost across the ERP.

    Returns {product_id_str: (cost_per_unit: float | None, source: str)}.
    Cost = all-time **weighted-average purchase cost** (SUM amount / SUM qty from
    purchase invoices) → catalog purchase_rate → unknown. Called by BOTH the
    Profit Margin insight and the Profit Margin report so a product's cost is the
    SAME number everywhere (CLAUDE.md §4B / flow.md — the Iron Rule).
    """
    ids = {str(p) for p in product_ids}
    if not ids:
        return {}

    from apps.purchase.models import PurchaseInvoiceItem
    from apps.products.models import Products

    invoice_avg = {}
    for row in (PurchaseInvoiceItem.objects.using(db_alias)
                .filter(purchase_invoice_id__is_deleted=False,
                        product_id__in=ids, quantity__gt=0)
                .values('product_id')
                .annotate(q=Sum('quantity'), a=Sum('amount'))):
        q = float(row['q'] or 0)
        invoice_avg[str(row['product_id'])] = (float(row['a'] or 0) / q) if q > 0 else None

    catalog = {
        str(pid): rate
        for pid, rate in Products.objects.using(db_alias)
        .filter(product_id__in=ids).values_list('product_id', 'purchase_rate')
    }

    return {
        pid: resolve_unit_cost(invoice_avg.get(pid), catalog.get(pid))
        for pid in ids
    }


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

    # Step 2: Resolve unit cost per product via the SHARED cost map (all-time
    # weighted-average purchase cost → catalog → unknown). Identical to what the
    # Profit Margin report uses, so the two never disagree.
    cost_map = get_product_cost_map(product_ids)

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

        # Cost from the shared cost map (same number the report uses).
        cost_per_unit, cost_source = cost_map.get(pid, (None, 'unknown'))

        if cost_per_unit is None:
            # Honest empty state — cost not set, so profit/margin are unknowable.
            total_cost = None
            profit = None
            margin_pct = None
            margin_status = 'NO_COST'
        else:
            total_cost = round(cost_per_unit * sold_qty, 2)
            profit = round(revenue - total_cost, 2)
            margin_pct = round((profit / revenue) * 100, 1) if revenue > 0 else 0
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
            'cost_per_unit': round(cost_per_unit, 2) if cost_per_unit is not None else None,
            'sell_per_unit': round(revenue / sold_qty, 2) if sold_qty > 0 else 0,
            'cost_source': cost_source,
        })

    # Sort: RED first, then YELLOW, GREEN, then NO_COST last; within a status by
    # margin ascending (NO_COST rows have no margin, so sort them by revenue).
    status_order = {'RED': 0, 'YELLOW': 1, 'GREEN': 2, 'NO_COST': 4}
    results.sort(key=lambda x: (
        status_order.get(x['status'], 3),
        x['margin_pct'] if x['margin_pct'] is not None else 0,
    ))

    return results, _build_summary(results)


def _build_summary(results):
    # Totals are computed ONLY from rows with a known cost — never fabricate
    # cost/profit for products whose cost is not set.
    known = [r for r in results if r['status'] != 'NO_COST']
    red = sum(1 for r in known if r['status'] == 'RED')
    yellow = sum(1 for r in known if r['status'] == 'YELLOW')
    green = sum(1 for r in known if r['status'] == 'GREEN')
    no_cost = sum(1 for r in results if r['status'] == 'NO_COST')

    revenue_known = sum(r['revenue'] for r in known)
    total_cost = sum(r['cost'] for r in known)
    total_profit = sum(r['profit'] for r in known)
    overall_margin = round((total_profit / revenue_known) * 100, 1) if revenue_known > 0 else 0

    return {
        'total_products': len(results),
        'red_count': red,
        'yellow_count': yellow,
        'green_count': green,
        'no_cost_count': no_cost,
        'total_revenue': round(sum(r['revenue'] for r in results), 2),
        'total_cost': round(total_cost, 2),
        'total_profit': round(total_profit, 2),
        'overall_margin': overall_margin,
        'revenue_with_cost': round(revenue_known, 2),
    }
