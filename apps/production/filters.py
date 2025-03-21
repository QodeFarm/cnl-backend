from django_filters import rest_framework as filters
from apps.production.models import Machine, ProductionStatus, WorkOrder, BOM, BillOfMaterials
from config.utils_methods import filter_uuid
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit


class WorkOrderFilter(filters.FilterSet):
    product = filters.CharFilter(field_name='product_id__name', lookup_expr='icontains')
    product_id = filters.CharFilter(method=filter_uuid)
    size = filters.CharFilter(field_name='size_id__size_name', lookup_expr='icontains')  # Assuming 'size_name' exists in Size
    color = filters.CharFilter(field_name='color_id__color_name', lookup_expr='icontains')  # Assuming 'color_name' exists in Color
    status_id = filters.CharFilter(field_name='status_id__status_name', lookup_expr='icontains')
    flow_status = filters.CharFilter(field_name='sale_order_id__flow_status_id__flow_status_name', lookup_expr='iexact')
    quantity = filters.RangeFilter()
    completed_qty = filters.RangeFilter()
    completed_qty = filters.RangeFilter()
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
        fields = ['product','bom_id','bom','notes','product_id','s', 'sort','page','limit']

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
