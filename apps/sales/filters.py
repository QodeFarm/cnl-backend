from django_filters import rest_framework as filters
from .models import SaleOrder, SaleInvoiceOrders, SaleReturnOrders
from config.utils_methods import filter_uuid
from django_filters import FilterSet, ChoiceFilter, DateFromToRangeFilter
from django_filters import rest_framework as filters
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name

class SaleOrderFilter(filters.FilterSet):
    # order_date = filters.DateFromToRangeFilter()
    # delivery_date = filters.DateFromToRangeFilter()
    # created_at = filters.DateFromToRangeFilter()
    # order_no = filters.CharFilter(lookup_expr='icontains')
    customer_id = filters.CharFilter(method=filter_uuid)
    # order_id = filters.CharFilter(method=filter_uuid)
    # remarks = filters.CharFilter(lookup_expr='icontains')
    # customer_name = filters.CharFilter(field_name='customer_id__name', lookup_expr='icontains')
    # sale_type_id = filters.CharFilter(method=filter_uuid)
    # sales_type_name = filters.CharFilter(field_name='sale_type_id__name', lookup_expr='icontains')
    # item_value = filters.RangeFilter()
    # advance_amount = filters.RangeFilter()
    # doc_amount = filters.RangeFilter()

    period_name = ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    created_at = DateFromToRangeFilter()

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
    
    class Meta:
        model = SaleOrder
        fields =[]

class SaleInvoiceOrdersFilter(filters.FilterSet):
    period_name = ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    created_at = DateFromToRangeFilter()

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
    
    class Meta:
        model = SaleInvoiceOrders
        fields =[]

class SaleReturnOrdersFilter(filters.FilterSet):
    period_name = ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    created_at = DateFromToRangeFilter()

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
    
    class Meta:
        model = SaleReturnOrders
        fields =[]