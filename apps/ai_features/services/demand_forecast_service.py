from decimal import Decimal
from datetime import datetime, timedelta
from collections import defaultdict
from django.db.models import Sum
from django.db.models import DecimalField as DjDecimalField
from django.db.models.functions import Coalesce, TruncMonth
from apps.products.models import Products
from apps.sales.models import SaleInvoiceItems
import numpy as np
from sklearn.linear_model import LinearRegression
import logging

logger = logging.getLogger(__name__)


def get_demand_forecast(period_days=365, forecast_days=90, limit=500, from_date=None, to_date=None):
    """
    ML-based demand forecasting for all products.

    Unlike stock_forecast (simple average), this uses Linear Regression to detect
    TRENDS in sales data — rising demand, falling demand, or stable.

    Args:
        period_days: How far back to look at sales history (default 365 days)
        forecast_days: How many days into the future to predict (default 90)

    Returns:
        (forecasts, summary)
        - forecasts: list of dicts with product + prediction data
        - summary: overall counts and totals
    """
    forecast_days = max(forecast_days, 1)
    end_date = to_date or datetime.now().date()
    start_date = from_date or (end_date - timedelta(days=period_days))

    # Get monthly sales per product (grouped by month)
    monthly_sales = SaleInvoiceItems.objects.filter(
        sale_invoice_id__invoice_date__gte=start_date,
        sale_invoice_id__invoice_date__lte=end_date
    ).annotate(
        month=TruncMonth('sale_invoice_id__invoice_date')
    ).values(
        'product_id', 'month'
    ).annotate(
        total_qty=Coalesce(Sum('quantity'), Decimal('0'), output_field=DjDecimalField())
    ).order_by('product_id', 'month')

    # Group by product
    product_monthly = defaultdict(list)
    for row in monthly_sales:
        if row['product_id']:
            pid = str(row['product_id']).replace('-', '')
            product_monthly[pid].append({
                'month': row['month'],
                'qty': float(row['total_qty']),
            })

    # Load products
    products = Products.objects.filter(
        is_deleted=False
    ).exclude(
        status='Inactive'
    ).select_related(
        'product_group_id',
        'category_id',
        'type_id',
        'unit_options_id'
    )[:limit]

    product_map = {}
    for p in products:
        pid = str(p.product_id).replace('-', '')
        product_map[pid] = p

    forecasts = []
    summary = {
        'total_products_analyzed': 0,
        'trending_up': 0,
        'trending_down': 0,
        'stable': 0,
        'insufficient_data': 0,
        'stockout_risk': 0,
    }

    forecast_months = max(forecast_days / 30, 1)

    for pid, monthly_data in product_monthly.items():
        product = product_map.get(pid)
        if not product:
            continue

        summary['total_products_analyzed'] += 1

        # Need at least 3 months of data for meaningful trend detection
        if len(monthly_data) < 3:
            summary['insufficient_data'] += 1
            continue

        # Prepare data for Linear Regression
        # X = month index (0, 1, 2, ...), Y = quantity sold
        months_sorted = sorted(monthly_data, key=lambda x: x['month'])
        X = np.array(range(len(months_sorted))).reshape(-1, 1)
        Y = np.array([m['qty'] for m in months_sorted])

        # Fit linear regression
        model = LinearRegression()
        model.fit(X, Y)

        slope = float(model.coef_[0])
        intercept = float(model.intercept_)

        # Predict next months
        last_index = len(months_sorted) - 1
        predicted_monthly = []
        for i in range(1, int(forecast_months) + 1):
            future_index = last_index + i
            predicted_qty = max(0, intercept + slope * future_index)
            predicted_monthly.append(round(predicted_qty, 1))

        total_predicted = round(sum(predicted_monthly), 1)

        # Calculate avg historical monthly sales for comparison
        avg_historical = round(np.mean(Y), 1)

        # Determine trend
        # slope_pct = how much monthly sales change as % of average
        if avg_historical > 0:
            slope_pct = round((slope / avg_historical) * 100, 1)
        else:
            slope_pct = 0.0

        if slope_pct > 5:
            trend = 'UP'
            summary['trending_up'] += 1
        elif slope_pct < -5:
            trend = 'DOWN'
            summary['trending_down'] += 1
        else:
            trend = 'STABLE'
            summary['stable'] += 1

        # Current stock vs predicted demand — will they run out?
        current_stock = float(product.balance) if product.balance else 0.0
        stock_vs_demand = round(current_stock - total_predicted, 1)

        if total_predicted > 0:
            days_of_stock = round(current_stock / (total_predicted / forecast_days))
        else:
            days_of_stock = 999

        if stock_vs_demand < 0:
            risk = 'HIGH'
            summary['stockout_risk'] += 1
        elif days_of_stock <= 30:
            risk = 'MEDIUM'
            summary['stockout_risk'] += 1
        else:
            risk = 'LOW'

        forecasts.append({
            'product': product,
            'current_stock': current_stock,
            'avg_monthly_sales': avg_historical,
            'trend': trend,
            'trend_slope': round(slope, 2),
            'trend_pct': slope_pct,
            'predicted_demand': total_predicted,
            'predicted_monthly': predicted_monthly,
            'stock_vs_demand': stock_vs_demand,
            'days_of_stock': min(days_of_stock, 999),
            'risk': risk,
            'data_months': len(months_sorted),
            'last_month_sales': round(months_sorted[-1]['qty'], 1),
        })

    # Sort: HIGH risk first, then by days_of_stock ascending
    risk_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
    forecasts.sort(key=lambda x: (risk_order.get(x['risk'], 3), x['days_of_stock']))

    return forecasts, summary
