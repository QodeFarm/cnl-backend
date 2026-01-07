from django_filters import rest_framework as filters
from apps.inventory.models import WarehouseLocations, Warehouses
from apps.products.models import Products
from config.utils_methods import filter_uuid
from django_filters import FilterSet, ChoiceFilter, DateFromToRangeFilter
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
logger = logging.getLogger(__name__)
import json
from django.core.exceptions import ValidationError

class WarehousesFilter(filters.FilterSet):
    city_id = filters.CharFilter(field_name='city_id__city_name', lookup_expr='icontains')
    state_id = filters.CharFilter(field_name='state_id__state_name', lookup_expr='icontains')
    name = filters.CharFilter(lookup_expr='icontains')
    code = filters.CharFilter(lookup_expr='icontains')
    phone = filters.CharFilter(lookup_expr='exact')
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
        model = Warehouses
        #do not change "name",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['name','code','phone','city_id','state_id','created_at','period_name','s','sort','page','limit']

class WarehouseLocationsFilter(filters.FilterSet):
    warehouse = filters.CharFilter(field_name='warehouse_id__name', lookup_expr='icontains')
    location_name = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    created_at = DateFromToRangeFilter()
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = WarehouseLocations
        #do not change "location_name",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['location_name','description','warehouse','created_at','s','sort','page','limit']


QUICK_PERIOD_DAYS_MAP = {
    'today': 1,
    'yesterday': 1,
    'last_week': 7,
    'current_month': 30,
    'last_month': 30,
    'last_six_months': 180,
    'current_quarter': 90,
    'year_to_date': 365,
    'last_year': 365,
}

class StockForecastReportFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    code = filters.CharFilter(lookup_expr='icontains')
    category = filters.CharFilter(field_name='category_id__category_name', lookup_expr='icontains')
    product_group = filters.CharFilter(field_name='product_group_id__group_name', lookup_expr='icontains')
    type = filters.CharFilter(field_name='type_id__type_name', lookup_expr='icontains')
    category_id = filters.CharFilter(method=filter_uuid)
    product_group_id = filters.CharFilter(method=filter_uuid)
    type_id = filters.CharFilter(method=filter_uuid)
    created_at = DateFromToRangeFilter()
    
    # Quick Period filter - will be used to calculate period_days
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    
    # Standard filters
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    
    def filter_by_period_name(self, queryset, name, value):
        # Store period_days based on quick period selection
        self.period_days = QUICK_PERIOD_DAYS_MAP.get(value, 180)
        # Don't filter products by created_at, just store period_days for sales calculation
        return queryset
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)

    class Meta:
        model = Products
        #do not change "name",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields = ['name', 'code', 'category', 'product_group', 'type', 'category_id', 'product_group_id', 'type_id', 'created_at', 'period_name', 's', 'sort', 'page', 'limit']