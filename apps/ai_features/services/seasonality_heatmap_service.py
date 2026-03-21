from django.db.models import Sum, F, Value, CharField
from django.db.models.functions import ExtractMonth, ExtractYear
from apps.sales.models import SaleInvoiceItems, SaleInvoiceOrders
from apps.products.models import Products
from datetime import date, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def get_seasonality_heatmap(period_months=24, from_date=None, to_date=None):
    today = to_date or date.today()
    start_date = from_date or (today - timedelta(days=period_months * 30))

    # Query: product x month aggregation from SaleInvoiceItems
    sale_filter = dict(
        sale_invoice_id__is_deleted=False,
        sale_invoice_id__invoice_date__gte=start_date,
    )
    if to_date:
        sale_filter['sale_invoice_id__invoice_date__lte'] = to_date
    raw = (
        SaleInvoiceItems.objects
        .filter(**sale_filter)
        .values(
            'product_id',
            month=ExtractMonth('sale_invoice_id__invoice_date'),
            year=ExtractYear('sale_invoice_id__invoice_date'),
        )
        .annotate(
            total_qty=Sum('quantity'),
            total_revenue=Sum('amount'),
        )
        .order_by('product_id', 'year', 'month')
    )

    if not raw:
        return [], {}

    # Collect product IDs
    product_ids = set(r['product_id'] for r in raw)
    products = {
        p.product_id: p
        for p in Products.objects.filter(
            product_id__in=product_ids, is_deleted=False
        ).select_related('product_group_id', 'category_id')
    }

    # Build: product_id → { month_num → { qty, revenue, count_years } }
    product_monthly = defaultdict(lambda: defaultdict(lambda: {'qty': 0, 'revenue': 0, 'years': set()}))
    for r in raw:
        pid = r['product_id']
        m = r['month']
        product_monthly[pid][m]['qty'] += float(r['total_qty'] or 0)
        product_monthly[pid][m]['revenue'] += float(r['total_revenue'] or 0)
        product_monthly[pid][m]['years'].add(r['year'])

    # Calculate number of distinct years per product to compute averages
    results = []
    for pid, months_data in product_monthly.items():
        product = products.get(pid)
        if not product:
            continue

        all_years = set()
        for m_data in months_data.values():
            all_years.update(m_data['years'])
        num_years = max(len(all_years), 1)

        monthly = []
        total_qty = 0
        for m_num in range(1, 13):
            md = months_data.get(m_num, {'qty': 0, 'revenue': 0})
            avg_qty = round(md['qty'] / num_years, 1)
            avg_revenue = round(md['revenue'] / num_years, 2)
            monthly.append({
                'month': m_num,
                'month_name': MONTH_NAMES[m_num - 1],
                'avg_qty': avg_qty,
                'avg_revenue': avg_revenue,
            })
            total_qty += avg_qty

        # Determine peak and low months
        if total_qty > 0:
            avg_monthly_qty = total_qty / 12
            for m in monthly:
                ratio = m['avg_qty'] / avg_monthly_qty if avg_monthly_qty > 0 else 0
                if ratio >= 1.5:
                    m['intensity'] = 'PEAK'
                elif ratio >= 1.0:
                    m['intensity'] = 'ABOVE_AVG'
                elif ratio >= 0.5:
                    m['intensity'] = 'NORMAL'
                elif ratio > 0:
                    m['intensity'] = 'LOW'
                else:
                    m['intensity'] = 'NONE'
        else:
            for m in monthly:
                m['intensity'] = 'NONE'

        # Find peak months
        peak_months = [m['month_name'] for m in monthly if m['intensity'] == 'PEAK']
        low_months = [m['month_name'] for m in monthly if m['intensity'] == 'LOW']

        results.append({
            'product': product,
            'total_avg_qty': round(total_qty, 1),
            'monthly': monthly,
            'peak_months': peak_months,
            'low_months': low_months,
            'data_years': num_years,
        })

    # Sort by total quantity descending (most sold products first)
    results.sort(key=lambda x: -x['total_avg_qty'])

    # Summary
    total_products = len(results)
    products_with_peaks = sum(1 for r in results if r['peak_months'])
    products_with_lows = sum(1 for r in results if r['low_months'])

    # Month totals across all products
    month_totals = [0.0] * 12
    for r in results:
        for m in r['monthly']:
            month_totals[m['month'] - 1] += m['avg_qty']
    busiest_month_idx = month_totals.index(max(month_totals)) if month_totals else 0
    slowest_month_idx = month_totals.index(min(month_totals)) if month_totals else 0

    summary = {
        'total_products_analyzed': total_products,
        'products_with_seasonal_peaks': products_with_peaks,
        'products_with_seasonal_lows': products_with_lows,
        'busiest_month': MONTH_NAMES[busiest_month_idx],
        'slowest_month': MONTH_NAMES[slowest_month_idx],
        'data_period_months': period_months,
        'month_totals': [{'month': MONTH_NAMES[i], 'total_qty': round(month_totals[i], 1)} for i in range(12)],
    }

    return results, summary
