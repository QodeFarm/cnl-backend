from django_filters import rest_framework as filters
from apps.hrms.models import Departments, Designations, EmployeeSalaryComponents, Employees, EmployeeSalary, EmployeeLeaves, JobCodes, JobTypes, LeaveApprovals, EmployeeLeaveBalance, EmployeeAttendance, LeaveTypes, SalaryComponents, Shifts, Swipes
from config.utils_methods import filter_uuid
from django_filters import DateFromToRangeFilter
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
logger = logging.getLogger(__name__)

class EmployeesFilter(filters.FilterSet):
    employee_id = filters.CharFilter(method=filter_uuid)
    first_name = filters.CharFilter(lookup_expr='icontains')
    last_name = filters.CharFilter(lookup_expr='icontains')
    email = filters.CharFilter(lookup_expr='exact')
    phone = filters.CharFilter(lookup_expr='exact')
    address = filters.CharFilter(lookup_expr='icontains')
    hire_date = filters.DateFilter()
    job_type_id = filters.CharFilter(field_name='job_type_id__job_type_name', lookup_expr='icontains')
    designation_id = filters.CharFilter(field_name='designation_id__designation_name', lookup_expr='icontains')
    job_code_id = filters.CharFilter(field_name='job_code_id__job_code', lookup_expr='icontains')
    department_id = filters.CharFilter(field_name='department_id__department_name', lookup_expr='icontains')
    shift_id = filters.CharFilter(field_name='shift_id__shift_name', lookup_expr='icontains')
    manager_id = filters.CharFilter(field_name='manager_id__first_name', lookup_expr='icontains')
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
        model = Employees
        #do not change "first_name",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['hire_date','first_name','last_name','employee_id','email','phone','address','hire_date','job_type_id','designation_id','job_code_id','department_id','shift_id','manager_id','created_at','period_name','s','sort','page','limit']


class EmployeeSalaryFilter(filters.FilterSet):
    salary_amount = filters.RangeFilter()
    salary_currency = filters.CharFilter(lookup_expr='icontains') 
    salary_start_date = filters.DateFilter()
    salary_end_date = filters.DateFilter() 
    employee_id = filters.CharFilter(field_name='employee_id__first_name', lookup_expr='icontains')
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
        model = EmployeeSalary
        #do not change "salary_amount",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['salary_amount','salary_currency','salary_start_date','salary_end_date','employee_id','created_at','period_name','s','sort','page','limit']

class EmployeeLeavesFilter(filters.FilterSet):
    start_date = filters.DateFilter()
    end_date = filters.DateFilter() 
    comments = filters.CharFilter(lookup_expr='icontains') 
    employee = filters.CharFilter(field_name='employee_id__first_name', lookup_expr='icontains')
    employee_id = filters.CharFilter(method=filter_uuid)
    leave_type_id = filters.CharFilter(method=filter_uuid)
    leave_type = filters.CharFilter(field_name='leave_type_id__leave_type_name', lookup_expr='icontains')
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
        model = EmployeeLeaves
        #do not change "start_date",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['employee','employee_id','leave_type','leave_type_id','start_date','end_date','comments','created_at','period_name','s','sort','page','limit']


class LeaveApprovalsFilter(filters.FilterSet):
    approval_date = DateFromToRangeFilter()
    status_id = filters.CharFilter(field_name='status_id__status_name', lookup_expr='icontains')
    leave_id = filters.CharFilter(field_name='leave_id__comments', lookup_expr='icontains')
    approver = filters.CharFilter(field_name='approver_id__first_name', lookup_expr='icontains')
    approver_id = filters.CharFilter(method=filter_uuid)
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
        model = LeaveApprovals
        #do not change "approval_date",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['approval_date','status_id','leave_id','approver','approver_id','created_at','period_name','s','sort','page','limit']


class EmployeeLeaveBalanceFilter(filters.FilterSet):
    employee_id = filters.CharFilter(method=filter_uuid)
    employee = filters.CharFilter(field_name='employee_id__first_name', lookup_expr='icontains')
    leave_type_id = filters.CharFilter(method=filter_uuid)
    leave_type = filters.CharFilter(field_name='leave_type_id__leave_type_name', lookup_expr='icontains')
    leave_balance = filters.RangeFilter()
    leave_bal = filters.NumberFilter(field_name='leave_balance', lookup_expr='exact', label='Leave Balance (exact match)')
    year = filters.CharFilter(lookup_expr='icontains') 
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
        model = EmployeeLeaveBalance
        #do not change "employee_id",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['employee_id','employee','leave_type_id','leave_type','leave_balance','leave_bal','year','created_at','period_name','s','sort','page','limit']

class EmployeeAttendanceFilter(filters.FilterSet):
    employee = filters.CharFilter(field_name='employee_id__first_name', lookup_expr='icontains')
    employee_id = filters.CharFilter(method=filter_uuid)
    attendance_date = filters.DateFilter()
    absent = filters.BooleanFilter()
    leave_duration = filters.ChoiceFilter(field_name='leave_duration',choices=[('First Half', 'First Half'),('Full Day', 'Full Day'),('Second Half', 'Second Half')])
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
        model = EmployeeAttendance
        #do not change "employee_id",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['employee','employee_id','attendance_date','absent','leave_duration','created_at','period_name','s','sort','page','limit']


