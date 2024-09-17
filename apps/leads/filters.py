from django_filters import rest_framework as filters
from apps.leads.models import LeadInteractions, Leads
from config.utils_methods import filter_uuid
from django_filters import FilterSet, ChoiceFilter, DateFromToRangeFilter
from django_filters import rest_framework as filters
from config.utils_filter_methods import PERIOD_NAME_CHOICES, apply_sorting, filter_by_pagination, filter_by_period_name, search_queryset
import logging
logger = logging.getLogger(__name__)
import json
from django.core.exceptions import ValidationError
from django.db.models import Max


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
        try:
            search_params = json.loads(value)
            self.search_params = search_params
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding search params: {e}")
            raise ValidationError("Invalid search parameter format.")

        queryset = search_queryset(queryset, search_params, self)
        return queryset.distinct()

    def filter_by_sort(self, queryset, name, value):
        queryset = apply_sorting(self, queryset)
        return queryset
    
    def filter_by_page(self, queryset, name, value):
        self.page_number = int(value)
        return queryset

    def filter_by_limit(self, queryset, name, value):
        self.limit = int(value)
        queryset = apply_sorting(self, queryset)
        paginated_queryset, total_count = filter_by_pagination(queryset.distinct(), self.page_number, self.limit)
        self.total_count = total_count
        return paginated_queryset
        
    class Meta:
        model = Leads
        #do not change "name",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['name','phone','email','lead_status_id','lead_status','assignee_id','assignee','score','created_at','notes', 'interaction_date','period_name','search','sort','page','limit']
