from django_filters import rest_framework as filters
from apps.production.models import Machine, ProductionStatus, WorkOrder, BOM, BillOfMaterials, WorkOrderMachine
from config.utils_methods import filter_uuid
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
from django_filters import rest_framework as filters
from .models import MaterialIssue, MaterialReceived, StockJournal, StockSummary


class WorkOrderFilter(filters.FilterSet):
    product = filters.CharFilter(field_name='product_id__name', lookup_expr='icontains')
    product_id = filters.CharFilter(method=filter_uuid)
    size = filters.CharFilter(field_name='size_id__size_name', lookup_expr='icontains')  # Assuming 'size_name' exists in Size
    color = filters.CharFilter(field_name='color_id__color_name', lookup_expr='icontains')  # Assuming 'color_name' exists in Color
    status = filters.CharFilter(field_name='status_id__status_name', lookup_expr='icontains')
    flow_status = filters.CharFilter(field_name='sale_order_id__flow_status_id__flow_status_name', lookup_expr='iexact')
    quantity = filters.RangeFilter()
    completed_qty = filters.RangeFilter()
    # pending_qty = filters.RangeFilter()
    start_date = filters.DateFromToRangeFilter()
    end_date = filters.DateFromToRangeFilter()
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
        model = WorkOrder 
        #do not change "product",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields = ['product','size','color','status_id','quantity','completed_qty','product_id','flow_status','start_date','end_date','created_at','period_name','s','sort','page','limit']

class BOMFilter(filters.FilterSet):
    bom_id = filters.CharFilter(method=filter_uuid)
    bom = filters.CharFilter(field_name='bom_name', lookup_expr='icontains')
    product_id = filters.CharFilter(method=filter_uuid)
    product = filters.CharFilter(field_name='product_id__name', lookup_expr='icontains')
    notes = filters.CharFilter(lookup_expr='icontains', label="Notes")
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    created_at = filters.DateFromToRangeFilter()
    completed_qty = filters.RangeFilter()

#  
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
        model = BOM 
        fields = ['product','bom_id','bom','notes','product_id','s','sort','page','limit']

class MaterialFilter(filters.FilterSet):
    bom_id = filters.CharFilter(method=filter_uuid)
    bom = filters.CharFilter(field_name='bom_id__bom_name', lookup_expr='icontains')
    product_id = filters.CharFilter(method=filter_uuid)
    product = filters.CharFilter(field_name='product_id__name', lookup_expr='icontains')
    size_id = filters.CharFilter(method=filter_uuid)
    size_name = filters.CharFilter(field_name='size_id__size_name', lookup_expr='icontains')
    color_id = filters.CharFilter(method=filter_uuid)
    color_name = filters.CharFilter(field_name='color_id__color_name', lookup_expr='icontains')      
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
        model = BillOfMaterials
        fields = ['product','bom_id','bom','product_id', 'product', 'color_id', 'color_name', 'size_id', 'size_name', 's', 'sort','page','limit']


class ProductionStatusFilter(filters.FilterSet):
    status_id = filters.CharFilter(method=filter_uuid)
    status_name = filters.CharFilter(lookup_expr='icontains')
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
        model = ProductionStatus 
        fields = ['status_id','status_name','created_at','s', 'sort','page','limit']


class MachineFilter(filters.FilterSet):
    machine_id = filters.CharFilter(method=filter_uuid)
    machine_name = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    status = filters.ChoiceFilter(field_name='status',choices=[('Operational', 'Operational'),('Out of Service', 'Out of Service'),('Under Maintenance', 'Under Maintenance')])
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
        model = Machine 
        fields = ['machine_id','machine_name','description','status','created_at','s', 'sort','page','limit']


# class StockJournalFilter(filters.FilterSet):
#     product = filters.CharFilter(field_name='product_id__name', lookup_expr='icontains')
#     product_id = filters.CharFilter(method=filter_uuid)
#     size = filters.CharFilter(field_name='size_id__size_name', lookup_expr='icontains')
#     color = filters.CharFilter(field_name='color_id__color_name', lookup_expr='icontains')
#     status = filters.CharFilter(field_name='status_id__status_name', lookup_expr='icontains')
#     bom_name = filters.CharFilter(field_name='bom_id__bom_name', lookup_expr='icontains')
#     quantity = filters.RangeFilter()
#     completed_qty = filters.RangeFilter()
#     created_at = filters.DateFromToRangeFilter()
#     period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
#     s = filters.CharFilter(method='filter_by_search', label="Search")
#     sort = filters.CharFilter(method='filter_by_sort', label="Sort")
#     page = filters.NumberFilter(method='filter_by_page', label="Page")
#     limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

