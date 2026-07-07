from django.contrib import admin

from .models import (
    JobTypes,
    Designations,
    JobCodes,
    Departments,
    Shifts,
    Employees,
    EmployeeSalary,
    SalaryComponents,
    EmployeeSalaryComponents,
    LeaveTypes,
    EmployeeLeaves,
    LeaveApprovals,
    EmployeeLeaveBalance,
    EmployeeAttendance,
    Swipes,
    Biometric,
    Timesheets,
    TimesheetEntries,
    TimesheetApprovals,
)

admin.site.register(JobTypes)
admin.site.register(Designations)
admin.site.register(JobCodes)
admin.site.register(Departments)
admin.site.register(Shifts)
admin.site.register(Employees)
admin.site.register(EmployeeSalary)
admin.site.register(SalaryComponents)
admin.site.register(EmployeeSalaryComponents)
admin.site.register(LeaveTypes)
admin.site.register(EmployeeLeaves)
admin.site.register(LeaveApprovals)
admin.site.register(EmployeeLeaveBalance)
admin.site.register(EmployeeAttendance)
admin.site.register(Swipes)
admin.site.register(Biometric)
admin.site.register(Timesheets)
admin.site.register(TimesheetEntries)
admin.site.register(TimesheetApprovals)
