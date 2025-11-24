from django_filters import rest_framework as filters

from config.utils_filter_methods import filter_by_limit, filter_by_page, filter_by_period_name, filter_by_search, filter_by_sort
from .models import AuditLog

PERIOD_NAME_CHOICES = [
    ('today', 'Today'),
    ('yesterday', 'Yesterday'),
    ('last_week', 'LastWeek'),
    ('current_month', 'CurrentMonth'),
    ('last_month', 'LastMonth'),
    ('last_six_months', 'LastSixMonths'),
    ('current_quarter', 'CurrentQuarter'),
    ('year_to_date', 'YearToDate'),
    ('last_year', 'LastYear'),
]


class AuditLogFilter(filters.FilterSet):
    # Global search
    s = filters.CharFilter(method="filter_by_search", label="Search")
    
    # Quick period filter (Today, This Week, This Month etc…)
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')

    # Date range filter
    created_at = filters.DateFromToRangeFilter()

    # Sorting support
    sort = filters.CharFilter(method="filter_by_sort")

    # Pagination
    page = filters.NumberFilter(method="filter_by_page")
    limit = filters.NumberFilter(method="filter_by_limit")


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
        model = AuditLog
        fields = ["created_at", "period_name", "s", "sort", "page", "limit"]
