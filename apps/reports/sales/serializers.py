from rest_framework import serializers


class SaleRegisterGeneralSerializer(serializers.Serializer):
    """One row per invoice — general register."""
    sale_invoice_id = serializers.UUIDField()
    invoice_no = serializers.CharField()
    invoice_date = serializers.DateField()
    bill_type = serializers.CharField()
    customer_name = serializers.CharField()
    city = serializers.CharField(allow_null=True)
    salesperson = serializers.CharField(allow_null=True)
    item_value = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    dis_amt = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    tax_amount = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    round_off = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    total_amount = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    paid_amount = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    pending_amount = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    due_date = serializers.DateField(allow_null=True)
    status = serializers.CharField(allow_null=True)


class SaleRegisterDetailedSerializer(serializers.Serializer):
    """One row per product per invoice — detailed register."""
    invoice_no = serializers.CharField()
    invoice_date = serializers.DateField()
    bill_type = serializers.CharField()
    customer_name = serializers.CharField()
    product_name = serializers.CharField()
    product_code = serializers.CharField(allow_null=True)
    hsn_code = serializers.CharField(allow_null=True)
    unit = serializers.CharField(allow_null=True)
    quantity = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    rate = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    amount = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    discount = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    cgst = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    sgst = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    igst = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)


class SaleRegisterColumnarTaxSerializer(serializers.Serializer):
    """Tax breakdown per invoice — columnar_tax_wise."""
    invoice_no = serializers.CharField()
    invoice_date = serializers.DateField()
    customer_name = serializers.CharField()
    taxable_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    cgst = serializers.DecimalField(max_digits=18, decimal_places=2)
    sgst = serializers.DecimalField(max_digits=18, decimal_places=2)
    igst = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_tax = serializers.DecimalField(max_digits=18, decimal_places=2)
    net_amount = serializers.DecimalField(max_digits=18, decimal_places=2)


class SaleRegisterGroupedSerializer(serializers.Serializer):
    """Generic grouped row — product_group, category, brand, hsn columnar types."""
    group_name = serializers.CharField()
    total_qty = serializers.DecimalField(max_digits=18, decimal_places=2)
    gross_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_discount = serializers.DecimalField(max_digits=18, decimal_places=2)
    cgst = serializers.DecimalField(max_digits=18, decimal_places=2)
    sgst = serializers.DecimalField(max_digits=18, decimal_places=2)
    igst = serializers.DecimalField(max_digits=18, decimal_places=2)
    net_amount = serializers.DecimalField(max_digits=18, decimal_places=2)


class SaleRegisterDailySummarySerializer(serializers.Serializer):
    """Day-wise invoice totals — daily_summary."""
    date = serializers.DateField()
    invoice_count = serializers.IntegerField()
    gross_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_discount = serializers.DecimalField(max_digits=18, decimal_places=2)
    tax_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    net_amount = serializers.DecimalField(max_digits=18, decimal_places=2)


class SaleRegisterDailyPaymentSerializer(serializers.Serializer):
    """Day-wise paid vs pending — daily_payment_summary."""
    date = serializers.DateField()
    invoice_count = serializers.IntegerField()
    total_billed = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_collected = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_pending = serializers.DecimalField(max_digits=18, decimal_places=2)


class SaleRegisterDailyTaxSerializer(serializers.Serializer):
    """Day-wise tax analysis — daily_tax_analysis."""
    date = serializers.DateField()
    taxable_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    cgst = serializers.DecimalField(max_digits=18, decimal_places=2)
    sgst = serializers.DecimalField(max_digits=18, decimal_places=2)
    igst = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_tax = serializers.DecimalField(max_digits=18, decimal_places=2)


class SaleRegisterMonthlySummarySerializer(serializers.Serializer):
    """Month-wise invoice totals — monthly_summary."""
    month = serializers.CharField()  # YYYY-MM format
    invoice_count = serializers.IntegerField()
    gross_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_discount = serializers.DecimalField(max_digits=18, decimal_places=2)
    tax_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    net_amount = serializers.DecimalField(max_digits=18, decimal_places=2)


class SaleRegisterMonthlyPaymentSerializer(serializers.Serializer):
    """Month-wise paid vs pending — monthly_payment_summary."""
    month = serializers.CharField()  # YYYY-MM format
    invoice_count = serializers.IntegerField()
    total_billed = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_collected = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_pending = serializers.DecimalField(max_digits=18, decimal_places=2)