class SwipesFilter(filters.FilterSet):
    employee_id = filters.CharFilter(field_name='employee_id__first_name', lookup_expr='icontains')
    swipe_time = DateFromToRangeFilter()
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
        model = Swipes
        #do not change "employee_id",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['employee_id','swipe_time','created_at','period_name','s','sort','page','limit']
        
        
class JobTypesFilter(filters.FilterSet):
    job_type_id = filters.UUIDFilter() 
    job_type_name = filters.CharFilter(lookup_expr='icontains') 
    created_at = filters.DateFromToRangeFilter() 
    updated_at = filters.DateFromToRangeFilter() 
    s = filters.CharFilter(method='filter_by_search', label="Search")  

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = JobTypes  
        fields = ['job_type_id', 'job_type_name', 'created_at', 'updated_at', 's']         


class DesignationsFilter(filters.FilterSet):
    designation_id = filters.UUIDFilter() 
    designation_name = filters.CharFilter(lookup_expr='icontains')  
    responsibilities = filters.CharFilter(lookup_expr='icontains') 
    created_at = filters.DateFromToRangeFilter()  
    updated_at = filters.DateFromToRangeFilter()  
    s = filters.CharFilter(method='filter_by_search', label="Search") 

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = Designations 
        fields = ['designation_id', 'designation_name', 'responsibilities', 'created_at', 'updated_at', 's']  
        
        
class JobCodesFilter(filters.FilterSet):
    job_code_id = filters.UUIDFilter() 
    job_code = filters.CharFilter(lookup_expr='icontains') 
    created_at = filters.DateFromToRangeFilter()  
    updated_at = filters.DateFromToRangeFilter()  
    s = filters.CharFilter(method='filter_by_search', label="Search")  

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = JobCodes  
        fields = ['job_code_id', 'job_code', 'created_at', 'updated_at', 's']    
        
            
class DepartmentsFilter(filters.FilterSet):
    department_id = filters.UUIDFilter() 
    department_name = filters.CharFilter(lookup_expr='icontains')  
    created_at = filters.DateFromToRangeFilter() 
    updated_at = filters.DateFromToRangeFilter() 
    s = filters.CharFilter(method='filter_by_search', label="Search") 

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = Departments 
        fields = ['department_id', 'department_name', 'created_at', 'updated_at', 's']        
            
            
class ShiftsFilter(filters.FilterSet):
    shift_id = filters.UUIDFilter()  
    shift_name = filters.CharFilter(lookup_expr='icontains')  
    start_time = filters.DateTimeFromToRangeFilter() 
    end_time = filters.DateTimeFromToRangeFilter()  
    created_at = filters.DateFromToRangeFilter()  
    updated_at = filters.DateFromToRangeFilter() 
    s = filters.CharFilter(method='filter_by_search', label="Search")  

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = Shifts 
        fields = ['shift_id', 'shift_name', 'start_time', 'end_time', 'created_at', 'updated_at', 's'] 
              
class SalaryComponentsFilter(filters.FilterSet):
    component_id = filters.UUIDFilter()  
    component_name = filters.CharFilter(lookup_expr='icontains')  
    created_at = filters.DateFromToRangeFilter()  
    updated_at = filters.DateFromToRangeFilter() 
    s = filters.CharFilter(method='filter_by_search', label="Search") 

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = SalaryComponents  
        fields = ['component_id', 'component_name', 'created_at', 'updated_at', 's']
        

class EmployeeSalaryComponentsFilter(filters.FilterSet):
    employee_component_id = filters.UUIDFilter()
    component_amount = filters.RangeFilter() 
    component_id = filters.UUIDFilter(field_name='component_id__component_name')  # Correct field name here
    salary_id = filters.UUIDFilter(field_name='salary_id__salary_amount')  # Correct field name here
    created_at = filters.DateFromToRangeFilter()  # Date range filter for created_at
    updated_at = filters.DateFromToRangeFilter()  # Date range filter for updated_at
    s = filters.CharFilter(method='filter_by_search', label="Search")

    def filter_by_search(self, queryset, name, value):
        # Implement custom search logic or delegate to an existing function
        return filter_by_search(queryset, self, value)

    class Meta:
        model = EmployeeSalaryComponents
        fields = ['employee_component_id', 'component_amount', 'component_id', 'salary_id', 'created_at', 'updated_at', 's']


class LeaveTypesFilter(filters.FilterSet):
    leave_type_name = filters.CharFilter(lookup_expr='icontains')  # Case-insensitive search for leave type name
    description = filters.CharFilter(lookup_expr='icontains')  # Case-insensitive search for description
    max_days_allowed = filters.RangeFilter()  # Range filter for max days allowed
    created_at = filters.DateFromToRangeFilter()  # Date range filter for created_at
    updated_at = filters.DateFromToRangeFilter()  # Date range filter for updated_at
    s = filters.CharFilter(method='filter_by_search', label="Search")

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    class Meta:
        model = LeaveTypes
        fields = ['leave_type_name', 'description', 'max_days_allowed', 'created_at', 'updated_at', 's']