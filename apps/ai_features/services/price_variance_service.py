"""
Purchase Price Variance Service
Compares purchase prices per product across vendors to detect overspending.
Identifies opportunities to save money by switching to cheaper vendors.
"""
import logging
from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg, Min, Max, Sum, F, Count
from django.utils import timezone

from apps.purchase.models import PurchaseInvoiceItem, PurchaseInvoiceOrders
from apps.products.models import Products

logger = logging.getLogger(__name__)


def get_price_variance(period_days=365, from_date=None, to_date=None):
    """
    Analyze purchase price variance across vendors for each product.

    For each product purchased from multiple vendors, calculates:
    - Average, min, max rate per vendor
    - Best available rate across all vendors
    - Overspend = (your_avg_rate - best_rate) × total_qty

    Returns: (variance_list, summary_dict)
    """
    cutoff = from_date or (timezone.now().date() - timedelta(days=period_days))
    end_cutoff = to_date

    # Get all purchase invoice items in the period
    qs_filter = dict(
        purchase_invoice_id__is_deleted=False,
        purchase_invoice_id__invoice_date__gte=cutoff,
    )
    if end_cutoff:
        qs_filter['purchase_invoice_id__invoice_date__lte'] = end_cutoff
    items = (
        PurchaseInvoiceItem.objects
        .filter(**qs_filter)
        .select_related(
            'product_id',
            'product_id__product_group_id',
            'purchase_invoice_id',
            'purchase_invoice_id__vendor_id',
        )
        .order_by('purchase_invoice_id__invoice_date')
    )

    if not items.exists():
        return [], _build_summary([])

    # Group by product → vendor → price data
    product_vendor_data = {}

    for item in items:
        product = item.product_id
        if not product:
            continue

        prod_id = str(product.product_id)
        invoice = item.purchase_invoice_id
        vendor = invoice.vendor_id if invoice else None
        if not vendor:
            continue

        vendor_id = str(vendor.vendor_id)

        if prod_id not in product_vendor_data:
            product_vendor_data[prod_id] = {
                'product': product,
                'vendors': {},
            }

        if vendor_id not in product_vendor_data[prod_id]['vendors']:
            product_vendor_data[prod_id]['vendors'][vendor_id] = {
                'vendor': vendor,
                'rates': [],
                'quantities': [],
                'amounts': [],
                'dates': [],
            }

        rate = float(item.rate) if item.rate else 0
        qty = float(item.quantity) if item.quantity else 0
        amount = float(item.amount) if item.amount else 0

        if rate > 0 and qty > 0:
            product_vendor_data[prod_id]['vendors'][vendor_id]['rates'].append(rate)
            product_vendor_data[prod_id]['vendors'][vendor_id]['quantities'].append(qty)
            product_vendor_data[prod_id]['vendors'][vendor_id]['amounts'].append(amount)
            product_vendor_data[prod_id]['vendors'][vendor_id]['dates'].append(
                invoice.invoice_date
            )

    results = []

    for prod_id, prod_data in product_vendor_data.items():
        vendors = prod_data['vendors']

        # Need at least 2 vendors to compare, or 1 vendor with multiple purchases
        if len(vendors) < 1:
            continue

        # Calculate stats per vendor for this product
        vendor_stats = []
        for vendor_id, v_data in vendors.items():
            rates = v_data['rates']
            quantities = v_data['quantities']
            if not rates:
                continue

            avg_rate = sum(rates) / len(rates)
            total_qty = sum(quantities)
            total_amount = sum(v_data['amounts'])

            # Price trend: compare first half avg vs second half avg
            if len(rates) >= 4:
                mid = len(rates) // 2
                first_half_avg = sum(rates[:mid]) / mid
                second_half_avg = sum(rates[mid:]) / (len(rates) - mid)
                pct_change = ((second_half_avg - first_half_avg) / first_half_avg) * 100 if first_half_avg else 0
                if pct_change > 5:
                    trend = 'INCREASING'
                elif pct_change < -5:
                    trend = 'DECREASING'
                else:
                    trend = 'STABLE'
            elif len(rates) >= 2:
                pct_change = ((rates[-1] - rates[0]) / rates[0]) * 100 if rates[0] else 0
                if pct_change > 5:
                    trend = 'INCREASING'
                elif pct_change < -5:
                    trend = 'DECREASING'
                else:
                    trend = 'STABLE'
            else:
                trend = 'STABLE'
                pct_change = 0

            vendor_stats.append({
                'vendor': v_data['vendor'],
                'avg_rate': round(avg_rate, 2),
                'min_rate': round(min(rates), 2),
                'max_rate': round(max(rates), 2),
                'latest_rate': round(rates[-1], 2),
                'total_qty': round(total_qty, 2),
                'total_amount': round(total_amount, 2),
                'purchase_count': len(rates),
                'trend': trend,
                'trend_pct': round(pct_change, 2),
            })

        if not vendor_stats:
            continue

        # Find best (lowest) average rate across all vendors for this product
        best_rate = min(vs['avg_rate'] for vs in vendor_stats)

        # Calculate overspend per vendor
        for vs in vendor_stats:
            overspend = (vs['avg_rate'] - best_rate) * vs['total_qty']
            vs['best_rate'] = best_rate
            vs['overspend'] = round(overspend, 2)

        # Only include vendors with overspend > 0, OR if single vendor (for visibility)
        for vs in vendor_stats:
            product = prod_data['product']
            results.append({
                'product': product,
                'vendor': vs['vendor'],
                'avg_rate': vs['avg_rate'],
                'min_rate': vs['min_rate'],
                'max_rate': vs['max_rate'],
                'latest_rate': vs['latest_rate'],
                'best_rate': vs['best_rate'],
                'total_qty': vs['total_qty'],
                'total_amount': vs['total_amount'],
                'overspend': vs['overspend'],
                'purchase_count': vs['purchase_count'],
                'trend': vs['trend'],
                'trend_pct': vs['trend_pct'],
            })

    # Sort by overspend descending (biggest savings first)
    results.sort(key=lambda x: x['overspend'], reverse=True)

    return results, _build_summary(results)


def _build_summary(results):
    """Build summary statistics for the price variance results."""
    total_overspend = sum(r['overspend'] for r in results)
    products_analyzed = len(set(str(r['product'].product_id) for r in results)) if results else 0
    vendors_compared = len(set(str(r['vendor'].vendor_id) for r in results)) if results else 0
    overspend_items = [r for r in results if r['overspend'] > 0]
    increasing_prices = sum(1 for r in results if r['trend'] == 'INCREASING')

    return {
        'total_overspend': round(total_overspend, 2),
        'products_analyzed': products_analyzed,
        'vendors_compared': vendors_compared,
        'overspend_items': len(overspend_items),
        'increasing_price_trends': increasing_prices,
    }
