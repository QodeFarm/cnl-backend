# from django.forms import DecimalField, IntegerField
from django_filters import rest_framework as filters
from .models import PaymentTransactions, QuickPacks, SaleCreditNotes, SaleDebitNotes, SaleOrder, SaleInvoiceOrders, SaleOrderItems, SaleReceipt, SaleReturnOrders, Workflow
from config.utils_methods import filter_uuid
from django_filters import FilterSet, ChoiceFilter ,DateFromToRangeFilter
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
from django.db.models import Q, Sum, F, Count, Max, OuterRef, Subquery, DecimalField, IntegerField
from django.db.models.functions import Coalesce
from rest_framework.response import Response
from django_filters import BaseInFilter, CharFilter
from django_filters import rest_framework as filters
from django_filters.filters import DateFilter, CharFilter, RangeFilter, NumberFilter

import django_filters

class CharInFilter(BaseInFilter, CharFilter):
    pass

logger = logging.getLogger(__name__)
class SaleOrderFilter(filters.FilterSet):
    order_no = filters.CharFilter(lookup_expr='icontains')
    customer_id = filters.CharFilter(method=filter_uuid)
    customer = filters.CharFilter(field_name='customer_id__name', lookup_expr='icontains')
    # order_date = filters.DateFromToRangeFilter()
    sale_estimate = filters.RangeFilter(field_name='sale_estimate')
    order_date = filters.DateFilter()
    sale_estimate = filters.RangeFilter(field_name='sale_estimate') 
    sale_type_id = filters.CharFilter(method=filter_uuid)
    sale_type = filters.CharFilter(field_name='sale_type_id__name', lookup_expr='icontains')
    order_status_id = filters.CharFilter(method=filter_uuid)
    created_at = filters.DateFromToRangeFilter()
    advance_amount = filters.RangeFilter()
    tax = filters.ChoiceFilter(field_name='tax', choices=SaleOrder.TAX_CHOICES)
    amount = filters.RangeFilter(field_name='item_value', lookup_expr='icontains')
    flow_status_name = filters.CharFilter(method='filter_by_flow_status_name')
    status_name = filters.CharFilter(field_name='order_status_id__status_name', lookup_expr='iexact')
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    # New filter to fetch all child sale orders based on parent order_no
    parent_order_no = filters.CharFilter(method='filter_child_orders')

    
    def filter_by_flow_status_name(self, queryset, name, value):
        values = [v.strip() for v in value.split(',')]
        q_filter = Q()
        for val in values:
            q_filter |= Q(flow_status_id__flow_status_name__iexact=val)
        return queryset.filter(q_filter)
    
    def filter_child_orders(self, queryset, name, value):
        """
        Fetch all child sale orders where order_no starts with the parent order number,
        and also include the parent order itself.
        """
        return queryset.filter(Q(order_no=value) | Q(order_no__startswith=f"{value}-"))  #  Fetch parent + child orders



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
        model = SaleOrder 
        #do not change "order_no",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields = ['order_no','order_date','sale_estimate','flow_status_name','customer_id','customer','sale_type_id','sale_type','order_status_id', 'status_name','created_at','advance_amount','tax','amount','period_name','s','sort','page','limit']

class SaleInvoiceOrdersFilter(filters.FilterSet):
    customer_id = filters.CharFilter(method=filter_uuid)
    customer = filters.CharFilter(field_name='customer_id__name', lookup_expr='icontains')
    sale_order_id = filters.CharFilter(method=filter_uuid)
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
        model = SaleInvoiceOrders
        #do not change "invoice_no",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['invoice_no','customer_id','customer','sale_order_id','invoice_date','total_amount','tax_amount','advance_amount','remarks','order_status_id','status_name', 'created_at','period_name','s','sort','page','limit']

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
        model = SaleReturnOrders
        #do not change "return_no",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['return_no','return_date','due_date','customer_id','customer','tax', 'tax_amount','total_amount','return_reason','remarks','order_status_id', 'status_name', 'created_at','period_name','s','sort','page','limit']
        
