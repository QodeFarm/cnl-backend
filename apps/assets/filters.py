from django_filters import rest_framework as filters
from apps.assets.models import AssetCategories, AssetMaintenance, AssetStatuses, Assets, Locations
from django_filters import FilterSet, ChoiceFilter, DateFromToRangeFilter
from config.utils_filter_methods import DocumentDateFromToRangeFilter, PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
logger = logging.getLogger(__name__)

class AssetsFilter(filters.FilterSet):
    # Date filters and Quick Period run on the document's own date, not the row's
    # insert timestamp — a backdated document belongs to the date on the document.
    document_date_field = 'purchase_date'

    # Report screens send from_date/to_date instead of purchase_date_after/_before.
    # Mapped to the same document date so both spellings filter identically.
    from_date = filters.DateFilter(field_name='purchase_date', lookup_expr='gte')
    to_date = filters.DateFilter(field_name='purchase_date', lookup_expr='lte')

    asset_category_id = filters.CharFilter(field_name='asset_category_id__category_name', lookup_expr='icontains')
    unit_options_id = filters.CharFilter(field_name='unit_options_id__unit_name', lookup_expr='icontains')
    asset_status_id= filters.CharFilter(field_name='asset_status_id__status_name', lookup_expr='icontains')
    location_id= filters.CharFilter(field_name='location_id__location_name', lookup_expr='icontains')
    name = filters.CharFilter(lookup_expr='icontains')
    # Range (purchase_date_after / purchase_date_before); exact form kept for old callers.
    purchase_date = filters.DateFromToRangeFilter()
    purchase_date_exact = filters.DateFilter(field_name='purchase_date')
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
    # Date filters and Quick Period run on the document's own date, not the row's
    # insert timestamp — a backdated document belongs to the date on the document.
    document_date_field = 'maintenance_date'

    # Report screens send from_date/to_date instead of maintenance_date_after/_before.
    # Mapped to the same document date so both spellings filter identically.
    from_date = filters.DateFilter(field_name='maintenance_date', lookup_expr='gte')
    to_date = filters.DateFilter(field_name='maintenance_date', lookup_expr='lte')

    asset_id = filters.CharFilter(field_name='asset_id__name', lookup_expr='icontains')
    maintenance_description = filters.CharFilter(lookup_expr='icontains')
    # Range (maintenance_date_after / maintenance_date_before) so the date filter and Quick Period work;
    # exact form kept for old callers. Handles DateField and DateTimeField alike.
    maintenance_date = DocumentDateFromToRangeFilter()
    maintenance_date_exact = filters.DateFilter(field_name='maintenance_date')
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

class AssetStatusesFilter(FilterSet):
    status_name = filters.CharFilter(lookup_expr='icontains')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    created_at = filters.DateFromToRangeFilter()

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = AssetStatuses 
        fields = ['status_name','created_at','s', 'sort','page','limit']

class AssetCategoriesFilter(FilterSet):
    category_name = filters.CharFilter(lookup_expr='icontains')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    created_at = filters.DateFromToRangeFilter()

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = AssetCategories 
        fields = ['category_name','created_at','s', 'sort','page','limit']

class LocationsFilter(FilterSet):
    location_name = filters.CharFilter(lookup_expr='icontains')
    address = filters.CharFilter(lookup_expr='icontains')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    created_at = filters.DateFromToRangeFilter()

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = Locations 
        fields = ['location_name','address','created_at','s', 'sort','page','limit']