#     def filter_by_period_name(self, queryset, name, value):
#         return filter_by_period_name(self, queryset, self.data, value)

#     def filter_by_search(self, queryset, name, value):
#         return filter_by_search(queryset, self, value)

#     def filter_by_sort(self, queryset, name, value):
#         return filter_by_sort(self, queryset, value)

#     def filter_by_page(self, queryset, name, value):
#         return filter_by_page(self, queryset, value)

#     def filter_by_limit(self, queryset, name, value):
#         return filter_by_limit(self, queryset, value)
    
#     class Meta:
#         model = WorkOrder
#         fields = ['product', 'size', 'color', 'status', 'quantity', 'completed_qty', 'product_id', 'created_at', 'period_name', 'bom_name', 's', 'sort', 'page', 'limit']

class BillOfMaterialsFilter(filters.FilterSet):
    bom = filters.CharFilter(field_name='bom_name', lookup_expr='icontains')
    code = filters.CharFilter(field_name='product_id__code', lookup_expr='icontains')
    unit_name = filters.CharFilter(field_name='product_id__unit_options_id__unit_name' ,  lookup_expr='icontains') 
    sales_rate = filters.RangeFilter(field_name='product_id__sales_rate') 
    dis_amount = filters.RangeFilter(field_name='product_id__dis_amount') 
    mrp = filters.RangeFilter(field_name='product_id__mrp')
    material_id = filters.CharFilter(method=filter_uuid)
    reference_id = filters.CharFilter(lookup_expr='icontains')
    product_id = filters.CharFilter(method=filter_uuid)
    product = filters.CharFilter(field_name='product_id__name', lookup_expr='icontains')
    size_id = filters.CharFilter(method=filter_uuid)
    size_name = filters.CharFilter(field_name='size_id__size_name', lookup_expr='icontains')
    color_id = filters.CharFilter(method=filter_uuid)
    color_name = filters.CharFilter(field_name='color_id__color_name', lookup_expr='icontains')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    created_at = filters.DateFromToRangeFilter()


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
        model = BillOfMaterials
        fields = ['material_id', 'reference_id', 'product_id', 'product','size_id', 'size_name', 'color_id', 'color_name','s', 'sort', 'page', 'limit']


class ProductionCostReportFilter(filters.FilterSet):
    product = filters.CharFilter(field_name='product_id__name', lookup_expr='icontains')
    total_quantity = filters.RangeFilter(field_name='quantity')
    total_cost = filters.RangeFilter(field_name='total_cost')
    created_at = filters.DateFromToRangeFilter(field_name='created_at')
    
    # Additional custom filters
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
        model = BillOfMaterials
        fields = ['product', 'total_quantity', 'total_cost', 'created_at', 's', 'sort', 'page', 'limit']
        

class ProductionSummaryReportFilter(filters.FilterSet):
    product = filters.CharFilter(field_name='product_id__name', lookup_expr='icontains')
    start_date = filters.DateFromToRangeFilter(field_name='start_date')
    end_date = filters.DateFromToRangeFilter(field_name='end_date')
    completion_percentage = filters.RangeFilter(field_name='completion_percentage')
    created_at = filters.DateFromToRangeFilter() 
    status_name = filters.CharFilter(field_name='status_id__status_name', lookup_expr='icontains')
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
        model = WorkOrder
        fields = ['product', 'start_date','status_name' ,'end_date', 'completion_percentage','created_at' ,'s', 'sort', 'page', 'limit']
        
class BOMReportFilter(filters.FilterSet):
    bom_name = filters.CharFilter(field_name='bom_name', lookup_expr='icontains')
    product = filters.CharFilter(field_name='product_id__name', lookup_expr='icontains')
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
        model = BOM
        fields = ['bom_name', 'product', 'created_at', 's', 'sort', 'page', 'limit']
        
