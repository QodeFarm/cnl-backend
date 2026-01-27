from django_filters import rest_framework as filters, FilterSet, CharFilter, NumberFilter
import datetime,django_filters
from django_filters import BooleanFilter
from .models import Color, ProductCategories, ProductGroups, ProductGstClassifications, ProductItemBalance, ProductPurchaseGl, ProductSalesGl, ProductStockUnits, Products, ProductVariation, Size
from config.utils_methods import filter_uuid
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
logger = logging.getLogger(__name__)

class ProductGroupsFilter(FilterSet):
    product_group_id = filters.CharFilter(method=filter_uuid)
    group_name = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
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
        model = ProductGroups 
        fields = ['product_group_id','group_name','description','created_at','s', 'sort','page','limit']

class ProductCategoriesFilter(FilterSet):
    category_id = filters.CharFilter(method='filter_uuid')
    category_name = filters.CharFilter(lookup_expr='icontains')
    code = filters.CharFilter(lookup_expr='icontains')
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
        model = ProductCategories 
        fields = ['category_id','category_name', 'code','created_at','s', 'sort','page','limit']

class ProductStockUnitsFilter(FilterSet):
    stock_unit_id = filters.CharFilter(method='filter_uuid')
    stock_unit_name = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    quantity_code_id = CharFilter(field_name='quantity_code_id__quantity_code_name', lookup_expr='exact')
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
        model = ProductStockUnits 
        fields = ['stock_unit_name','quantity_code_id','description','created_at','s', 'sort','page','limit']

class ProductGstClassificationsFilter(FilterSet):
    type = filters.ChoiceFilter(choices=ProductGstClassifications.TYPE_CHOICES, field_name='type')
    code = filters.CharFilter(lookup_expr='icontains')
    hsn_or_sac_code = filters.CharFilter(lookup_expr='icontains')
    hsn_description = filters.CharFilter(lookup_expr='icontains')
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
        model = ProductGstClassifications 
        fields = ['type','code','hsn_or_sac_code','hsn_description','created_at','s', 'sort','page','limit']

class ProductSalesGlFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    sales_accounts = filters.CharFilter(lookup_expr='exact')
    code = filters.CharFilter(lookup_expr='icontains')
    inactive = filters.BooleanFilter()
    type = filters.CharFilter(lookup_expr='exact')
    account_no = filters.CharFilter(lookup_expr='exact')
    is_loan_account = filters.BooleanFilter()
    rtgs_ifsc_code = filters.CharFilter(lookup_expr='icontains')
    address = filters.CharFilter(lookup_expr='icontains')
    pan = filters.CharFilter(lookup_expr='exact')
    employee = filters.BooleanFilter()
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
        model = ProductSalesGl 
        fields = ['name','sales_accounts','code','inactive','type','account_no','is_loan_account','address','pan','rtgs_ifsc_code','employee','created_at','s', 'sort','page','limit']

class ProductPurchaseGlFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    purchase_accounts = filters.CharFilter(lookup_expr='exact')
    code = filters.CharFilter(lookup_expr='icontains')
    inactive = filters.BooleanFilter()
    type = filters.CharFilter(lookup_expr='exact')
    account_no = filters.CharFilter(lookup_expr='exact')
    is_loan_account = filters.BooleanFilter()
    rtgs_ifsc_code = filters.CharFilter(lookup_expr='icontains')
    address = filters.CharFilter(lookup_expr='icontains')
    pan = filters.CharFilter(lookup_expr='exact')
    employee = filters.BooleanFilter()
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
        model = ProductPurchaseGl 
        fields = ['name','purchase_accounts','code','inactive','type','account_no','is_loan_account','rtgs_ifsc_code','address','employee','pan','created_at','s', 'sort','page','limit']

class ProductsFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    code = filters.CharFilter(lookup_expr='icontains')
    barcode = filters.CharFilter(lookup_expr='exact')
    category_id = filters.CharFilter(method=filter_uuid)
    product_id = filters.CharFilter(method=filter_uuid)
    category = CharFilter(field_name='category_id__category_name', lookup_expr='exact')
    product_group_id = filters.CharFilter(method=filter_uuid)
    group_name = CharFilter(field_name='product_group_id__group_name', lookup_expr='exact')
    type_id = filters.CharFilter(method=filter_uuid)
    type_name = CharFilter(field_name='type_id__type_name', lookup_expr='exact')    
    gst_classification_id = filters.CharFilter(method=filter_uuid)
    hsn_or_sac_code = CharFilter(field_name='gst_classification_id__hsn_or_sac_code', lookup_expr='exact')
    purchase_rate = filters.RangeFilter()
    sales_rate = filters.RangeFilter()
    wholesale_rate = filters.RangeFilter()
    dealer_rate = filters.RangeFilter()
    mrp = filters.RangeFilter()
    discount = filters.RangeFilter()
    dis_amount = filters.RangeFilter()
    hsn_code = filters.CharFilter(lookup_expr='icontains')
    print_name = filters.CharFilter(lookup_expr='icontains')
    # balance = filters.NumberFilter()
    balance = filters.NumberFilter(
        field_name='productitembalance__balance',
        lookup_expr='exact'
    )
    unit_options_id = filters.CharFilter(method=filter_uuid)
    unit_options = filters.CharFilter(field_name='unit_options_id__unit_name', lookup_expr='icontains')
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    stock_unit_id = filters.CharFilter(method=filter_uuid)
    stock_unit = filters.CharFilter(field_name='stock_unit_id__stock_unit_name', lookup_expr='icontains')
    pack_unit_id = filters.CharFilter(method=filter_uuid)
    pack_unit_name = filters.CharFilter(field_name='pack_unit_id__stock_unit_name', lookup_expr='icontains') 
    g_pack_unit_id = filters.CharFilter(method=filter_uuid)
    g_pack_unit_name = filters.CharFilter(field_name='g_pack_unit_id__stock_unit_name', lookup_expr='icontains')    
    purchase_rate = filters.RangeFilter()
    wholesale_rate = filters.RangeFilter()
    dealer_rate = filters.RangeFilter()
    created_at = filters.DateFromToRangeFilter() 
    updated_at = filters.DateFromToRangeFilter()  
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    updated_at = filters.DateFromToRangeFilter()
    created_at = filters.DateFromToRangeFilter()
    
    # warehouse_name = filters.CharFilter(
    #     field_name='productitembalance__warehouse_location_id__warehouse_id__name',
    #     lookup_expr='icontains'
    # )
    # location_name = filters.CharFilter(
    #     field_name='productitembalance__warehouse_location_id__location_name',
    #     lookup_expr='icontains'
    # )

    warehouse_id = filters.UUIDFilter(field_name="productitembalance__warehouse_location_id__warehouse_id",lookup_expr="exact")
    warehouse_name = filters.CharFilter(
        field_name='productitembalance__warehouse_location_id__warehouse_id__name', 
        lookup_expr='icontains'
    )
    loction_id = filters.UUIDFilter(field_name="productitembalance__warehouse_location_id",lookup_expr="exact")
    location_name = filters.CharFilter(
        field_name='productitembalance__warehouse_location_id__location_name',
        lookup_expr='icontains'
    ) 

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
        model = Products
        #do not change "name",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['name','code','product_group_id','group_name','category_id','category','type_id','type_name','warehouse_id','location_name','warehouse_name','loction_id','category','stock_unit','wholesale_rate','dealer_rate','purchase_rate','balance','unit_options_id','unit_options','sales_rate','mrp','discount','dis_amount','hsn_code','print_name','barcode', 'updated_at','created_at','period_name','s','sort','page','limit']


class ProductItemBalanceFilter(FilterSet):
    product_balance_id = filters.CharFilter(method=filter_uuid)
    product_id = filters.CharFilter(method=filter_uuid)
    product = filters.CharFilter(field_name='product_id__name', lookup_expr='icontains')
    quantity = django_filters.NumberFilter(field_name='quantity', lookup_expr='exact')
    warehouse_location_id = filters.CharFilter(field_name='warehouse_location_id__location_name', lookup_expr='icontains')
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
        model = ProductItemBalance
        fields =['product','warehouse_location_id','quantity','created_at','s','sort','page','limit']

class ProductVariationFilter(FilterSet):
    product_variation_id = filters.CharFilter(method=filter_uuid)
    product_id = filters.CharFilter(method=filter_uuid)
    product_name = filters.CharFilter(field_name='product_id__name', lookup_expr='icontains')
    size_id = filters.CharFilter(method=filter_uuid)
    size_name = filters.CharFilter(field_name='size_id__size_name', lookup_expr='icontains')
    color_id = filters.CharFilter(method=filter_uuid)
    color_name = filters.CharFilter(field_name='color_id__color_name', lookup_expr='icontains')    
    size_isnull = BooleanFilter(field_name='size_id', lookup_expr='isnull')
    color_isnull = BooleanFilter(field_name='color_id', lookup_expr='isnull')       

    class Meta:
        model = ProductVariation
        fields =[]        

class SizeFilter(django_filters.FilterSet):
    size_name = django_filters.CharFilter(lookup_expr='icontains') 
    size_category = django_filters.CharFilter(lookup_expr='icontains') 
    size_system = django_filters.CharFilter(lookup_expr='icontains')
    length = django_filters.RangeFilter()
    height = django_filters.RangeFilter()
    width = django_filters.RangeFilter() 
    size_unit = django_filters.CharFilter(lookup_expr='icontains') 
    description = django_filters.CharFilter(lookup_expr='icontains')
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
        model = Size
        fields = ['size_name','size_category','size_system','length','height', 'width','size_unit','description', 'created_at','s','sort','page','limit']
            
class ColorFilter(FilterSet):
    color_name = filters.CharFilter(lookup_expr='icontains')
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
        model = Color 
        fields = ['color_name','created_at','s', 'sort','page','limit']
