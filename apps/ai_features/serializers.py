from rest_framework import serializers


class LowStockProductSerializer(serializers.Serializer):
    product_id = serializers.UUIDField()
    name = serializers.CharField()
    code = serializers.CharField()
    balance = serializers.IntegerField()
    minimum_level = serializers.IntegerField()
    maximum_level = serializers.IntegerField(allow_null=True)
    shortage = serializers.IntegerField()
    reorder_qty = serializers.IntegerField()
    severity = serializers.CharField()
    product_group = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()

    def get_product_group(self, obj):
        if obj.product_group_id:
            return {'id': str(obj.product_group_id.product_group_id), 'name': obj.product_group_id.group_name}
        return None

    def get_category(self, obj):
        if obj.category_id:
            return {'id': str(obj.category_id.category_id), 'name': obj.category_id.category_name}
        return None

    def get_unit(self, obj):
        if obj.unit_options_id:
            return {'id': str(obj.unit_options_id.unit_options_id), 'name': obj.unit_options_id.unit_name}
        return None


class StockForecastAlertSerializer(serializers.Serializer):
    product_id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()
    product_group = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    current_stock = serializers.FloatField()
    average_sales = serializers.FloatField()
    difference = serializers.FloatField()
    status = serializers.CharField()
    days_remaining = serializers.IntegerField()
    recommended_action = serializers.SerializerMethodField()

    def get_product_id(self, obj):
        return str(obj['product'].product_id)

    def get_name(self, obj):
        return obj['product'].name

    def get_code(self, obj):
        return obj['product'].code

    def get_product_group(self, obj):
        pg = obj['product'].product_group_id
        if pg:
            return {'id': str(pg.product_group_id), 'name': pg.group_name}
        return None

    def get_type(self, obj):
        t = obj['product'].type_id
        if t:
            return {'id': str(t.type_id), 'name': t.type_name}
        return None

    def get_category(self, obj):
        c = obj['product'].category_id
        if c:
            return {'id': str(c.category_id), 'name': c.category_name}
        return None

    def get_recommended_action(self, obj):
        return 'CREATE_WORK_ORDER'


class DebtDefaulterSerializer(serializers.Serializer):
    customer_id = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    customer_code = serializers.SerializerMethodField()
    total_overdue_amount = serializers.FloatField()
    overdue_invoices_count = serializers.IntegerField()
    oldest_overdue_date = serializers.DateField()
    max_overdue_days = serializers.IntegerField()
    risk_level = serializers.CharField()
    credit_limit = serializers.FloatField(allow_null=True)
    credit_utilization = serializers.FloatField(allow_null=True)

    def get_customer_id(self, obj):
        return str(obj['customer'].customer_id)

    def get_customer_name(self, obj):
        return obj['customer'].name

    def get_customer_code(self, obj):
        return obj['customer'].code


class InactiveCustomerSerializer(serializers.Serializer):
    customer_id = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    customer_code = serializers.SerializerMethodField()
    last_activity_date = serializers.DateField(allow_null=True)
    days_inactive = serializers.IntegerField()
    risk_level = serializers.CharField()
    total_invoices = serializers.IntegerField()

    def get_customer_id(self, obj):
        return str(obj['customer'].customer_id)

    def get_customer_name(self, obj):
        return obj['customer'].name

    def get_customer_code(self, obj):
        return obj['customer'].code


class DeadStockSerializer(serializers.Serializer):
    product_id = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_code = serializers.SerializerMethodField()
    product_type = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    balance = serializers.IntegerField()
    purchase_rate = serializers.FloatField()
    dead_stock_value = serializers.FloatField()
    last_sold_date = serializers.DateField(allow_null=True)
    days_since_last_sale = serializers.IntegerField(allow_null=True)

    def get_product_id(self, obj):
        return str(obj['product'].product_id)

    def get_product_name(self, obj):
        return obj['product'].name

    def get_product_code(self, obj):
        return obj['product'].code

    def get_product_type(self, obj):
        t = obj['product'].type_id
        if t:
            return {'id': str(t.type_id), 'name': t.type_name}
        return None

    def get_category(self, obj):
        c = obj['product'].category_id
        if c:
            return {'id': str(c.category_id), 'name': c.category_name}
        return None


