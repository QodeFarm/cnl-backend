from decimal import Decimal
from django.db.models import F
from apps.products.models import Products
from apps.production.models import BOM, BillOfMaterials, ProductionStatus, WorkOrder
import logging

logger = logging.getLogger(__name__)


def get_work_order_suggestions(limit=500):
    """
    Find products below minimum_level that have a BOM defined,
    meaning they can be manufactured. Check raw material availability.
    """
    # Products below minimum stock that have at least one BOM
    low_stock_products = (
        Products.objects
        .filter(
            is_deleted=False,
            balance__lt=F('minimum_level'),
            minimum_level__isnull=False,
            bom__is_deleted=False,  # Has at least one active BOM
        )
        .select_related('type_id', 'category_id', 'product_group_id')
        .distinct()[:limit]
    )

    if not low_stock_products:
        return []

    results = []
    for product in low_stock_products:
        # Get the BOM for this product
        bom = (
            BOM.objects
            .filter(product_id=product.product_id, is_deleted=False)
            .first()
        )
        if not bom:
            continue

        # Get BOM components (raw materials needed)
        bom_items = (
            BillOfMaterials.objects
            .filter(reference_id=str(bom.bom_id), is_deleted=False)
            .select_related('product_id')
        )

        if not bom_items.exists():
            continue

        # Calculate suggested quantity
        max_level = product.maximum_level or (product.minimum_level * 2)
        if max_level < product.minimum_level:
            max_level = product.minimum_level * 2
        shortage = max(0, product.minimum_level - product.balance)
        suggested_qty = max(0, max_level - product.balance)

        # Check raw material availability for each BOM component
        materials = []
        can_produce = True
        max_producible = None

        for item in bom_items:
            raw_material = item.product_id  # FK to Products
            if not raw_material:
                continue
            required_per_unit = item.quantity or 0
            total_required = required_per_unit * suggested_qty
            available = raw_material.balance or 0

            is_sufficient = available >= total_required
            if not is_sufficient:
                can_produce = False

            # How many finished goods can we make with available raw material?
            if required_per_unit > 0:
                producible = available // required_per_unit
                if max_producible is None:
                    max_producible = producible
                else:
                    max_producible = min(max_producible, producible)

            materials.append({
                'product_id': str(raw_material.product_id),
                'product_name': raw_material.name,
                'product_code': raw_material.code,
                'required_per_unit': required_per_unit,
                'total_required': total_required,
                'available': available,
                'shortage': max(0, total_required - available),
                'is_sufficient': is_sufficient,
            })

        results.append({
            'product': product,
            'bom_id': str(bom.bom_id),
            'bom_name': bom.bom_name,
            'current_balance': product.balance,
            'minimum_level': product.minimum_level,
            'maximum_level': max_level,
            'shortage': shortage,
            'suggested_qty': suggested_qty,
            'can_produce': can_produce,
            'max_producible_qty': max_producible or 0,
            'materials': materials,
        })

    # Sort: producible first, then by shortage severity
    results.sort(key=lambda x: (not x['can_produce'], -x['shortage']))

    return results


def create_work_order(product_id, quantity):
    """
    Create a WorkOrder for a product with its BOM components.
    Returns the created WorkOrder or raises an exception.
    """
    product = Products.objects.get(product_id=product_id, is_deleted=False)

    bom = (
        BOM.objects
        .filter(product_id=product_id, is_deleted=False)
        .first()
    )
    if not bom:
        raise ValueError(f"No BOM defined for product {product.name}")

    bom_items = (
        BillOfMaterials.objects
        .filter(reference_id=str(bom.bom_id), is_deleted=False)
    )
    if not bom_items.exists():
        raise ValueError(f"BOM '{bom.bom_name}' has no materials defined")

    # Verify raw material availability
    for item in bom_items:
        total_needed = item.quantity * quantity
        if item.product_id.balance < total_needed:
            raise ValueError(
                f"Insufficient raw material: {item.product_id.name} "
                f"(need {total_needed}, have {item.product_id.balance})"
            )

    # Get 'open' status
    open_status = ProductionStatus.objects.filter(status_name='open').first()
    if not open_status:
        raise ValueError("ProductionStatus 'open' not found in database")

    # Create the WorkOrder
    work_order = WorkOrder.objects.create(
        product_id=product,
        quantity=quantity,
        status_id=open_status,
    )

    # Create BOM items for this work order and deduct raw material stock
    for item in bom_items:
        total_needed = item.quantity * quantity
        BillOfMaterials.objects.create(
            reference_id=str(work_order.work_order_id),
            product_id=item.product_id,
            size_id=item.size_id,
            color_id=item.color_id,
            quantity=total_needed,
            original_quantity=total_needed,
            unit_cost=item.unit_cost,
            total_cost=item.unit_cost * total_needed,
        )
        # Deduct raw material stock (same as existing WorkOrder creation logic)
        raw_material = item.product_id
        raw_material.balance -= total_needed
        raw_material.save()

    return work_order
