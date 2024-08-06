from django_filters import rest_framework as filters
from .models import SaleOrder, SaleInvoiceOrders
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

#==========================common-utility-function===================================

import datetime
from django.utils import timezone
from datetime import date, datetime, timedelta, timezone
from django_filters import FilterSet, ChoiceFilter, DateFromToRangeFilter, DateFilter
# from dateutil.relativedelta import relativedelta

PERIOD_NAME_CHOICES = [
    ('today', 'Today'),
    ('yesterday', 'Yesterday'),
    ('last_week', 'LastWeek'),
    ('current_month', 'CurrentMonth'),
    ('last_month', 'LastMonth'),
    ('last_six_months', 'LastSixMonths'),
    ('current_quarter', 'CurrentQuarter'),
    ('year_to_date', 'YearToDate'),
    ('last_year', 'LastYear'),
]

class SaleInvoiceOrdersFilter(FilterSet):
    period_name = ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    created_at = DateFromToRangeFilter()

    def filter_by_period_name(self, queryset, name, value):
        today = timezone.now().date()
        start_date = None
        end_date = today

        # Check if custom from_date and to_date are provided in the URL
        from_date = self.data.get('created_at_after')
        to_date = self.data.get('created_at_before')

        if from_date and to_date:
            try:
                start_date = datetime.datetime.strptime(from_date, '%Y-%m-%d').date()
                end_date = datetime.datetime.strptime(to_date, '%Y-%m-%d').date()
            except ValueError:
                # Handle invalid date format
                print(f"Invalid date format: from_date={from_date}, to_date={to_date}")
                return queryset.none()
        else:
            # Determine the date range based on the period_name selected
            if value == 'today':
                start_date = end_date
            elif value == 'yesterday':
                start_date = end_date - datetime.timedelta(days=1)
                end_date = start_date
            elif value == 'last_week':
                start_date = today - datetime.timedelta(days=today.weekday() + 7)
                end_date = start_date + datetime.timedelta(days=6)
            elif value == 'current_month':
                start_date = today.replace(day=1)
            elif value == 'last_month':
                first_day_of_current_month = today.replace(day=1)
                last_day_of_last_month = first_day_of_current_month - datetime.timedelta(days=1)
                start_date = last_day_of_last_month.replace(day=1)
                end_date = last_day_of_last_month
            elif value == 'last_six_months':
                start_date = today - datetime.timedelta(days=180)
                # six_months_ago = today - relativedelta(months=6)
                # start_date = six_months_ago.replace(day=1)
                # end_date = today
            elif value == 'current_quarter':
                quarter = (today.month - 1) // 3 + 1
                start_date = today.replace(month=(quarter - 1) * 3 + 1, day=1)
            elif value == 'year_to_date':
                # start_date = today.replace(month=1, day=1)
                start_date = today.replace(month=4, day=1)
            elif value == 'last_year':
                # start_date = today.replace(month=1, day=1) - datetime.timedelta(days=365)
                # end_date = today.replace(month=12, day=31)
                start_date = today.replace(month=4, day=1) - datetime.timedelta(days=365)
                end_date = today.replace(month=3, day=31)

  
        # Convert start_date and end_date to datetime objects with min and max times
        if start_date:
            start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
        if end_date:
            end_datetime = datetime.datetime.combine(end_date, datetime.time.max)

        # Apply filters
        if start_datetime and end_datetime:
            queryset = queryset.filter(created_at__gte=start_datetime, created_at__lte=end_datetime)

        return queryset
    
    class Meta:
        model = SaleInvoiceOrders
        fields =[]