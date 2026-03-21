from decimal import Decimal
from datetime import datetime, timedelta
from collections import defaultdict
from django.db.models import Sum
from django.db.models.functions import Coalesce, TruncMonth
from django.db.models import DecimalField as DjDecimalField
from apps.products.models import Products
from apps.production.models import BOM, BillOfMaterials
from apps.sales.models import SaleInvoiceItems
import logging

logger = logging.getLogger(__name__)


def get_what_if_simulation(growth_pct=20, forecast_months=3, period_days=365, from_date=None, to_date=None):
    """
    What-If Scenario Simulator:
    "If my sales grow by X%, can my raw materials handle it?"

    1. Gets avg monthly sales per finished product (from SaleInvoiceItems)
    2. Applies growth multiplier to project future demand
    3. Explodes projected demand through BOM to raw materials
    4. Compares required raw materials to current stock (Products.balance)
    5. Calculates shortfall and estimated purchase cost

    Args:
        growth_pct: Sales growth percentage (e.g. 20 means +20%)
        forecast_months: How many months to project forward
        period_days: Historical lookback for avg sales calculation

    Returns:
        (materials_list, summary)
    """
    end_date = to_date or datetime.now().date()
    start_date = from_date or (end_date - timedelta(days=period_days))
    actual_days = (end_date - start_date).days or 1
    months_of_data = max(Decimal(str(actual_days)) / Decimal('30'), Decimal('1'))
    growth_multiplier = Decimal('1') + Decimal(str(growth_pct)) / Decimal('100')

    # --- Step 1: Avg monthly sales per finished product ---
    monthly_sales = (
        SaleInvoiceItems.objects
        .filter(
            sale_invoice_id__invoice_date__gte=start_date,
            sale_invoice_id__invoice_date__lte=end_date,
        )
        .values('product_id')
        .annotate(
            total_qty=Coalesce(Sum('quantity'), Decimal('0'), output_field=DjDecimalField())
        )
    )

    product_avg_monthly = {}
    for row in monthly_sales:
        if row['product_id']:
            avg = row['total_qty'] / months_of_data
            product_avg_monthly[row['product_id']] = avg

    if not product_avg_monthly:
        return [], {
            'growth_pct': growth_pct,
            'forecast_months': forecast_months,
            'total_materials_analyzed': 0,
            'materials_short': 0,
            'materials_ok': 0,
            'total_additional_cost': 0,
            'can_handle_growth': True,
        }

    # --- Step 2: Load BOM structure ---
    bom_records = (
        BOM.objects
        .filter(is_deleted=False)
        .values('bom_id', 'product_id')
    )
    finished_product_to_bom_id = {}
    for b in bom_records:
        finished_product_to_bom_id[b['product_id']] = str(b['bom_id'])

    bom_material_rows = (
        BillOfMaterials.objects
        .filter(is_deleted=False)
        .values('reference_id', 'product_id', 'quantity', 'unit_cost')
    )

    # bom_id -> list of {raw_material_id, qty_per_unit, unit_cost}
    bom_id_to_materials = defaultdict(list)
    for row in bom_material_rows:
        bom_id_to_materials[row['reference_id']].append({
            'raw_material_id': row['product_id'],
            'qty_per_unit': Decimal(str(row['quantity'])) if row['quantity'] else Decimal('0'),
            'unit_cost': Decimal(str(row['unit_cost'])) if row['unit_cost'] else Decimal('0'),
        })

    # --- Step 3: Project demand and explode through BOM ---
    # For each finished product with sales, apply growth and calculate raw material needs
    raw_material_demand = defaultdict(lambda: {
        'total_needed': Decimal('0'),
        'unit_cost': Decimal('0'),
        'demanded_by': [],  # which finished products drive this demand
    })

    products_simulated = 0
    for finished_id, avg_monthly in product_avg_monthly.items():
        bom_id = finished_product_to_bom_id.get(finished_id)
        if not bom_id:
            continue  # No BOM = not a manufactured product, skip

        projected_monthly = avg_monthly * growth_multiplier
        projected_total = projected_monthly * Decimal(str(forecast_months))
        products_simulated += 1

        materials = bom_id_to_materials.get(bom_id, [])
        for mat in materials:
            rm_id = mat['raw_material_id']
            needed = projected_total * mat['qty_per_unit']
            raw_material_demand[rm_id]['total_needed'] += needed
            if mat['unit_cost'] > 0:
                raw_material_demand[rm_id]['unit_cost'] = mat['unit_cost']
            raw_material_demand[rm_id]['demanded_by'].append({
                'finished_product_id': finished_id,
                'projected_qty': float(round(projected_total, 2)),
                'material_per_unit': float(mat['qty_per_unit']),
                'material_needed': float(round(needed, 2)),
            })

    if not raw_material_demand:
        return [], {
            'growth_pct': growth_pct,
            'forecast_months': forecast_months,
            'total_materials_analyzed': 0,
            'materials_short': 0,
            'materials_ok': 0,
            'total_additional_cost': 0,
            'can_handle_growth': True,
            'products_simulated': products_simulated,
        }

    # --- Step 4: Load raw material products and compare ---
    rm_ids = list(raw_material_demand.keys())
    raw_materials = (
        Products.objects
        .filter(product_id__in=rm_ids, is_deleted=False)
        .exclude(status='Inactive')
        .select_related('product_group_id', 'category_id', 'unit_options_id')
    )

    # Also load finished product names for the demanded_by list
    all_finished_ids = set()
    for rm_data in raw_material_demand.values():
        for db in rm_data['demanded_by']:
            all_finished_ids.add(db['finished_product_id'])

    finished_names = dict(
        Products.objects
        .filter(product_id__in=list(all_finished_ids))
        .values_list('product_id', 'name')
    )

    results = []
    summary = {
        'growth_pct': growth_pct,
        'forecast_months': forecast_months,
        'total_materials_analyzed': 0,
        'materials_short': 0,
        'materials_ok': 0,
        'total_additional_cost': 0.0,
        'can_handle_growth': True,
        'products_simulated': products_simulated,
    }

    for product in raw_materials:
        pid = product.product_id
        demand_info = raw_material_demand.get(pid)
        if not demand_info:
            continue

        current_stock = Decimal(str(product.balance)) if product.balance else Decimal('0')
        total_needed = demand_info['total_needed']
        unit_cost = demand_info['unit_cost']

        shortfall = total_needed - current_stock
        if shortfall < 0:
            shortfall = Decimal('0')

        additional_cost = shortfall * unit_cost if unit_cost > 0 else Decimal('0')

        if shortfall > 0:
            status_label = 'SHORT'
            summary['materials_short'] += 1
            summary['can_handle_growth'] = False
        else:
            status_label = 'OK'
            summary['materials_ok'] += 1

        stock_coverage_pct = float(round(
            (current_stock / total_needed * 100) if total_needed > 0 else Decimal('999'),
            1
        ))

        # Enrich demanded_by with finished product names
        demanded_by = []
        for db in demand_info['demanded_by']:
            db_copy = dict(db)
            db_copy['finished_product_name'] = finished_names.get(
                db['finished_product_id'], 'Unknown'
            )
            demanded_by.append(db_copy)

        summary['total_materials_analyzed'] += 1
        summary['total_additional_cost'] += float(round(additional_cost, 2))

        results.append({
            'product': product,
            'current_stock': float(round(current_stock, 2)),
            'total_needed': float(round(total_needed, 2)),
            'shortfall': float(round(shortfall, 2)),
            'unit_cost': float(round(unit_cost, 2)),
            'additional_cost': float(round(additional_cost, 2)),
            'stock_coverage_pct': min(stock_coverage_pct, 999.0),
            'status': status_label,
            'demanded_by': demanded_by,
        })

    # Sort: SHORT first, then by shortfall descending
    status_order = {'SHORT': 0, 'OK': 1}
    results.sort(key=lambda x: (status_order.get(x['status'], 2), -x['shortfall']))

    summary['total_additional_cost'] = round(summary['total_additional_cost'], 2)

    return results, summary