class SaleOrdersItemsilter(filters.FilterSet):
    sale_order_id = filters.CharFilter(method=filter_uuid)
    
    class Meta:
        model = SaleOrderItems
        fields =['sale_order_id']

class QuickPacksFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    lot_qty = filters.NumberFilter(field_name='lot_qty', lookup_expr='exact')
    description = filters.CharFilter(lookup_expr='icontains')
    active = filters.ChoiceFilter(field_name='active',choices=[('N', 'No'),('Y', 'Yes')])
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
        model = QuickPacks
        #do not change "name",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['name','lot_qty','description','active','created_at','period_name','s','sort','page','limit']

class SaleReceiptFilter(filters.FilterSet):
    sale_invoice_id = filters.CharFilter(field_name='sale_invoice_id__customer_id__name', lookup_expr='icontains')
    sale_invoice = filters.CharFilter(field_name='sale_invoice_id__invoice_no', lookup_expr='icontains')
    # receipt_name = filters.CharFilter(lookup_expr='icontains')
    # description = filters.CharFilter(lookup_expr='icontains')
    customer = filters.CharFilter(field_name='customer_id__name', lookup_expr='icontains')
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
        model = SaleReceipt
        #do not change "sale_invoice_id",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['sale_invoice_id','sale_invoice','receipt_name','description','created_at','period_name','s','sort','page','limit']

class WorkflowFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    created_at = DateFromToRangeFilter()


    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = Workflow 
        fields = ['name','created_at','s', 'sort','page','limit']



class SaleCreditNotesFilter(filters.FilterSet):
    customer_id = filters.CharFilter(method=filter_uuid)
    customer = filters.CharFilter(field_name='customer_id__name', lookup_expr='iexact')
    sale_invoice_id = filters.CharFilter(field_name='sale_invoice_id__invoice_no', lookup_expr='iexact')
    credit_note_number = filters.CharFilter(lookup_expr='icontains')
    credit_date = filters.DateFilter()
    total_amount = filters.RangeFilter()
    reason = filters.CharFilter(lookup_expr='icontains')
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
        model = SaleCreditNotes
        #do not change "return_no",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['credit_date','customer','customer_id','sale_invoice_id','credit_note_number','reason','total_amount','order_status_id','status_name', 'created_at','period_name','s','sort','page','limit']
        
class SaleDebitNotesFilter(filters.FilterSet):
    # customer_id = filters.CharFilter(method=filter_uuid)
    customer = filters.CharFilter(field_name='customer_id__name', lookup_expr='iexact')
    sale_invoice_id = filters.CharFilter(field_name='sale_invoice_id__invoice_no', lookup_expr='iexact')
    debit_note_number = filters.CharFilter(lookup_expr='icontains')
    debit_date = filters.DateFilter()
    total_amount = filters.RangeFilter()
    reason = filters.CharFilter(lookup_expr='icontains')
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
        model = SaleDebitNotes
        fields = ['debit_date','customer','sale_invoice_id','debit_note_number','reason','total_amount','order_status_id','status_name','created_at','period_name','s','sort','page', 'limit', ]
 
 
  
class OutstandingSalesReportFilter(filters.FilterSet):
    """
    Filter for Outstanding Sales Report showing pending payments from customers.
    """
    customer_id = filters.UUIDFilter(field_name='customer_id')
    customer_name = filters.CharFilter(field_name='customer_id__name', lookup_expr='icontains')
    min_total_pending = filters.NumberFilter(field_name='total_pending', lookup_expr='gte')
    max_total_pending = filters.NumberFilter(field_name='total_pending', lookup_expr='lte')
    invoice_date_after = filters.DateFilter(field_name='invoice_date', lookup_expr='gte')
    invoice_date_before = filters.DateFilter(field_name='invoice_date', lookup_expr='lte')
    
    class Meta:
        model = SaleInvoiceOrders
        fields = ['customer_id', 'customer_name', 'min_total_pending', 'max_total_pending',
                 'invoice_date_after', 'invoice_date_before']


