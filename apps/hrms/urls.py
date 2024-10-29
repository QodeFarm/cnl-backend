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
router.register(r'organisation', OrganisationViewSet)
router.register(r'employee_compensation_history', EmployeeCompensationHistoryViewSet)
router.register(r'organisation_branches', OrganisationBranchesViewSet)
router.register(r'employee_history', EmployeeHistoryViewSet)
router.register(r'previous_company_history', PreviousCompanyHistoryViewSet)
router.register(r'Employee_salary', EmployeesalaryViewSet)
router.register(r'hardware', HardwareViewSet)
router.register(r'salary_components', SalaryComponentsViewSet)
router.register(r'employee_salary_components', EmployeeSalaryComponentsViewSet)
router.register(r'benefits', BenefitsViewSet)
router.register(r'benefit_providers', BenefitProvidersViewSet)
router.register(r'employee_benefits', EmployeeBenefitsViewSet)
router.register(r'employee_benefit_providers', EmployeeBenefitProvidersViewSet)
router.register(r'employee_onboarding', EmployeeHardwareAssignmentViewSet)
router.register(r'employee_hardware_assignment', EmployeeHardwareAssignmentViewSet)

# router.register(r'statuses', StatusesViewSet, basename = 'status')
router.register(r'leave_types', LeaveTypesViewSet)
router.register(r'employee_leaves', EmployeeLeavesViewSet)
router.register(r'leave_approvals', LeaveApprovalsViewSet)
router.register(r'employee_leave_balance', EmployeeLeaveBalanceViewSet)

router.register(r'attendance', AttendanceViewSet)
router.register(r'swipes', SwipesViewSet)
router.register(r'biometric', BiometricViewSet)

urlpatterns = [
    path('', include(router.urls)),  
]