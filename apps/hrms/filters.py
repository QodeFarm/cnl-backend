from django_filters import rest_framework as filters
from apps.hrms.models import Departments, Designations, EmployeeSalaryComponents, Employees, EmployeeSalary, EmployeeLeaves, JobCodes, JobTypes, LeaveApprovals, EmployeeLeaveBalance, EmployeeAttendance, LeaveTypes, SalaryComponents, Shifts, Swipes, Timesheets, TimesheetEntries, TimesheetApprovals
from config.utils_methods import filter_uuid
from django_filters import DateFromToRangeFilter
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
logger = logging.getLogger(__name__)

class EmployeesFilter(filters.FilterSet):
    employee_id = filters.CharFilter(method=filter_uuid)
    first_name = filters.CharFilter(lookup_expr='icontains')
    last_name = filters.CharFilter(lookup_expr='icontains')
    full_name = filters.CharFilter(lookup_expr='icontains')
    email = filters.CharFilter(lookup_expr='exact')
    phone = filters.CharFilter(lookup_expr='exact')
    address = filters.CharFilter(lookup_expr='icontains')
    hire_date = filters.DateFilter()
    job_type_id = filters.CharFilter(field_name='job_type_id__job_type_name', lookup_expr='icontains')
    designation_id = filters.CharFilter(field_name='designation_id__designation_name', lookup_expr='icontains')
    job_code_id = filters.CharFilter(field_name='job_code_id__job_code', lookup_expr='icontains')
    department_id = filters.CharFilter(field_name='department_id__department_name', lookup_expr='icontains')
    shift_id = filters.CharFilter(field_name='shift_id__shift_name', lookup_expr='icontains')
    manager_id = filters.CharFilter(field_name='manager_id__full_name', lookup_expr='icontains')
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
        fields =['hire_date','first_name','last_name','full_name','employee_id','email','phone','address','hire_date','job_type_id','designation_id','job_code_id','department_id','shift_id','manager_id','created_at','period_name','s','sort','page','limit']


class EmployeeSalaryFilter(filters.FilterSet):
    salary_amount = filters.RangeFilter()
    salary_currency = filters.CharFilter(lookup_expr='icontains') 
    salary_start_date = filters.DateFilter()
    salary_end_date = filters.DateFilter() 
    # employee_id = filters.CharFilter(field_name='employee_id__full_name', lookup_expr='icontains')
    employee_name = filters.CharFilter(field_name='employee_id__full_name', lookup_expr='icontains', label='Employee Name')
    employee_id = filters.CharFilter(field_name='employee_id', lookup_expr='exact', label='Employee ID')
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
        fields =['salary_amount','salary_currency','salary_start_date','salary_end_date','employee_name', 'employee_id','created_at','period_name','s','sort','page','limit']

class EmployeeLeavesFilter(filters.FilterSet):
    start_date = filters.DateFilter()
    end_date = filters.DateFilter() 
    comments = filters.CharFilter(lookup_expr='icontains') 
    employee = filters.CharFilter(field_name='employee_id__full_name', lookup_expr='icontains')
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
    approval_date = filters.DateFilter()
    status_id = filters.CharFilter(field_name='status_id__status_name', lookup_expr='icontains')
    status_name = filters.CharFilter(field_name='status_id__status_name', lookup_expr='icontains')
    # leave_id = filters.CharFilter(field_name='leave_id__comments', lookup_expr='icontains')
    leave_id = filters.CharFilter(field_name='leave_id__employee_id__full_name', lookup_expr='icontains')
    approver = filters.CharFilter(field_name='approver_id__full_name', lookup_expr='icontains')
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
        fields =['created_at','approval_date','status_id','leave_id','approver','approver_id','period_name','s','page','limit']


class EmployeeLeaveBalanceFilter(filters.FilterSet):
    employee_id = filters.CharFilter(method=filter_uuid)
    employee = filters.CharFilter(field_name='employee_id__full_name', lookup_expr='icontains')
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
    employee = filters.CharFilter(field_name='employee_id__full_name', lookup_expr='icontains')
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
    employee_id = filters.CharFilter(field_name='employee_id__full_name', lookup_expr='icontains')
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
    job_type_name = filters.CharFilter(lookup_expr='icontains')
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
        model = JobTypes 
        fields = ['job_type_name','created_at','s', 'sort','page','limit']

class DesignationsFilter(filters.FilterSet):
    designation_name = filters.CharFilter(lookup_expr='icontains')
    responsibilities = filters.CharFilter(lookup_expr='icontains')
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
        model = Designations 
        fields = ['designation_name','responsibilities','created_at','s', 'sort','page','limit']


class JobCodesFilter(filters.FilterSet):
    job_code = filters.CharFilter(lookup_expr='icontains')
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
        model = JobCodes 
        fields = ['job_code','created_at','s', 'sort','page','limit']

class DepartmentsFilter(filters.FilterSet):
    department_name = filters.CharFilter(lookup_expr='icontains')
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
        model = Departments 
        fields = ['department_name','created_at','s', 'sort','page','limit']

class ShiftsFilter(filters.FilterSet):
    shift_name = filters.CharFilter(lookup_expr='icontains')
    start_time = filters.DateTimeFilter()
    end_time = filters.DateTimeFilter()
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
        model = Shifts 
        fields = ['shift_name','start_time','end_time','created_at','s', 'sort','page','limit']

