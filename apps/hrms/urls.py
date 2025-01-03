from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

#add your urls
router = DefaultRouter()

router.register(r'job_types', JobTypesViewSet)
router.register(r'designations', DesignationsViewSet)
router.register(r'job_codes', JobCodesViewSet)
router.register(r'departments', DepartmentsViewSet)
router.register(r'shifts', ShiftsViewSet)
router.register(r'employees', EmployeesViewSet)
router.register(r'employee_details', EmployeeDetailsViewSet)
router.register(r'employee_salary', EmployeeSalaryViewSet)
router.register(r'salary_components', SalaryComponentsViewSet)
router.register(r'employee_salary_components', EmployeeSalaryComponentsViewSet)
router.register(r'leave_types', LeaveTypesViewSet)
router.register(r'employee_leaves', EmployeeLeavesViewSet)
router.register(r'leave_approvals', LeaveApprovalsViewSet)
router.register(r'employee_leave_balance', EmployeeLeaveBalanceViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'swipes', SwipesViewSet)
router.register(r'biometric', BiometricViewSet)

urlpatterns = [
    path('', include(router.urls)),  
    path('employee/', EmployeeView.as_view(), name='employee_list_create'),
    path('employee/<str:pk>/', EmployeeView.as_view(), name='employee_detail_update_delete'),
]