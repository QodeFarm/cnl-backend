from apps.reports.base.filters import BaseReportFilter


# ─────────────────────────────────────────────────────────────
# Step 3 — Pending Registers, Trading Registers, Credit/Debit
# ─────────────────────────────────────────────────────────────

class SaleOrderFilter(BaseReportFilter):
    """Sale Order Register + Pending Sale Orders."""
    date_field = "order_date"
    customer_id_field = "customer_id"
    customer_name_field = "customer_id__name"
    default_sort_field = "order_date"
    default_sort_order = "desc"
    allowed_sort_fields = [
        "order_date", "order_no", "customer_id__name",
        "delivery_date", "total_amount",
    ]

    def apply_secondary_filters(self, queryset):
        params = self.params

        order_status = params.get("order_status", "").strip()
        if order_status:
            queryset = queryset.filter(order_status_id__status_name__iexact=order_status)
            self._applied["order_status"] = order_status

        flow_status = params.get("flow_status", "").strip()
        if flow_status:
            queryset = queryset.filter(
                flow_status_id__flow_status_name__icontains=flow_status
            )
            self._applied["flow_status"] = flow_status

        sale_type = params.get("sale_type", "").strip()
        if sale_type:
            queryset = queryset.filter(sale_type_id__name__icontains=sale_type)
            self._applied["sale_type"] = sale_type

        delivery_from = self._parse_date(params.get("delivery_from"))
        if delivery_from:
            queryset = queryset.filter(delivery_date__gte=delivery_from)
            self._applied["delivery_from"] = str(delivery_from)

        delivery_to = self._parse_date(params.get("delivery_to"))
        if delivery_to:
            queryset = queryset.filter(delivery_date__lte=delivery_to)
            self._applied["delivery_to"] = str(delivery_to)

        min_amount = params.get("min_amount")
        if min_amount:
            try:
                queryset = queryset.filter(total_amount__gte=min_amount)
                self._applied["min_amount"] = min_amount
            except Exception:
                pass

        max_amount = params.get("max_amount")
        if max_amount:
            try:
                queryset = queryset.filter(total_amount__lte=max_amount)
                self._applied["max_amount"] = max_amount
            except Exception:
                pass

        search_q = self.get_search_query(["order_no", "customer_id__name"])
        if search_q:
            queryset = queryset.filter(search_q)

        return queryset


class DeliveryChallanFilter(BaseReportFilter):
    """Sale Challan Register + Pending Sale Challans."""
    date_field = "challan_date"
    customer_id_field = "customer_id"
    customer_name_field = "customer_id__name"
    default_sort_field = "challan_date"
    default_sort_order = "desc"
    allowed_sort_fields = [
        "challan_date", "challan_no", "customer_id__name", "total_amount",
    ]

    def apply_secondary_filters(self, queryset):
        params = self.params

        is_converted = params.get("is_converted", "").strip().lower()
        if is_converted in ("true", "1", "yes"):
            queryset = queryset.filter(is_converted=True)
            self._applied["is_converted"] = True
        elif is_converted in ("false", "0", "no"):
            queryset = queryset.filter(is_converted=False)
            self._applied["is_converted"] = False

        search_q = self.get_search_query(["challan_no", "customer_id__name"])
        if search_q:
            queryset = queryset.filter(search_q)

        return queryset


class SaleReturnFilter(BaseReportFilter):
    """Sale Return Register."""
    date_field = "return_date"
    customer_id_field = "customer_id"
    customer_name_field = "customer_id__name"
    default_sort_field = "return_date"
    default_sort_order = "desc"
    allowed_sort_fields = [
        "return_date", "return_no", "customer_id__name", "total_amount",
    ]

    def apply_secondary_filters(self, queryset):
        params = self.params

        bill_type = params.get("bill_type", "").strip().upper()
        if bill_type in ("CASH", "CREDIT", "OTHERS"):
            queryset = queryset.filter(bill_type=bill_type)
            self._applied["bill_type"] = bill_type

        min_amount = params.get("min_amount")
        if min_amount:
            try:
                queryset = queryset.filter(total_amount__gte=min_amount)
                self._applied["min_amount"] = min_amount
            except Exception:
                pass

        search_q = self.get_search_query([
            "return_no", "customer_id__name", "return_reason",
        ])
        if search_q:
            queryset = queryset.filter(search_q)

        return queryset