class SalesByProductReportFilter(filters.FilterSet):
    product = filters.CharFilter(field_name='product_id__name', lookup_expr='icontains')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    total_sales = filters.RangeFilter()  #New filter for total sales amount
    total_quantity_sold = filters.RangeFilter() 


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
        model = SaleOrderItems
        fields = [  'total_sales', 's', 'sort', 'page', 'limit']  
        
class SalesByCustomerReportFilter(filters.FilterSet):
    customer = filters.CharFilter()
    total_sales = filters.RangeFilter() 
    created_at = filters.DateFromToRangeFilter()
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
        model = SaleOrder
        fields = ['customer','total_sales','created_at','s','sort','page','limit']   
        

class SalesByProductReportFilter(filters.FilterSet):
    product = filters.CharFilter(field_name="product_id__name", lookup_expr="icontains")  
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    total_sales = filters.RangeFilter()  
    created_at = filters.DateFromToRangeFilter()
    s = filters.CharFilter(method="filter_by_search", label="Search")
    sort = filters.CharFilter(method="filter_by_sort", label="Sort")
    page = filters.NumberFilter(method="filter_by_page", label="Page")
    limit = filters.NumberFilter(method="filter_by_limit", label="Limit")
    
    
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
        model = SaleOrderItems
        fields = ["product", "total_sales",'created_at','s','sort','page','limit']
                       
                       

class OutstandingSalesReportFilter(filters.FilterSet):
    customer = filters.CharFilter(field_name='customer', lookup_expr='iexact')
    total_invoice = filters.RangeFilter()
    total_paid = filters.RangeFilter()
    total_pending = filters.RangeFilter()
    created_at = filters.filters.DateFromToRangeFilter()
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
        
        model = SaleOrder  
        fields = [
            'customer', 'total_invoice', 'total_paid', 'total_pending','created_at',
            's', 'sort', 'page', 'limit'
        ]

class SalesOrderReportFilter(django_filters.FilterSet):
    order_no = CharFilter(field_name="order_no", lookup_expr="icontains")
    customer = CharFilter(field_name="customer_id__name", lookup_expr="icontains")
    order_date = DateFromToRangeFilter(field_name="order_date")
    status_name = filters.CharFilter(field_name='order_status_id__status_name', lookup_expr='iexact')
    
    sale_type = CharFilter(field_name="sale_type_id__name", lookup_expr="icontains")
    amount = NumberFilter(field_name="item_value")  # Assuming this is the total order amount
    created_at = filters.filters.DateFromToRangeFilter()
    s = CharFilter(method="filter_by_search", label="Search")
    sort = CharFilter(method="filter_by_sort", label="Sort")
    page = NumberFilter(method="filter_by_page", label="Page")
    limit = NumberFilter(method="filter_by_limit", label="Limit")

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)

    class Meta:
        model = SaleOrder
        fields = ["order_no", "customer", "order_date", "sale_type", "status_name", "amount",'created_at' ,"s", "sort", "page", "limit"]




class SalesInvoiceReportFilter(filters.FilterSet):
    invoice_no = filters.CharFilter(field_name="invoice_no", lookup_expr="icontains")
    customer = filters.CharFilter(field_name="customer_id__name", lookup_expr="icontains")
    invoice_date = filters.DateFromToRangeFilter(field_name="invoice_date")
    bill_type = filters.CharFilter(field_name="bill_type", lookup_expr="iexact")
    item_value = filters.RangeFilter(field_name="item_value")
    dis_amt = filters.RangeFilter(field_name="dis_amt")
    tax_amount = filters.RangeFilter(field_name="tax_amount")
    total_amount = filters.RangeFilter(field_name="total_amount")
    due_date = filters.DateFromToRangeFilter(field_name="due_date")
    status_name = filters.CharFilter(field_name='order_status_id', lookup_expr='iexact')
    created_at = filters.DateFromToRangeFilter(field_name="created_at")
    
    # Additional filters for search, sort, pagination
    s = filters.CharFilter(method="filter_by_search", label="Search")
    sort = filters.CharFilter(method="filter_by_sort", label="Sort")
    page = filters.NumberFilter(method="filter_by_page", label="Page")
    limit = filters.NumberFilter(method="filter_by_limit", label="Limit")

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    class Meta:
        model = ''
        fields = [
            'invoice_no', 'customer', 'invoice_date', 'bill_type', 
            'status_name', 'total_amount', 'created_at',
            's', 'sort', 'page', 'limit'
        ]
        
        