class BestVendorSerializer(serializers.Serializer):
    product_id = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_code = serializers.SerializerMethodField()
    vendors = serializers.SerializerMethodField()

    def get_product_id(self, obj):
        return str(obj['product'].product_id)

    def get_product_name(self, obj):
        return obj['product'].name

    def get_product_code(self, obj):
        return obj['product'].code

    def get_vendors(self, obj):
        result = []
        for v in obj['vendors']:
            result.append({
                'vendor_id': str(v['vendor'].vendor_id),
                'vendor_name': v['vendor'].name,
                'vendor_code': v['vendor'].code,
                'avg_rate': v['avg_rate'],
                'total_qty_purchased': v['total_qty_purchased'],
                'purchase_count': v['purchase_count'],
                'price_score': v['price_score'],
                'delivery_score': v['delivery_score'],
                'quality_score': v['quality_score'],
                'total_score': v['total_score'],
                'return_qty': v['return_qty'],
                'is_best': v['is_best'],
            })
        return result


class WorkOrderSuggestionSerializer(serializers.Serializer):
    product_id = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_code = serializers.SerializerMethodField()
    bom_id = serializers.CharField()
    bom_name = serializers.CharField()
    current_balance = serializers.IntegerField()
    minimum_level = serializers.IntegerField()
    maximum_level = serializers.IntegerField()
    shortage = serializers.IntegerField()
    suggested_qty = serializers.IntegerField()
    can_produce = serializers.BooleanField()
    max_producible_qty = serializers.IntegerField()
    materials = serializers.ListField()

    def get_product_id(self, obj):
        return str(obj['product'].product_id)

    def get_product_name(self, obj):
        return obj['product'].name

    def get_product_code(self, obj):
        return obj['product'].code


class WorkOrderCreatedSerializer(serializers.Serializer):
    work_order_id = serializers.UUIDField()
    product_id = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    quantity = serializers.IntegerField()
    status = serializers.SerializerMethodField()

    def get_product_id(self, obj):
        return str(obj.product_id.product_id) if obj.product_id else None

    def get_product_name(self, obj):
        return obj.product_id.name if obj.product_id else None

    def get_status(self, obj):
        return obj.status_id.status_name if obj.status_id else None


class ReorderSuggestionSerializer(serializers.Serializer):
    product_id = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_code = serializers.SerializerMethodField()
    current_balance = serializers.IntegerField()
    minimum_level = serializers.IntegerField()
    maximum_level = serializers.IntegerField()
    shortage = serializers.IntegerField()
    reorder_qty = serializers.IntegerField()
    best_vendor_id = serializers.CharField()
    best_vendor_name = serializers.CharField()
    latest_rate = serializers.FloatField()
    estimated_cost = serializers.FloatField()
    all_vendors = serializers.ListField()

    def get_product_id(self, obj):
        return str(obj['product'].product_id)

    def get_product_name(self, obj):
        return obj['product'].name

    def get_product_code(self, obj):
        return obj['product'].code


class PurchaseOrderCreatedSerializer(serializers.Serializer):
    purchase_order_id = serializers.UUIDField()
    order_no = serializers.CharField()
    vendor_name = serializers.SerializerMethodField()
    order_date = serializers.DateField()
    total_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    order_status = serializers.SerializerMethodField()

    def get_vendor_name(self, obj):
        return obj.vendor_id.name if obj.vendor_id else None

    def get_order_status(self, obj):
        return obj.order_status_id.status_name if obj.order_status_id else None


