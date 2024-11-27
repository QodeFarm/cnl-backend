# utils.py

from collections import defaultdict

def prepare_monthly_sales_data(results):
    months = [
        "January", "February", "March", "April", "May",
        "June", "July", "August", "September", "October",
        "November", "December"
    ]
    sales_count = [0] * 12

    for result in results:
        month_index = int(result[0]) - 1
        sales_count[month_index] = result[1]

    return {
        "month": months,
        "sales_count": sales_count,
    }

def prepare_trend_data(results, labels, data_indexes):
    """Prepares data for trend-based queries like daily, weekly, or monthly sales."""
    trend_data = {label: [] for label in labels}

    for entry in results:
        for label, index in zip(labels, data_indexes):
            trend_data[label].append(entry[index])

    return trend_data

def prepare_high_selling_data(results, time_labels):
    """Prepares data for high-selling products by weekly, monthly, or yearly time frames."""
    product_names = set()
    sales_data = defaultdict(lambda: [0] * len(time_labels))

    for time_unit, product, sales in results:
        if product not in product_names:
            product_names.add(product)
        
        time_index = time_labels.index(time_unit)
        sales_data[product][time_index] += sales
    
    return {
        "label": time_labels,
        "product_names": sorted(product_names),
        "sales_data": [sales_data[product] for product in sorted(product_names)],
    }

def prepare_revenue_data(results, label):
    """Prepares revenue data with a given label."""
    return {
        "label": label,
        "revenue": results[0][0]
    }

def prepare_revenue_series(results):
    """Prepares a revenue series data format."""
    months_or_time_units, revenue = zip(*results)
    return {
        "label": months_or_time_units,
        "revenue": revenue
    }
