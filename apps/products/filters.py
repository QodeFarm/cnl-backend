from django_filters import rest_framework as filters, FilterSet, CharFilter, NumberFilter
import datetime,django_filters
from django.utils import timezone
from .models import ProductGstClassifications, ProductItemBalance
from config.utils_methods import filter_uuid

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
    #Foreign key relations or functions
    category_id = filters.CharFilter(method=filter_uuid)
    product_id = filters.CharFilter(method=filter_uuid)
    category_name = CharFilter(field_name='category_id__category_name', lookup_expr='exact')
    product_group_id = filters.CharFilter(method=filter_uuid)
    group_name = CharFilter(field_name='product_group_id__group_name', lookup_expr='exact')
    type_id = filters.CharFilter(method=filter_uuid)
    type_name = CharFilter(field_name='type_id__type_name', lookup_expr='exact')    
    gst_classification_id = filters.CharFilter(method=filter_uuid)
    hsn_or_sac_code = CharFilter(field_name='gst_classification_id__hsn_or_sac_code', lookup_expr='exact')
    #Date filters - custom methods
    created_at = filters.DateFromToRangeFilter()

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