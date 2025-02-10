from django_filters import rest_framework as filters
from apps.assets.models import AssetCategories, AssetMaintenance, AssetStatuses, Assets, Locations
from django_filters import FilterSet, ChoiceFilter, DateFromToRangeFilter
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
logger = logging.getLogger(__name__)

class AssetsFilter(filters.FilterSet):
    asset_category_id = filters.CharFilter(field_name='asset_category_id__category_name', lookup_expr='icontains')
    unit_options_id = filters.CharFilter(field_name='unit_options_id__unit_name', lookup_expr='icontains')
    asset_status_id= filters.CharFilter(field_name='asset_status_id__status_name', lookup_expr='icontains')
    location_id= filters.CharFilter(field_name='location_id__location_name', lookup_expr='icontains')
    name = filters.CharFilter(lookup_expr='icontains')
    purchase_date = filters.DateFilter()
    price = DateFromToRangeFilter()
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
        model = Assets
        #do not change "name",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['name','price','purchase_date','asset_category_id','unit_options_id','asset_status_id','location_id','created_at','period_name','s','sort','page','limit']


class AssetMaintenanceFilter(filters.FilterSet):
    asset_id = filters.CharFilter(field_name='asset_id__name', lookup_expr='icontains')
    maintenance_description = filters.CharFilter(lookup_expr='icontains')
    maintenance_date = filters.DateFilter()
    cost = DateFromToRangeFilter()
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
        model = AssetMaintenance
        #do not change "asset_id",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['asset_id','maintenance_description','maintenance_date','cost','created_at','period_name','s','sort','page','limit']
        
        
class AssetCategoriesFilter(filters.FilterSet):
    category_name = filters.CharFilter(lookup_expr='icontains')  
    created_at = filters.DateFromToRangeFilter() 
    updated_at = filters.DateFromToRangeFilter() 
    s = filters.CharFilter(method='filter_by_search', label="Search")

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = AssetCategories
        fields = ['category_name', 'created_at', 'updated_at', 's']
        
        
class AssetStatusesFilter(filters.FilterSet):
    asset_status_id = filters.UUIDFilter(field_name='asset_status_id')  # Filter by asset_status_id
    status_name = filters.CharFilter(lookup_expr='icontains')  # Case-insensitive search for status_name
    created_at = filters.DateFromToRangeFilter()  # Date range filter for created_at
    updated_at = filters.DateFromToRangeFilter()  # Date range filter for updated_at
    s = filters.CharFilter(method='filter_by_search', label="Search")

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = AssetStatuses
        fields = ['asset_status_id','status_name', 'created_at', 'updated_at', 's']  
        
        
class LocationsFilter(filters.FilterSet):
    location_id = filters.UUIDFilter(field_name='location_id') 
    location_name = filters.CharFilter(lookup_expr='icontains')  
    address = filters.CharFilter(lookup_expr='icontains')  
    created_at = filters.DateFromToRangeFilter() 
    updated_at = filters.DateFromToRangeFilter()  
    s = filters.CharFilter(method='filter_by_search', label="Search")

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = Locations
        fields = ['location_id', 'location_name', 'address', 'created_at', 'updated_at', 's']              