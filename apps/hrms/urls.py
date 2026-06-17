from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

# add your urls
router = DefaultRouter()

router.register(r'job_types', JobTypesViewSet)
router.register(r'designations', DesignationsViewSet)
router.register(r'job_codes', JobCodesViewSet)
router.register(r'departments', DepartmentsViewSet)
router.register(r'shifts', ShiftsViewSet)
router.register(r'employees_get', EmployeesViewSet)
router.register(r'employee_salary', EmployeeSalaryViewSet)
router.register(r'salary_components', SalaryComponentsViewSet)
router.register(r'employee_salary_components', EmployeeSalaryComponentsViewSet)
router.register(r'leave_types', LeaveTypesViewSet)
router.register(r'employee_leaves_get', EmployeeLeavesViewSet)
router.register(r'leave_approvals', LeaveApprovalsViewSet)
router.register(r'employee_leave_balance', EmployeeLeaveBalanceViewSet)
router.register(r'employee_attendance', EmployeeAttendanceViewSet)
router.register(r'swipes', SwipesViewSet)
router.register(r'biometric', BiometricViewSet)

# Timesheet ViewSets  — simple CRUD via DRF router.
# Convention: <resource>_get  is the router-managed ViewSet;
#             <resource>/     is the APIView with full business logic.
# (Mirrors the employee_leaves_get vs employee_leaves/ pattern.)
router.register(r'timesheet_entries', TimesheetEntriesViewSet)
router.register(r'timesheet_approvals_get', TimesheetApprovalsViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # --- existing APIView endpoints ---
    path('employee_leaves/', EmployeeLeavesView.as_view(), name='employee-leaves-list-create'),
    path('employee_leaves/<str:pk>/', EmployeeLeavesView.as_view(), name='employee-leaves-detail-update-delete'),
    path('employees/', EmployeeView.as_view(), name='employee-list-create'),
    path('employees/<str:pk>/', EmployeeView.as_view(), name='employee-detail-update-delete'),

    # --- Timesheet APIView endpoints ---
    # Full lifecycle: list, create, retrieve, update, soft-delete, restore.
    path('timesheets/', TimesheetsView.as_view(), name='timesheets-list-create'),

    # --- Timesheet → Invoice (ad-hoc billable hours) ---
    # NOTE: these fixed paths MUST be declared BEFORE 'timesheets/<str:pk>/'
    # so they are not captured as a pk.
    path('billable_timesheets/', BillableTimesheetsView.as_view(), name='billable-timesheets-list'),
    path('timesheets/create_invoice/', TimesheetInvoiceCreateView.as_view(), name='timesheet-create-invoice'),

    path('timesheets/<str:pk>/', TimesheetsView.as_view(), name='timesheets-detail-update-delete'),

    # Workflow action endpoints — each changes the approval state.
    path('timesheets/<str:pk>/submit/', TimesheetSubmitView.as_view(), name='timesheet-submit'),
    path('timesheets/<str:pk>/approve/', TimesheetApproveView.as_view(), name='timesheet-approve'),
    path('timesheets/<str:pk>/reject/', TimesheetRejectView.as_view(), name='timesheet-reject'),
    # Employee Portal URLs
    # path('api/employee/portal/login/', EmployeePortalLoginView.as_view(), name='employee_portal_login'),
    # path('api/employee/portal/logout/', EmployeePortalLogoutView.as_view(), name='employee_portal_logout'),
    # path('api/employee/portal/profile/', EmployeePortalProfileView.as_view(), name='employee_portal_profile'),
    path('employee/generate-credentials/', GenerateEmployeeCredentials.as_view()),
    path('employee/login/', EmployeePortalLoginView.as_view()),
    path('employee/logout/', EmployeePortalLogoutView.as_view(), name='employee_logout'),
    path('employees/generate-credentials/<uuid:employee_id>/', GenerateEmployeeCredentialsView.as_view(), name='generate_employee_credentials'),
    path('employees/send-credentials/<uuid:employee_id>/', 
         SendEmployeeCredentialsView.as_view(), 
         name='send-employee-credentials'),
]