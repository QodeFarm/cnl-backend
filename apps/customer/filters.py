from django_filters import rest_framework as filters
import uuid
from django.db.models import Q
from apps.customer.models import Customer
from config.utils_methods import filter_uuid
from config.utils_filter_methods import PERIOD_NAME_CHOICES, apply_sorting, filter_by_pagination, filter_by_period_name, search_queryset
import logging
logger = logging.getLogger(__name__)
import json
from django.core.exceptions import ValidationError

class LedgerAccountsFilters(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    type = filters.CharFilter(lookup_expr='exact')
    ledger_group_id = filters.CharFilter(field_name='ledger_group_id__name', lookup_expr='exact')
    account_no = filters.CharFilter(lookup_expr='exact')
    pan = filters.CharFilter(lookup_expr='exact')

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
    search = filters.CharFilter(method='filter_by_search', label="Search")
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
        try:
            search_params = json.loads(value)
            self.search_params = search_params  # Set the search_params as an instance attribute
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding search params: {e}")
            raise ValidationError("Invalid search parameter format.")

        queryset = search_queryset(queryset, search_params, self)
        return queryset

    def filter_by_sort(self, queryset, name, value):
        return apply_sorting(self, queryset)

    def filter_by_page(self, queryset, name, value):
        self.page_number = int(value)
        return queryset

    def filter_by_limit(self, queryset, name, value):
        self.limit = int(value)
        queryset = apply_sorting(self, queryset)
        paginated_queryset, total_count = filter_by_pagination(queryset, self.page_number, self.limit)
        self.total_count = total_count
        return paginated_queryset
    
    class Meta:
        model = Customer
        #do not change "name",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields = ['name','gst','ledger_account_id','created_at','email', 'phone', 'city_id','period_name','search','sort','page','limit']

    
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