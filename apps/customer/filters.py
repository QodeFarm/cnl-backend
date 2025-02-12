from django_filters import rest_framework as filters
import uuid
from django.db.models import Q
from apps.customer.models import Customer, LedgerAccounts
from config.utils_methods import filter_uuid
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
logger = logging.getLogger(__name__)

class LedgerAccountsFilters(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    code = filters.CharFilter(lookup_expr='exact')
    inactive = filters.BooleanFilter()
    type = filters.CharFilter(lookup_expr='exact')
    account_no = filters.CharFilter(lookup_expr='exact')
    is_loan_account = filters.BooleanFilter()
    pan = filters.CharFilter(lookup_expr='exact')
    address = filters.CharFilter(lookup_expr='icontains')
    ledger_group_id = filters.CharFilter(field_name='ledger_group_id__name', lookup_expr='exact')
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
        model = LedgerAccounts 
        fields = ['name','code','inactive','type','account_no','is_loan_account','pan','address','ledger_group_id','created_at','s', 'sort','page','limit']

class CustomerFilters(filters.FilterSet):
    identification = filters.CharFilter(lookup_expr='exact')
    contact_person = filters.CharFilter(lookup_expr='exact')
    cin = filters.CharFilter(lookup_expr='exact')
    pan = filters.CharFilter(lookup_expr='exact')
    tax_type = filters.CharFilter(lookup_expr='exact')
    ledger_account_id = filters.CharFilter(field_name='ledger_account_id__name', lookup_expr='exact')
    gst_category_id = filters.CharFilter(field_name='gst_category_id__name', lookup_expr='exact')
    max_credit_days = filters.RangeFilter(lookup_expr='exact')
    name = filters.CharFilter(lookup_expr='icontains')
    gst = filters.CharFilter(lookup_expr='icontains')
    created_at = filters.DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    # Fields from CustomerAddress
    email = filters.CharFilter(field_name='customeraddresses__email', lookup_expr='icontains', label="Email")
    phone = filters.CharFilter(field_name='customeraddresses__phone', lookup_expr='icontains', label="Phone")
    city_id = filters.CharFilter(field_name='customeraddresses__city_id__city_name', lookup_expr='icontains', label="City")
    
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
        model = Customer
        #do not change "name",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields = ['name','gst','ledger_account_id','created_at','email', 'phone', 'city_id','period_name','s','sort','page','limit']

    
class CustomerAttachmentsFilters(filters.FilterSet):
    customer_id = filters.CharFilter(field_name='customer_id__name', lookup_expr='exact')
    attachment_name = filters.CharFilter(lookup_expr='exact')

class CustomerAddressesFilters(filters.FilterSet):
    customer_id = filters.CharFilter(method=filter_uuid)
    city_id = filters.CharFilter(field_name='city_id__city_name', lookup_expr='exact')
    state_id = filters.CharFilter(field_name='state_id__state_name', lookup_expr='exact')
    country_id = filters.CharFilter(field_name='country_id__country_name', lookup_expr='exact')
    pin_code = filters.CharFilter(lookup_expr='exact')
    phone = filters.CharFilter(lookup_expr='exact')
    email = filters.CharFilter(lookup_expr='exact')

    def filter_customer_id(self, queryset, name, value):
        try:
            uuid.UUID(value)
        except ValueError:
            # If the UUID is invalid, return an empty queryset
            return queryset.none()
        return queryset.filter(Q(bank_detail_id=value))