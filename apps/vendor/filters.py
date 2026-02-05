from django_filters import rest_framework as filters
from apps.finance.models import JournalEntryLines, PaymentTransaction
from django.db.models import Q
from apps.sales.models import PaymentTransactions
from apps.vendor.models import Vendor, VendorAgent, VendorCategory, VendorPaymentTerms
from config.utils_methods import filter_uuid
from django_filters import FilterSet, ChoiceFilter, DateFromToRangeFilter
from django_filters import rest_framework as filters
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_simple_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
logger = logging.getLogger(__name__)

class VendorFilter(FilterSet): #verified
    name = filters.CharFilter(lookup_expr='icontains')
    gst_no = filters.CharFilter(lookup_expr='icontains')
    vendor_category_id = filters.CharFilter(field_name='vendor_category_id__name', lookup_expr='icontains')
    ledger_account_id = filters.CharFilter(method=filter_uuid)
    ledger_account = filters.CharFilter(field_name='ledger_account_id__name', lookup_expr='icontains')
    created_at = filters.DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    # Fields from VendorAddress
    email = filters.CharFilter(field_name='vendoraddress__email', lookup_expr='icontains', label="Email")
    phone = filters.CharFilter(field_name='vendoraddress__phone', lookup_expr='icontains', label="Phone")
    city_id = filters.CharFilter(field_name='vendoraddress__city_id__city_name', lookup_expr='icontains', label="City")
    is_deleted = filters.BooleanFilter()
    search = filters.CharFilter(method='filter_by_search_dropdown', label="Simple Search")
    
    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value).distinct()

    def filter_by_search_dropdown(self, queryset, name, value):
        """Simple search for dropdown - searches name, print_name, code"""
        return filter_by_simple_search(queryset, value, ['name', 'print_name', 'code'])

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = Vendor
        #do not change "name",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields = ['name','gst_no','vendor_category_id','ledger_account_id','ledger_account', 'is_deleted','created_at', 'city_id','email', 'phone','period_name','s','search','sort','page','limit']

class VendorAgentFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    code = filters.CharFilter(lookup_expr='icontains')
    commission_rate = filters.NumberFilter()
    rate_on = filters.ChoiceFilter(choices=VendorAgent.RATE_ON_CHOICES)
    amount_type = filters.ChoiceFilter(choices=VendorAgent.AMOUNT_TYPE_CHOICES)
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
        model = VendorAgent 
        fields = ['name','code','commission_rate','rate_on','amount_type','created_at','s', 'sort','page','limit']

class VendorCategoryFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
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
        model = VendorCategory 
        fields = ['name','code','created_at','s', 'sort','page','limit']

class VendorPaymentTermsFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    code = filters.CharFilter(lookup_expr='icontains')
    fixed_days = filters.NumberFilter()
    no_of_fixed_days = filters.NumberFilter()
    payment_cycle = filters.CharFilter(lookup_expr='icontains')  
    run_on = filters.CharFilter(lookup_expr='icontains')
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
        model = VendorPaymentTerms 
        fields = ['name','code','fixed_days','no_of_fixed_days','payment_cycle','run_on','created_at','s', 'sort','page','limit']

class VendorSummaryReportFilter(filters.FilterSet):
    """
    Filter for Vendor Summary Report that shows total purchases and pending payments.
    """
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    min_total_purchases = filters.NumberFilter(field_name='total_purchases', lookup_expr='gte')
    max_total_purchases = filters.NumberFilter(field_name='total_purchases', lookup_expr='lte')
    min_total_pending = filters.NumberFilter(field_name='total_pending', lookup_expr='gte')
    max_total_pending = filters.NumberFilter(field_name='total_pending', lookup_expr='lte')
    purchase_date_after = filters.DateFilter(field_name='last_purchase_date', lookup_expr='gte')
    purchase_date_before = filters.DateFilter(field_name='last_purchase_date', lookup_expr='lte')
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
        model = Vendor
        fields = ['name', 'min_total_purchases', 'max_total_purchases', 
                 'min_total_pending', 'max_total_pending', 
                 'purchase_date_after', 'purchase_date_before',
                 's', 'sort', 'page', 'limit']

