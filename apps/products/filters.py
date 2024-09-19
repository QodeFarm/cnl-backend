from django_filters import rest_framework as filters, FilterSet, CharFilter, NumberFilter
import datetime,django_filters
from .models import ProductGstClassifications, ProductItemBalance, Products
from config.utils_methods import filter_uuid
from config.utils_filter_methods import PERIOD_NAME_CHOICES, apply_sorting, filter_by_pagination, filter_by_period_name, search_queryset
import logging
logger = logging.getLogger(__name__)
import json
from django.core.exceptions import ValidationError

class ProductGroupsFilter(FilterSet):
    group_name = filters.CharFilter(lookup_expr='icontains')

class ProductCategoriesFilter(FilterSet):
    category_name = filters.CharFilter(lookup_expr='icontains')
    code = filters.CharFilter(lookup_expr='icontains')

class ProductStockUnitsFilter(FilterSet):
    stock_unit_name = filters.CharFilter(lookup_expr='icontains')
    quantity_code_id = filters.NumberFilter()
    quantity_code_name = CharFilter(field_name='quantity_code_id__quantity_code_name', lookup_expr='exact')

class ProductGstClassificationsFilter(FilterSet):
    type = filters.ChoiceFilter(choices=ProductGstClassifications.TYPE_CHOICES, field_name='type')
    code = filters.CharFilter(lookup_expr='icontains')
    hsn_or_sac_code = filters.CharFilter(lookup_expr='icontains')

class ProductSalesGlFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    sales_accounts = filters.CharFilter(lookup_expr='exact')
    code = filters.CharFilter(lookup_expr='icontains')
    type = filters.CharFilter(lookup_expr='exact')
    account_no = filters.CharFilter(lookup_expr='exact')
    rtgs_ifsc_code = filters.CharFilter(lookup_expr='icontains')
    address = filters.CharFilter(lookup_expr='icontains')
    pan = filters.CharFilter(lookup_expr='exact')
    employee = filters.BooleanFilter()

class ProductPurchaseGlFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    purchase_accounts = filters.CharFilter(lookup_expr='exact')
    code = filters.CharFilter(lookup_expr='icontains')
    type = filters.CharFilter(lookup_expr='exact')
    account_no = filters.CharFilter(lookup_expr='exact')
    rtgs_ifsc_code = filters.CharFilter(lookup_expr='icontains')
    address = filters.CharFilter(lookup_expr='icontains')
    pan = filters.CharFilter(lookup_expr='exact')
    employee = filters.BooleanFilter()

class ProductsFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    code = filters.CharFilter(lookup_expr='icontains')
    barcode = filters.CharFilter(lookup_expr='exact')
    category_id = filters.CharFilter(method=filter_uuid)
    product_id = filters.CharFilter(method=filter_uuid)
    category_name = CharFilter(field_name='category_id__category_name', lookup_expr='exact')
    product_group_id = filters.CharFilter(method=filter_uuid)
    group_name = CharFilter(field_name='product_group_id__group_name', lookup_expr='exact')
    type_id = filters.CharFilter(method=filter_uuid)
    type_name = CharFilter(field_name='type_id__type_name', lookup_expr='exact')    
    gst_classification_id = filters.CharFilter(method=filter_uuid)
    hsn_or_sac_code = CharFilter(field_name='gst_classification_id__hsn_or_sac_code', lookup_expr='exact')
    created_at = filters.DateFromToRangeFilter()
    sales_rate = filters.RangeFilter()
    mrp = filters.RangeFilter()
    discount = filters.RangeFilter()
    dis_amount = filters.RangeFilter()
    hsn_code = filters.CharFilter(lookup_expr='icontains')
    print_name = filters.CharFilter(lookup_expr='icontains')
    unit_options_id = filters.CharFilter(method=filter_uuid)
    unit_options = filters.CharFilter(field_name='unit_options_id__unit_name', lookup_expr='icontains')
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
        model = Products
        #do not change "name",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['name','code','unit_options_id','unit_options','sales_rate','mrp','discount','dis_amount','hsn_code','print_name','barcode', 'created_at','period_name','search','sort','page','limit']


class ProductItemBalanceFilter(FilterSet):
    product_balance_id = filters.CharFilter(method=filter_uuid)
    product_id = filters.CharFilter(method=filter_uuid)
    product_name = filters.CharFilter(field_name='product_id__name', lookup_expr='icontains')
    balance = django_filters.NumberFilter(field_name='balance', lookup_expr='exact')
    location_id = filters.CharFilter(lookup_expr='icontains')
    warehouse_id = filters.CharFilter(method=filter_uuid)
    warehouse_name = filters.CharFilter(field_name='warehouse_id__name', lookup_expr='icontains')

    class Meta:
        model = ProductItemBalance
        fields =[]