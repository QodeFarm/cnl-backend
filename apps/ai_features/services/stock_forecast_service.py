from decimal import Decimal
from datetime import timedelta
from django.db.models import Sum
from django.db.models import DecimalField as DjDecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from apps.products.models import Products
from apps.sales.models import SaleInvoiceItems, SaleOrderItems


def get_at_risk_stock_forecast(period_days=180, limit=500, from_date=None, to_date=None):
    """
    Computes stock forecast for ALL products, then returns only RED and YELLOW
    status products with a summary. This avoids pagination issues when the
    AI dashboard needs to see all at-risk inventory at once.
    """
    end_date = to_date or timezone.now().date()
    start_date = from_date or (end_date - timedelta(days=period_days))
    actual_days = (end_date - start_date).days or 1
    months = max(actual_days / 30, 1)

    # Get sales data from SaleInvoiceItems + SaleOrderItems
    invoice_sales = SaleInvoiceItems.objects.filter(
        sale_invoice_id__invoice_date__gte=start_date,
        sale_invoice_id__invoice_date__lte=end_date
    ).values('product_id').annotate(
        total_sales=Coalesce(Sum('quantity'), Decimal('0'))
    )

    order_sales = SaleOrderItems.objects.filter(
        sale_order_id__order_date__gte=start_date,
        sale_order_id__order_date__lte=end_date
    ).values('product_id').annotate(
        total_sales=Coalesce(Sum('quantity'), Decimal('0'), output_field=DjDecimalField())
    )

    sales_dict = {}
    for item in invoice_sales:
        if item['product_id']:
            pid = str(item['product_id']).replace('-', '')
            sales_dict[pid] = Decimal(item['total_sales'])
    for item in order_sales:
        if item['product_id']:
            pid = str(item['product_id']).replace('-', '')
            if pid in sales_dict:
                sales_dict[pid] += Decimal(item['total_sales'])
            else:
                sales_dict[pid] = Decimal(item['total_sales'])

    # Query all non-deleted products with related data
    products = Products.objects.filter(
        is_deleted=False
    ).exclude(
        status='Inactive'
    ).select_related(
        'product_group_id',
        'category_id',
        'type_id',
        'unit_options_id'
    ).order_by('-created_at')[:limit]

    at_risk = []
    summary = {'red': 0, 'yellow': 0, 'green': 0, 'total': 0}

    for product in products:
        summary['total'] += 1
        current_stock = float(product.balance) if product.balance else 0.0
        pid = str(product.product_id).replace('-', '')
        total_sales = float(sales_dict.get(pid, 0))
        avg_sales = round(total_sales / months, 2)
        difference = round(current_stock - avg_sales, 2)

        # Status logic — matches ProductStockForecastSerializer exactly
        if avg_sales <= 0:
            status = 'GREEN'
        elif current_stock <= 0 or difference < 0:
            status = 'RED'
        elif current_stock < (avg_sales * 2):
            status = 'YELLOW'
        else:
            status = 'GREEN'

        if status == 'GREEN':
            summary['green'] += 1
            continue

        # Days remaining calculation
        if avg_sales <= 0:
            days_remaining = 999
        elif current_stock <= 0:
            days_remaining = 0
        else:
            days_remaining = round(current_stock / (avg_sales / 30))

        summary[status.lower()] += 1
        at_risk.append({
            'product': product,
            'current_stock': current_stock,
            'average_sales': avg_sales,
            'difference': difference,
            'status': status,
            'days_remaining': days_remaining,
        })

    # Sort: RED first, then by days_remaining ascending
    at_risk.sort(key=lambda x: (0 if x['status'] == 'RED' else 1, x['days_remaining']))

    return at_risk, summary, {
        'period_days': period_days,
        'start_date': str(start_date),
        'end_date': str(end_date),
        'months': round(months, 1),
    }