class CreditDebitNoteFilter(BaseReportFilter):
    """Credit / Debit Note Register — applied to each model separately."""
    date_field = "created_at"
    customer_id_field = "customer_id"
    customer_name_field = "customer_id__name"
    default_sort_field = "created_at"
    default_sort_order = "desc"
    allowed_sort_fields = ["created_at", "customer_id__name", "total_amount"]

    def apply_secondary_filters(self, queryset):
        search_q = self.get_search_query(["customer_id__name"])
        if search_q:
            queryset = queryset.filter(search_q)
        return queryset


# ─────────────────────────────────────────────────────────────
# Step 4 — Payment Reminder + Customer Aging
# ─────────────────────────────────────────────────────────────

class PaymentReminderFilter(BaseReportFilter):
    """
    Payment Reminder — invoices with pending_amount > 0.
    date_field targets invoice_date; due date range via due_from/due_to.
    """
    date_field = "invoice_date"
    customer_id_field = "customer_id"
    customer_name_field = "customer_id__name"
    default_sort_field = "due_date"
    default_sort_order = "asc"
    allowed_sort_fields = [
        "due_date", "invoice_date", "customer_id__name",
        "pending_amount", "total_amount",
    ]

    def apply_secondary_filters(self, queryset):
        params = self.params

        due_from = self._parse_date(params.get("due_from"))
        if due_from:
            queryset = queryset.filter(due_date__gte=due_from)
            self._applied["due_from"] = str(due_from)

        due_to = self._parse_date(params.get("due_to"))
        if due_to:
            queryset = queryset.filter(due_date__lte=due_to)
            self._applied["due_to"] = str(due_to)

        min_pending = params.get("min_pending")
        if min_pending:
            try:
                queryset = queryset.filter(pending_amount__gte=min_pending)
                self._applied["min_pending"] = min_pending
            except Exception:
                pass

        city = params.get("city", "").strip()
        if city:
            queryset = queryset.filter(
                customer_address_id__city_id__city_name__icontains=city
            )
            self._applied["city"] = city

        search_q = self.get_search_query(["invoice_no", "customer_id__name"])
        if search_q:
            queryset = queryset.filter(search_q)

        return queryset


# ─────────────────────────────────────────────────────────────
# Step 5 — MIS Reports + Sales Order Analysis
# ─────────────────────────────────────────────────────────────

class NewCustomersFilter(BaseReportFilter):
    """New Customers — customers whose first invoice is in the date range."""
    date_field = "invoice_date"
    customer_id_field = "customer_id"
    customer_name_field = "customer_id__name"
    default_sort_field = "invoice_date"
    default_sort_order = "asc"

    def apply_secondary_filters(self, queryset):
        params = self.params
        city = params.get("city", "").strip()
        if city:
            queryset = queryset.filter(
                customer_address_id__city_id__city_name__icontains=city
            )
            self._applied["city"] = city
        search_q = self.get_search_query(["customer_id__name", "customer_id__code"])
        if search_q:
            queryset = queryset.filter(search_q)
        return queryset


class SalesOrderAnalysisFilter(BaseReportFilter):
    """Sales Order Analysis — SaleOrder grouped by customer."""
    date_field = "order_date"
    customer_id_field = "customer_id"
    customer_name_field = "customer_id__name"
    default_sort_field = "order_date"
    default_sort_order = "desc"

    def apply_secondary_filters(self, queryset):
        params = self.params
        sale_type = params.get("sale_type", "").strip()
        if sale_type:
            queryset = queryset.filter(sale_type_id__name__icontains=sale_type)
            self._applied["sale_type"] = sale_type
        order_status = params.get("order_status", "").strip()
        if order_status:
            queryset = queryset.filter(order_status_id__status_name__iexact=order_status)
            self._applied["order_status"] = order_status
        flow_status = params.get("flow_status", "").strip()
        if flow_status:
            queryset = queryset.filter(flow_status_id__flow_status_name__icontains=flow_status)
            self._applied["flow_status"] = flow_status
        search_q = self.get_search_query(["customer_id__name", "order_no"])
        if search_q:
            queryset = queryset.filter(search_q)
        return queryset


class CustomerAgingFilter(BaseReportFilter):
    """
    Customer Aging — same base queryset as Payment Reminder.
    as_of_date is handled separately in the view (Python-level bucket calc).
    """
    date_field = "invoice_date"
    customer_id_field = "customer_id"
    customer_name_field = "customer_id__name"
    default_sort_field = "customer_id__name"
    default_sort_order = "asc"
    allowed_sort_fields = ["customer_id__name", "pending_amount"]

    def apply_secondary_filters(self, queryset):
        params = self.params

        city = params.get("city", "").strip()
        if city:
            queryset = queryset.filter(
                customer_address_id__city_id__city_name__icontains=city
            )
            self._applied["city"] = city

        min_pending = params.get("min_pending")
        if min_pending:
            try:
                queryset = queryset.filter(pending_amount__gte=min_pending)
                self._applied["min_pending"] = min_pending
            except Exception:
                pass

        search_q = self.get_search_query(["customer_id__name"])
        if search_q:
            queryset = queryset.filter(search_q)

        return queryset


