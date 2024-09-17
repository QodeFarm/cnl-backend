from django_filters import rest_framework as filters
from apps.vendor.models import Vendor, VendorAddress
from config.utils_methods import filter_uuid
from django_filters import FilterSet, ChoiceFilter, DateFromToRangeFilter
from django_filters import rest_framework as filters
from config.utils_filter_methods import PERIOD_NAME_CHOICES, apply_sorting, filter_by_pagination, filter_by_period_name, search_queryset
import logging
logger = logging.getLogger(__name__)
import json
from django.core.exceptions import ValidationError

class VendorFilter(FilterSet): #verified
    name = filters.CharFilter(lookup_expr='icontains')
    gst_no = filters.CharFilter(lookup_expr='icontains')
    vendor_category_id = filters.CharFilter(method=filter_uuid)
    vendor_category = filters.CharFilter(field_name='vendor_category_id__name', lookup_expr='icontains')
    ledger_account_id = filters.CharFilter(method=filter_uuid)
    ledger_account = filters.CharFilter(field_name='ledger_account_id__name', lookup_expr='icontains')
    created_at = filters.DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    search = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    # Fields from VendorAddress
    email = filters.CharFilter(field_name='vendoraddress__email', lookup_expr='icontains', label="Email")
    phone = filters.CharFilter(field_name='vendoraddress__phone', lookup_expr='icontains', label="Phone")
    city_id = filters.CharFilter(field_name='vendoraddress__city_id__city_name', lookup_expr='icontains', label="City")
    
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
        model = Vendor
        #do not change "name",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields = ['name','gst_no','vendor_category_id','vendor_category','ledger_account_id','ledger_account','created_at', 'city_id','email', 'phone','period_name','search','sort','page','limit']