# ─────────────────────────────────────────────────────────────
# Step 3 — Pending Registers, Trading Registers, Credit/Debit
# ─────────────────────────────────────────────────────────────

class SaleOrderRegisterSerializer(serializers.Serializer):
    """One row per sale order."""
    sale_order_id = serializers.UUIDField()
    order_no = serializers.CharField()
    order_date = serializers.DateField()
    delivery_date = serializers.DateField(allow_null=True)
    customer_name = serializers.CharField()
    sale_type = serializers.CharField(allow_null=True)
    flow_status = serializers.CharField(allow_null=True)
    order_status = serializers.CharField(allow_null=True)
    item_value = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    tax_amount = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    total_amount = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)


class DeliveryChallanRegisterSerializer(serializers.Serializer):
    """One row per delivery challan."""
    delivery_challan_id = serializers.UUIDField()
    challan_no = serializers.CharField()
    challan_date = serializers.DateField()
    customer_name = serializers.CharField()
    linked_order_no = serializers.CharField(allow_null=True)
    salesperson = serializers.CharField(allow_null=True)
    item_value = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    tax_amount = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    total_amount = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    is_converted = serializers.BooleanField()
    order_status = serializers.CharField(allow_null=True)


class SaleReturnRegisterSerializer(serializers.Serializer):
    """One row per sale return."""
    sale_return_id = serializers.UUIDField()
    return_no = serializers.CharField()
    return_date = serializers.DateField()
    bill_type = serializers.CharField()
    customer_name = serializers.CharField()
    against_invoice_no = serializers.CharField(allow_null=True)
    return_reason = serializers.CharField(allow_null=True)
    item_value = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    tax_amount = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    total_amount = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    order_status = serializers.CharField(allow_null=True)


class CreditDebitNoteRegisterSerializer(serializers.Serializer):
    """One row per credit or debit note (combined)."""
    note_id = serializers.UUIDField()
    note_number = serializers.CharField()
    note_type = serializers.CharField()   # 'Credit' or 'Debit'
    note_date = serializers.DateField()
    customer_name = serializers.CharField()
    against_invoice_no = serializers.CharField(allow_null=True)
    reason = serializers.CharField(allow_null=True)
    total_amount = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    order_status = serializers.CharField(allow_null=True)


# ─────────────────────────────────────────────────────────────
# Step 4 — Payment Reminder + Customer Aging
# ─────────────────────────────────────────────────────────────

class PaymentReminderDetailSerializer(serializers.Serializer):
    """One row per overdue invoice — payment reminder detail view."""
    sale_invoice_id = serializers.UUIDField()
    invoice_no = serializers.CharField()
    invoice_date = serializers.DateField()
    due_date = serializers.DateField(allow_null=True)
    customer_name = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    paid_amount = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    pending_amount = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    days_overdue = serializers.IntegerField(allow_null=True)
    status = serializers.CharField(allow_null=True)


class PaymentReminderSummarySerializer(serializers.Serializer):
    """One row per customer — payment reminder summary view."""
    customer_id = serializers.UUIDField()
    customer_name = serializers.CharField()
    total_invoices = serializers.IntegerField()
    total_billed = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_pending = serializers.DecimalField(max_digits=18, decimal_places=2)
    oldest_due_date = serializers.DateField(allow_null=True)


class CustomerAgingSerializer(serializers.Serializer):
    """One row per customer — aging buckets."""
    customer_id = serializers.UUIDField()
    customer_name = serializers.CharField()
    total_outstanding = serializers.DecimalField(max_digits=18, decimal_places=2)
    current = serializers.DecimalField(max_digits=18, decimal_places=2)   # not yet due
    days_1_30 = serializers.DecimalField(max_digits=18, decimal_places=2)
    days_31_60 = serializers.DecimalField(max_digits=18, decimal_places=2)
    days_61_90 = serializers.DecimalField(max_digits=18, decimal_places=2)
    days_91_120 = serializers.DecimalField(max_digits=18, decimal_places=2)
    days_120_plus = serializers.DecimalField(max_digits=18, decimal_places=2)


# ─────────────────────────────────────────────────────────────
# Step 5 — MIS Reports + Sales Order Analysis
# ─────────────────────────────────────────────────────────────

class NewCustomerSerializer(serializers.Serializer):
    """One row per new customer — MIS New Customers."""
    customer_id = serializers.UUIDField()
    customer_name = serializers.CharField()
    customer_code = serializers.CharField(allow_null=True)
    first_invoice_date = serializers.DateField()
    total_invoices = serializers.IntegerField()
    total_sales_value = serializers.DecimalField(max_digits=18, decimal_places=2)


