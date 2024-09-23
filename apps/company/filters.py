import django_filters,uuid
from .models import Companies, Branches, BranchBankDetails
from django.db.models import Q
from config.utils_methods import filter_uuid
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
logger = logging.getLogger(__name__)
import json
from django.core.exceptions import ValidationError

class CompaniesFilters(django_filters.FilterSet):
    company_id = django_filters.CharFilter(method=filter_uuid)
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    code = django_filters.CharFilter(field_name='code', lookup_expr='exact')
    num_branches = django_filters.NumberFilter(field_name='num_branches', lookup_expr='exact')
    num_employees = django_filters.RangeFilter(field_name='num_employees')
    
    class Meta:
        model = Companies
        fields = ['company_id','name', 'code', 'num_branches', 'num_employees']

class BranchesFilters(django_filters.FilterSet):
    branch_id = django_filters.CharFilter(method=filter_uuid)
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    code = django_filters.CharFilter(field_name='code', lookup_expr='exact')
    phone = django_filters.CharFilter(lookup_expr='icontains')
    address = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    city_id = django_filters.CharFilter(field_name='city_id__city_name', lookup_expr='exact')
    state_id = django_filters.CharFilter(field_name='state_id__state_name', lookup_expr='exact')
    status_id = django_filters.CharFilter(field_name='status_id__status_name', lookup_expr='exact')
    country = django_filters.CharFilter(field_name='country_id__country_name', lookup_expr='exact')
    created_at = django_filters.DateFromToRangeFilter()
    period_name = django_filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    search = django_filters.CharFilter(method='filter_by_search', label="Search")
    sort = django_filters.CharFilter(method='filter_by_sort', label="Sort")
    page = django_filters.NumberFilter(method='filter_by_page', label="Page")
    limit = django_filters.NumberFilter(method='filter_by_limit', label="Limit")


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
        model = Branches
        #do not change "name",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields = ['name','code','email','phone','address','branch_id','city_id','state_id','status_id','country','created_at','period_name','search','sort','page','limit']

class BranchBankDetailsFilters(django_filters.FilterSet):
    bank_detail_id = django_filters.CharFilter(method=filter_uuid)
    bank_name = django_filters.CharFilter(field_name='bank_name', lookup_expr='icontains')
    branch_id = django_filters.CharFilter(field_name='branch_id', lookup_expr='exact')
    branch_name = django_filters.CharFilter(field_name='bank_name', lookup_expr='icontains')

    class Meta:
        model = BranchBankDetails
        fields = ['bank_detail_id','bank_name', 'branch_id','branch_name']