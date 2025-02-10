from django_filters import rest_framework as filters
from apps.tasks.models import Tasks
from config.utils_methods import filter_uuid
from django_filters import FilterSet, ChoiceFilter, DateFromToRangeFilter
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
logger = logging.getLogger(__name__)

class TasksFilter(filters.FilterSet):
    user_id = filters.CharFilter(field_name='user_id__first_name', lookup_expr='icontains')
    group_id = filters.CharFilter(field_name='group_id__group_name', lookup_expr='icontains')
    priority_id = filters.CharFilter(field_name='priority_id__priority_name', lookup_expr='icontains')
    status_id = filters.CharFilter(field_name='status_id__status_name', lookup_expr='icontains')
    description = filters.CharFilter(field_name='description', lookup_expr='icontains')
    title = filters.CharFilter(lookup_expr='icontains')
    due_date = filters.DateFilter()
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
        model = Tasks
        #do not change "title",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['title','user_id','group_id','description','priority_id','status_id','due_date','created_at','period_name','s','sort','page','limit']
