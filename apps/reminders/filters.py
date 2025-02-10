from django_filters import rest_framework as filters
from apps.reminders.models import NotificationFrequencies, NotificationMethods, ReminderTypes, Reminders, ReminderRecipients, ReminderSettings, ReminderLogs
from config.utils_methods import filter_uuid
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
logger = logging.getLogger(__name__)

class NotificationFrequenciesFilter(filters.FilterSet):
    frequency_id = filters.CharFilter(method=filter_uuid)
    frequency_name = filters.CharFilter(lookup_expr='icontains')
    search = filters.CharFilter(method='filter_by_search', label="Search")
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
        model = NotificationFrequencies 
        fields = ['frequency_id','frequency_name','created_at','search', 'sort','page','limit']

class NotificationMethodsFilter(filters.FilterSet):
    method_id = filters.CharFilter(method=filter_uuid)
    method_name = filters.CharFilter(lookup_expr='icontains')
    search = filters.CharFilter(method='filter_by_search', label="Search")
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
        model = NotificationMethods 
        fields = ['method_id','method_name','created_at','search', 'sort','page','limit']
		
class ReminderTypesFilter(filters.FilterSet):
    reminder_type_id = filters.CharFilter(method=filter_uuid)
    type_name = filters.CharFilter(lookup_expr='icontains')
    search = filters.CharFilter(method='filter_by_search', label="Search")
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
        model = ReminderTypes 
        fields = ['reminder_type_id','type_name','created_at','search', 'sort','page','limit']

class RemindersFilter(filters.FilterSet):
    reminder_id = filters.CharFilter(method=filter_uuid)
    reminder_type_id = filters.CharFilter(field_name='reminder_type_id__type_name', lookup_expr='icontains')
    subject = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    reminder_date = filters.DateFilter(lookup_expr='exact')
    is_recurring = filters.BooleanFilter()
    recurring_frequency = filters.ChoiceFilter(choices=Reminders.RECURRING_FREQUENCY_CHOICES)
    created_at = filters.DateFromToRangeFilter()
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
        model = Reminders 
        fields = ['reminder_id','reminder_type_id','subject','description','reminder_date','is_recurring','recurring_frequency','created_at','period_name','s','sort','page','limit']


class ReminderRecipientsFilter(filters.FilterSet):
    recipient_id = filters.CharFilter(method=filter_uuid)
    reminder_id = filters.CharFilter(field_name='reminder_id__subject', lookup_expr='icontains')
    recipient_user_id = filters.CharFilter(field_name='employee_id__name', lookup_expr='icontains')
    recipient_email = filters.CharFilter(lookup_expr='icontains')
    notification_method_id = filters.CharFilter(field_name='notification_method_id__method_name', lookup_expr='icontains')
    created_at = filters.DateFromToRangeFilter()
 
    class Meta:
        model = ReminderRecipients 
        fields = ['recipient_id','reminder_id','recipient_user_id','recipient_email','notification_method_id','created_at']


class ReminderSettingsFilter(filters.FilterSet):
    setting_id = filters.CharFilter(method=filter_uuid)
    user_id = filters.CharFilter(field_name='user_id__first_name', lookup_expr='icontains')
    notification_frequency_id = filters.CharFilter(field_name='notification_frequency_id__frequency_name', lookup_expr='icontains')
    notification_method_id = filters.CharFilter(field_name='notification_method_id__method_name', lookup_expr='icontains')
    search = filters.CharFilter(method='filter_by_search', label="Search")
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
        model = ReminderSettings 
        fields = ['setting_id','user_id','notification_frequency_id','notification_method_id','created_at','search','sort','page','limit']


class ReminderLogsFilter(filters.FilterSet):
    log_id = filters.CharFilter(method=filter_uuid)
    reminder_id = filters.CharFilter(field_name='reminder_id__subject', lookup_expr='icontains')
    log_date = filters.DateFromToRangeFilter()
    log_action = filters.ChoiceFilter(choices=ReminderLogs.LOG_ACTION_CHOICES)
    created_at = filters.DateFromToRangeFilter()
 
    class Meta:
        model = ReminderLogs 
        fields = ['log_id','reminder_id','log_date','log_action','created_at']

		