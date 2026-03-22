from decimal import Decimal
from datetime import datetime, timedelta
from collections import defaultdict
from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from django.db.models import DecimalField as DjDecimalField
from apps.products.models import Products
from apps.production.models import BOM, BillOfMaterials, WorkOrder
import logging

logger = logging.getLogger(__name__)


def get_raw_material_forecast(period_days=365, from_date=None, to_date=None):
    """
    Forecasts how many days of raw materials remain based on
    PRODUCTION CONSUMPTION (WorkOrder + BOM), NOT sales data.

    Raw materials are never sold — they are consumed when work orders
    are completed. This service tracks that consumption rate and
    predicts when each raw material will run out.

    Args:
        period_days: How far back to look at production history (default 180)

    Returns:
        (results, summary)
    """
    end_date = to_date or datetime.now().date()
    start_date = from_date or (end_date - timedelta(days=period_days))
    actual_days = (end_date - start_date).days or 1
    months = max(Decimal(str(actual_days)) / Decimal('30'), Decimal('1'))

    # ──────────────────────────────────────────────────────
    # Step 1: Find all raw materials (products used in BOMs)
    # ──────────────────────────────────────────────────────
    bom_material_rows = (
        BillOfMaterials.objects
        .filter(is_deleted=False)
        .values('product_id', 'reference_id', 'quantity')
    )

    if not bom_material_rows.exists():
        return [], {
            'total_raw_materials': 0,
            'critical_count': 0,
            'warning_count': 0,
            'safe_count': 0,
        }

    # Build mapping: raw_material_product_id → list of BOM entries
    # Each BOM entry tells us: which finished product's BOM, qty per unit
    raw_material_ids = set()
    bom_id_to_materials = defaultdict(list)  # bom_id → material entries
    material_to_bom_ids = defaultdict(set)   # raw_mat_id → set of bom_ids

    for row in bom_material_rows:
        rm_id = row['product_id']
        bom_ref = row['reference_id']
        qty = row['quantity']
        raw_material_ids.add(rm_id)
        bom_id_to_materials[bom_ref].append({
            'raw_material_id': rm_id,
            'qty_per_unit': qty,
        })
        material_to_bom_ids[rm_id].add(bom_ref)

    # ──────────────────────────────────────────────────────
    # Step 2: Find finished products linked to each BOM
    # ──────────────────────────────────────────────────────
    bom_records = (
        BOM.objects
        .filter(is_deleted=False)
        .values('bom_id', 'product_id__name', 'product_id')
    )

    bom_id_to_finished = {}
    finished_product_to_bom_id = {}
    for b in bom_records:
        bom_str = str(b['bom_id'])
        bom_id_to_finished[bom_str] = {
            'product_id': b['product_id'],
            'product_name': b['product_id__name'],
        }
        finished_product_to_bom_id[b['product_id']] = bom_str

    # ──────────────────────────────────────────────────────
    # Step 3: Calculate consumption from completed WorkOrders
    # ──────────────────────────────────────────────────────
    # Get work orders with completed quantities in the period
    # Use start_date OR created_at for date filtering (start_date can be null)
    from django.db.models import Q
    work_orders = (
        WorkOrder.objects
        .filter(
            Q(start_date__gte=start_date) | Q(start_date__isnull=True, created_at__gte=start_date),
            is_deleted=False,
            completed_qty__gt=0,
        )
        .values('product_id', 'completed_qty')
    )

    # For each work order, figure out which raw materials were consumed
    # consumption = completed_qty × qty_per_unit (from BOM)
    consumption = defaultdict(Decimal)  # raw_material_id → total consumed

    for wo in work_orders:
        finished_id = wo['product_id']
        completed = Decimal(str(wo['completed_qty']))
        bom_id = finished_product_to_bom_id.get(finished_id)
        if not bom_id:
            continue

        materials_in_bom = bom_id_to_materials.get(bom_id, [])
        for mat in materials_in_bom:
            rm_id = mat['raw_material_id']
            qty_per = Decimal(str(mat['qty_per_unit']))
            consumption[rm_id] += completed * qty_per

    # ──────────────────────────────────────────────────────
    # Step 4: Load raw material products with current stock
    # ──────────────────────────────────────────────────────
    raw_materials = (
        Products.objects
        .filter(
            product_id__in=raw_material_ids,
            is_deleted=False,
        )
        .exclude(status='Inactive')
        .select_related('product_group_id', 'category_id', 'type_id', 'unit_options_id')
    )

    # ──────────────────────────────────────────────────────
    # Step 5: Calculate days remaining for each raw material
    # ──────────────────────────────────────────────────────
    results = []
    summary = {
        'total_raw_materials': 0,
        'critical_count': 0,
        'warning_count': 0,
        'safe_count': 0,
    }

    for product in raw_materials:
        pid = product.product_id
        total_consumed = consumption.get(pid, Decimal('0'))
        current_balance = Decimal(str(product.balance)) if product.balance else Decimal('0')

        avg_monthly = total_consumed / months if months > 0 else Decimal('0')
        avg_daily = avg_monthly / Decimal('30') if avg_monthly > 0 else Decimal('0')

        # Days remaining
        if avg_daily <= 0:
            if current_balance > 0:
                days_remaining = 999  # Has stock but no recent consumption
                status_label = 'GREEN'
            else:
                days_remaining = 0
                status_label = 'RED'  # No stock AND it's a raw material in BOM
        elif current_balance <= 0:
            days_remaining = 0
            status_label = 'RED'
        else:
            days_remaining = int(current_balance / avg_daily)
            if days_remaining <= 7:
                status_label = 'RED'
            elif days_remaining <= 30:
                status_label = 'YELLOW'
            else:
                status_label = 'GREEN'

        summary['total_raw_materials'] += 1
        if status_label == 'RED':
            summary['critical_count'] += 1
        elif status_label == 'YELLOW':
            summary['warning_count'] += 1
        else:
            summary['safe_count'] += 1

        # Find which finished products use this raw material
        used_in = []
        for bom_id in material_to_bom_ids.get(pid, set()):
            finished_info = bom_id_to_finished.get(bom_id)
            if finished_info:
                # Find qty_per_unit for this material in this BOM
                qty_per = 0
                for mat in bom_id_to_materials.get(bom_id, []):
                    if mat['raw_material_id'] == pid:
                        qty_per = mat['qty_per_unit']
                        break
                used_in.append({
                    'product_name': finished_info['product_name'],
                    'qty_per_unit': qty_per,
                })

        # Estimated stockout date
        if days_remaining > 0 and days_remaining < 999:
            stockout_date = str(end_date + timedelta(days=days_remaining))
        elif days_remaining == 0:
            stockout_date = str(end_date)
        else:
            stockout_date = None

        results.append({
            'product': product,
            'current_balance': float(current_balance),
            'total_consumed': float(total_consumed),
            'avg_monthly_consumption': round(float(avg_monthly), 2),
            'avg_daily_consumption': round(float(avg_daily), 2),
            'days_remaining': min(days_remaining, 999),
            'status': status_label,
            'used_in_products': used_in,
            'estimated_stockout_date': stockout_date,
        })

    # Sort: RED first, then YELLOW, then by days_remaining ascending
    status_order = {'RED': 0, 'YELLOW': 1, 'GREEN': 2}
    results.sort(key=lambda x: (status_order.get(x['status'], 3), x['days_remaining']))

    return results, summary
