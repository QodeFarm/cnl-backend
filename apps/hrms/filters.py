from django_filters import rest_framework as filters
from apps.hrms.models import Employees
from config.utils_methods import filter_uuid
from django_filters import FilterSet, ChoiceFilter, DateFromToRangeFilter
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
logger = logging.getLogger(__name__)
import json
from django.core.exceptions import ValidationError

class EmployeesFilter(filters.FilterSet):
    designation_id = filters.CharFilter(field_name='designation_id__designation_name', lookup_expr='icontains')
    department_id = filters.CharFilter(field_name='department_id__department_name', lookup_expr='icontains')
    name = filters.CharFilter(lookup_expr='icontains')
    email = filters.CharFilter(lookup_expr='exact')
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
        model = Employees
        #do not change "name",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['name','email','phone','designation_id','department_id','created_at','period_name','search','sort','page','limit']
