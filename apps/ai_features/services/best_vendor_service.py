from decimal import Decimal
from django.db.models import Sum, Count, Min, Max, Avg, Q, F
from apps.purchase.models import (
    PurchaseInvoiceItem, PurchaseInvoiceOrders,
    PurchaseOrders, PurchaseReturnItems, PurchaseReturnOrders,
)
from apps.vendor.models import Vendor
from apps.products.models import Products
import logging

logger = logging.getLogger(__name__)

WEIGHT_PRICE = 0.4
WEIGHT_DELIVERY = 0.3
WEIGHT_QUALITY = 0.3


def get_best_vendors(from_date=None, to_date=None):
    # Step 1: Get all vendor-product combinations from purchase invoices
    base_filter = dict(purchase_invoice_id__is_deleted=False)
    if from_date:
        base_filter['purchase_invoice_id__invoice_date__gte'] = from_date
    if to_date:
        base_filter['purchase_invoice_id__invoice_date__lte'] = to_date
    vendor_product_data = (
        PurchaseInvoiceItem.objects
        .filter(**base_filter)
        .values(
            'product_id',
            vendor_id=F('purchase_invoice_id__vendor_id'),
        )
        .annotate(
            avg_rate=Avg('rate'),
            total_qty=Sum('quantity'),
            total_amount=Sum('amount'),
            purchase_count=Count('purchase_invoice_item_id'),
        )
    )

    if not vendor_product_data:
        return []

    # Step 2: Get min/max rate per product (for price score normalization)
    product_rate_range = {}
    for row in vendor_product_data:
        pid = row['product_id']
        rate = float(row['avg_rate'] or 0)
        if pid not in product_rate_range:
            product_rate_range[pid] = {'min': rate, 'max': rate}
        else:
            product_rate_range[pid]['min'] = min(product_rate_range[pid]['min'], rate)
            product_rate_range[pid]['max'] = max(product_rate_range[pid]['max'], rate)

    # Step 3: Delivery score — on-time deliveries per vendor
    # On time = PurchaseInvoiceOrders.invoice_date <= PurchaseOrders.delivery_date
    # Since PO and PI are separate, we match by vendor_id
    vendor_delivery = {}
    purchase_orders = (
        PurchaseOrders.objects
        .filter(is_deleted=False, delivery_date__isnull=False)
        .values('vendor_id')
        .annotate(
            total_orders=Count('purchase_order_id'),
        )
    )
    for po in purchase_orders:
        vid = po['vendor_id']
        vendor_delivery[vid] = {'total': po['total_orders'], 'on_time': 0}

    # Count on-time: invoices where invoice_date <= expected delivery_date from PO
    on_time_counts = (
        PurchaseInvoiceOrders.objects
        .filter(
            is_deleted=False,
            vendor_id__in=vendor_delivery.keys(),
        )
        .values('vendor_id')
        .annotate(
            on_time=Count(
                'purchase_invoice_id',
                filter=Q(invoice_date__lte=F('delivery_date'))
            ),
            total_invoices=Count('purchase_invoice_id'),
        )
    )
    for row in on_time_counts:
        vid = row['vendor_id']
        if vid in vendor_delivery:
            vendor_delivery[vid]['on_time'] = row['on_time']
            # Use max of PO count and invoice count for accuracy
            vendor_delivery[vid]['total'] = max(vendor_delivery[vid]['total'], row['total_invoices'])

    # Step 4: Quality score — return ratio per vendor per product
    return_data = (
        PurchaseReturnItems.objects
        .filter(purchase_return_id__is_deleted=False)
        .values(
            'product_id',
            vendor_id=F('purchase_return_id__vendor_id'),
        )
        .annotate(
            return_qty=Sum('quantity'),
        )
    )
    return_map = {}
    for row in return_data:
        key = (row['vendor_id'], row['product_id'])
        return_map[key] = float(row['return_qty'] or 0)

    # Step 5: Calculate scores
    # Collect vendor and product IDs for bulk lookup
    vendor_ids = set()
    product_ids = set()
    for row in vendor_product_data:
        vendor_ids.add(row['vendor_id'])
        product_ids.add(row['product_id'])

    vendors = {
        v.vendor_id: v
        for v in Vendor.objects.filter(vendor_id__in=vendor_ids, is_deleted=False)
    }
    products = {
        p.product_id: p
        for p in Products.objects.filter(product_id__in=product_ids, is_deleted=False)
            .select_related('type_id', 'category_id', 'product_group_id')
    }

    scored = {}  # keyed by product_id -> list of vendor scores

    for row in vendor_product_data:
        pid = row['product_id']
        vid = row['vendor_id']

        vendor = vendors.get(vid)
        product = products.get(pid)
        if not vendor or not product:
            continue

        # Price score
        rate_range = product_rate_range.get(pid, {'min': 0, 'max': 0})
        avg_rate = float(row['avg_rate'] or 0)
        if rate_range['max'] == rate_range['min']:
            price_score = 100.0  # Only one vendor or all same price
        else:
            price_score = 100 * (1 - (avg_rate - rate_range['min']) / (rate_range['max'] - rate_range['min']))

        # Delivery score
        delivery_info = vendor_delivery.get(vid, {'total': 0, 'on_time': 0})
        if delivery_info['total'] > 0:
            delivery_score = 100 * (delivery_info['on_time'] / delivery_info['total'])
        else:
            delivery_score = 50.0  # No delivery data, neutral score

        # Quality score
        total_purchased = float(row['total_qty'] or 0)
        returned = return_map.get((vid, pid), 0)
        if total_purchased > 0:
            quality_score = max(0, 100 * (1 - returned / total_purchased))
        else:
            quality_score = 50.0

        final_score = round(
            (price_score * WEIGHT_PRICE) +
            (delivery_score * WEIGHT_DELIVERY) +
            (quality_score * WEIGHT_QUALITY),
            2
        )

        entry = {
            'vendor': vendor,
            'avg_rate': avg_rate,
            'total_qty_purchased': float(row['total_qty'] or 0),
            'purchase_count': row['purchase_count'],
            'price_score': round(price_score, 2),
            'delivery_score': round(delivery_score, 2),
            'quality_score': round(quality_score, 2),
            'total_score': final_score,
            'return_qty': returned,
        }

        if pid not in scored:
            scored[pid] = {'product': product, 'vendors': []}
        scored[pid]['vendors'].append(entry)

    # Sort vendors within each product by total_score descending
    results = []
    for pid, data in scored.items():
        data['vendors'].sort(key=lambda x: -x['total_score'])
        # Mark best vendor
        if data['vendors']:
            data['vendors'][0]['is_best'] = True
            for v in data['vendors'][1:]:
                v['is_best'] = False
        results.append(data)

    # Sort products by number of vendors (more competitive products first)
    results.sort(key=lambda x: -len(x['vendors']))

    return results
