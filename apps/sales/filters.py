from django_filters import rest_framework as filters
from .models import QuickPacks, SaleCreditNotes, SaleDebitNotes, SaleOrder, SaleInvoiceOrders, SaleOrderItems, SaleReceipt, SaleReturnOrders, Workflow
from config.utils_methods import filter_uuid
from django_filters import FilterSet, ChoiceFilter ,DateFromToRangeFilter
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
from django.db.models import Q
logger = logging.getLogger(__name__)

class SaleOrderFilter(filters.FilterSet):
    order_no = filters.CharFilter(lookup_expr='icontains')
    customer_id = filters.CharFilter(method=filter_uuid)
    customer = filters.CharFilter(field_name='customer_id__name', lookup_expr='icontains')
    # order_date = filters.DateFromToRangeFilter()
    sale_estimate = filters.RangeFilter(field_name='sale_estimate')
    flow_status_name = filters.CharFilter(field_name='flow_status_id__flow_status_name', lookup_expr='iexact')
    order_date = filters.DateFilter()
    sale_estimate = filters.RangeFilter(field_name='sale_estimate') 
    sale_type_id = filters.CharFilter(method=filter_uuid)
    sale_type = filters.CharFilter(field_name='sale_type_id__name', lookup_expr='icontains')
    order_status_id = filters.CharFilter(method=filter_uuid)
    created_at = filters.DateFromToRangeFilter()
    advance_amount = filters.RangeFilter()
    tax = filters.ChoiceFilter(field_name='tax', choices=SaleOrder.TAX_CHOICES)
    amount = filters.RangeFilter(field_name='item_value', lookup_expr='icontains')
    flow_status_name = filters.CharFilter(field_name='flow_status_id__flow_status_name', lookup_expr='iexact')
    status_name = filters.CharFilter(field_name='order_status_id__status_name', lookup_expr='iexact')
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    # New filter to fetch all child sale orders based on parent order_no
    parent_order_no = filters.CharFilter(method='filter_child_orders')
    
    # def filter_child_orders(self, queryset, name, value):
    #     """
    #     Fetch all child sale orders where order_no starts with the parent order number.
    #     Example: If parent_order_no = 'SO-2501-00002', fetch 'SO-2501-00002-01', 'SO-2501-00002-02', etc.
    #     """
    #     if value:
    #         return queryset.filter(order_no=value) | (order_no__startswith=f"{value}-")  # Correct filtering
    #     return queryset
    
    def filter_child_orders(self, queryset, name, value):
        """
        Fetch all child sale orders where order_no starts with the parent order number,
        and also include the parent order itself.
        """
        return queryset.filter(Q(order_no=value) | Q(order_no__startswith=f"{value}-"))  # ✅ Fetch parent + child orders



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
        fields = ['order_no','order_date','sale_estimate','flow_status_name','customer_id','customer','sale_type_id','sale_type','order_status_id','flow_status_name','status_name','created_at','advance_amount','tax','amount','period_name','s','sort','page','limit']

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
 
 
  