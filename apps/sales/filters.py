from django_filters import rest_framework as filters
from .models import SaleOrder, SaleInvoiceOrders, SaleOrderItems, SaleReturnOrders
from config.utils_methods import filter_uuid
from django_filters import FilterSet, ChoiceFilter, DateFromToRangeFilter
from django_filters import rest_framework as filters
from config.utils_filter_methods import PERIOD_NAME_CHOICES, apply_sorting, filter_by_pagination, filter_by_period_name, search_queryset
import logging
logger = logging.getLogger(__name__)
import json
from django.core.exceptions import ValidationError

class SaleOrderFilter(filters.FilterSet):
    order_no = filters.CharFilter(lookup_expr='icontains')
    customer_id = filters.CharFilter(method=filter_uuid)
    customer = filters.CharFilter(field_name='customer_id__name', lookup_expr='icontains')
    # order_date = filters.DateFromToRangeFilter()
    order_date = filters.DateFilter()
    sale_type_id = filters.CharFilter(method=filter_uuid)
    sale_type = filters.CharFilter(field_name='sale_type_id__name', lookup_expr='icontains')
    order_status_id = filters.CharFilter(method=filter_uuid)
    created_at = filters.DateFromToRangeFilter()
    advance_amount = filters.RangeFilter()
    tax = filters.ChoiceFilter(choices=SaleOrder.TAX_CHOICES)
    amount = filters.RangeFilter(field_name='item_value', lookup_expr='icontains')
    flow_status = filters.CharFilter(field_name='flow_status', lookup_expr='iexact')
    status_name = filters.CharFilter(field_name='order_status_id__status_name', lookup_expr='iexact')
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    search = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

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
        model = SaleOrder 
        #do not change "order_no",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields = ['order_no','order_date','customer_id','customer','sale_type_id','sale_type','order_status_id','status_name','created_at','advance_amount','tax','amount','period_name','page','limit','sort','search']

class SaleInvoiceOrdersFilter(filters.FilterSet):
    customer_id = filters.CharFilter(method=filter_uuid)
    customer = filters.CharFilter(field_name='customer_id__name', lookup_expr='icontains')
    invoice_date = filters.DateFilter()
    total_amount = filters.RangeFilter()
    tax_amount = filters.RangeFilter()
    invoice_no = filters.CharFilter(lookup_expr='icontains')
    advance_amount = filters.RangeFilter()
    remarks= filters.CharFilter(lookup_expr='icontains')
    order_status_id = filters.CharFilter(method=filter_uuid)
    status_name = filters.CharFilter(field_name='order_status_id__status_name', lookup_expr='iexact')
    created_at = filters.DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    search = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

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
        model = SaleInvoiceOrders
        #do not change "invoice_no",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['invoice_no','customer_id','customer','invoice_date','total_amount','tax_amount','advance_amount','remarks','order_status_id','status_name', 'created_at','period_name','page','limit','sort','search']

class SaleReturnOrdersFilter(filters.FilterSet):
    customer_id = filters.CharFilter(method=filter_uuid)
    customer = filters.CharFilter(field_name='customer_id__name', lookup_expr='icontains')
    return_date = filters.DateFilter()
    due_date= filters.DateFilter()
    return_no = filters.CharFilter(lookup_expr='icontains')
    tax = filters.ChoiceFilter(choices=SaleReturnOrders.TAX_CHOICES)
    tax_amount = filters.RangeFilter()
    total_amount = filters.RangeFilter()
    return_reason = filters.CharFilter(lookup_expr='icontains')
    remarks= filters.CharFilter(lookup_expr='icontains')
    order_status_id = filters.CharFilter(method=filter_uuid)
    status_name = filters.CharFilter(field_name='order_status_id__status_name', lookup_expr='iexact')
    created_at = DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    search = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

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
        model = SaleReturnOrders
        #do not change "return_no",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['return_no','return_date','due_date','customer_id','customer','tax', 'tax_amount','total_amount','return_reason','remarks','order_status_id', 'status_name', 'created_at','period_name','page','limit','sort','search']
        
class SaleOrdersItemsilter(filters.FilterSet):
    sale_order_id = filters.CharFilter(method=filter_uuid)
    
    class Meta:
        model = SaleOrderItems
        fields =['sale_order_id']