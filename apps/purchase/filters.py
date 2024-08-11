from django_filters import rest_framework as filters
from .models import PurchaseOrders, PurchaseInvoiceOrders, PurchaseReturnOrders
from django_filters import FilterSet, ChoiceFilter, DateFromToRangeFilter
from config.utils_filter_methods import PERIOD_NAME_CHOICES
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name

class PurchaseOrdersFilter(filters.FilterSet):
    period_name = ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    created_at = DateFromToRangeFilter()

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
    
    class Meta:
        model = PurchaseOrders
        fields =['created_at']

class PurchaseInvoiceOrdersFilter(filters.FilterSet):
    period_name = ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    created_at = DateFromToRangeFilter()

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
    
    class Meta:
        model = PurchaseInvoiceOrders
        fields =[]

class PurchaseReturnOrdersFilter(filters.FilterSet):
    period_name = ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    created_at = DateFromToRangeFilter()

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
    
    class Meta:
        model = PurchaseReturnOrders
        fields =[]