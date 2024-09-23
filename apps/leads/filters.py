from django_filters import rest_framework as filters
from apps.leads.models import LeadInteractions, Leads
from config.utils_methods import filter_uuid
from django_filters import FilterSet, ChoiceFilter, DateFromToRangeFilter
from django_filters import rest_framework as filters
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
logger = logging.getLogger(__name__)
import json
from django.core.exceptions import ValidationError

class LeadsFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    phone = filters.CharFilter(lookup_expr='exact')
    email = filters.CharFilter(lookup_expr='exact')
    lead_status_id = filters.CharFilter(method=filter_uuid)
    lead_status = filters.CharFilter(field_name='lead_status_id__status_name', lookup_expr='icontains')
    assignee_id = filters.CharFilter(method=filter_uuid)
    assignee = filters.CharFilter(field_name='assignee_id__name', lookup_expr='icontains')  
    score = filters.NumberFilter()  
    created_at = DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    search = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    # Adding interaction filters
    interaction_date = filters.DateFilter(field_name='interaction__interaction_date', lookup_expr='exact')
    notes = filters.CharFilter(field_name='interaction__notes', lookup_expr='icontains')

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value).distinct()

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
        
    class Meta:
        model = Leads
        #do not change "name",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['name','phone','email','lead_status_id','lead_status','assignee_id','assignee','score','created_at','notes', 'interaction_date','period_name','search','sort','page','limit']