# class SalesTaxReportFilter(filters.FilterSet):
#     gst_type = filters.CharFilter(field_name='gst_type', lookup_expr='icontains')
#     total_taxable = filters.RangeFilter()
#     total_tax = filters.RangeFilter()
#     total_cess = filters.RangeFilter()
#     invoice_date = filters.DateFromToRangeFilter(field_name='invoice_date')
    
#     class Meta:
#         model = SaleInvoiceOrders
#         # Note: Since the query returns dicts (aggregated data), model isn’t used directly.
#         fields = ['gst_type', 'total_taxable', 'total_tax', 'total_cess', 'invoice_date']        
  
  

class SalesTaxByProductReportFilter(filters.FilterSet):
    product = filters.CharFilter(field_name='product', lookup_expr='icontains')
    gst_type = filters.CharFilter(field_name='gst_type', lookup_expr='icontains')
    total_sales = filters.RangeFilter()
    total_tax = filters.RangeFilter()
    invoice_date = filters.DateFromToRangeFilter(field_name='sale_invoice_id__invoice_date')

    class Meta:
        model = SaleOrderItems  # The queryset returns dicts from an annotated query.
        fields = ['product', 'gst_type', 'total_sales', 'total_tax', 'invoice_date']                  


import django_filters

class SalespersonPerformanceReportFilter(filters.FilterSet):
    salesperson = filters.CharFilter(field_name='salesperson', lookup_expr='icontains')
    total_sales = filters.RangeFilter()
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    def filter_by_search(self, queryset, name, value):
            return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)

    class Meta:
        model = None  # The queryset returns dictionaries.
        fields = ['salesperson', 'total_sales', 's', 'sort', 'page', 'limit']


class ProfitMarginReportFilter(filters.FilterSet):
    product = filters.CharFilter(field_name='product', lookup_expr='icontains')
    total_sales = filters.RangeFilter()
    profit_margin = filters.RangeFilter()
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)

    class Meta:
        model = None 
        fields = ['product', 'total_sales', 'profit_margin', 's', 'sort', 'page', 'limit']
        
        
class PaymentTransactionsReportFilter(filters.FilterSet):
    """
    Filter for Sales Payment Receipts Report showing all payment transactions
    """
    # Customer filters
    customer = filters.CharFilter(field_name='customer__name', lookup_expr='icontains')
    customer_id = filters.NumberFilter(field_name='customer__customer_id')
    
    # Receipt filters
    payment_receipt_no = filters.CharFilter(lookup_expr='icontains')
    
    
    
    # Invoice filters
    invoice_no = filters.CharFilter(field_name='sale_invoice__invoice_no', lookup_expr='icontains')
    
    # Date filters
    payment_date = filters.DateFilter(field_name='payment_date', lookup_expr='gte')
      # Payment details filters
    payment_method = filters.CharFilter(lookup_expr='icontains')
    payment_status = filters.ChoiceFilter(
        choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed')], lookup_expr='exact'
    )
    status_name = filters.CharFilter(field_name='payment_status', lookup_expr='iexact')
    
    # Amount filters
    min_amount = filters.NumberFilter(field_name='adjusted_now', lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name='adjusted_now', lookup_expr='lte')
    
    # Standard filters used across your application
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    created_at = filters.DateFromToRangeFilter(field_name='created_at')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    class Meta:
        model = PaymentTransactions
        fields = [
            'customer', 'customer_id', 'payment_receipt_no', 'invoice_no', 
            'payment_date', 'payment_method', 'payment_status', 
            'min_amount', 'max_amount', 'status_name', 'period_name', 'created_at', 's', 'sort', 'page', 'limit'
        ]        