class NoSalesCustomerSerializer(serializers.Serializer):
    """One row per customer with no sales — MIS No Sales Customers."""
    customer_id = serializers.UUIDField()
    customer_name = serializers.CharField()
    customer_code = serializers.CharField(allow_null=True)
    last_invoice_date = serializers.DateField(allow_null=True)
    days_since_last_sale = serializers.IntegerField(allow_null=True)


class LimitExceededCustomerSerializer(serializers.Serializer):
    """One row per customer whose outstanding > credit_limit."""
    customer_id = serializers.UUIDField()
    customer_name = serializers.CharField()
    customer_code = serializers.CharField(allow_null=True)
    credit_limit = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    total_outstanding = serializers.DecimalField(max_digits=18, decimal_places=2)
    exceeded_by = serializers.DecimalField(max_digits=18, decimal_places=2)


class SalesOrderAnalysisSerializer(serializers.Serializer):
    """One row per customer — sales order analysis."""
    customer_id = serializers.UUIDField()
    customer_name = serializers.CharField()
    total_orders = serializers.IntegerField()
    completed_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=18, decimal_places=2)
    avg_order_value = serializers.DecimalField(max_digits=18, decimal_places=2)


# ─────────────────────────────────────────────────────────────
# Step 6 — Analysis Reports (beats MaxxERP)
# ─────────────────────────────────────────────────────────────

class ProductSalesAnalysisSerializer(serializers.Serializer):
    """One row per product — product-wise sales analysis."""
    product_id = serializers.UUIDField()
    product_name = serializers.CharField()
    product_code = serializers.CharField(allow_null=True)
    total_qty = serializers.DecimalField(max_digits=18, decimal_places=2)
    gross_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_discount = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_tax = serializers.DecimalField(max_digits=18, decimal_places=2)
    net_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    avg_rate = serializers.DecimalField(max_digits=18, decimal_places=2)


class CustomerSalesAnalysisSerializer(serializers.Serializer):
    """One row per customer — customer-wise sales analysis."""
    customer_id = serializers.UUIDField()
    customer_name = serializers.CharField()
    total_invoices = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_pending = serializers.DecimalField(max_digits=18, decimal_places=2)
    avg_invoice_value = serializers.DecimalField(max_digits=18, decimal_places=2)
    last_invoice_date = serializers.DateField(allow_null=True)


class SalespersonAnalysisSerializer(serializers.Serializer):
    """One row per salesperson — performance analysis."""
    salesperson_id = serializers.UUIDField()
    salesperson_name = serializers.CharField()
    total_invoices = serializers.IntegerField()
    total_sales = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_collected = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_pending = serializers.DecimalField(max_digits=18, decimal_places=2)
    collection_pct = serializers.DecimalField(max_digits=5, decimal_places=2)


class ProfitMarginSerializer(serializers.Serializer):
    """One row per product — profit margin analysis."""
    product_id = serializers.UUIDField()
    product_name = serializers.CharField()
    product_code = serializers.CharField(allow_null=True)
    total_qty = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_revenue = serializers.DecimalField(max_digits=18, decimal_places=2)
    # cost / profit / margin are null when the product has no known cost
    # (cost_source == 'unknown') — never faked to 0/100%. Shared with the insight.
    total_cost = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    gross_profit = serializers.DecimalField(max_digits=18, decimal_places=2, allow_null=True)
    margin_pct = serializers.DecimalField(max_digits=7, decimal_places=2, allow_null=True)
    cost_source = serializers.CharField(required=False)


class SalesTrendSerializer(serializers.Serializer):
    """One row per period — year-over-year comparison."""
    period = serializers.CharField()          # e.g. "2025-01" or "2025-Q1"
    current_year_sales = serializers.DecimalField(max_digits=18, decimal_places=2)
    previous_year_sales = serializers.DecimalField(max_digits=18, decimal_places=2)
    growth_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    growth_pct = serializers.DecimalField(max_digits=6, decimal_places=2)


class GstSummarySerializer(serializers.Serializer):
    """One row per invoice — GST summary."""
    invoice_no = serializers.CharField()
    invoice_date = serializers.DateField()
    customer_name = serializers.CharField()
    taxable_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    cgst = serializers.DecimalField(max_digits=18, decimal_places=2)
    sgst = serializers.DecimalField(max_digits=18, decimal_places=2)
    igst = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_tax = serializers.DecimalField(max_digits=18, decimal_places=2)
    net_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
