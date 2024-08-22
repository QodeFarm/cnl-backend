from django_filters import rest_framework as filters
from .models import SaleOrder, SaleInvoiceOrders, SaleReturnOrders
from config.utils_methods import filter_uuid
from django_filters import FilterSet, ChoiceFilter, DateFromToRangeFilter
from django_filters import rest_framework as filters
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name

class SaleOrderFilter(filters.FilterSet):
    customer_id = filters.CharFilter(method=filter_uuid)
    order_status_id = filters.CharFilter(method=filter_uuid)
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    created_at = filters.DateFromToRangeFilter()
    status_name = filters.CharFilter(field_name='order_status_id__status_name', lookup_expr='iexact')

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
    
    class Meta:
        model = SaleOrder
        fields = ['customer_id', 'order_status_id', 'period_name', 'created_at', 'status_name']

class SaleInvoiceOrdersFilter(filters.FilterSet):
    customer_id = filters.CharFilter(method=filter_uuid)
    order_status_id = filters.CharFilter(method=filter_uuid)
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    created_at = filters.DateFromToRangeFilter()
    status_name = filters.CharFilter(field_name='order_status_id__status_name', lookup_expr='iexact')

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
    
    class Meta:
        model = SaleInvoiceOrders
        fields =['customer_id', 'order_status_id', 'period_name', 'created_at', 'status_name']

class SaleReturnOrdersFilter(filters.FilterSet):
    customer_id = filters.CharFilter(method=filter_uuid)
    order_status_id = filters.CharFilter(method=filter_uuid)
    period_name = ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    created_at = DateFromToRangeFilter()
    status_name = filters.CharFilter(field_name='order_status_id__status_name', lookup_expr='iexact')

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
    
    class Meta:
        model = SaleReturnOrders
        fields =['customer_id', 'order_status_id', 'period_name', 'created_at', 'status_name']