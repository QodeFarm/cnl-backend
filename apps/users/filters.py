from django_filters import rest_framework as filters
from .models import RolePermissions, Roles, User
from config.utils_methods import filter_uuid
from django_filters import FilterSet, ChoiceFilter ,DateFromToRangeFilter
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
logger = logging.getLogger(__name__)

class RolePermissionsFilter(filters.FilterSet):
    
    role_id = filters.CharFilter(method=filter_uuid)

    # class Meta:
    #     model = RolePermissions
    #     fields =['role_id']
   
class RolesFilter(FilterSet):
    role_name = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
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
        model = Roles 
        fields = ['role_name','description','created_at','s', 'sort','page','limit']

class UserFilter(FilterSet):
    username = filters.CharFilter(lookup_expr='icontains')
    email = filters.CharFilter(lookup_expr='exact')
    mobile = filters.CharFilter(lookup_expr='exact')
    role = filters.CharFilter(field_name='role_id__role_name', lookup_expr='icontains')
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
        model = User 
        fields = ['username','email','mobile','role','created_at','s', 'sort','page','limit']