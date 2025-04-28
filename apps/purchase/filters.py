from django_filters import rest_framework as filters
from config.utils_methods import filter_uuid
from .models import PurchaseOrders, PurchaseInvoiceOrders, PurchaseReturnOrders, PurchaseorderItems, Products
from django_filters import FilterSet, ChoiceFilter, DateFromToRangeFilter
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
logger = logging.getLogger(__name__)

class PurchaseOrdersFilter(filters.FilterSet):
    vendor_id = filters.CharFilter(method=filter_uuid)
    vendor = filters.CharFilter(field_name='vendor_id__name', lookup_expr='icontains')
    purchase_type_id = filters.CharFilter(field_name='purchase_type_id__name', lookup_expr='icontains')
    order_date = filters.DateFilter()
    order_no = filters.CharFilter(lookup_expr='icontains')
    tax = filters.ChoiceFilter(choices=PurchaseOrders.TAX_CHOICES)
    tax_amount = filters.RangeFilter()
    total_amount = filters.RangeFilter()
    remarks= filters.CharFilter(lookup_expr='icontains')
    order_status_id = filters.CharFilter(method=filter_uuid)
    status_name = filters.CharFilter(field_name='order_status_id__status_name', lookup_expr='iexact')
    created_at = DateFromToRangeFilter()
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
        model = PurchaseOrders
        #do not change "order_no",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['order_no','order_date','vendor_id','vendor','purchase_type_id','tax', 'tax_amount','total_amount','remarks','order_status_id','status_name','created_at','period_name','s','sort','page','limit']

class PurchaseInvoiceOrdersFilter(filters.FilterSet):
    vendor_id = filters.CharFilter(method=filter_uuid)
    vendor = filters.CharFilter(field_name='vendor_id__name', lookup_expr='icontains')
    purchase_type_id = filters.CharFilter(method=filter_uuid)
    purchase_type = filters.CharFilter(field_name='purchase_type_id__name', lookup_expr='icontains')
    invoice_date = filters.DateFilter()
    invoice_no = filters.CharFilter(lookup_expr='icontains')
    supplier_invoice_no= filters.CharFilter(lookup_expr='icontains')
    tax = filters.ChoiceFilter(choices=PurchaseOrders.TAX_CHOICES)
    tax_amount = filters.RangeFilter()
    total_amount = filters.RangeFilter()
    advance_amount = filters.RangeFilter()
    remarks= filters.CharFilter(lookup_expr='icontains')
    order_status_id = filters.CharFilter(method=filter_uuid)
    status_name = filters.CharFilter(field_name='order_status_id__status_name', lookup_expr='iexact')
    created_at = DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    # Landed Cost Report – Total cost including taxes, shipping, filter fields
    vendor_name = filters.CharFilter(field_name='vendor_name', lookup_expr='icontains')
    due_date = DateFromToRangeFilter()
    cess_amount = DateFromToRangeFilter()
    transport_charges = DateFromToRangeFilter()
    dis_amt = DateFromToRangeFilter()
    round_off = DateFromToRangeFilter()
    landed_cost = filters.RangeFilter(field_name='landed_cost') 

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
        model = PurchaseInvoiceOrders
        #do not change "invoice_no",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['invoice_no','invoice_date','supplier_invoice_no','vendor_id','vendor','purchase_type_id','purchase_type','tax', 'tax_amount','total_amount','advance_amount','remarks','order_status_id','status_name','created_at','period_name','vendor_name','landed_cost','s','sort','page','limit']

class PurchaseReturnOrdersFilter(filters.FilterSet):
    vendor_id = filters.CharFilter(method=filter_uuid)
    vendor = filters.CharFilter(field_name='vendor_id__name', lookup_expr='icontains')
    purchase_type_id = filters.CharFilter(method=filter_uuid)
    purchase_type = filters.CharFilter(field_name='purchase_type_id__name', lookup_expr='icontains')
    return_no = filters.CharFilter(lookup_expr='icontains')
    due_date = filters.DateFilter()
    return_reason = filters.CharFilter(field_name='return_reason', lookup_expr='icontains')
    tax = filters.ChoiceFilter(choices=PurchaseOrders.TAX_CHOICES)
    tax_amount = filters.RangeFilter()
    total_amount = filters.RangeFilter()
    remarks= filters.CharFilter(lookup_expr='icontains')
    order_status_id = filters.CharFilter(method=filter_uuid)
    status_name = filters.CharFilter(field_name='order_status_id__status_name', lookup_expr='iexact')
    created_at = DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    
  # New fields added based on the `PurchaseReturnOrders` model
    return_date = filters.DateFilter()
    ref_no = filters.CharFilter(lookup_expr='icontains')  
    ref_date = filters.DateFilter()  
    payment_term_id = filters.CharFilter(method=filter_uuid)  
    email = filters.CharFilter(lookup_expr='icontains')  
    item_value = filters.RangeFilter()  
    discount = filters.RangeFilter() 
    dis_amt = filters.RangeFilter()  
    taxable = filters.RangeFilter() 
    cess_amount = filters.RangeFilter()  
    transport_charges = filters.RangeFilter()  
    round_off = filters.RangeFilter() 
    shipping_address = filters.CharFilter(lookup_expr='icontains')  
    billing_address = filters.CharFilter(lookup_expr='icontains')  

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
        model = PurchaseReturnOrders
        #do not change "return_no",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        # fields =['return_no','due_date','vendor_id','vendor','purchase_type_id','purchase_type','order_status_id','status_name','return_reason','tax', 'tax_amount','total_amount','remarks','created_at','period_name','s','sort','page','limit']
        fields = ['return_no', 'due_date', 'vendor_id', 'vendor', 'purchase_type_id', 'purchase_type','order_status_id', 'status_name', 'return_reason', 'tax', 'tax_amount', 'total_amount','remarks', 'created_at', 'period_name', 's', 'sort', 'page', 'limit','ref_no', 'ref_date', 'payment_term_id', 'email', 'item_value', 'discount', 'dis_amt','taxable', 'cess_amount', 'transport_charges', 'round_off', 'shipping_address', 'billing_address']


