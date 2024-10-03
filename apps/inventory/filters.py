from django_filters import rest_framework as filters
from apps.inventory.models import WarehouseLocations, Warehouses
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
    search = filters.CharFilter(method='filter_by_search', label="Search")
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
<<<<<<< HEAD
        fields =['name','code','phone','city_id','city','state_id', 'state','created_at','period_name','page','limit','sort','search']

class WareHouseLocationsFilter(filters.FilterSet):
    location_name = filters.CharFilter(lookup_expr='icontains')
    warehouse = filters.CharFilter(field_name='warehouse_id__name', lookup_expr='icontains')
    
    class Meta:
        model = WarehouseLocations
        fields = ['location_name', 'warehouse']

=======
        fields =['name','code','phone','city_id','state_id','created_at','period_name','search','sort','page','limit']
>>>>>>> 84a04a30e7a9c24423aeeac856039fa3bb46ac99
