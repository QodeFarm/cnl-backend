from django_filters import rest_framework as filters
from apps.hrms.models import Employees, EmployeeSalary, EmployeeSalaryComponents, EmployeeLeaves, LeaveApprovals, EmployeeLeaveBalance, Attendance, Swipes
from config.utils_methods import filter_uuid
from django_filters import FilterSet, ChoiceFilter, DateFromToRangeFilter
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
logger = logging.getLogger(__name__)

class EmployeesFilter(filters.FilterSet):
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
    created_at = DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    search = filters.CharFilter(method='filter_by_search', label="Search")
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
        fields =['first_name','last_name','email','phone','address','hire_date','job_type_id','designation_id','job_code_id','department_id','shift_id','created_at','period_name','search','sort','page','limit']


class EmployeeSalaryFilter(filters.FilterSet):
    salary_amount = filters.RangeFilter()
    salary_currency = filters.CharFilter(lookup_expr='icontains') 
    salary_start_date = filters.DateFilter()
    salary_end_date = filters.DateFilter() 
    employee_id = filters.CharFilter(field_name='employee_id__first_name', lookup_expr='icontains')
    created_at = DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    search = filters.CharFilter(method='filter_by_search', label="Search")
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
        fields =['salary_amount','salary_currency','salary_start_date','salary_end_date','employee_id','created_at','period_name','search','sort','page','limit']

class EmployeeSalaryComponentsFilter(filters.FilterSet):
    component_id = filters.CharFilter(field_name='component_id__component_name', lookup_expr='icontains')
    component_amount = filters.RangeFilter()
    salary_id = filters.CharFilter(field_name='salary_id__salary_amount', lookup_expr='icontains')
    created_at = DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    search = filters.CharFilter(method='filter_by_search', label="Search")
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
        model = EmployeeSalaryComponents
        #do not change "component_id",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['component_id','component_amount','salary_id','created_at','period_name','search','sort','page','limit']


class EmployeeLeavesFilter(filters.FilterSet):
    start_date = filters.DateFilter()
    end_date = filters.DateFilter() 
    status_id = filters.CharFilter(field_name='status_id__status_name', lookup_expr='icontains')
    comments = filters.CharFilter(lookup_expr='icontains') 
    employee_id = filters.CharFilter(field_name='employee_id__first_name', lookup_expr='icontains')
    leave_type_id = filters.CharFilter(field_name='leave_type_id__leave_type_name', lookup_expr='icontains')
    created_at = DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    search = filters.CharFilter(method='filter_by_search', label="Search")
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
        fields =['start_date','end_date','status_id','comments','employee_id','leave_type_id','created_at','period_name','search','sort','page','limit']


class LeaveApprovalsFilter(filters.FilterSet):
    approval_date = DateFromToRangeFilter()
    comments = filters.CharFilter(lookup_expr='icontains') 
    status_id = filters.CharFilter(field_name='status_id__status_name', lookup_expr='icontains')
    leave_id = filters.CharFilter(field_name='leave_id__comments', lookup_expr='icontains')
    approver_id = filters.CharFilter(field_name='approver_id__first_name', lookup_expr='icontains')
    created_at = DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    search = filters.CharFilter(method='filter_by_search', label="Search")
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
        fields =['approval_date','comments','status_id','leave_id','approver_id','created_at','period_name','search','sort','page','limit']


class EmployeeLeaveBalanceFilter(filters.FilterSet):
    employee_id = filters.CharFilter(field_name='employee_id__first_name', lookup_expr='icontains')
    leave_type_id = filters.CharFilter(field_name='leave_type_id__leave_type_name', lookup_expr='icontains')
    leave_balance = DateFromToRangeFilter()
    year = filters.CharFilter(lookup_expr='icontains') 
    created_at = DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    search = filters.CharFilter(method='filter_by_search', label="Search")
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
        fields =['employee_id','leave_type_id','leave_balance','year','created_at','period_name','search','sort','page','limit']

class AttendanceFilter(filters.FilterSet):
    employee_id = filters.CharFilter(field_name='employee_id__first_name', lookup_expr='icontains')
    attendance_date = filters.DateFilter()
    clock_in_time = DateFromToRangeFilter()
    clock_out_time = DateFromToRangeFilter()
    status_id = filters.CharFilter(field_name='status_id__status_name', lookup_expr='icontains')
    department_id = filters.CharFilter(field_name='department_id__department_name', lookup_expr='icontains')
    shift_id = filters.CharFilter(field_name='shift_id__shift_name', lookup_expr='icontains')
    created_at = DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    search = filters.CharFilter(method='filter_by_search', label="Search")
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
        model = Attendance
        #do not change "employee_id",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields =['employee_id','attendance_date','clock_in_time','clock_out_time','status_id','department_id','shift_id','created_at','period_name','search','sort','page','limit']


class SwipesFilter(filters.FilterSet):
    employee_id = filters.CharFilter(field_name='employee_id__first_name', lookup_expr='icontains')
    swipe_time = DateFromToRangeFilter()
    created_at = DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    search = filters.CharFilter(method='filter_by_search', label="Search")
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
        fields =['employee_id','swipe_time','created_at','period_name','search','sort','page','limit']
