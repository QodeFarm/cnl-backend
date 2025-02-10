from django_filters import rest_framework as filters, FilterSet, CharFilter

from apps.production.models import BOM
from .models import BrandSalesman,Country, CustomerPaymentTerms, FirmStatuses, GPackageUnit, GstCategories, GstTypes, LedgerGroups, OrderStatuses, OrderTypes, PackageUnit, PaymentLinkTypes, PriceCategories, ProductBrands, ProductItemType, ProductTypes, ProductUniqueQuantityCodes, PurchaseTypes, SaleTypes, State, City, Statuses, TaskPriorities, Territory, Transporters, UnitOptions, UserGroupMembers, UserGroups
import django_filters
from config.utils_filter_methods import filter_by_search, filter_by_sort, filter_by_page, filter_by_limit



class CountryFilters(django_filters.FilterSet):
    country_name = django_filters.CharFilter(field_name='country_name', lookup_expr='icontains')
    country_code = django_filters.CharFilter(field_name='country_code', lookup_expr='exact')

    class Meta:
        model = Country
        fields = ['country_name', 'country_code']
    
class StateFilters(django_filters.FilterSet):
    state_name = django_filters.CharFilter(field_name='state_name', lookup_expr='icontains')
    state_code = django_filters.CharFilter(field_name='state_code', lookup_expr='exact')
    country_name = django_filters.CharFilter(field_name='country_id__country_name', lookup_expr='icontains')

    class Meta:
        model = State
        fields = ['state_name', 'state_code', 'country_name']

class CityFilters(django_filters.FilterSet):
    city_name = django_filters.CharFilter(field_name='city_name', lookup_expr='icontains')
    city_code = django_filters.CharFilter(field_name='city_code', lookup_expr='exact')
    state_name = django_filters.CharFilter(field_name='state_id__state_name', lookup_expr='icontains')
    country_name = django_filters.CharFilter(field_name='state_id__country_id__country_name', lookup_expr='icontains')

    class Meta:
        model = City
        fields = ['city_name', 'city_code', 'state_name', 'country_name']


class LedgerGroupsFilters(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    code = filters.CharFilter(lookup_expr='icontains')
    inactive = filters.BooleanFilter()
    under_group = filters.CharFilter(lookup_expr='exact')
    nature = filters.CharFilter(lookup_expr='exact')
    s = filters.CharFilter(method='filter_by_search', label="Search")

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)
    class Meta:
        model = LedgerGroups
        fields = [ 'ledger_group_id','name','code','inactive','under_group','nature','created_at','updated_at','s',]

class FirmStatusesFilters(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)
    
    class Meta:
        model = FirmStatuses
        fields = ['name','s']

class TerritoryFilters(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    code = filters.CharFilter(lookup_expr='exact')
    s = filters.CharFilter(method='filter_by_search', label="Search")
   
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)
    
    class Meta:
        model = Territory
        fields = ['name','code','s']


