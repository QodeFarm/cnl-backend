from django_filters import rest_framework as filters
import uuid
from django.db.models import Q
from apps.customer.models import Customer
from apps.customfields.models import CustomField
from config.utils_filter_methods import filter_by_limit, filter_by_page, filter_by_search, filter_by_sort
from config.utils_methods import filter_uuid


class CustomFieldValuesFilters(filters.FilterSet):
    entity_data_id = filters.CharFilter(field_name='entity_data_id', lookup_expr='exact')
    entity_id = filters.CharFilter(field_name='entity_id', lookup_expr='exact')
    
class CustomFieldOptionsFilters(filters.FilterSet):
    custom_field_id = filters.CharFilter(field_name='custom_field_id_id', lookup_expr='exact')


class CustomFieldFilter(filters.FilterSet):
    field_name = filters.CharFilter(lookup_expr='icontains')
    entity_id = filters.CharFilter(field_name='entity_id__entity_name', lookup_expr='icontains')
    field_type_id = filters.CharFilter(field_name='field_type_id__field_type_name', lookup_expr='icontains')
    is_required = filters.BooleanFilter()
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
        model = CustomField 
        fields = ['field_name','entity_id','field_type_id','is_required','created_at','s', 'sort','page','limit']