"""
GST reports — built from REAL tax data on invoice items (cgst/sgst/igst).

GSTR-3B = the period tax-liability summary: Output Tax (from sales invoice items)
minus Input Tax Credit (from purchase invoice items) = Net GST payable, split by
tax type (CGST / SGST / IGST). No fabrication — if there is no tax, it shows ₹0.00.
"""
from decimal import Decimal

from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import Coalesce

from rest_framework.response import Response

from apps.reports.base.views import BaseReportView
from apps.reports.base.pagination import get_page_and_limit, paginate_list
from apps.reports.base.response import build_report_response
from apps.sales.models import SaleInvoiceItems
from apps.purchase.models import PurchaseInvoiceItem

ZERO = Value(Decimal("0.00"), output_field=DecimalField(max_digits=18, decimal_places=2))


class Gstr3bView(BaseReportView):
    """GSTR-3B — net GST payable for the period (output tax − input credit)."""
    report_type = "gstr3b"
    report_label = "GSTR-3B (Tax Liability)"
    module = "gst"
    cache_ttl = 900

    @staticmethod
    def _flat_params(request):
        params = dict(request.query_params)
        return {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in params.items()}

    def get(self, request, *args, **kwargs):
        from apps.reports.base.cache import get_cached, set_cached

        flat = self._flat_params(request)
        page, limit = get_page_and_limit(request)
        db_alias = self._get_db_alias(request) or "default"
        cache_params = {**flat, "_page": page, "_limit": limit}

        cached = get_cached(self.module, self.report_type, db_alias, cache_params)
        if cached is not None:
            return Response(cached)

        from_date = flat.get("from_date") or None
        to_date = flat.get("to_date") or None
        filters_applied = {}

        # Output tax = sales invoice items
        sq = SaleInvoiceItems.objects.using(db_alias).filter(sale_invoice_id__is_deleted=False)
        if from_date:
            sq = sq.filter(sale_invoice_id__invoice_date__gte=from_date); filters_applied["from_date"] = from_date
        if to_date:
            sq = sq.filter(sale_invoice_id__invoice_date__lte=to_date); filters_applied["to_date"] = to_date
        out = sq.aggregate(
            cgst=Coalesce(Sum("cgst"), ZERO), sgst=Coalesce(Sum("sgst"), ZERO),
            igst=Coalesce(Sum("igst"), ZERO), taxable=Coalesce(Sum("amount"), ZERO),
        )

        # Input tax credit = purchase invoice items
        pq = PurchaseInvoiceItem.objects.using(db_alias).filter(purchase_invoice_id__is_deleted=False)
        if from_date:
            pq = pq.filter(purchase_invoice_id__invoice_date__gte=from_date)
        if to_date:
            pq = pq.filter(purchase_invoice_id__invoice_date__lte=to_date)
        inp = pq.aggregate(
            cgst=Coalesce(Sum("cgst"), ZERO), sgst=Coalesce(Sum("sgst"), ZERO),
            igst=Coalesce(Sum("igst"), ZERO), taxable=Coalesce(Sum("amount"), ZERO),
        )

        rows = []
        for label, key in (("CGST", "cgst"), ("SGST", "sgst"), ("IGST", "igst")):
            o = out[key] or Decimal("0.00")
            i = inp[key] or Decimal("0.00")
            rows.append({
                "tax_type": label,
                "output_tax": o,
                "input_credit": i,
                "net_payable": o - i,
            })

        total_output = sum(r["output_tax"] for r in rows)
        total_input = sum(r["input_credit"] for r in rows)
        summary = {
            "taxable_sales": str(out["taxable"]),
            "taxable_purchases": str(inp["taxable"]),
            "total_output_tax": str(total_output),
            "total_input_credit": str(total_input),
            "net_gst_payable": str(total_output - total_input),
        }

        data, total = paginate_list(rows, page, limit)
        resp = build_report_response(
            report_type=self.report_type, report_label=self.report_label,
            data=data, summary=summary, filters_applied=filters_applied,
            page=page, limit=limit, total=total,
        )
        if self.cache_ttl > 0:
            set_cached(self.module, self.report_type, db_alias, cache_params, resp.data, self.cache_ttl)
        return resp