class CustomerCategoriesFilters(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    code = filters.CharFilter(lookup_expr='exact')

class GstCategoriesFilters(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)
    
    class Meta:
        model = GstCategories
        fields = ['name','s']

class CustomerPaymentTermsFilters(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    code = filters.CharFilter(lookup_expr='exact')
    fixed_days = filters.NumberFilter(lookup_expr='exact')
    no_of_fixed_days = filters.RangeFilter(lookup_expr='exact')
    payment_cycle = filters.CharFilter(lookup_expr='icontains')
    run_on = filters.CharFilter(lookup_expr='icontains')      
    s = filters.CharFilter(method='filter_by_search', label="Search")
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)
    
    class Meta:
        model = CustomerPaymentTerms
        fields = ['name','code','fixed_days','no_of_fixed_days','payment_cycle','run_on','s']
        
class PriceCategoriesFilters(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    code = filters.CharFilter(lookup_expr='exact')
    s = filters.CharFilter(method='filter_by_search', label="Search")
   
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)
    
    class Meta:
        model = PriceCategories
        fields = ['name','code','s']
    
class TransportersFilters(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    code = filters.CharFilter(lookup_expr='exact')
    gst_no = filters.CharFilter(lookup_expr='exact')
    website_url = filters.CharFilter(lookup_expr='icontains')  
    s = filters.CharFilter(method='filter_by_search', label="Search")
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = Transporters
        fields = ['name','code','gst_no','website_url','s']

class ProductTypesFilter(FilterSet):
    type_id = filters.CharFilter(method='filter_uuid')
    type_name = filters.CharFilter(lookup_expr='icontains')
    created_at = filters.DateFromToRangeFilter()
    updated_at = filters.DateFromToRangeFilter()
    s = filters.CharFilter(method='filter_by_search', label="Search")

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = ProductTypes
        fields = ['type_id', 'type_name', 'created_at', 'updated_at', 's']

class ProductUniqueQuantityCodesFilter(FilterSet):
    quantity_code_name = filters.CharFilter(lookup_expr='icontains')
    created_at = filters.DateFromToRangeFilter() 
    updated_at = filters.DateFromToRangeFilter()  
    s = filters.CharFilter(method='filter_by_search', label="Search")

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = ProductUniqueQuantityCodes
        fields = ['quantity_code_name', 'created_at', 'updated_at','s']
	
class UnitOptionsFilter(FilterSet):
    unit_name = filters.CharFilter(lookup_expr='icontains')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    created_at = filters.DateFromToRangeFilter()  
    updated_at = filters.DateFromToRangeFilter() 
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)
    class Meta:
        model = UnitOptions
        fields = ['unit_name', 'created_at', 'updated_at','s']

class ProductDrugTypesFilter(FilterSet):
    drug_type_name = filters.CharFilter(lookup_expr='icontains')
	
class ProductItemTypeFilter(FilterSet):
    item_name = filters.CharFilter(lookup_expr='icontains')
    created_at = django_filters.DateFromToRangeFilter()
    updated_at = django_filters.DateFromToRangeFilter()
    s = django_filters.CharFilter(method='filter_by_search', label="Search")

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = ProductItemType
        fields = ['item_name', 'created_at', 'updated_at', 's']
	
class BrandSalesmanFilter(FilterSet):
    code = filters.CharFilter(lookup_expr='icontains')
    name = filters.CharFilter(lookup_expr='icontains')
    rate_on = filters.ChoiceFilter(choices=BrandSalesman.RATE_ON_CHOICES, field_name='rate_on')

class ProductBrandsFilter(FilterSet):
    brand_id = filters.CharFilter(method='filter_uuid')
    brand_name = filters.CharFilter(lookup_expr='icontains')
    code = filters.CharFilter(lookup_expr='icontains')
    brand_salesman_name = filters.CharFilter(field_name='brand_salesman_id__name', lookup_expr='icontains')  
    name = CharFilter(field_name='brand_salesman_id__name', lookup_expr='exact')
    created_at = filters.DateFromToRangeFilter()
    updated_at = filters.DateFromToRangeFilter()
    s = filters.CharFilter(method='filter_by_search', label="Search")

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = ProductBrands
        fields = ['brand_id','brand_name','code','brand_salesman_name','created_at','updated_at','s',]
    
class UserGroupsFilter(filters.FilterSet):
    group_id = filters.CharFilter(method='filter_uuid') 
    group_name = filters.CharFilter(lookup_expr='icontains')  
    description = filters.CharFilter(lookup_expr='icontains')  
    created_at = filters.DateFromToRangeFilter()  
    s = filters.CharFilter(method='filter_by_search', label="Search") 

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)  

    class Meta:
        model = UserGroups
        fields = ['group_id', 'group_name', 'description', 'created_at', 's']
        
class PackageUnitFilter(filters.FilterSet):
    unit_name = filters.CharFilter(lookup_expr='icontains') 
    created_at = filters.DateFromToRangeFilter()  
    s = filters.CharFilter(method='filter_by_search', label="Search")  

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = PackageUnit
        fields = ['unit_name', 'created_at', 's']     
        

class GPackageUnitFilter(filters.FilterSet):
    unit_name = filters.CharFilter(lookup_expr='icontains')  
    created_at = filters.DateFromToRangeFilter()  
    s = filters.CharFilter(method='filter_by_search', label="Search")  

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = GPackageUnit
        fields = ['unit_name', 'created_at', 's']    
        
        
        
class StatusesFilter(filters.FilterSet):
    status_name = filters.CharFilter(lookup_expr='icontains') 
    created_at = filters.DateFromToRangeFilter()  
    s = filters.CharFilter(method='filter_by_search', label="Search")  

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = Statuses
        fields = ['status_name', 'created_at', 's']        
               
               
