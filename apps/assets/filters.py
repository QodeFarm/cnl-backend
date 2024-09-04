from django_filters import rest_framework as filters
from apps.assets.models import AssetMaintenance, Assets
from config.utils_methods import filter_uuid
from django_filters import FilterSet, ChoiceFilter, DateFromToRangeFilter
from config.utils_filter_methods import PERIOD_NAME_CHOICES, apply_sorting, filter_by_pagination, filter_by_period_name, search_queryset
import logging
logger = logging.getLogger(__name__)
import json
from django.core.exceptions import ValidationError

class AssetsFilter(filters.FilterSet):
    asset_category_id = filters.CharFilter(method=filter_uuid)
    category = filters.CharFilter(field_name='asset_category_id__category_name', lookup_expr='icontains')
    unit_options_id = filters.CharFilter(method=filter_uuid)
    unit_options = filters.CharFilter(field_name='unit_options_id__unit_name', lookup_expr='icontains')
    asset_status_id = filters.CharFilter(method=filter_uuid)
    status= filters.CharFilter(field_name='asset_status_id__status_name', lookup_expr='icontains')
    location_id = filters.CharFilter(method=filter_uuid)
    location= filters.CharFilter(field_name='location_id__location_name', lookup_expr='icontains')
    name = filters.CharFilter(lookup_expr='icontains')
    purchase_date = filters.DateFilter()
    price = DateFromToRangeFilter()
    created_at = DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    search = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
     
    def filter_by_search(self, queryset, name, value):
        try:
            search_params = json.loads(value)
            self.search_params = search_params  # Set the search_params as an instance attribute
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding search params: {e}")
            raise ValidationError("Invalid search parameter format.")

        queryset = search_queryset(queryset, search_params, self)
        return queryset

    def filter_by_sort(self, queryset, name, value):
        return apply_sorting(self, queryset)

    def filter_by_page(self, queryset, name, value):
        self.page_number = int(value)
        return queryset

    def filter_by_limit(self, queryset, name, value):
        self.limit = int(value)
        queryset = apply_sorting(self, queryset)
        paginated_queryset, total_count = filter_by_pagination(queryset, self.page_number, self.limit)
        self.total_count = total_count
        return paginated_queryset
    
    class Meta:
        model = Assets
        #do not change "name",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['name','price','purchase_date','asset_category_id','category','unit_options_id', 'unit_options','asset_status_id','status','location_id','location','created_at','period_name','page','limit','sort','search']


class AssetMaintenanceFilter(filters.FilterSet):
    asset_id = filters.CharFilter(method=filter_uuid)
    asset = filters.CharFilter(field_name='asset_id__name', lookup_expr='icontains')
    maintenance_description = filters.CharFilter(lookup_expr='icontains')
    maintenance_date = filters.DateFilter()
    cost = DateFromToRangeFilter()
    created_at = DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    search = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
     
    def filter_by_search(self, queryset, name, value):
        try:
            search_params = json.loads(value)
            self.search_params = search_params  # Set the search_params as an instance attribute
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding search params: {e}")
            raise ValidationError("Invalid search parameter format.")

        queryset = search_queryset(queryset, search_params, self)
        return queryset

    def filter_by_sort(self, queryset, name, value):
        return apply_sorting(self, queryset)

    def filter_by_page(self, queryset, name, value):
        self.page_number = int(value)
        return queryset

    def filter_by_limit(self, queryset, name, value):
        self.limit = int(value)
        queryset = apply_sorting(self, queryset)
        paginated_queryset, total_count = filter_by_pagination(queryset, self.page_number, self.limit)
        self.total_count = total_count
        return paginated_queryset
    
    class Meta:
        model = AssetMaintenance
        #do not change "maintenance_date",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['asset','asset_id','maintenance_description','maintenance_date','cost','created_at','period_name','page','limit','sort','search']