class DemandForecastSerializer(serializers.Serializer):
    product_id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()
    product_group = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    current_stock = serializers.FloatField()
    avg_monthly_sales = serializers.FloatField()
    trend = serializers.CharField()
    trend_slope = serializers.FloatField()
    trend_pct = serializers.FloatField()
    predicted_demand = serializers.FloatField()
    predicted_monthly = serializers.ListField(child=serializers.FloatField())
    stock_vs_demand = serializers.FloatField()
    days_of_stock = serializers.IntegerField()
    risk = serializers.CharField()
    data_months = serializers.IntegerField()
    last_month_sales = serializers.FloatField()

    def get_product_id(self, obj):
        return str(obj['product'].product_id)

    def get_name(self, obj):
        return obj['product'].name

    def get_code(self, obj):
        return obj['product'].code

    def get_product_group(self, obj):
        pg = obj['product'].product_group_id
        if pg:
            return {'id': str(pg.product_group_id), 'name': pg.group_name}
        return None

    def get_category(self, obj):
        c = obj['product'].category_id
        if c:
            return {'id': str(c.category_id), 'name': c.category_name}
        return None


class ChurnRiskSerializer(serializers.Serializer):
    customer_id = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    customer_code = serializers.SerializerMethodField()
    recency_days = serializers.IntegerField()
    last_purchase_date = serializers.DateField(allow_null=True)
    purchase_count = serializers.IntegerField()
    total_spent = serializers.FloatField()
    r_score = serializers.IntegerField()
    f_score = serializers.IntegerField()
    m_score = serializers.IntegerField()
    rfm_score = serializers.FloatField()
    segment = serializers.CharField()

    def get_customer_id(self, obj):
        return str(obj['customer'].customer_id)

    def get_customer_name(self, obj):
        return obj['customer'].name

    def get_customer_code(self, obj):
        return obj['customer'].code


class CashFlowForecastSerializer(serializers.Serializer):
    week = serializers.IntegerField()
    start_date = serializers.CharField()
    end_date = serializers.CharField()
    inflow = serializers.FloatField()
    outflow_vendor = serializers.FloatField()
    outflow_expense = serializers.FloatField()
    total_outflow = serializers.FloatField()
    net = serializers.FloatField()
    cumulative = serializers.FloatField()


class ExpenseAnomalySerializer(serializers.Serializer):
    category_id = serializers.CharField()
    category_name = serializers.CharField()
    month = serializers.CharField()
    month_total = serializers.FloatField()
    category_mean = serializers.FloatField()
    category_std_dev = serializers.FloatField()
    deviation_score = serializers.FloatField()
    excess_amount = serializers.FloatField()
    severity = serializers.CharField()
    top_expenses = serializers.ListField()


class PriceVarianceSerializer(serializers.Serializer):
    product_id = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_code = serializers.SerializerMethodField()
    vendor_id = serializers.SerializerMethodField()
    vendor_name = serializers.SerializerMethodField()
    avg_rate = serializers.FloatField()
    min_rate = serializers.FloatField()
    max_rate = serializers.FloatField()
    latest_rate = serializers.FloatField()
    best_rate = serializers.FloatField()
    total_qty = serializers.FloatField()
    total_amount = serializers.FloatField()
    overspend = serializers.FloatField()
    purchase_count = serializers.IntegerField()
    trend = serializers.CharField()
    trend_pct = serializers.FloatField()

    def get_product_id(self, obj):
        return str(obj['product'].product_id)

    def get_product_name(self, obj):
        return obj['product'].name

    def get_product_code(self, obj):
        return obj['product'].code

    def get_vendor_id(self, obj):
        return str(obj['vendor'].vendor_id)

    def get_vendor_name(self, obj):
        return obj['vendor'].name


