from django_filters import rest_framework as filters
from config.utils_methods import filter_uuid
from .models import PurchaseOrders, PurchaseInvoiceOrders, PurchaseReturnOrders
from django_filters import FilterSet, ChoiceFilter, DateFromToRangeFilter
from config.utils_filter_methods import PERIOD_NAME_CHOICES
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name

class PurchaseOrdersFilter(filters.FilterSet):
    vendor_id = filters.CharFilter(method=filter_uuid)
    order_status_id = filters.CharFilter(method=filter_uuid)
    status_name = filters.CharFilter(field_name='order_status_id__status_name', lookup_expr='iexact')
    period_name = ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    created_at = DateFromToRangeFilter()

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
    
    class Meta:
        model = PurchaseOrders
        fields =['vendor_id','order_status_id','status_name','period_name','created_at']

class PurchaseInvoiceOrdersFilter(filters.FilterSet):
    vendor_id = filters.CharFilter(method=filter_uuid)
    order_status_id = filters.CharFilter(method=filter_uuid)
    status_name = filters.CharFilter(field_name='order_status_id__status_name', lookup_expr='iexact')
    period_name = ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    created_at = DateFromToRangeFilter()

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
    
    class Meta:
        model = PurchaseInvoiceOrders
        fields =['vendor_id','order_status_id','status_name','period_name','created_at']

class PurchaseReturnOrdersFilter(filters.FilterSet):
    vendor_id = filters.CharFilter(method=filter_uuid)
    order_status_id = filters.CharFilter(method=filter_uuid)
    status_name = filters.CharFilter(field_name='order_status_id__status_name', lookup_expr='iexact')
    period_name = ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    created_at = DateFromToRangeFilter()

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
    
    class Meta:
        model = PurchaseReturnOrders
        fields =['vendor_id','order_status_id','status_name','period_name','created_at']
