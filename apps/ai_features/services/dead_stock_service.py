from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Q, Sum
from apps.products.models import Products
from apps.sales.models import SaleInvoiceItems, SaleInvoiceOrders
from apps.production.models import WorkOrder, BillOfMaterials
import logging

logger = logging.getLogger(__name__)

DEFAULT_DEAD_STOCK_DAYS = 90


def get_dead_stock(dead_days=None, limit=500, from_date=None, to_date=None):
    if dead_days is None:
        dead_days = DEFAULT_DEAD_STOCK_DAYS

    cutoff_date = from_date or (date.today() - timedelta(days=dead_days))

    # All active products with stock > 0
    products = list(
        Products.objects.filter(
            is_deleted=False,
            balance__gt=0,
        ).select_related('type_id', 'category_id', 'product_group_id')
    )

    if not products:
        return []

    # Products sold in the period (via invoice items joined to invoices)
    sold_filter = dict(
        sale_invoice_id__invoice_date__gte=cutoff_date,
        sale_invoice_id__is_deleted=False,
    )
    if to_date:
        sold_filter['sale_invoice_id__invoice_date__lte'] = to_date
    sold_product_ids = set(
        SaleInvoiceItems.objects
        .filter(**sold_filter)
        .values_list('product_id', flat=True)
        .distinct()
    )

    # Products consumed in production during the period
    # WorkOrders created/started in the period
    wo_filter = dict(
        is_deleted=False,
        created_at__date__gte=cutoff_date,
    )
    if to_date:
        wo_filter['created_at__date__lte'] = to_date
    recent_work_order_ids = list(
        WorkOrder.objects
        .filter(**wo_filter)
        .values_list('work_order_id', flat=True)
    )

    # BillOfMaterials.reference_id is a CharField storing the BOM/WorkOrder UUID
    consumed_product_ids = set()
    if recent_work_order_ids:
        wo_id_strings = [str(wid) for wid in recent_work_order_ids]
        consumed_product_ids = set(
            BillOfMaterials.objects
            .filter(
                reference_id__in=wo_id_strings,
                is_deleted=False,
            )
            .values_list('product_id', flat=True)
            .distinct()
        )

    # Dead stock = has balance but not sold and not consumed
    active_product_ids = sold_product_ids | consumed_product_ids

    results = []
    for product in products:
        if product.product_id in active_product_ids:
            continue

        purchase_rate = product.purchase_rate or Decimal('0')
        dead_value = float(product.balance * purchase_rate)

        results.append({
            'product': product,
            'balance': product.balance,
            'purchase_rate': float(purchase_rate),
            'dead_stock_value': dead_value,
            'last_sold_date': None,  # Will be enriched below
            'days_since_last_sale': None,
        })

    # Enrich with last sold date
    if results:
        dead_product_ids = [r['product'].product_id for r in results]

        # Get last sale date per dead product
        from django.db.models import Max
        last_sales = dict(
            SaleInvoiceItems.objects
            .filter(
                product_id__in=dead_product_ids,
                sale_invoice_id__is_deleted=False,
            )
            .values('product_id')
            .annotate(last_date=Max('sale_invoice_id__invoice_date'))
            .values_list('product_id', 'last_date')
        )

        today = date.today()
        for r in results:
            pid = r['product'].product_id
            last_date = last_sales.get(pid)
            r['last_sold_date'] = last_date
            if last_date:
                r['days_since_last_sale'] = (today - last_date).days

    # Sort by dead stock value descending (highest locked capital first)
    results.sort(key=lambda x: -x['dead_stock_value'])

    return results