class SalesRegisterFilter(BaseReportFilter):
    """
    Invoice-level filter — used for register types:
    general, cancelled, daily_summary, daily_payment_summary,
    monthly_summary, monthly_payment_summary
    """
    date_field = "invoice_date"
    customer_id_field = "customer_id"
    customer_name_field = "customer_id__name"
    salesperson_field = "order_salesman_id"
    default_sort_field = "invoice_date"
    default_sort_order = "desc"
    allowed_sort_fields = [
        "invoice_date", "invoice_no", "customer_id__name",
        "total_amount", "pending_amount", "paid_amount",
    ]

    def apply_secondary_filters(self, queryset):
        params = self.params

        bill_type = params.get("bill_type", "").strip().upper()
        if bill_type in ("CASH", "CREDIT", "OTHERS"):
            queryset = queryset.filter(bill_type=bill_type)
            self._applied["bill_type"] = bill_type

        status_name = params.get("status", "").strip()
        if status_name:
            queryset = queryset.filter(order_status_id__status_name__iexact=status_name)
            self._applied["status"] = status_name

        city = params.get("city", "").strip()
        if city:
            queryset = queryset.filter(
                customer_address_id__city_id__city_name__icontains=city
            )
            self._applied["city"] = city

        min_amount = params.get("min_amount")
        if min_amount:
            try:
                queryset = queryset.filter(total_amount__gte=min_amount)
                self._applied["min_amount"] = min_amount
            except Exception:
                pass

        max_amount = params.get("max_amount")
        if max_amount:
            try:
                queryset = queryset.filter(total_amount__lte=max_amount)
                self._applied["max_amount"] = max_amount
            except Exception:
                pass

        search_q = self.get_search_query(["invoice_no", "customer_id__name", "ref_no"])
        if search_q:
            queryset = queryset.filter(search_q)

        return queryset


class SalesRegisterItemFilter(BaseReportFilter):
    """
    Item-level filter — used for register types:
    detailed, columnar_tax_wise, columnar_product_group,
    columnar_product_category, columnar_product_brand,
    columnar_hsn_wise, daily_tax_analysis
    """
    date_field = "sale_invoice_id__invoice_date"
    customer_id_field = "sale_invoice_id__customer_id"
    customer_name_field = "sale_invoice_id__customer_id__name"
    salesperson_field = "sale_invoice_id__order_salesman_id"
    product_id_field = "product_id"
    product_name_field = "product_id__name"
    default_sort_field = "sale_invoice_id__invoice_date"
    default_sort_order = "desc"
    allowed_sort_fields = [
        "sale_invoice_id__invoice_date",
        "sale_invoice_id__invoice_no",
        "product_id__name",
        "quantity",
        "amount",
    ]

    def apply_secondary_filters(self, queryset):
        params = self.params

        bill_type = params.get("bill_type", "").strip().upper()
        if bill_type in ("CASH", "CREDIT", "OTHERS"):
            queryset = queryset.filter(sale_invoice_id__bill_type=bill_type)
            self._applied["bill_type"] = bill_type

        city = params.get("city", "").strip()
        if city:
            queryset = queryset.filter(
                sale_invoice_id__customer_address_id__city_id__city_name__icontains=city
            )
            self._applied["city"] = city

        product_group_id = params.get("product_group_id", "").strip()
        if product_group_id:
            queryset = queryset.filter(product_id__product_group_id=product_group_id)
            self._applied["product_group_id"] = product_group_id

        product_category_id = params.get("product_category_id", "").strip()
        if product_category_id:
            queryset = queryset.filter(product_id__category_id=product_category_id)
            self._applied["product_category_id"] = product_category_id

        product_brand_id = params.get("product_brand_id", "").strip()
        if product_brand_id:
            queryset = queryset.filter(product_id__brand_id=product_brand_id)
            self._applied["product_brand_id"] = product_brand_id

        hsn_code = params.get("hsn_code", "").strip()
        if hsn_code:
            queryset = queryset.filter(product_id__hsn_code__icontains=hsn_code)
            self._applied["hsn_code"] = hsn_code

        search_q = self.get_search_query([
            "sale_invoice_id__invoice_no",
            "sale_invoice_id__customer_id__name",
            "product_id__name",
            "product_id__code",
        ])
        if search_q:
            queryset = queryset.filter(search_q)

        return queryset