class PurchasesbyVendorReportFilter(filters.FilterSet):
    vendor = filters.CharFilter(field_name='vendor', lookup_expr='icontains') 
    total_purchases = filters.RangeFilter(field_name='total_purchases') 
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
        fields = ['vendor', 'total_purchases', 's', 'sort', 'page', 'limit']

class PurchaseOrderItemsFilter(filters.FilterSet):
    purchase_order_item_id = filters.CharFilter(method=filter_uuid)
    purchase_order_id = filters.CharFilter(method=filter_uuid)
    product_id = filters.CharFilter(method=filter_uuid)
    product = filters.CharFilter(field_name='product_id__name', lookup_expr='icontains')
    unit_options_id = filters.CharFilter(method=filter_uuid)
    size_id = filters.CharFilter(method=filter_uuid)
    size_name = filters.CharFilter(field_name='size_id__size_name', lookup_expr='icontains')
    color_id = filters.CharFilter(method=filter_uuid)
    color_name = filters.CharFilter(field_name='color_id__color_name', lookup_expr='icontains')
    print_name = filters.CharFilter(lookup_expr='icontains')
    quantity = filters.RangeFilter()
    total_boxes = filters.RangeFilter()
    rate = filters.RangeFilter()
    amount = filters.RangeFilter()
    tax = filters.RangeFilter()
    remarks = filters.CharFilter(lookup_expr='icontains')
    discount = filters.RangeFilter()
    created_at = filters.DateFromToRangeFilter()
    
    # Additional fields from the Purchase Price Variance Report
    vendor_name = filters.CharFilter(field_name='purchase_order_id__vendor_id__name', lookup_expr='icontains')
    order_date = filters.DateFromToRangeFilter(field_name='purchase_order_id__order_date')
    min_price = filters.RangeFilter()
    max_price = filters.RangeFilter()
    avg_price = filters.RangeFilter()
    
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
        model = PurchaseorderItems
        fields = ['purchase_order_item_id', 'purchase_order_id', 'product_id', 'product','unit_options_id', 'size_id', 'size_name', 'color_id', 'color_name','print_name', 'quantity', 'total_boxes', 'rate', 'amount', 'tax', 'remarks', 'discount', 'created_at', 'vendor_name', 'order_date','min_price','max_price','avg_price','s', 'sort', 'page', 'limit']


class OutstandingPurchaseFilter(filters.FilterSet):
    vendor_name = filters.CharFilter(field_name='vendor_name', lookup_expr='icontains')  
    invoice_num = filters.CharFilter(field_name='invoice_num', lookup_expr='icontains')  
    invoice_dates = filters.DateFilter(field_name='invoice_dates') 
    due_dates = filters.DateFilter(field_name='due_dates')  
    total_amounts = filters.RangeFilter(field_name='total_amounts')  
    advance_payments = filters.RangeFilter(field_name='advance_payments')  
    outstanding_amount = filters.RangeFilter(field_name='outstanding_amount')  
    payment_status = filters.ChoiceFilter( field_name='payment_status')  
    created_at = DateFromToRangeFilter()
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
        model = PurchaseInvoiceOrders
        fields = ['vendor_name', 'invoice_num', 'invoice_dates', 'due_dates', 'total_amounts','advance_payments', 'outstanding_amount', 'payment_status','created_at', 's', 'sort', 'page', 'limit']


class PurchasesByVendorReportFilter(filters.FilterSet):
    vendor = filters.CharFilter(field_name='vendor', lookup_expr='icontains')
    total_purchase = filters.RangeFilter()
    order_count = filters.RangeFilter()
    created_at = DateFromToRangeFilter()
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
        model = PurchaseInvoiceOrders  # Base model for reference.
        # Although the queryset is aggregated, these fields are used for filtering.
        fields = ['vendor', 'total_purchase', 'order_count','s', 'sort', 'page', 'limit']

class StockReplenishmentReportFilter(filters.FilterSet):
    """Filter for Stock Replenishment Report"""
    name = filters.CharFilter(lookup_expr='icontains')
    current_stock = filters.RangeFilter()
    minimum_stock = filters.RangeFilter()
    reorder_quantity = filters.RangeFilter()
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    
    def filter_by_search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)
    
    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)
    
    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)
    
    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = Products
        fields = ['name', 'current_stock', 'minimum_stock', 'reorder_quantity', 's', 'sort', 'page', 'limit']
