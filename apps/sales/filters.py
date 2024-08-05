from django_filters import rest_framework as filters
from .models import SaleOrder
# from .models import SaleOrder,Invoices,PaymentTransactions,OrderItems,Shipments,SalesPriceList,SaleOrderReturns
from config.utils_methods import filter_uuid

class SaleOrderFilter(filters.FilterSet):
    # order_date = filters.DateFromToRangeFilter()
    # delivery_date = filters.DateFromToRangeFilter()
    # created_at = filters.DateFromToRangeFilter()
    # order_no = filters.CharFilter(lookup_expr='icontains')
    customer_id = filters.CharFilter(method=filter_uuid)
    # order_id = filters.CharFilter(method=filter_uuid)
    # remarks = filters.CharFilter(lookup_expr='icontains')
    # customer_name = filters.CharFilter(field_name='customer_id__name', lookup_expr='icontains')
    # sale_type_id = filters.CharFilter(method=filter_uuid)
    # sales_type_name = filters.CharFilter(field_name='sale_type_id__name', lookup_expr='icontains')
    # item_value = filters.RangeFilter()
    # advance_amount = filters.RangeFilter()
    # doc_amount = filters.RangeFilter()

    class Meta:
        model = SaleOrder
        fields =[]

# class InvoicesFilter(filters.FilterSet):
#     invoice_date = filters.DateFilter()            
#     due_date = filters.DateFromToRangeFilter()     
#     status = filters.CharFilter(lookup_expr='icontains')
#     total_amount = filters.RangeFilter()          
#     sale_type_id = filters.NumberFilter()
#     sales_type_name = filters.CharFilter(field_name='sale_type_id__name', lookup_expr='icontains')
#     warehouse_id = filters.NumberFilter()
#     warehouse_name = filters.CharFilter(field_name ='warehouse_id__name', lookup_expr='icontains' )

#     class Meta:
#         model = Invoices
#         fields = ['invoice_date', 'due_date', 'status', 'total_amount']

# class PaymentTransactionsFilter(filters.FilterSet):
#     payment_date = filters.RangeFilter()
#     payment_status =filters.CharFilter(lookup_expr='icontains')
#     amount = filters.RangeFilter()

#     class Meta:
#         model = PaymentTransactions
#         fields = ['payment_date', 'payment_status', 'amount']

# class OrderItemsFilter(filters.FilterSet):
#     order_id = filters.CharFilter(method=filter_uuid)
#     product_id = filters.CharFilter(method=filter_uuid)
#     product_name = filters.CharFilter(field_name='product_id__name',lookup_expr='icontains')
#     amount = filters.RangeFilter()
#     rate= filters.RangeFilter()
   

#     class Meta:
#         model = OrderItems
#         fields = ['order_id', 'product_id', 'amount','rate']

# class ShipmentsFilter(filters.FilterSet):
#     shipping_date = filters.DateFilter()
#     order_id = filters.CharFilter(method=filter_uuid)
#     shipping_tracking_no = filters.CharFilter(field_name='shipping_tracking_no', lookup_expr='icontains')

#     class Meta:
#         model = Shipments
#         fields = ['shipping_date', 'order_id','shipping_tracking_no']

# class SalesPriceListFilter(filters.FilterSet):
#     effective_From = filters.DateFilter()
#     effective_date = filters.DateFilter()
#     effective_range = filters.DateFromToRangeFilter(field_name='effective_From')
#     customer_category_id = filters.NumberFilter()
#     customer_category_name = filters.CharFilter(field_name='customer_category_id__name',lookup_expr='icontains')
#     brand_id = filters.CharFilter(method=filter_uuid)
#     brand_name = filters.CharFilter(field_name='brand_id__name',lookup_expr='icontains')
#     # product_group_id = filters.NumberFilter(field_name='group_id__id')

#     class Meta:
#         model = SalesPriceList
#         fields = ['effective_From', 'effective_date','effective_range','customer_category_id','customer_category_name','brand_id']

# class SaleOrderReturnsFilter(filters.FilterSet):
#     sales_return_no = filters.CharFilter(lookup_expr='icontains')
#     due_date = filters.DateFilter()
#     sale_id = filters.CharFilter(method=filter_uuid)
#     class Meta:
#         model = SaleOrderReturns
#         fields = ['sales_return_no', 'due_date','sale_id']