class MachineUtilizationReportFilter(filters.FilterSet):
    machine_name = filters.CharFilter(field_name='machine_name', lookup_expr='icontains')
    total_usage_hours = filters.RangeFilter(field_name='total_usage_hours')
    total_work_orders = filters.RangeFilter(field_name='total_work_orders')
    avg_usage_per_work_order = filters.RangeFilter(field_name='avg_usage_per_work_order')
    total_work_time = filters.RangeFilter(field_name='total_work_time')
    downtime_hours = filters.RangeFilter(field_name='downtime_hours')
 # Instead of 'created_at', use the WorkOrder's start_date and end_date.
    start_date_after = filters.DateFilter(field_name='work_order_id__start_date', lookup_expr='gte')
    start_date_before = filters.DateFilter(field_name='work_order_id__start_date', lookup_expr='lte')
    end_date_after = filters.DateFilter(field_name='work_order_id__end_date', lookup_expr='gte')
    end_date_before = filters.DateFilter(field_name='work_order_id__end_date', lookup_expr='lte')

    # Additional filters for custom search, sort, page, and limit.
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
            model = WorkOrderMachine
            fields = ['machine_name', 'total_usage_hours', 'total_work_orders', 'avg_usage_per_work_order', 'total_work_time', 'downtime_hours','start_date_after','start_date_before','end_date_after','end_date_before',
                     's', 'sort', 'page', 'limit']

class RawMaterialConsumptionReportFilter(filters.FilterSet):
    """Filter for Raw Material Consumption Report data"""
    product = filters.CharFilter(field_name='product_id__name', lookup_expr='icontains')
    total_consumed_quantity_min = filters.NumberFilter(field_name='total_consumed_quantity', lookup_expr='gte')
    total_consumed_quantity_max = filters.NumberFilter(field_name='total_consumed_quantity', lookup_expr='lte')
    total_cost_min = filters.NumberFilter(field_name='total_cost', lookup_expr='gte')
    total_cost_max = filters.NumberFilter(field_name='total_cost', lookup_expr='lte')
    date_from = filters.DateFilter(field_name='updated_at', lookup_expr='gte')
    date_to = filters.DateFilter(field_name='updated_at', lookup_expr='lte')
    
    # Additional custom filters
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
        model = BillOfMaterials
        fields = ['product','total_consumed_quantity_min','total_consumed_quantity_max','total_cost_min','total_cost_max','date_from','date_to','s', 'sort', 'page', 'limit']



class MaterialIssueFilter(filters.FilterSet):
    issue_no = filters.CharFilter(lookup_expr='icontains')
    product = filters.CharFilter(field_name='materialissueitem__product_id__name', lookup_expr='icontains')
    production_floor = filters.CharFilter(field_name='production_floor_id__name', lookup_expr='icontains')
    created_at = filters.DateFromToRangeFilter()
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
        model = MaterialIssue
        fields = ['issue_no', 'production_floor', 'created_at', 'product', 's', 'sort', 'page', 'limit']

class MaterialReceivedFilter(filters.FilterSet):
    receipt_no = filters.CharFilter(lookup_expr='icontains')
    product = filters.CharFilter(field_name='materialreceiveditem__product_id__name', lookup_expr='icontains')
    production_floor = filters.CharFilter(field_name='production_floor_id__name', lookup_expr='icontains')
    created_at = filters.DateFromToRangeFilter()
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
        model = MaterialReceived
        fields = ['receipt_no', 'production_floor', 'created_at', 'product', 's', 'sort', 'page', 'limit']

class StockJournalFilter(filters.FilterSet):
    product = filters.CharFilter(field_name='product_id__name', lookup_expr='icontains')
    transaction_type = filters.CharFilter(lookup_expr='icontains')
    quantity = filters.RangeFilter()
    reference_id = filters.CharFilter(lookup_expr='icontains')
    created_at = filters.DateFromToRangeFilter()
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
        model = StockJournal
        fields = ['product', 'transaction_type', 'quantity','reference_id', 'created_at', 's', 'sort', 'page', 'limit']

class StockSummaryFilter(filters.FilterSet):
    product = filters.CharFilter(field_name='product_id__name', lookup_expr='icontains')
    unit = filters.CharFilter(field_name='unit_options_id__unit_name', lookup_expr='icontains')
    opening_quantity = filters.RangeFilter()
    received_quantity = filters.RangeFilter()
    issued_quantity = filters.RangeFilter()
    closing_quantity = filters.RangeFilter()
    sales_rate = filters.RangeFilter()
    mrp = filters.RangeFilter()
    purchase_rate = filters.RangeFilter()
    period_start = filters.DateFromToRangeFilter()
    period_end = filters.DateFromToRangeFilter()
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
        model = StockSummary
        fields = [
            'product', 'unit', 'opening_quantity', 'received_quantity', 'issued_quantity',
            'closing_quantity', 'sales_rate', 'mrp', 'purchase_rate',
            'period_start', 'period_end','created_at', 's', 'sort', 'page', 'limit'
        ]      
