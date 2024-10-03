from django_filters import rest_framework as filters
from apps.production.models import WorkOrder
from config.utils_methods import filter_uuid
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
logger = logging.getLogger(__name__)


class WorkOrderFilter(filters.FilterSet):
    product = filters.CharFilter(field_name='product_id__name', lookup_expr='icontains')
    status_id = filters.CharFilter(field_name='status_id__status_name', lookup_expr='icontains')
    quantity = filters.RangeFilter()
    start_date = filters.DateFromToRangeFilter()
    end_date = filters.DateFromToRangeFilter()
    created_at = filters.DateFromToRangeFilter()
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
        model = WorkOrder 
        #do not change "product",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields = ['product','status_id','quantity','start_date','end_date','created_at','period_name','search','sort','page','limit']