class VendorLedgerReportFilter(filters.FilterSet):
    """
    Filter for Vendor Ledger Report with date range and transaction type filtering options.
    """
    vendor_id = filters.CharFilter(method=filter_uuid)
    start_date = filters.DateFilter(field_name='journal_entry_id__entry_date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='journal_entry_id__entry_date', lookup_expr='lte')
    reference_number = filters.CharFilter(field_name='journal_entry_id__reference', lookup_expr='icontains')
    transaction_type = filters.CharFilter(method='filter_transaction_type')
    min_amount = filters.NumberFilter(method='filter_min_amount')
    max_amount = filters.NumberFilter(method='filter_max_amount')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    def filter_transaction_type(self, queryset, name, value):
        """Filter transactions by type based on reference number patterns"""
        if value.lower() == 'purchase order':
            return queryset.filter(journal_entry_id__reference__startswith='PO-')
        elif value.lower() == 'purchase invoice':
            return queryset.filter(Q(journal_entry_id__reference__startswith='PI-') | 
                                   Q(journal_entry_id__reference__startswith='PINV-'))
        elif value.lower() == 'purchase return':
            return queryset.filter(journal_entry_id__reference__startswith='PR-')
        elif value.lower() == 'credit note':
            return queryset.filter(journal_entry_id__reference__startswith='CN-')
        elif value.lower() == 'debit note':
            return queryset.filter(journal_entry_id__reference__startswith='DN-')
        elif value.lower() == 'payment':
            return queryset.filter(journal_entry_id__reference__startswith='PMT-')
        return queryset

    def filter_min_amount(self, queryset, name, value):
        """Filter transactions with amount greater than or equal to the specified value"""
        if value:
            # Using Q objects to check both debit and credit
            return queryset.filter(Q(debit__gte=value) | Q(credit__gte=value))
        return queryset

    def filter_max_amount(self, queryset, name, value):
        """Filter transactions with amount less than or equal to the specified value"""
        if value:
            return queryset.filter(Q(debit__lte=value) | Q(credit__lte=value))
        return queryset

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)

    class Meta:
        model = JournalEntryLines
        fields = ['vendor_id', 'start_date', 'end_date', 'reference_number', 
                'transaction_type', 'min_amount', 'max_amount', 's', 'sort', 'page', 'limit']

class VendorOutstandingReportFilter(filters.FilterSet):
    """
    Filter for Vendor Outstanding Report showing pending dues to vendors.
    """
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    min_total_pending = filters.NumberFilter(field_name='total_pending', lookup_expr='gte')
    max_total_pending = filters.NumberFilter(field_name='total_pending', lookup_expr='lte')
    min_due_days = filters.NumberFilter(method='filter_by_min_due_days')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    
    def filter_by_min_due_days(self, queryset, name, value):
        """Filter vendors with invoices outstanding for at least the specified number of days"""
        if value:
            from django.utils import timezone
            from datetime import timedelta
            cutoff_date = timezone.now().date() - timedelta(days=int(value))
            return queryset.filter(purchaseinvoiceorders__due_date__lte=cutoff_date)
        return queryset
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = Vendor
        fields = ['name', 'min_total_pending', 'max_total_pending', 'min_due_days',
                 's', 'sort', 'page', 'limit']

class VendorPerformanceReportFilter(filters.FilterSet):
    """
    Filter for Vendor Performance Report analyzing delivery and service quality.
    """
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    min_on_time_percentage = filters.NumberFilter(field_name='on_time_percentage', lookup_expr='gte')
    max_on_time_percentage = filters.NumberFilter(field_name='on_time_percentage', lookup_expr='lte')
    min_quality_rating = filters.NumberFilter(field_name='quality_rating', lookup_expr='gte')
    max_quality_rating = filters.NumberFilter(field_name='quality_rating', lookup_expr='lte')
    min_total_orders = filters.NumberFilter(field_name='total_orders', lookup_expr='gte')
    order_date_after = filters.DateFilter(field_name='last_order_date', lookup_expr='gte')
    order_date_before = filters.DateFilter(field_name='last_order_date', lookup_expr='lte')
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
        model = Vendor
        fields = ['name', 'min_on_time_percentage', 'max_on_time_percentage',
                 'min_quality_rating', 'max_quality_rating', 'min_total_orders',
                 'order_date_after', 'order_date_before', 's', 'sort', 'page', 'limit']

class VendorPaymentReportFilter(filters.FilterSet):
    """
    Filter for Vendor Payment Report showing payments made to vendors.
    """
    invoice_id = filters.CharFilter(lookup_expr='icontains')
    payment_date_after = filters.DateFilter(field_name='payment_date', lookup_expr='gte')
    payment_date_before = filters.DateFilter(field_name='payment_date', lookup_expr='lte')
    payment_method = filters.CharFilter(lookup_expr='icontains')
    payment_status = filters.CharFilter(lookup_expr='iexact')
    min_amount = filters.NumberFilter(field_name='amount', lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name='amount', lookup_expr='lte')
    reference_number = filters.CharFilter(lookup_expr='icontains')
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
        model = PaymentTransaction
        fields = ['invoice_id', 'payment_date_after', 'payment_date_before',
                 'payment_method', 'payment_status', 'min_amount', 'max_amount', 
                 'reference_number', 's', 'sort', 'page', 'limit']
