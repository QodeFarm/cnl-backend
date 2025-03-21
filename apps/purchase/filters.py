from django_filters import rest_framework as filters
from config.utils_methods import filter_uuid
from .models import PurchaseOrders, PurchaseInvoiceOrders, PurchaseReturnOrders
from django_filters import FilterSet, ChoiceFilter, DateFromToRangeFilter
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
logger = logging.getLogger(__name__)

class PurchaseOrdersFilter(filters.FilterSet):
    vendor_id = filters.CharFilter(method=filter_uuid)
    vendor = filters.CharFilter(field_name='vendor_id__name', lookup_expr='icontains')
    purchase_type_id = filters.CharFilter(field_name='purchase_type_id__name', lookup_expr='icontains')
    order_date = filters.DateFilter()
    order_no = filters.CharFilter(lookup_expr='icontains')
    tax = filters.ChoiceFilter(choices=PurchaseOrders.TAX_CHOICES)
    tax_amount = filters.RangeFilter()
    total_amount = filters.RangeFilter()
    remarks= filters.CharFilter(lookup_expr='icontains')
    order_status_id = filters.CharFilter(method=filter_uuid)
    status_name = filters.CharFilter(field_name='order_status_id__status_name', lookup_expr='iexact')
    created_at = DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
     
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = PurchaseOrders
        #do not change "order_no",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['order_no','order_date','vendor_id','vendor','purchase_type_id','tax', 'tax_amount','total_amount','remarks','order_status_id','status_name','created_at','period_name','s','sort','page','limit']

class PurchaseInvoiceOrdersFilter(filters.FilterSet):
    vendor_id = filters.CharFilter(method=filter_uuid)
    vendor = filters.CharFilter(field_name='vendor_id__name', lookup_expr='icontains')
    purchase_type_id = filters.CharFilter(method=filter_uuid)
    purchase_type = filters.CharFilter(field_name='purchase_type_id__name', lookup_expr='icontains')
    invoice_date = filters.DateFilter()
    invoice_no = filters.CharFilter(lookup_expr='icontains')
    supplier_invoice_no= filters.CharFilter(lookup_expr='icontains')
    tax = filters.ChoiceFilter(choices=PurchaseOrders.TAX_CHOICES)
    tax_amount = filters.RangeFilter()
    total_amount = filters.RangeFilter()
    advance_amount = filters.RangeFilter()
    remarks= filters.CharFilter(lookup_expr='icontains')
    order_status_id = filters.CharFilter(method=filter_uuid)
    status_name = filters.CharFilter(field_name='order_status_id__status_name', lookup_expr='iexact')
    created_at = DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
     
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = PurchaseInvoiceOrders
        #do not change "invoice_no",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['invoice_no','invoice_date','supplier_invoice_no','vendor_id','vendor','purchase_type_id','purchase_type','tax', 'tax_amount','total_amount','advance_amount','remarks','order_status_id','status_name','created_at','period_name','s','sort','page','limit']

class PurchaseReturnOrdersFilter(filters.FilterSet):
    vendor_id = filters.CharFilter(method=filter_uuid)
    vendor = filters.CharFilter(field_name='vendor_id__name', lookup_expr='icontains')
    purchase_type_id = filters.CharFilter(method=filter_uuid)
    purchase_type = filters.CharFilter(field_name='purchase_type_id__name', lookup_expr='icontains')
    return_no = filters.CharFilter(lookup_expr='icontains')
    due_date = filters.DateFilter()
    return_reason = filters.CharFilter(field_name='return_reason', lookup_expr='icontains')
    tax = filters.ChoiceFilter(choices=PurchaseOrders.TAX_CHOICES)
    tax_amount = filters.RangeFilter()
    total_amount = filters.RangeFilter()
    remarks= filters.CharFilter(lookup_expr='icontains')
    order_status_id = filters.CharFilter(method=filter_uuid)
    status_name = filters.CharFilter(field_name='order_status_id__status_name', lookup_expr='iexact')
    created_at = DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
     
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = PurchaseReturnOrders
        #do not change "return_no",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['return_no','due_date','vendor_id','vendor','purchase_type_id','purchase_type','order_status_id','status_name','return_reason','tax', 'tax_amount','total_amount','remarks','created_at','period_name','s','sort','page','limit']