class OrderStatusesFilter(filters.FilterSet):
    order_status_id = filters.UUIDFilter()  
    status_name = filters.CharFilter(lookup_expr='icontains')  
    description = filters.CharFilter(lookup_expr='icontains')  
    created_at = filters.DateFromToRangeFilter() 
    updated_at = filters.DateFromToRangeFilter()  
    s = filters.CharFilter(method='filter_by_search', label="Search")  
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = OrderStatuses  
        fields = ['order_status_id', 'status_name', 'description', 'created_at', 'updated_at', 's'] 

class OrderTypesFilter(filters.FilterSet):
    order_type_id = filters.UUIDFilter() 
    name = filters.CharFilter(lookup_expr='icontains')  
    created_at = filters.DateFromToRangeFilter()  
    updated_at = filters.DateFromToRangeFilter() 
    s = filters.CharFilter(method='filter_by_search', label="Search")  
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = OrderTypes 
        fields = ['order_type_id', 'name', 'created_at', 'updated_at', 's'] 
        
        
class PurchaseTypesFilter(filters.FilterSet):
    purchase_type_id = filters.UUIDFilter() 
    name = filters.CharFilter(lookup_expr='icontains') 
    created_at = filters.DateFromToRangeFilter()  
    updated_at = filters.DateFromToRangeFilter() 
    s = filters.CharFilter(method='filter_by_search', label="Search")  

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = PurchaseTypes  
        fields = ['purchase_type_id', 'name', 'created_at', 'updated_at', 's']  
        
        
class SaleTypesFilter(filters.FilterSet):
    sale_type_id = filters.UUIDFilter() 
    name = filters.CharFilter(lookup_expr='icontains') 
    created_at = filters.DateFromToRangeFilter() 
    updated_at = filters.DateFromToRangeFilter()  
    s = filters.CharFilter(method='filter_by_search', label="Search")  
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = SaleTypes  
        fields = ['sale_type_id', 'name', 'created_at', 'updated_at', 's']  
        
        
class GstTypesFilter(django_filters.FilterSet):
    gst_type_id = filters.UUIDFilter() 
    name = filters.CharFilter(lookup_expr='icontains')  
    created_at = filters.DateFromToRangeFilter()  
    updated_at = filters.DateFromToRangeFilter()  
    s = filters.CharFilter(method='filter_by_search', label="Search")  

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = GstTypes  
        fields = ['gst_type_id', 'name', 'created_at', 'updated_at', 's'] 
        
            
class PaymentLinkTypesFilter(django_filters.FilterSet):
    payment_link_type_id = filters.UUIDFilter() 
    name = filters.CharFilter(lookup_expr='icontains')  
    description = filters.CharFilter(lookup_expr='icontains') 
    created_at = filters.DateFromToRangeFilter() 
    updated_at = filters.DateFromToRangeFilter()  
    s = filters.CharFilter(method='filter_by_search', label="Search") 

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = PaymentLinkTypes  
        fields = ['payment_link_type_id', 'name', 'description', 'created_at', 'updated_at', 's']        
        
        
class TaskPrioritiesFilter(filters.FilterSet):
    priority_id = filters.UUIDFilter(field_name='priority_id')  
    priority_name = filters.CharFilter(lookup_expr='icontains') 
    created_at = filters.DateFromToRangeFilter() 
    updated_at = filters.DateFromToRangeFilter() 
    s = filters.CharFilter(method='filter_by_search', label="Search")

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = TaskPriorities
        fields = ['priority_id', 'priority_name', 'created_at', 'updated_at', 's']   
        
        
             
             
class UserGroupMembersFilter(filters.FilterSet):
    member_id = filters.UUIDFilter(method='filter_uuid')  
    group_id = filters.UUIDFilter(field_name='group_id__group_name') 
    employee_id = filters.UUIDFilter(field_name='employee_id__employee_id') 
    created_at = filters.DateFromToRangeFilter()  
    updated_at = filters.DateFromToRangeFilter()  
    s = filters.CharFilter(method='filter_by_search', label="Search") 

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = UserGroupMembers
        fields = ['member_id', 'group_id', 'employee_id', 'created_at', 'updated_at', 's']             