"""
Purchase report filters — mirror the sales register filters but adapted to the
real Purchase models:
  • entity is the VENDOR (not customer)
  • there is no bill_type; purchases use `voucher` (GST_Purchase / Purchase)
    and `tax_code` (Local / Exempted)
  • the agent is `vendor_agent_id` (not salesperson)
  • city is reached via vendor_address_id -> city_id -> city_name
"""

from apps.reports.base.filters import BaseReportFilter


class PurchaseRegisterFilter(BaseReportFilter):
    """
    Invoice-level filter — used for register types:
    general, cancelled, daily_summary, daily_payment_summary,
    monthly_summary, monthly_payment_summary
    """
    date_field = "invoice_date"
    vendor_id_field = "vendor_id"
    vendor_name_field = "vendor_id__name"
    default_sort_field = "invoice_date"
    default_sort_order = "desc"
    allowed_sort_fields = [
        "invoice_date", "invoice_no", "vendor_id__name",
        "total_amount", "pending_amount", "paid_amount",
    ]

    def apply_secondary_filters(self, queryset):
        params = self.params

        voucher = params.get("voucher", "").strip()
        if voucher:
            queryset = queryset.filter(voucher__iexact=voucher)
            self._applied["voucher"] = voucher

        tax_code = params.get("tax_code", "").strip()
        if tax_code:
            queryset = queryset.filter(tax_code__iexact=tax_code)
            self._applied["tax_code"] = tax_code

        status_name = params.get("status", "").strip()
        if status_name:
            queryset = queryset.filter(order_status_id__status_name__iexact=status_name)
            self._applied["status"] = status_name

        agent_id = params.get("agent_id", "").strip()
        if agent_id:
            queryset = queryset.filter(vendor_agent_id=agent_id)
            self._applied["agent_id"] = agent_id

        city = params.get("city", "").strip()
        if city:
            queryset = queryset.filter(
                vendor_address_id__city_id__city_name__icontains=city
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

        search_q = self.get_search_query(
            ["invoice_no", "supplier_invoice_no", "vendor_id__name"]
        )
        if search_q:
            queryset = queryset.filter(search_q)

        return queryset


class PurchaseOrderFilter(BaseReportFilter):
    """Purchase Order Register + Pending Purchase Orders."""
    date_field = "order_date"
    vendor_id_field = "vendor_id"
    vendor_name_field = "vendor_id__name"
    default_sort_field = "order_date"
    default_sort_order = "desc"
    allowed_sort_fields = [
        "order_date", "order_no", "vendor_id__name", "delivery_date", "total_amount",
    ]

    def apply_secondary_filters(self, queryset):
        params = self.params

        status_name = params.get("status", "").strip() or params.get("order_status", "").strip()
        if status_name:
            queryset = queryset.filter(order_status_id__status_name__iexact=status_name)
            self._applied["status"] = status_name

        purchase_type = params.get("purchase_type", "").strip()
        if purchase_type:
            queryset = queryset.filter(purchase_type_id__name__icontains=purchase_type)
            self._applied["purchase_type"] = purchase_type

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

        search_q = self.get_search_query(["order_no", "vendor_id__name"])
        if search_q:
            queryset = queryset.filter(search_q)

        return queryset


class PurchaseReturnFilter(BaseReportFilter):
    """Purchase Return Register."""
    date_field = "return_date"
    vendor_id_field = "vendor_id"
    vendor_name_field = "vendor_id__name"
    default_sort_field = "return_date"
    default_sort_order = "desc"
    allowed_sort_fields = [
        "return_date", "return_no", "vendor_id__name", "total_amount",
    ]

    def apply_secondary_filters(self, queryset):
        params = self.params

        status_name = params.get("status", "").strip()
        if status_name:
            queryset = queryset.filter(order_status_id__status_name__iexact=status_name)
            self._applied["status"] = status_name

        min_amount = params.get("min_amount")
        if min_amount:
            try:
                queryset = queryset.filter(total_amount__gte=min_amount)
                self._applied["min_amount"] = min_amount
            except Exception:
                pass

        search_q = self.get_search_query(
            ["return_no", "vendor_id__name", "return_reason", "ref_no"]
        )
        if search_q:
            queryset = queryset.filter(search_q)

        return queryset


class BillPaymentFilter(BaseReportFilter):
    """Bill Payment Register — payments made to vendors."""
    date_field = "payment_date"
    vendor_id_field = "vendor"
    vendor_name_field = "vendor__name"
    default_sort_field = "payment_date"
    default_sort_order = "desc"
    allowed_sort_fields = ["payment_date", "amount", "vendor__name"]

    def apply_secondary_filters(self, queryset):
        params = self.params

        payment_status = params.get("payment_status", "").strip()
        if payment_status:
            queryset = queryset.filter(payment_status__iexact=payment_status)
            self._applied["payment_status"] = payment_status

        payment_method = params.get("payment_method", "").strip()
        if payment_method:
            queryset = queryset.filter(payment_method__icontains=payment_method)
            self._applied["payment_method"] = payment_method

        search_q = self.get_search_query(["payment_receipt_no", "vendor__name", "bill_no"])
        if search_q:
            queryset = queryset.filter(search_q)

        return queryset


class VendorOutstandingFilter(BaseReportFilter):
    """Vendor Outstanding / Aging — purchase invoices with pending_amount > 0."""
    date_field = "invoice_date"
    vendor_id_field = "vendor_id"
    vendor_name_field = "vendor_id__name"
    default_sort_field = "due_date"
    default_sort_order = "asc"
    allowed_sort_fields = [
        "due_date", "invoice_date", "vendor_id__name", "pending_amount", "total_amount",
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

        search_q = self.get_search_query(
            ["invoice_no", "supplier_invoice_no", "vendor_id__name"]
        )
        if search_q:
            queryset = queryset.filter(search_q)

        return queryset


class PurchaseRegisterItemFilter(BaseReportFilter):
    """
    Item-level filter — used for register types:
    detailed, columnar_tax_wise, columnar_product_group,
    columnar_product_category, columnar_product_brand,
    columnar_hsn_wise, daily_tax_analysis
    """
    date_field = "purchase_invoice_id__invoice_date"
    vendor_id_field = "purchase_invoice_id__vendor_id"
    vendor_name_field = "purchase_invoice_id__vendor_id__name"
    product_id_field = "product_id"
    product_name_field = "product_id__name"
    default_sort_field = "purchase_invoice_id__invoice_date"
    default_sort_order = "desc"
    allowed_sort_fields = [
        "purchase_invoice_id__invoice_date",
        "purchase_invoice_id__invoice_no",
        "product_id__name",
        "quantity",
        "amount",
    ]

    def apply_secondary_filters(self, queryset):
        params = self.params

        voucher = params.get("voucher", "").strip()
        if voucher:
            queryset = queryset.filter(purchase_invoice_id__voucher__iexact=voucher)
            self._applied["voucher"] = voucher

        city = params.get("city", "").strip()
        if city:
            queryset = queryset.filter(
                purchase_invoice_id__vendor_address_id__city_id__city_name__icontains=city
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
            "purchase_invoice_id__invoice_no",
            "purchase_invoice_id__vendor_id__name",
            "product_id__name",
            "product_id__code",
        ])
        if search_q:
            queryset = queryset.filter(search_q)

        return queryset