class RawMaterialForecastSerializer(serializers.Serializer):
    product_id = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_code = serializers.SerializerMethodField()
    product_group = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    current_balance = serializers.FloatField()
    total_consumed = serializers.FloatField()
    avg_monthly_consumption = serializers.FloatField()
    avg_daily_consumption = serializers.FloatField()
    days_remaining = serializers.IntegerField()
    status = serializers.CharField()
    used_in_products = serializers.ListField()
    estimated_stockout_date = serializers.CharField(allow_null=True)

    def get_product_id(self, obj):
        return str(obj['product'].product_id)

    def get_product_name(self, obj):
        return obj['product'].name

    def get_product_code(self, obj):
        return obj['product'].code

    def get_product_group(self, obj):
        pg = obj['product'].product_group_id
        if pg:
            return {'id': str(pg.product_group_id), 'name': pg.group_name}
        return None

    def get_category(self, obj):
        cat = obj['product'].category_id
        if cat:
            return {'id': str(cat.category_id), 'name': cat.category_name}
        return None

    def get_unit(self, obj):
        unit = obj['product'].unit_options_id
        if unit:
            return {'id': str(unit.unit_options_id), 'name': unit.unit_name}
        return None

class ProfitMarginSerializer(serializers.Serializer):
    product_id = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_code = serializers.SerializerMethodField()
    product_group = serializers.SerializerMethodField()
    revenue = serializers.FloatField()
    cost = serializers.FloatField()
    profit = serializers.FloatField()
    margin_pct = serializers.FloatField()
    status = serializers.CharField()
    sold_qty = serializers.FloatField()
    cost_per_unit = serializers.FloatField()
    sell_per_unit = serializers.FloatField()
    cost_source = serializers.CharField()

    def get_product_id(self, obj):
        return str(obj['product'].product_id)

    def get_product_name(self, obj):
        return obj['product'].name

    def get_product_code(self, obj):
        return obj['product'].code

    def get_product_group(self, obj):
        pg = obj['product'].product_group_id
        if pg:
            return {'id': str(pg.product_group_id), 'name': pg.group_name}
        return None


class MoneyBleedingCategorySerializer(serializers.Serializer):
    category = serializers.CharField()
    label = serializers.CharField()
    module = serializers.CharField()
    amount = serializers.FloatField()
    percentage = serializers.FloatField()
    item_count = serializers.IntegerField()
    severity = serializers.CharField()
    top_items = serializers.ListField()


class SeasonalityProductSerializer(serializers.Serializer):
    product_id = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_code = serializers.SerializerMethodField()
    product_group = serializers.SerializerMethodField()
    total_avg_qty = serializers.FloatField()
    monthly = serializers.ListField()
    peak_months = serializers.ListField(child=serializers.CharField())
    low_months = serializers.ListField(child=serializers.CharField())
    data_years = serializers.IntegerField()

    def get_product_id(self, obj):
        return str(obj['product'].product_id)

    def get_product_name(self, obj):
        return obj['product'].name

    def get_product_code(self, obj):
        return obj['product'].code

    def get_product_group(self, obj):
        pg = obj['product'].product_group_id
        if pg:
            return {'id': str(pg.product_group_id), 'name': pg.group_name}
        return None


class WhatIfMaterialSerializer(serializers.Serializer):
    product_id = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    product_code = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    current_stock = serializers.FloatField()
    total_needed = serializers.FloatField()
    shortfall = serializers.FloatField()
    unit_cost = serializers.FloatField()
    additional_cost = serializers.FloatField()
    stock_coverage_pct = serializers.FloatField()
    status = serializers.CharField()
    demanded_by = serializers.ListField()

    def get_product_id(self, obj):
        return str(obj['product'].product_id)

    def get_product_name(self, obj):
        return obj['product'].name

    def get_product_code(self, obj):
        return obj['product'].code

    def get_unit(self, obj):
        unit = obj['product'].unit_options_id
        if unit:
            return {'id': str(unit.unit_options_id), 'name': unit.unit_name}
        return None