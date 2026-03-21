from decimal import Decimal
from django.db.models import Avg, Max, F
from django.db import transaction
from django.utils import timezone
from apps.products.models import Products
from apps.purchase.models import (
    PurchaseOrders, PurchaseorderItems,
    PurchaseInvoiceItem, PurchaseInvoiceOrders,
)
from apps.vendor.models import Vendor
import logging

logger = logging.getLogger(__name__)


def get_reorder_suggestions(limit=500):
    """
    Find products below minimum_level that have purchase history,
    meaning they are purchased (not manufactured). Suggests best vendor + qty.
    """
    low_stock_products = (
        Products.objects
        .filter(
            is_deleted=False,
            balance__lt=F('minimum_level'),
            minimum_level__isnull=False,
        )
        .select_related('unit_options_id')[:limit]
    )

    if not low_stock_products:
        return []

    results = []
    for product in low_stock_products:
        # Find vendors who have supplied this product (from purchase invoices)
        vendor_data = (
            PurchaseInvoiceItem.objects
            .filter(
                product_id=product.product_id,
                purchase_invoice_id__is_deleted=False,
            )
            .values(
                vendor_id=F('purchase_invoice_id__vendor_id'),
                vendor_name=F('purchase_invoice_id__vendor_id__name'),
            )
            .annotate(
                avg_rate=Avg('rate'),
                last_rate=Max('rate'),
                latest_date=Max('purchase_invoice_id__invoice_date'),
            )
            .order_by('avg_rate')
        )

        if not vendor_data.exists():
            continue

        # Best vendor = lowest average rate
        best = vendor_data.first()

        # Get the most recent rate for accurate pricing
        latest_invoice_item = (
            PurchaseInvoiceItem.objects
            .filter(
                product_id=product.product_id,
                purchase_invoice_id__vendor_id=best['vendor_id'],
                purchase_invoice_id__is_deleted=False,
            )
            .order_by('-purchase_invoice_id__invoice_date')
            .first()
        )
        latest_rate = latest_invoice_item.rate if latest_invoice_item else best['avg_rate']

        max_level = product.maximum_level or (product.minimum_level * 2)
        if max_level < product.minimum_level:
            max_level = product.minimum_level * 2
        shortage = max(0, product.minimum_level - product.balance)
        reorder_qty = max(0, max_level - product.balance)
        estimated_cost = Decimal(str(reorder_qty)) * (latest_rate or Decimal('0'))

        # All vendors who supply this product (for alternatives)
        all_vendors = [
            {
                'vendor_id': str(v['vendor_id']),
                'vendor_name': v['vendor_name'],
                'avg_rate': float(v['avg_rate'] or 0),
                'latest_date': v['latest_date'].isoformat() if v['latest_date'] else None,
            }
            for v in vendor_data
        ]

        results.append({
            'product': product,
            'current_balance': product.balance,
            'minimum_level': product.minimum_level,
            'maximum_level': max_level,
            'shortage': shortage,
            'reorder_qty': reorder_qty,
            'best_vendor_id': str(best['vendor_id']),
            'best_vendor_name': best['vendor_name'],
            'latest_rate': float(latest_rate or 0),
            'estimated_cost': float(estimated_cost),
            'all_vendors': all_vendors,
        })

    results.sort(key=lambda x: -x['shortage'])
    return results


def create_purchase_order(items):
    """
    Create PurchaseOrders grouped by vendor.
    items: list of dicts with product_id, vendor_id, quantity, rate
    Returns list of created PurchaseOrder objects.
    """
    if not items:
        raise ValueError("No items provided for purchase order creation")

    # Group items by vendor
    vendor_groups = {}
    for item in items:
        vid = item['vendor_id']
        if vid not in vendor_groups:
            vendor_groups[vid] = []
        vendor_groups[vid].append(item)

    created_orders = []

    with transaction.atomic():
        for vendor_id, vendor_items in vendor_groups.items():
            try:
                vendor = Vendor.objects.get(vendor_id=vendor_id)
            except Vendor.DoesNotExist:
                raise ValueError(f"Vendor with ID '{vendor_id}' not found")

            # Calculate order totals
            total_amount = Decimal('0')
            for vi in vendor_items:
                qty = Decimal(str(vi['quantity']))
                rate = Decimal(str(vi['rate']))
                total_amount += qty * rate

            # Create PurchaseOrder (order_no and status auto-set by model save())
            po = PurchaseOrders.objects.create(
                vendor_id=vendor,
                order_date=timezone.now().date(),
                tax='Exclusive',
                item_value=total_amount,
                total_amount=total_amount,
                taxable=total_amount,
                remarks='Auto-generated by AI Reorder System',
            )

            # Create PurchaseorderItems
            for vi in vendor_items:
                product = Products.objects.get(product_id=vi['product_id'], is_deleted=False)
                qty = Decimal(str(vi['quantity']))
                rate = Decimal(str(vi['rate']))
                amount = qty * rate

                PurchaseorderItems.objects.create(
                    purchase_order_id=po,
                    product_id=product,
                    unit_options_id=product.unit_options_id,
                    quantity=qty,
                    rate=rate,
                    amount=amount,
                )

            created_orders.append(po)

    return created_orders