class SalaryComponentsFilter(filters.FilterSet):
    component_name = filters.CharFilter(lookup_expr='icontains')
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
        model = SalaryComponents 
        fields = ['component_name','created_at','s', 'sort','page','limit']

class EmployeeSalaryComponentsFilter(filters.FilterSet):
    component_id = filters.CharFilter(field_name='component_id__component_name', lookup_expr='icontains')
    component_amount = filters.RangeFilter()
    salary_id = filters.CharFilter(field_name='salary_id__salary_amount', lookup_expr='icontains')
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
        model = EmployeeSalaryComponents 
        fields = ['component_id','component_amount','salary_id','created_at','s', 'sort','page','limit']

class LeaveTypesFilter(filters.FilterSet):
    leave_type_name = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    max_days_allowed = filters.NumberFilter()
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
        model = LeaveTypes
        fields = ['leave_type_name','description','max_days_allowed','created_at','s', 'sort','page','limit']


# ===================== timesheets ====================================

class TimesheetsFilter(filters.FilterSet):
    """
    Filter set for the Timesheets model.

    Supports:
      - employee_id   : exact UUID match
      - employee      : partial name match on employee's full_name
      - department    : partial match on the employee's department name
                        (allows HR to filter all timesheets for a department)
      - start_date    : exact date match
      - end_date      : exact date match
      - created_at    : date-range filter (from / to)
      - period_name   : shortcut period e.g. "This Week", "This Month"
      - s             : global search across key fields
      - sort / page / limit : standard pagination helpers
    """
    employee_id = filters.CharFilter(method=filter_uuid)
    employee = filters.CharFilter(
        field_name='employee_id__full_name',
        lookup_expr='icontains',
    )
    department = filters.CharFilter(
        field_name='employee_id__department_id__department_name',
        lookup_expr='icontains',
    )
    # --- billing filters ---
    customer_id = filters.CharFilter(method=filter_uuid)
    customer = filters.CharFilter(
        field_name='customer_id__name',
        lookup_expr='icontains',
    )
    is_billable = filters.BooleanFilter()
    invoiced = filters.CharFilter(lookup_expr='exact')
    start_date = filters.DateFilter()
    end_date = filters.DateFilter()
    created_at = DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(
        choices=PERIOD_NAME_CHOICES,
        method='filter_by_period_name',
    )
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
        model = Timesheets
        # NOTE: 'employee' must be first — the summary/ordering logic in
        # filter_by_page relies on the 0th index field for descending default sort.
        fields = [
            'employee', 'employee_id', 'department',
            'customer', 'customer_id', 'is_billable', 'invoiced',
            'start_date', 'end_date',
            'created_at', 'period_name',
            's', 'sort', 'page', 'limit',
        ]


class TimesheetEntriesFilter(filters.FilterSet):
    """
    Filter set for TimesheetEntries.

    Supports:
      - timesheet_id  : exact UUID match on the parent timesheet
      - employee      : partial name match traversing timesheet → employee
      - work_date     : exact date match
      - created_at    : date-range filter
      - period_name / s / sort / page / limit : standard helpers
    """
    timesheet_id = filters.CharFilter(method=filter_uuid)
    employee = filters.CharFilter(
        field_name='timesheet_id__employee_id__full_name',
        lookup_expr='icontains',
    )
    work_date = filters.DateFilter()
    created_at = DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(
        choices=PERIOD_NAME_CHOICES,
        method='filter_by_period_name',
    )
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
        model = TimesheetEntries
        fields = [
            'timesheet_id', 'employee', 'work_date',
            'created_at', 'period_name',
            's', 'sort', 'page', 'limit',
        ]


class TimesheetApprovalsFilter(filters.FilterSet):
    """
    Filter set for TimesheetApprovals.

    Supports:
      - timesheet_approval_id : exact UUID match
      - timesheet_id          : exact UUID match on the parent timesheet
      - employee              : partial name match traversing approval → timesheet → employee
      - status_id             : partial match on status_name
      - status_name           : alias of status_id filter (convenience)
      - approver              : partial name match on approver's full_name
      - approver_id           : exact UUID match on the approver
      - approval_date         : exact date match
      - created_at            : date-range filter
      - period_name / s / sort / page / limit : standard helpers
    """
    timesheet_approval_id = filters.CharFilter(method=filter_uuid)
    timesheet_id = filters.CharFilter(method=filter_uuid)
    employee = filters.CharFilter(
        field_name='timesheet_id__employee_id__full_name',
        lookup_expr='icontains',
    )
    status_id = filters.CharFilter(
        field_name='status_id__status_name',
        lookup_expr='icontains',
    )
    status_name = filters.CharFilter(
        field_name='status_id__status_name',
        lookup_expr='icontains',
    )
    approver = filters.CharFilter(
        field_name='approver_id__full_name',
        lookup_expr='icontains',
    )
    approver_id = filters.CharFilter(method=filter_uuid)
    approval_date = filters.DateFilter()
    created_at = DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(
        choices=PERIOD_NAME_CHOICES,
        method='filter_by_period_name',
    )
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
        model = TimesheetApprovals
        # 'employee' first — same reasoning as TimesheetsFilter.
        fields = [
            'employee', 'timesheet_approval_id', 'timesheet_id',
            'status_id', 'status_name',
            'approver', 'approver_id', 'approval_date',
            'created_at', 'period_name',
            's', 'sort', 'page', 'limit',
        ]
