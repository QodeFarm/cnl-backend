from rest_framework import viewsets
from apps.hrms.filters import EmployeesFilter
from .models import *
from .serializers import *
from config.utils_filter_methods import list_filtered_objects
from config.utils_methods import list_all_objects, create_instance, update_instance
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import OrderingFilter


class JobTypesViewSet(viewsets.ModelViewSet):
    queryset = JobTypes.objects.all()
    serializer_class = JobTypesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
		
class DesignationsViewSet(viewsets.ModelViewSet):
    queryset = Designations.objects.all()
    serializer_class = DesignationsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
		
class JobCodesViewSet(viewsets.ModelViewSet):
    queryset = JobCodes.objects.all()
    serializer_class = JobCodesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs) 
		
class DepartmentsViewSet(viewsets.ModelViewSet):
    queryset = Departments.objects.all()
    serializer_class = DepartmentsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)  
		
class ShiftsViewSet(viewsets.ModelViewSet):
    queryset = Shifts.objects.all()
    serializer_class = ShiftsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
		
class EmployeesViewSet(viewsets.ModelViewSet):
    queryset = Employees.objects.all()
    serializer_class = EmployeesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
		
class EmployeeDetailsViewSet(viewsets.ModelViewSet):
    queryset = EmployeeDetails.objects.all()
    serializer_class = EmployeeDetailsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
		
class OrganisationViewSet(viewsets.ModelViewSet):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs) 
		
class EmployeeCompensationHistoryViewSet(viewsets.ModelViewSet):
    queryset = EmployeeCompensationHistory.objects.all()
    serializer_class = EmployeeCompensationHistorySerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs) 
		
class OrganisationBranchesViewSet(viewsets.ModelViewSet):
    queryset = OrganisationBranches.objects.all()
    serializer_class = OrganisationBranchesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
		
class EmployeeHistoryViewSet(viewsets.ModelViewSet):
    queryset = EmployeeHistory.objects.all()
    serializer_class = EmployeeHistorySerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)    

class PreviousCompanyHistoryViewSet(viewsets.ModelViewSet):
    queryset = PreviousCompanyHistory.objects.all()
    serializer_class = PreviousCompanyHistorySerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)   

class EmployeesalaryViewSet(viewsets.ModelViewSet):
    queryset = Employeesalary.objects.all()
    serializer_class = EmployeesalarySerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)		

class HardwareViewSet(viewsets.ModelViewSet):
    queryset = Hardware.objects.all()
    serializer_class = HardwareSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs) 


class SalaryComponentsViewSet(viewsets.ModelViewSet):
    queryset = SalaryComponents.objects.all()
    serializer_class = SalaryComponentsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)		

class EmployeeSalaryComponentsViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSalaryComponents.objects.all()
    serializer_class = EmployeeSalaryComponentsSerializer 

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)  
		
class BenefitsViewSet(viewsets.ModelViewSet):
    queryset = Benefits.objects.all()
    serializer_class = BenefitsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs) 

class BenefitProvidersViewSet(viewsets.ModelViewSet):
    queryset = BenefitProviders.objects.all()
    serializer_class = BenefitProvidersSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)	

class EmployeeBenefitsViewSet(viewsets.ModelViewSet):
    queryset = EmployeeBenefits.objects.all()
    serializer_class = EmployeeBenefitsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs) 		

class EmployeeBenefitProvidersViewSet(viewsets.ModelViewSet):
    queryset = EmployeeBenefitProviders.objects.all()
    serializer_class = EmployeeBenefitProvidersSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)    

class EmployeeOnbordingViewSet(viewsets.ModelViewSet):
    queryset = EmployeeOnboarding.objects.all()
    serializer_class = EmployeeOnbordingSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
 
class EmployeeHardwareAssignmentViewSet(viewsets.ModelViewSet):
    queryset = EmployeeHardwareAssignment.objects.all()
    serializer_class = EmployeeHardwareAssignmentSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)  
        
# //=====================leaves====================================      

# class StatusesViewSet(viewsets.ModelViewSet):
#     queryset = Statuses.objects.all()
#     serializer_class = StatusesSerializer

#     def list(self, request, *args, **kwargs):
#         return list_all_objects(self, request, *args, **kwargs)

#     def create(self, request, *args, **kwargs):
#         return create_instance(self, request, *args, **kwargs)

#     def update(self, request, *args, **kwargs):
#         return update_instance(self, request, *args, **kwargs)
    
class LeaveTypesViewSet(viewsets.ModelViewSet):
    queryset = LeaveTypes.objects.all()
    serializer_class = LeavesTypesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class EmployeeLeavesViewSet(viewsets.ModelViewSet):
    queryset = EmployeeLeaves.objects.all()
    serializer_class = EmployeeLeavesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
 
class LeaveApprovalsViewSet(viewsets.ModelViewSet):
    queryset = LeaveApprovals.objects.all()
    serializer_class = LeaveApprovalsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs) 
        
class EmployeeLeaveBalanceViewSet(viewsets.ModelViewSet):
    queryset = EmployeeLeaveBalance.objects.all()
    serializer_class = EmployeeLeaveBalanceSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
         
# =====================attendance====================================      

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)    

class SwipesViewSet(viewsets.ModelViewSet):
    queryset = Swipes.objects.all()
    serializer_class = SwipesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)    

class BiometricViewSet(viewsets.ModelViewSet):
    queryset = Biometric.objects.all()
    serializer_class = BiometricSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)    



# class DesignationsView(viewsets.ModelViewSet):
#     queryset = Designations.objects.all()
#     serializer_class = DesignationsSerializer

#     def list(self, request, *args, **kwargs):
#         return list_all_objects(self, request, *args, **kwargs)

#     def create(self, request, *args, **kwargs):
#         return create_instance(self, request, *args, **kwargs)

#     def update(self, request, *args, **kwargs):
#         return update_instance(self, request, *args, **kwargs)

# class DepartmentsView(viewsets.ModelViewSet):
#     queryset = Departments.objects.all()
#     serializer_class = DepartmentsSerializer

#     def list(self, request, *args, **kwargs):
#         return list_all_objects(self, request, *args, **kwargs)

#     def create(self, request, *args, **kwargs):
#         return create_instance(self, request, *args, **kwargs)

#     def update(self, request, *args, **kwargs):
#         return update_instance(self, request, *args, **kwargs)

# class EmployeesView(viewsets.ModelViewSet):
#     queryset = Employees.objects.all()
#     serializer_class = EmployeesSerializer
#     filter_backends = [DjangoFilterBackend,OrderingFilter]
#     filterset_class = EmployeesFilter
#     ordering_fields = []

#     def list(self, request, *args, **kwargs):
#         return list_filtered_objects(self, request, Employees,*args, **kwargs)

#     def create(self, request, *args, **kwargs):
#         return create_instance(self, request, *args, **kwargs)

#     def update(self, request, *args, **kwargs):
#         return update_instance(self, request, *args, **kwargs)
