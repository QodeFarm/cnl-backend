import logging
from requests import Response
from rest_framework import viewsets, status
from django.db import transaction
from rest_framework.views import APIView
from django.http import  Http404
from django.shortcuts import get_object_or_404
from .models import JobTypes, Designations, JobCodes, Departments, Shifts, Employees, EmployeeSalary, SalaryComponents, EmployeeSalaryComponents, LeaveTypes, EmployeeLeaves, LeaveApprovals, EmployeeLeaveBalance, EmployeeAttendance, Swipes, Biometric, TimesheetApprovals, TimesheetEntries, Timesheets
from .serializers import EmployeePortalLoginSerializer, JobTypesSerializer, DesignationsSerializer, JobCodesSerializer, DepartmentsSerializer, ShiftsSerializer, EmployeesSerializer, EmployeeSalarySerializer, SalaryComponentsSerializer, EmployeeSalaryComponentsSerializer, LeavesTypesSerializer, EmployeeLeavesSerializer, LeaveApprovalsSerializer, EmployeeLeaveBalanceSerializer, EmployeeAttendanceSerializer, SwipesSerializer, BiometricSerializer, TimesheetApprovalsSerializer, TimesheetEntriesSerializer, TimesheetsSerializer
from config.utils_methods import build_response, generic_data_creation, get_object_or_none, get_related_data, list_all_objects, create_instance, update_instance, update_multi_instances, soft_delete, validate_input_pk, validate_multiple_data, validate_payload_data, validate_put_method_data
from config.utils_filter_methods import filter_response, list_filtered_objects
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from apps.masters.models import Statuses
from apps.hrms.filters import DepartmentsFilter, DesignationsFilter, EmployeeSalaryComponentsFilter, EmployeesFilter, EmployeeSalaryFilter, EmployeeLeavesFilter, JobCodesFilter, JobTypesFilter, LeaveApprovalsFilter, EmployeeLeaveBalanceFilter, EmployeeAttendanceFilter, LeaveTypesFilter, SalaryComponentsFilter, ShiftsFilter, SwipesFilter, TimesheetsFilter, TimesheetEntriesFilter, TimesheetApprovalsFilter
from django.utils.timezone import now
from datetime import datetime
from decimal import Decimal

def get_current_year():
    return str(now().year)

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)

class JobTypesViewSet(viewsets.ModelViewSet):
    queryset = JobTypes.objects.all().order_by('-created_at')	
    serializer_class = JobTypesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = JobTypesFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Job Types"
    log_pk_field = "job_type_id"
    log_display_field = "job_type_name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, JobTypes,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

		
class DesignationsViewSet(viewsets.ModelViewSet):
    queryset = Designations.objects.all().order_by('-created_at')
    serializer_class = DesignationsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = DesignationsFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Designations"
    log_pk_field = "designation_id"
    log_display_field = "designation_name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Designations,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
		
class JobCodesViewSet(viewsets.ModelViewSet):
    queryset = JobCodes.objects.all().order_by('-created_at')
    serializer_class = JobCodesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = JobCodesFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Job Codes"
    log_pk_field = "job_code_id"
    log_display_field = "job_code"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, JobCodes,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs) 
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
		
class DepartmentsViewSet(viewsets.ModelViewSet):
    queryset = Departments.objects.all().order_by('-created_at')
    serializer_class = DepartmentsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = DepartmentsFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Departments"
    log_pk_field = "department_id"
    log_display_field = "department_name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Departments,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)  
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
		
class ShiftsViewSet(viewsets.ModelViewSet):
    queryset = Shifts.objects.all().order_by('-created_at')
    serializer_class = ShiftsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ShiftsFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Shifts"
    log_pk_field = "shift_id"
    log_display_field = "shift_name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Shifts,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
		
class EmployeesViewSet(viewsets.ModelViewSet):
    queryset = Employees.objects.all().order_by('-created_at')	
    serializer_class = EmployeesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = EmployeesFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Employees"
    log_pk_field = "employee_id"
    log_display_field = "full_name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Employees,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
		
class EmployeeSalaryViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSalary.objects.all().order_by('-created_at')	
    serializer_class = EmployeeSalarySerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = EmployeeSalaryFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Employee Salary"
    log_pk_field = "salary_id"
    log_display_field = "salary_amount"
    
    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, EmployeeSalary,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)	
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)	

class SalaryComponentsViewSet(viewsets.ModelViewSet):
    queryset = SalaryComponents.objects.all().order_by('-created_at')	
    serializer_class = SalaryComponentsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = SalaryComponentsFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Salary Component"
    log_pk_field = "component_id"
    log_display_field = "component_name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, SalaryComponents,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)		

class EmployeeSalaryComponentsViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSalaryComponents.objects.all().order_by('-created_at')	
    serializer_class = EmployeeSalaryComponentsSerializer 
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = EmployeeSalaryComponentsFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Employee Salary Component"
    log_pk_field = "employee_component_id"
    log_display_field = "component_amount"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, EmployeeSalaryComponents,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)  
		
# //=====================leaves====================================      

class LeaveTypesViewSet(viewsets.ModelViewSet):
    queryset = LeaveTypes.objects.all().order_by('-created_at')
    serializer_class = LeavesTypesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = LeaveTypesFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Leave Types"
    log_pk_field = "leave_type_id"
    log_display_field = "leave_type_name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, LeaveTypes,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
    
class EmployeeLeavesViewSet(viewsets.ModelViewSet):
    queryset = EmployeeLeaves.objects.all().order_by('-created_at')	
    serializer_class = EmployeeLeavesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = EmployeeLeavesFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Employee Leaves"
    log_pk_field = "leave_id"
    log_display_field = "leave_id"
    
    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, EmployeeLeaves,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
    
class LeaveApprovalsViewSet(viewsets.ModelViewSet):
    queryset = LeaveApprovals.objects.all().order_by('-created_at')	
    serializer_class = LeaveApprovalsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = LeaveApprovalsFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Leave Approvals"
    log_pk_field = "approval_id"
    log_display_field = "approval_id"
    
    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, LeaveApprovals,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs) 

class EmployeeLeaveBalanceViewSet(viewsets.ModelViewSet):
    queryset = EmployeeLeaveBalance.objects.all().order_by('-created_at')	
    serializer_class = EmployeeLeaveBalanceSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = EmployeeLeaveBalanceFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Employee Leave Balance"
    log_pk_field = "balance_id"
    log_display_field = "leave_balance"
    
    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, EmployeeLeaveBalance,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
         
# =====================attendance====================================      
    
class EmployeeAttendanceViewSet(viewsets.ModelViewSet):
    queryset = EmployeeAttendance.objects.all().order_by('-created_at')
    serializer_class = EmployeeAttendanceSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = EmployeeAttendanceFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Employee Attendance"
    log_pk_field = "employee_attendance_id"
    log_display_field = "attendance_date"
    
    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, EmployeeAttendance,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        # Validate to prevent duplicates
        validation_response = self.validate(request.data)
        if validation_response:
            return validation_response
        
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs) 
    

    def validate(self, data):
        employee_id = data.get('employee_id')
        attendance_date = data.get('attendance_date')

        # Check for duplicate attendance date for the employee
        if EmployeeAttendance.objects.filter(employee_id=employee_id, attendance_date=attendance_date).exists():
            # Returning response with build_response for duplicate records
            message = f"Attendance already exists for employee {employee_id} on {attendance_date}. Please select another attendance_date."
            return build_response(count=0,message=message,data=[],status_code=status.HTTP_400_BAD_REQUEST)
        return None    

class SwipesViewSet(viewsets.ModelViewSet):
    queryset = Swipes.objects.all().order_by('-created_at')	
    serializer_class = SwipesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = SwipesFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Swipes"
    log_pk_field = "swipe_id"
    log_display_field = "swipe_time"
    
    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Swipes,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs) 
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)   

class BiometricViewSet(viewsets.ModelViewSet):
    queryset = Biometric.objects.all().order_by('-created_at')
    serializer_class = BiometricSerializer
    
    #log actions
    log_actions = True
    log_module_name = "Biometric"
    log_pk_field = "biometric_id"
    log_display_field = "biometric_entry_id"

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)    


# ------------  API --------------  

class EmployeeLeavesView(APIView):
    """
    API ViewSet for handling Lead creation and related data.
    """

    def get_object(self, pk):
        try:
            return EmployeeLeaves.objects.get(pk=pk)
        except EmployeeLeaves.DoesNotExist:
            logger.warning(f"EmployeeLeaves with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
           
    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            result = validate_input_pk(self, kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            logger.info("Retrieving all EmployeeLeaves")

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 

            queryset = EmployeeLeaves.objects.all().order_by('-created_at')

            # Apply filters manually
            if request.query_params:
                filterset = EmployeeLeavesFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs 

            total_count = EmployeeLeaves.objects.count()

            serializer = EmployeeLeavesSerializer(queryset, many=True)
            logger.info("EmployeeLeaves data retrieved successfully.")
            # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
            return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a EmployeeLeaves and its related data (LeaveApprovals).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)
            
            # Retrieve the EmployeeLeaves instance
            employee_leaves = get_object_or_404(EmployeeLeaves, pk=pk)
            employee_leaves_serializer = EmployeeLeavesSerializer(employee_leaves)

            # Retrieve LeaveApprovals data
            approval_data = get_related_data(LeaveApprovals, LeaveApprovalsSerializer, 'leave_id', pk)
            leave_approvals_data = approval_data[0] if approval_data else {}

            # Customizing the response data
            custom_data = {
                "employee_leaves": employee_leaves_serializer.data,
                "leave_approvals": leave_approvals_data
            }
            logger.info("EmployeeLeaves and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error("EmployeeLeaves with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("An error occurred while retrieving EmployeeLeaves with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a vendor and its related attachments, and addresses.
        """
        try:
            # Get the EmployeeLeaves instance
            instance = EmployeeLeaves.objects.get(pk=pk)

            # Delete the main EmployeeLeaves instance
            instance.is_deleted=True
            instance.save()

            logger.info(f"EmployeeLeaves with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except EmployeeLeaves.DoesNotExist:
            logger.warning(f"EmployeeLeaves with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting EmployeeLeaves with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
     
    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        """
        Restores a soft-deleted EmployeeLeaves record (is_deleted=True → is_deleted=False).
        """
        try:
            instance = EmployeeLeaves.objects.get(pk=pk)

            if not instance.is_deleted:
                logger.info(f"EmployeeLeaves with ID {pk} is already active.")
                return build_response(0, "Record is already active", [], status.HTTP_400_BAD_REQUEST)

            instance.is_deleted = False
            instance.save()

            logger.info(f"EmployeeLeaves with ID {pk} restored successfully.")
            return build_response(1, "Record restored successfully", [], status.HTTP_200_OK)

        except EmployeeLeaves.DoesNotExist:
            logger.warning(f"EmployeeLeaves with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error restoring EmployeeLeaves with ID {pk}: {str(e)}")
            return build_response(0, "Record restoration failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # Handling POST requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Extracting data from the request
        given_data = request.data

        # ---------------------- D A T A   V A L I D A T I O N ----------------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        errors = {}        

        # Validate EmployeeLeaves Data
        employee_leaves_data = given_data.pop('employee_leaves', None)  # parent_data

        # Ensure mandatory data is present
        if not employee_leaves_data:
            logger.error("EmployeeLeaves is mandatory but not provided.")
            return build_response(0, "EmployeeLeaves is mandatory", [], status.HTTP_400_BAD_REQUEST)
        else:
            employee_leaves_error = validate_payload_data(self, employee_leaves_data, EmployeeLeavesSerializer)

            if employee_leaves_error:
                errors["employee_leaves"] = employee_leaves_error

            # Additional validation for start_date and end_date
            start_date = employee_leaves_data.get('start_date')
            end_date = employee_leaves_data.get('end_date')

            if start_date and end_date:
                try:
                    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")

                    # if start_date_obj > end_date_obj:
                    #     errors["date_validation"] = "Start date must be earlier than or equal to the end date."
                    if end_date_obj < start_date_obj:
                        errors["date_validation"] = "End date must be later than or equal to the start date."
                except ValueError as e:
                    logger.error(f"Date parsing error: {e}")
                    errors["date_format"] = "Invalid date format. Please use YYYY-MM-DD."

        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """

        # Hence the data is validated , further it can be created.
        custom_data = {
            'employee_leaves':{},
            'leave_approvals':{}
            }

        # Create EmployeeLeaves Data
        new_employee_leaves_data = generic_data_creation(self, [employee_leaves_data], EmployeeLeavesSerializer)
        employee_leaves_data = new_employee_leaves_data[0]
        custom_data["employee_leaves"] = employee_leaves_data
        logger.info('EmployeeLeaves - created*')

        leave_id = employee_leaves_data.get("leave_id", None)  # Fetch journal_entry_id from mew instance

        if leave_id:  # Ensure leave_id is valid

            # Set default approvals status to 'Open'
            status_instance = get_object_or_none(Statuses, status_name='Open')  # Assuming the default status is 'Open'
            if status_instance is not None:
                # Directly use status_id in balance_payload
                errors["leave_approvals"] = {"status_id": [status_instance.status_id]}
            else:
                errors["leave_approvals"] = {"status_id": ["Invalid status_id."]}
                # ✅ Return proper Response
                return build_response(0, "ValidationError: Invalid status", errors, status.HTTP_400_BAD_REQUEST)

            manager_id = employee_leaves_data.get("employee", {}).get("manager_id", None)  # Get manager_id from employee_leaves

            # Ensure manager_id exists
            if not manager_id:
                errors["leave_approvals"] = {"approver_id": ["Manager not found."]}
                # ✅ Return proper Response
                return build_response(0, "ValidationError: Manager not found", errors, status.HTTP_400_BAD_REQUEST)

            balance_payload = {
                "leave_id": leave_id,
                "status_id": status_instance.status_id,  # Using the status ID
                "approver_id": manager_id,  # Using manager_id as approver
            }

            leave_approvals = generic_data_creation(self, [balance_payload], LeaveApprovalsSerializer)
            custom_data["leave_approvals"] = leave_approvals[0]
            logger.info('LeaveApprovals - created')

        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)

    # Handling put requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"put\" not allowed."]
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):
        #----------------------------------- D A T A  V A L I D A T I O N -----------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        # Get the given data from request
        given_data = request.data

        # Validated EmployeeLeaves Data
        employee_leaves_data = given_data.pop('employee_leaves', None)
        if employee_leaves_data:
            employee_leaves_data['leave_id'] = pk
            employee_leaves_error = validate_payload_data(self, employee_leaves_data , EmployeeLeavesSerializer)

        # Validated LeaveApprovals Data
        leave_approvals_data = given_data.pop('leave_approvals', None)
        if leave_approvals_data:
            exclude_fields = ['leave_id']
            leave_approvals_error = validate_multiple_data(self, leave_approvals_data,LeaveApprovalsSerializer, exclude_fields)
        else:
            leave_approvals_error = [] 
            
        # Ensure mandatory data is present
        if not employee_leaves_data:
            logger.error("EmployeeLeaves data mandatory but not provided.")
            return build_response(0, "EmployeeLeaves data mandatory but not provided.", [], status.HTTP_400_BAD_REQUEST)
        
        errors = {}
        if employee_leaves_error:
            errors["employee_leaves"] = employee_leaves_error
        if leave_approvals_error:
            errors["leave_approvals"] = leave_approvals_error
        if errors:
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)
            
            # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#
        try:
            # Update the 'EmployeeLeaves'
            if employee_leaves_data:
                emp_leaves_data = update_multi_instances(self, pk, [employee_leaves_data], EmployeeLeaves, EmployeeLeavesSerializer,[],main_model_related_field='leave_id', current_model_pk_field='leave_id')

            # Update LeaveApprovals Data
            approval_data = update_multi_instances(self,pk, leave_approvals_data, LeaveApprovals, LeaveApprovalsSerializer, ['leave_id'], main_model_related_field='leave_id', current_model_pk_field='approval_id')
            custom_data = [
                {"employee_leaves":emp_leaves_data[0]},
                {"leave_approvals":approval_data[0] if approval_data else {}}
            ]

            return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)
        except Exception:
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#------------------------------  employeee API ---------------------------------------- 

class EmployeeView(APIView):
    """
    API ViewSet for handling Lead creation and related data.
    """

    def get_object(self, pk):
        try:
            return Employees.objects.get(pk=pk)
        except Employees.DoesNotExist:
            logger.warning(f"Employees with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
           
    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            result = validate_input_pk(self, kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            logger.info("Retrieving all Employees")

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 

            queryset = Employees.objects.all().order_by('-created_at')	

            # Apply filters manually
            if request.query_params:
                filterset = EmployeesFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs 

            total_count = Employees.objects.count()

            serializer = EmployeesSerializer(queryset, many=True)
            logger.info("Employees data retrieved successfully.")
            # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
            return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a Employees and its related data (EmployeeDetails).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)
            
            # Retrieve the Employees instance
            employee = get_object_or_404(Employees, pk=pk)
            employee_serializer = EmployeesSerializer(employee)

            # Retrieve EmployeeLeaveBalance data
            employee_leave_balance_data = get_related_data(EmployeeLeaveBalance, EmployeeLeaveBalanceSerializer, 'employee_id', pk)
            emp_leave_balance_data = employee_leave_balance_data if employee_leave_balance_data else []

            # Customizing the response data
            custom_data = {
                "employee": employee_serializer.data,
                "employee_leave_balance": emp_leave_balance_data
            }
            logger.info("Employee and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error("Employee with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("An error occurred while retrieving Employees with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a vendor and its related attachments, and addresses.
        """
        try:
            # Get the Employees instance
            instance = Employees.objects.get(pk=pk)

            # Delete the main vendor instance
            instance.is_deleted=True
            instance.save()

            logger.info(f"Vendor with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except Employees.DoesNotExist:
            logger.warning(f"Employees with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting Employees with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        """
        Restores a soft-deleted Employees record (is_deleted=True → is_deleted=False).
        """
        try:
            instance = Employees.objects.get(pk=pk)

            if not instance.is_deleted:
                logger.info(f"Employees with ID {pk} is already active.")
                return build_response(0, "Record is already active", [], status.HTTP_400_BAD_REQUEST)

            instance.is_deleted = False
            instance.save()

            logger.info(f"Employees with ID {pk} restored successfully.")
            return build_response(1, "Record restored successfully", [], status.HTTP_200_OK)

        except Employees.DoesNotExist:
            logger.warning(f"Employees with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error restoring Employees with ID {pk}: {str(e)}")
            return build_response(0, "Record restoration failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    # Handling POST requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Extracting data from the request
        given_data = request.data

        # ---------------------- D A T A   V A L I D A T I O N ----------------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        errors = {}        

        # Validate Employees Data
        employee_data = given_data.pop('employee', None)  # parent_data

        # Ensure mandatory data is present
        if not employee_data:
            logger.error("Employee is mandatory but not provided.")
            return build_response(0, "Employee is mandatory", [], status.HTTP_400_BAD_REQUEST)
        else:

            # ---------------------- P I C T U R E   V A L I D A T I O N ----------------------#
            picture_data = employee_data.get('picture', None)

            if not picture_data:
                return build_response(
                    0,
                    "Employee Govt ID proof picture is mandatory.",
                    [],
                    status.HTTP_400_BAD_REQUEST
                )

            if not isinstance(picture_data, list):
                return build_response(
                    0,
                    "'picture' field in employee must be a list.",
                    [],
                    status.HTTP_400_BAD_REQUEST
                )

            for attachment in picture_data:
                if not all(key in attachment for key in ['uid', 'name', 'attachment_name', 'file_size', 'attachment_path']):
                    return build_response(
                        0,
                        "Missing required fields in some picture data.",
                        [],
                        status.HTTP_400_BAD_REQUEST
                    )

            employee_error = validate_payload_data(self, employee_data, EmployeesSerializer)

            if employee_error:
                errors["employee"] = employee_error

        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """

        # Hence the data is validated , further it can be created.
        custom_data = {
            'employee': {},
            'employee_leave_balance': []
        }

        # Create Employees Data
        new_employee_data = generic_data_creation(self, [employee_data], EmployeesSerializer)
        employee_data = new_employee_data[0]
        custom_data["employee"] = employee_data
        logger.info('Employee - created*')

        # Fetch employee_id from the new instance
        employee_id = employee_data.get("employee_id", None)

        if employee_id:  # Ensure employee_id is valid
            # Fetch leave types data
            leave_types = LeaveTypes.objects.values('leave_type_name', 'leave_type_id', 'max_days_allowed')

            # Create EmployeeLeaveBalance records for each leave type
            for leave_type in leave_types:
                balance_payload = {
                    "employee_id": employee_id,
                    "leave_type_id": leave_type.get('leave_type_id'),
                    "leave_balance": leave_type.get('max_days_allowed'),
                    "year": get_current_year(),
                }

                employee_leave_balance = generic_data_creation(
                    self,
                    [balance_payload],
                    EmployeeLeaveBalanceSerializer
                )

                # Append the created leave balance to custom_data
                custom_data["employee_leave_balance"].append(employee_leave_balance[0])

            logger.info('EmployeeLeaveBalance - created*')

        else:
            return build_response(
                0,
                "EmployeeLeaveBalance record creation failed.",
                [],
                status.HTTP_400_BAD_REQUEST
            )

        return build_response(
            1,
            "Record created successfully",
            custom_data,
            status.HTTP_201_CREATED
        )
    
    # @transaction.atomic
    # def create(self, request, *args, **kwargs):
    #     # Extracting data from the request
    #     given_data = request.data

    #     # ---------------------- D A T A   V A L I D A T I O N ----------------------------------#
    #     """
    #     All the data in request will be validated here. it will handle the following errors:
    #     - Invalid data types
    #     - Invalid foreign keys
    #     - nulls in required fields
    #     """
    #     errors = {}        

    #     # Validate Employees Data
    #     employee_data = given_data.pop('employee', None)  # parent_data

    #     # Ensure mandatory data is present
    #     if not employee_data:
    #         logger.error("Employee is mandatory but not provided.")
    #         return build_response(0, "Employee is mandatory", [], status.HTTP_400_BAD_REQUEST)
    #     else:
    #         employee_error = validate_payload_data(self, employee_data, EmployeesSerializer)

    #         if employee_error:
    #             errors["employee"] = employee_error

    #     if errors:
    #         return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

    #     # ---------------------- D A T A   C R E A T I O N ----------------------------#
    #     """
    #     After the data is validated, this validated data is created as new instances.
    #     """

    #     # Hence the data is validated , further it can be created.
    #     custom_data = {
    #         'employee':{},
    #         'employee_leave_balance':[]
    #         }

    #     # Create Employees Data
    #     new_employee_data = generic_data_creation(self, [employee_data], EmployeesSerializer)
    #     employee_data = new_employee_data[0]
    #     custom_data["employee"] = employee_data
    #     logger.info('Employee - created*')

    #     # Fetch employee_id from the new instance
    #     employee_id = employee_data.get("employee_id", None)

    #     if employee_id:  # Ensure employee_id is valid
    #         # Fetch leave types data
    #         leave_types = LeaveTypes.objects.values('leave_type_name', 'leave_type_id', 'max_days_allowed')

    #         # Create EmployeeLeaveBalance records for each leave type
    #         for leave_type in leave_types:
    #             balance_payload = {
    #             "employee_id":employee_id,
    #             "leave_type_id":leave_type.get('leave_type_id'),
    #             "leave_balance":leave_type.get('max_days_allowed'),
    #             "year":get_current_year(),
    #             }

    #             employee_leave_balance = generic_data_creation(self, [balance_payload], EmployeeLeaveBalanceSerializer)
    #             # Append the created leave balance to custom_data
    #             custom_data["employee_leave_balance"].append(employee_leave_balance[0])

    #         logger.info('EmployeeLeaveBalance - created*')

    #     else:
    #         return build_response(0, "EmployeeLeaveBalance record creation failed.", [], status.HTTP_400_BAD_REQUEST)

    #     return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)
    
    # Handling put requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"put\" not allowed."]
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):
        #----------------------------------- D A T A  V A L I D A T I O N -----------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        # Get the given data from request
        given_data = request.data

        # Validated Employees Data
        employee_data = given_data.pop('employee', None)
        if employee_data:
            employee_data['employee_id'] = pk
            employee_error = validate_payload_data(self, employee_data , EmployeesSerializer)

        # Ensure mandatory data is present
        if not employee_data:
            logger.error("Employee data mandatory but not provided.")
            return build_response(0, "Employee data mandatory but not provided.", [], status.HTTP_400_BAD_REQUEST)
        
        errors = {}
        if employee_error:
            errors["employee"] = employee_error
        if errors:
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)
            
            # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#
        try:
            # Update the 'Employees'
            if employee_data:
                update_fields = []# No need to update any fields
                emp_data = update_multi_instances(self, pk, [employee_data], Employees, EmployeesSerializer, update_fields,main_model_related_field='employee_id', current_model_pk_field='employee_id')

            custom_data = [
                {"employee":emp_data[0]},
            ]

            return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)
        except Exception:
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==============================================================================
#  TIMESHEETS  —  ViewSets (simple CRUD) + APIView (full lifecycle)
# ==============================================================================

# ------------------------------------------------------------------------------
#  Helper used by both TimesheetsView.create() and TimesheetsView.update()
# ------------------------------------------------------------------------------

def _compute_total_hours(timesheet_id):
    """
    Sum hours_worked for all entries that belong to the given timesheet_id.
    Returns a Decimal so it can be stored directly in the DecimalField.
    """
    from django.db.models import Sum
    result = TimesheetEntries.objects.filter(
        timesheet_id=timesheet_id
    ).aggregate(total=Sum('hours_worked'))
    return result['total'] or Decimal('0.00')


def _compute_billable_amount(timesheet_id, total_hours):
    """
    Compute billable_amount = total_hours * billing_rate, but only when the
    timesheet is marked billable and a rate is set. Returns None otherwise
    (so non-billable / internal timesheets keep a clean null).
    """
    ts = Timesheets.objects.filter(pk=timesheet_id).only(
        'is_billable', 'billing_rate'
    ).first()
    if ts and ts.is_billable and ts.billing_rate is not None:
        return Decimal(str(total_hours)) * ts.billing_rate
    return None


def _get_timesheet_status(timesheet_id):
    """
    Return the current approval status_name for a timesheet, or 'Draft' when
    no TimesheetApprovals record exists yet.
    """
    approval = TimesheetApprovals.objects.filter(
        timesheet_id=timesheet_id
    ).select_related('status_id').first()
    if approval is None:
        return 'Draft'
    return approval.status_id.status_name


# ------------------------------------------------------------------------------
#  Simple ModelViewSet for TimesheetEntries  (individual entry CRUD)
# ------------------------------------------------------------------------------

class TimesheetEntriesViewSet(viewsets.ModelViewSet):
    """
    Standard CRUD for individual timesheet entries.

    Use this ViewSet when you need to:
      - List all entries (with filtering by timesheet_id, employee, work_date)
      - Retrieve a single entry
      - Create / update / soft-delete a single entry

    NOTE: Creating entries individually via this ViewSet does NOT recompute
    the parent Timesheets.total_hours.  Use the TimesheetsView (POST / PUT)
    to manage a full timesheet with entries in a single atomic call, which
    does recompute total_hours automatically.
    """
    queryset = TimesheetEntries.objects.all().order_by('-created_at')
    serializer_class = TimesheetEntriesSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = TimesheetEntriesFilter
    ordering_fields = ['created_at']

    # Audit log fields — same pattern as every other ViewSet in this file.
    log_actions = True
    log_module_name = "Timesheet Entries"
    log_pk_field = "entry_id"
    log_display_field = "work_date"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, TimesheetEntries, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)


# ------------------------------------------------------------------------------
#  Simple ModelViewSet for TimesheetApprovals  (approval record CRUD)
# ------------------------------------------------------------------------------

class TimesheetApprovalsViewSet(viewsets.ModelViewSet):
    """
    Standard CRUD for timesheet approval records.

    Managers use PATCH / PUT on this ViewSet to:
      - Approve a timesheet: set status_id to the 'Approved' Statuses UUID
        and populate approval_date.
      - Reject  a timesheet: set status_id to the 'Rejected' Statuses UUID,
        populate approval_date, and optionally set rejection_reason.

    The frontend approval screen (Timesheet Approvals) calls this ViewSet.
    """
    queryset = TimesheetApprovals.objects.all().order_by('-created_at')
    serializer_class = TimesheetApprovalsSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = TimesheetApprovalsFilter
    ordering_fields = ['created_at']

    # Audit log fields.
    log_actions = True
    log_module_name = "Timesheet Approvals"
    log_pk_field = "timesheet_approval_id"
    log_display_field = "approval_date"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, TimesheetApprovals, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)


# ------------------------------------------------------------------------------
#  Full lifecycle APIView for Timesheets  (mirrors EmployeeLeavesView exactly)
# ------------------------------------------------------------------------------

class TimesheetsView(APIView):
    """
    Handles the complete timesheet lifecycle in a single API surface.

    GET    /hrms/timesheets/         -> paginated, filtered list
    GET    /hrms/timesheets/<pk>/    -> full detail: header + entries + approval
    POST   /hrms/timesheets/         -> create header + entries atomically
    PUT    /hrms/timesheets/<pk>/    -> replace header + entries atomically
    DELETE /hrms/timesheets/<pk>/    -> soft-delete (Draft timesheets only)
    PATCH  /hrms/timesheets/<pk>/    -> restore a soft-deleted timesheet

    Business rules enforced here:
      - A timesheet cannot be edited or deleted once it has been submitted
        (i.e. a TimesheetApprovals record with status Open or Approved exists).
      - A rejected timesheet CAN be edited and re-submitted.
      - At least one entry row is required.
      - Duplicate detection: same employee + start_date + end_date is blocked.
    """

    # ------------------------------------------------------------------
    # LIST
    # ------------------------------------------------------------------

    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:
            result = validate_input_pk(self, kwargs['pk'])
            return result if result else self.retrieve(request, *args, **kwargs)

        try:
            logger.info("Retrieving all Timesheets")

            page  = int(request.query_params.get('page',  1))
            limit = int(request.query_params.get('limit', 10))

            queryset = Timesheets.objects.all().order_by('-created_at')

            if request.query_params:
                filterset = TimesheetsFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs

            total_count = Timesheets.objects.count()
            serializer  = TimesheetsSerializer(queryset, many=True)

            logger.info("Timesheets retrieved successfully.")
            return filter_response(
                queryset.count(), "Success", serializer.data,
                page, limit, total_count, status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Error retrieving timesheets: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ------------------------------------------------------------------
    # DETAIL
    # ------------------------------------------------------------------

    def retrieve(self, request, *args, **kwargs):
        """
        Returns the full timesheet detail in one response:
          {
            "timesheet": { ... },
            "timesheet_entries": [ { ... }, ... ],
            "timesheet_approvals": { ... }   or {}
          }
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            timesheet = get_object_or_404(Timesheets, pk=pk)
            timesheet_data = TimesheetsSerializer(timesheet).data

            # All entries for this timesheet, ordered by work_date ascending.
            entries_qs = TimesheetEntries.objects.filter(
                timesheet_id=pk
            ).order_by('work_date')
            entries_data = TimesheetEntriesSerializer(entries_qs, many=True).data

            # There is at most one approval record per timesheet.
            approval_data = get_related_data(
                TimesheetApprovals, TimesheetApprovalsSerializer, 'timesheet_id', pk
            )
            approval = approval_data[0] if approval_data else {}

            custom_data = {
                'timesheet': timesheet_data,
                'timesheet_entries': list(entries_data),
                'timesheet_approvals': approval,
            }

            logger.info(f"Timesheet {pk} and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error(f"Timesheet with pk {kwargs.get('pk')} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(f"Error retrieving timesheet {kwargs.get('pk')}: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ------------------------------------------------------------------
    # CREATE  (POST)
    # ------------------------------------------------------------------

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Expected request body:
        {
            "timesheet": {
                "employee_id": "<uuid>",
                "start_date":  "YYYY-MM-DD",
                "end_date":    "YYYY-MM-DD",
                "notes":       "optional text"
            },
            "timesheet_entries": [
                { "work_date": "YYYY-MM-DD", "hours_worked": 8.0, "description": "..." },
                ...
            ]
        }

        Steps:
          1. Validate timesheet header data.
          2. Validate each entry row (hours range, date inside period).
          3. Create the Timesheets record.
          4. Create each TimesheetEntries record, injecting the new timesheet_id.
          5. Compute total_hours and save it back on the Timesheets record.
          6. Return the full detail response.
        """
        given_data = request.data
        errors = {}

        # ---- 1. Validate timesheet header --------------------------------
        timesheet_data = given_data.get('timesheet', None)

        if not timesheet_data:
            logger.error("'timesheet' key is mandatory but was not provided.")
            return build_response(
                0, "'timesheet' data is mandatory", [], status.HTTP_400_BAD_REQUEST
            )

        timesheet_error = validate_payload_data(self, timesheet_data, TimesheetsSerializer)
        if timesheet_error:
            errors['timesheet'] = timesheet_error

        # ---- 2. Validate entries list ------------------------------------
        entries_data = given_data.get('timesheet_entries', None)

        if not entries_data:
            errors['timesheet_entries'] = "At least one timesheet entry is required."
        elif not isinstance(entries_data, list):
            errors['timesheet_entries'] = "'timesheet_entries' must be a list."
        else:
            entry_errors = []
            start_date_str = timesheet_data.get('start_date', '')
            end_date_str   = timesheet_data.get('end_date', '')

            for idx, entry in enumerate(entries_data):
                row_errors = {}

                hours = entry.get('hours_worked')
                if hours is None:
                    row_errors['hours_worked'] = "hours_worked is required."
                else:
                    try:
                        hours_val = Decimal(str(hours))
                        if hours_val <= 0 or hours_val > 24:
                            row_errors['hours_worked'] = (
                                "hours_worked must be between 0.01 and 24.00."
                            )
                    except Exception:
                        row_errors['hours_worked'] = "hours_worked must be a valid number."

                work_date_str = entry.get('work_date')
                if not work_date_str:
                    row_errors['work_date'] = "work_date is required."
                else:
                    try:
                        work_date  = datetime.strptime(work_date_str, "%Y-%m-%d").date()
                        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                        end_date   = datetime.strptime(end_date_str,   "%Y-%m-%d").date()
                        if work_date < start_date or work_date > end_date:
                            row_errors['work_date'] = (
                                f"work_date {work_date_str} must fall within the "
                                f"timesheet period ({start_date_str} to {end_date_str})."
                            )
                    except ValueError:
                        row_errors['work_date'] = (
                            "Invalid date format. Use YYYY-MM-DD."
                        )

                if row_errors:
                    entry_errors.append({f"entry[{idx}]": row_errors})

            if entry_errors:
                errors['timesheet_entries'] = entry_errors

        if errors:
            return build_response(
                0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST
            )

        # ---- 3. Create the Timesheets header record ----------------------
        new_timesheet_list = generic_data_creation(
            self, [timesheet_data], TimesheetsSerializer
        )
        new_timesheet = new_timesheet_list[0]
        timesheet_id  = new_timesheet.get('timesheet_id')
        logger.info(f"Timesheet {timesheet_id} created.")

        # ---- 4. Create each entry, injecting the timesheet_id -----------
        created_entries = []
        for entry in entries_data:
            entry_payload = {**entry, 'timesheet_id': timesheet_id}
            new_entry_list = generic_data_creation(
                self, [entry_payload], TimesheetEntriesSerializer
            )
            created_entries.append(new_entry_list[0])
        logger.info(f"{len(created_entries)} entries created for timesheet {timesheet_id}.")

        # ---- 5. Compute and persist total_hours + billable_amount -------
        total = _compute_total_hours(timesheet_id)
        billable_amt = _compute_billable_amount(timesheet_id, total)
        Timesheets.objects.filter(pk=timesheet_id).update(
            total_hours=total, billable_amount=billable_amt
        )
        new_timesheet['total_hours'] = str(total)
        new_timesheet['billable_amount'] = str(billable_amt) if billable_amt is not None else None

        # ---- 6. Return full detail response -----------------------------
        custom_data = {
            'timesheet':           new_timesheet,
            'timesheet_entries':   created_entries,
            'timesheet_approvals': {},
        }
        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)

    # ------------------------------------------------------------------
    # UPDATE  (PUT)
    # ------------------------------------------------------------------

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):
        """
        Replaces the timesheet header and all its entries in a single call.

        Business rules:
          - Blocked when the timesheet status is 'Open' (submitted, awaiting approval).
          - Blocked when the timesheet status is 'Approved'.
          - Allowed when status is 'Draft' (no approval record) or 'Rejected'.

        Steps:
          1. Check the timesheet exists and is editable.
          2. Validate the new header data.
          3. Validate the new entries list.
          4. Update the Timesheets record.
          5. Delete the old entries and create the new ones.
          6. Recompute total_hours.
          7. Return the full detail response.
        """
        given_data = request.data
        errors = {}

        # ---- 1. Existence and editability check -------------------------
        try:
            timesheet_instance = Timesheets.objects.get(pk=pk)
        except Timesheets.DoesNotExist:
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

        current_status = _get_timesheet_status(pk)
        if current_status in ('Open', 'Approved'):
            return build_response(
                0,
                f"Timesheet cannot be edited because its current status is '{current_status}'. "
                "Only Draft or Rejected timesheets can be edited.",
                [],
                status.HTTP_400_BAD_REQUEST,
            )

        # ---- 2. Validate timesheet header --------------------------------
        timesheet_data = given_data.get('timesheet', None)
        if not timesheet_data:
            return build_response(
                0, "'timesheet' data is mandatory", [], status.HTTP_400_BAD_REQUEST
            )

        timesheet_data['timesheet_id'] = pk
        timesheet_error = validate_payload_data(self, timesheet_data, TimesheetsSerializer)
        if timesheet_error:
            errors['timesheet'] = timesheet_error

        # ---- 3. Validate entries list ------------------------------------
        entries_data = given_data.get('timesheet_entries', None)
        if not entries_data:
            errors['timesheet_entries'] = "At least one timesheet entry is required."
        elif not isinstance(entries_data, list):
            errors['timesheet_entries'] = "'timesheet_entries' must be a list."
        else:
            entry_errors = []
            start_date_str = timesheet_data.get('start_date', '')
            end_date_str   = timesheet_data.get('end_date', '')

            for idx, entry in enumerate(entries_data):
                row_errors = {}

                hours = entry.get('hours_worked')
                if hours is None:
                    row_errors['hours_worked'] = "hours_worked is required."
                else:
                    try:
                        hours_val = Decimal(str(hours))
                        if hours_val <= 0 or hours_val > 24:
                            row_errors['hours_worked'] = (
                                "hours_worked must be between 0.01 and 24.00."
                            )
                    except Exception:
                        row_errors['hours_worked'] = "hours_worked must be a valid number."

                work_date_str = entry.get('work_date')
                if not work_date_str:
                    row_errors['work_date'] = "work_date is required."
                else:
                    try:
                        work_date  = datetime.strptime(work_date_str, "%Y-%m-%d").date()
                        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                        end_date   = datetime.strptime(end_date_str,   "%Y-%m-%d").date()
                        if work_date < start_date or work_date > end_date:
                            row_errors['work_date'] = (
                                f"work_date {work_date_str} must fall within the "
                                f"timesheet period ({start_date_str} to {end_date_str})."
                            )
                    except ValueError:
                        row_errors['work_date'] = "Invalid date format. Use YYYY-MM-DD."

                if row_errors:
                    entry_errors.append({f"entry[{idx}]": row_errors})

            if entry_errors:
                errors['timesheet_entries'] = entry_errors

        if errors:
            return build_response(
                0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST
            )

        # ---- 4. Update the Timesheets header ----------------------------
        try:
            updated_timesheet_list = update_multi_instances(
                self, pk,
                [timesheet_data],
                Timesheets,
                TimesheetsSerializer,
                [],
                main_model_related_field='timesheet_id',
                current_model_pk_field='timesheet_id',
            )
            updated_timesheet = updated_timesheet_list[0]
            logger.info(f"Timesheet {pk} header updated.")

        except Exception as e:
            logger.exception(f"Error updating timesheet {pk}: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

        # ---- 5. Replace entries -----------------------------------------
        # Hard delete all existing entries then create fresh ones.
        # Entries have no independent lifecycle; PUT is a full replacement.
        TimesheetEntries.objects.filter(timesheet_id=pk).delete()

        created_entries = []
        for entry in entries_data:
            entry_payload = {**entry, 'timesheet_id': pk}
            new_entry_list = generic_data_creation(
                self, [entry_payload], TimesheetEntriesSerializer
            )
            created_entries.append(new_entry_list[0])
        logger.info(f"{len(created_entries)} entries replaced for timesheet {pk}.")

        # ---- 6. Recompute total_hours + billable_amount ------------------
        total = _compute_total_hours(pk)
        billable_amt = _compute_billable_amount(pk, total)
        Timesheets.objects.filter(pk=pk).update(
            total_hours=total, billable_amount=billable_amt
        )
        updated_timesheet['total_hours'] = str(total)
        updated_timesheet['billable_amount'] = str(billable_amt) if billable_amt is not None else None

        # ---- 7. Return full detail response -----------------------------
        approval_data = get_related_data(
            TimesheetApprovals, TimesheetApprovalsSerializer, 'timesheet_id', pk
        )
        custom_data = {
            'timesheet':           updated_timesheet,
            'timesheet_entries':   created_entries,
            'timesheet_approvals': approval_data[0] if approval_data else {},
        }
        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

    # ------------------------------------------------------------------
    # SOFT DELETE  (DELETE)
    # ------------------------------------------------------------------

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Soft-deletes a timesheet (sets is_deleted=True).
        Only allowed when the timesheet is in 'Draft' state (no approval record).
        """
        try:
            instance = Timesheets.objects.get(pk=pk)
        except Timesheets.DoesNotExist:
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

        current_status = _get_timesheet_status(pk)
        if current_status != 'Draft':
            return build_response(
                0,
                f"Timesheet cannot be deleted because its current status is '{current_status}'. "
                "Only Draft timesheets can be deleted.",
                [],
                status.HTTP_400_BAD_REQUEST,
            )

        instance.is_deleted = True
        instance.save()

        logger.info(f"Timesheet {pk} soft-deleted successfully.")
        return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)

    # ------------------------------------------------------------------
    # RESTORE  (PATCH)
    # ------------------------------------------------------------------

    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        """
        Restores a soft-deleted timesheet (sets is_deleted=False).
        Mirrors the PATCH restore pattern used by EmployeeLeavesView.
        """
        try:
            instance = Timesheets.objects.get(pk=pk)
        except Timesheets.DoesNotExist:
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

        if not instance.is_deleted:
            return build_response(
                0, "Record is already active", [], status.HTTP_400_BAD_REQUEST
            )

        instance.is_deleted = False
        instance.save()

        logger.info(f"Timesheet {pk} restored successfully.")
        return build_response(1, "Record restored successfully", [], status.HTTP_200_OK)


# ------------------------------------------------------------------------------
#  Submit / Approve / Reject  —  dedicated action endpoints
# ------------------------------------------------------------------------------

class TimesheetSubmitView(APIView):
    """
    POST /hrms/timesheets/<pk>/submit/

    Moves a timesheet from Draft -> Open (submitted, awaiting approval).

    Logic:
      - Timesheet must exist and not be deleted.
      - Status must be 'Draft' (no approval record) or 'Rejected'
        (employee corrected and is re-submitting).
      - The employee's manager_id is used as the approver.
        If manager_id is not set, the API returns a clear error.
      - If a previous TimesheetApprovals record exists (Rejected state),
        its status is updated back to 'Open' (no duplicate record created).
      - If no approval record exists (Draft state), a new one is created.
    """

    @transaction.atomic
    def post(self, request, pk, *args, **kwargs):
        # ---- Fetch the timesheet ----------------------------------------
        try:
            timesheet = Timesheets.objects.select_related('employee_id').get(pk=pk)
        except Timesheets.DoesNotExist:
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

        if timesheet.is_deleted:
            return build_response(
                0, "Cannot submit a deleted timesheet.", [], status.HTTP_400_BAD_REQUEST
            )

        # ---- Guard: only Draft or Rejected timesheets can be submitted --
        current_status = _get_timesheet_status(pk)
        if current_status in ('Open', 'Approved'):
            return build_response(
                0,
                f"Timesheet is already '{current_status}' and cannot be re-submitted.",
                [],
                status.HTTP_400_BAD_REQUEST,
            )

        # ---- Resolve the 'Open' Status record ---------------------------
        open_status = get_object_or_none(Statuses, status_name='Open')
        if open_status is None:
            logger.error("Status 'Open' not found in masters.Statuses table.")
            return build_response(
                0,
                "System configuration error: 'Open' status not found. "
                "Please contact your administrator.",
                [],
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ---- Resolve the manager (approver) ----------------------------
        employee = timesheet.employee_id
        if not employee.manager_id_id:
            return build_response(
                0,
                f"Employee '{employee.full_name}' does not have a manager assigned. "
                "Please assign a manager before submitting a timesheet.",
                [],
                status.HTTP_400_BAD_REQUEST,
            )

        manager = employee.manager_id

        # ---- Create or update the approval record -----------------------
        existing_approval = TimesheetApprovals.objects.filter(
            timesheet_id=pk
        ).first()

        if existing_approval:
            # Re-submission after rejection: reset to Open, clear rejection reason.
            existing_approval.status_id        = open_status
            existing_approval.approver_id      = manager
            existing_approval.approval_date    = None
            existing_approval.rejection_reason = None
            existing_approval.save()
            approval_data = TimesheetApprovalsSerializer(existing_approval).data
            logger.info(f"Timesheet {pk} re-submitted; approval record reset to Open.")
        else:
            # First submission: create a new approval record.
            approval_payload = {
                'timesheet_id': pk,
                'status_id':    open_status.status_id,
                'approver_id':  manager.employee_id,
            }
            new_approval_list = generic_data_creation(
                self, [approval_payload], TimesheetApprovalsSerializer
            )
            approval_data = new_approval_list[0]
            logger.info(f"Timesheet {pk} submitted; approval record created.")

        return build_response(
            1, "Timesheet submitted successfully for approval.", approval_data, status.HTTP_200_OK
        )


class TimesheetApproveView(APIView):
    """
    POST /hrms/timesheets/<pk>/approve/

    Moves a timesheet approval from Open -> Approved.

    Request body (optional):
    {
        "approval_date": "YYYY-MM-DD"   (defaults to today)
    }
    """

    @transaction.atomic
    def post(self, request, pk, *args, **kwargs):
        try:
            timesheet = Timesheets.objects.get(pk=pk)
        except Timesheets.DoesNotExist:
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

        approval = TimesheetApprovals.objects.filter(timesheet_id=pk).first()
        if approval is None:
            return build_response(
                0,
                "This timesheet has not been submitted yet (no approval record found).",
                [],
                status.HTTP_400_BAD_REQUEST,
            )

        if approval.status_id.status_name != 'Open':
            return build_response(
                0,
                f"Only 'Open' timesheets can be approved. "
                f"Current status: '{approval.status_id.status_name}'.",
                [],
                status.HTTP_400_BAD_REQUEST,
            )

        approved_status = get_object_or_none(Statuses, status_name='Approved')
        if approved_status is None:
            logger.error("Status 'Approved' not found in masters.Statuses table.")
            return build_response(
                0,
                "System configuration error: 'Approved' status not found.",
                [],
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        approval_date_str = request.data.get('approval_date')
        try:
            approval_date = (
                datetime.strptime(approval_date_str, "%Y-%m-%d").date()
                if approval_date_str
                else now().date()
            )
        except ValueError:
            return build_response(
                0, "Invalid approval_date format. Use YYYY-MM-DD.", [], status.HTTP_400_BAD_REQUEST
            )

        approval.status_id     = approved_status
        approval.approval_date = approval_date
        approval.save()

        logger.info(f"Timesheet {pk} approved on {approval_date}.")
        return build_response(
            1,
            "Timesheet approved successfully.",
            TimesheetApprovalsSerializer(approval).data,
            status.HTTP_200_OK,
        )


class TimesheetRejectView(APIView):
    """
    POST /hrms/timesheets/<pk>/reject/

    Moves a timesheet approval from Open -> Rejected.

    Request body (optional):
    {
        "rejection_reason": "Hours on Monday are incorrect.",
        "approval_date":    "YYYY-MM-DD"   (defaults to today)
    }
    """

    @transaction.atomic
    def post(self, request, pk, *args, **kwargs):
        try:
            timesheet = Timesheets.objects.get(pk=pk)
        except Timesheets.DoesNotExist:
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

        approval = TimesheetApprovals.objects.filter(timesheet_id=pk).first()
        if approval is None:
            return build_response(
                0,
                "This timesheet has not been submitted yet (no approval record found).",
                [],
                status.HTTP_400_BAD_REQUEST,
            )

        if approval.status_id.status_name != 'Open':
            return build_response(
                0,
                f"Only 'Open' timesheets can be rejected. "
                f"Current status: '{approval.status_id.status_name}'.",
                [],
                status.HTTP_400_BAD_REQUEST,
            )

        rejected_status = get_object_or_none(Statuses, status_name='Rejected')
        if rejected_status is None:
            logger.error("Status 'Rejected' not found in masters.Statuses table.")
            return build_response(
                0,
                "System configuration error: 'Rejected' status not found.",
                [],
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        approval_date_str = request.data.get('approval_date')
        try:
            approval_date = (
                datetime.strptime(approval_date_str, "%Y-%m-%d").date()
                if approval_date_str
                else now().date()
            )
        except ValueError:
            return build_response(
                0, "Invalid approval_date format. Use YYYY-MM-DD.", [], status.HTTP_400_BAD_REQUEST
            )

        approval.status_id        = rejected_status
        approval.approval_date    = approval_date
        approval.rejection_reason = request.data.get('rejection_reason', None)
        approval.save()

        logger.info(f"Timesheet {pk} rejected on {approval_date}.")
        return build_response(
            1,
            "Timesheet rejected successfully.",
            TimesheetApprovalsSerializer(approval).data,
            status.HTTP_200_OK,
        )


# ==============================================================================
#  TIMESHEET → INVOICE  (ad-hoc billable hours)
# ==============================================================================

class BillableTimesheetsView(APIView):
    """
    GET /hrms/billable_timesheets/

    Returns timesheets that are READY TO BE INVOICED, i.e. all three hold:
      - is_billable = True
      - the latest approval status is 'Approved'
      - invoiced = 'NO'  (not yet billed)

    Supports the same filters as the normal timesheet list (customer, date
    range, period_name, search, pagination) via TimesheetsFilter.

    Finance uses this list to pick which approved billable hours to turn
    into an invoice.
    """

    def get(self, request, *args, **kwargs):
        try:
            logger.info("Retrieving billable (invoice-eligible) timesheets")

            page  = int(request.query_params.get('page',  1))
            limit = int(request.query_params.get('limit', 10))

            # Base eligibility: billable + approved + not yet invoiced + active.
            # 'approvals' is the related_name on TimesheetApprovals.timesheet_id.
            queryset = (
                Timesheets.objects
                .filter(
                    is_billable=True,
                    invoiced='NO',
                    is_deleted=False,
                    approvals__status_id__status_name='Approved',
                )
                .distinct()
                .order_by('-created_at')
            )

            # Apply the standard timesheet filters on top of the eligibility base.
            if request.query_params:
                filterset = TimesheetsFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs

            total_count = queryset.count()
            serializer  = TimesheetsSerializer(queryset, many=True)

            logger.info("Billable timesheets retrieved successfully.")
            return filter_response(
                queryset.count(), "Success", serializer.data,
                page, limit, total_count, status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Error retrieving billable timesheets: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


class TimesheetInvoiceCreateView(APIView):
    """
    POST /hrms/timesheets/create_invoice/

    Converts approved billable timesheets into a single Sale Invoice
    (reusing the existing SaleInvoiceOrders / SaleInvoiceItems engine — no
    new invoice entity is created).

    Request body:
    {
        "customer_id":   "<uuid>",            # client to bill
        "product_id":    "<uuid>",            # the 'Professional Services' product
        "timesheet_ids": ["<uuid>", "<uuid>"] # approved + billable + un-invoiced
    }

    Rules enforced (all must hold for EVERY timesheet, else 400):
      - exists, not deleted
      - is_billable = True
      - approval status = 'Approved'
      - invoiced = 'NO'   (prevents double-billing)
      - belongs to the given customer_id

    On success (atomic):
      1. Builds one SaleInvoiceOrders (bill_type CREDIT, status auto 'Pending',
         invoice_no auto-generated by the model's save()).
      2. Creates one SaleInvoiceItems line per timesheet
         (quantity = total_hours, rate = billing_rate, amount = billable_amount).
      3. Flips each timesheet to invoiced='YES' and links sale_invoice_id.
    """

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Local imports avoid any cross-app circular import at module load time.
        from apps.sales.models import SaleInvoiceOrders, SaleInvoiceItems
        from apps.products.models import Products
        from apps.customer.models import Customer, CustomerAddresses

        data           = request.data
        customer_id    = data.get('customer_id')
        product_id     = data.get('product_id')
        timesheet_ids  = data.get('timesheet_ids')

        # ---- 1. Basic payload validation --------------------------------
        if not customer_id:
            return build_response(0, "'customer_id' is required.", [], status.HTTP_400_BAD_REQUEST)
        if not product_id:
            return build_response(0, "'product_id' (service item) is required.", [], status.HTTP_400_BAD_REQUEST)
        if not timesheet_ids or not isinstance(timesheet_ids, list):
            return build_response(0, "'timesheet_ids' must be a non-empty list.", [], status.HTTP_400_BAD_REQUEST)

        customer = get_object_or_none(Customer, customer_id=customer_id)
        if customer is None:
            return build_response(0, "Customer not found.", [], status.HTTP_400_BAD_REQUEST)

        product = get_object_or_none(Products, product_id=product_id)
        if product is None:
            return build_response(0, "Service product not found.", [], status.HTTP_400_BAD_REQUEST)

        # ---- 2. Validate every timesheet is eligible --------------------
        timesheets = []
        for ts_id in timesheet_ids:
            ts = get_object_or_none(Timesheets, timesheet_id=ts_id)
            if ts is None or ts.is_deleted:
                return build_response(0, f"Timesheet {ts_id} not found.", [], status.HTTP_400_BAD_REQUEST)
            if not ts.is_billable:
                return build_response(0, f"Timesheet {ts_id} is not marked billable.", [], status.HTTP_400_BAD_REQUEST)
            if ts.invoiced == 'YES':
                return build_response(0, f"Timesheet {ts_id} is already invoiced.", [], status.HTTP_400_BAD_REQUEST)
            if _get_timesheet_status(ts.timesheet_id) != 'Approved':
                return build_response(0, f"Timesheet {ts_id} is not approved yet.", [], status.HTTP_400_BAD_REQUEST)
            if str(ts.customer_id_id) != str(customer_id):
                return build_response(
                    0,
                    f"Timesheet {ts_id} belongs to a different customer. "
                    "All selected timesheets must be for the same customer.",
                    [],
                    status.HTTP_400_BAD_REQUEST,
                )
            timesheets.append(ts)

        # ---- 3. Compute amounts -----------------------------------------
        line_payloads = []
        item_value = Decimal('0.00')
        for ts in timesheets:
            hours = Decimal(str(ts.total_hours or 0))
            rate  = Decimal(str(ts.billing_rate or 0))
            amount = ts.billable_amount if ts.billable_amount is not None else (hours * rate)
            amount = Decimal(str(amount))
            item_value += amount
            line_payloads.append({
                'timesheet': ts,
                'quantity':  hours,
                'rate':      rate,
                'amount':    amount,
                'print_name': (
                    f"Billable hours — {ts.start_date} to {ts.end_date}"
                ),
            })

        # ---- 3b. Resolve the customer's default addresses ----------------
        # The invoice PDF prints billing_address / shipping_address from the
        # invoice record itself, so we copy them from the customer's saved
        # addresses (preferring a 'Billing' / 'Shipping' typed address, with a
        # sensible fallback). This keeps the printed invoice complete.
        def _compose_address(addr):
            if not addr:
                return None
            parts = [addr.address, getattr(addr, 'pin_code', None)]
            return ', '.join([p for p in parts if p]) or None

        active_addresses = CustomerAddresses.objects.filter(
            customer_id=customer, is_deleted=False
        )
        billing_addr = (
            active_addresses.filter(address_type='Billing').first()
            or active_addresses.first()
        )
        shipping_addr = (
            active_addresses.filter(address_type='Shipping').first()
            or billing_addr
        )

        billing_address_text  = _compose_address(billing_addr)
        shipping_address_text  = _compose_address(shipping_addr)
        customer_email = billing_addr.email if (billing_addr and billing_addr.email) else None

        # ---- 4. Create the invoice header -------------------------------
        # bill_type 'CREDIT' keeps it on the default DB (the 'Others' path
        # routes to the alternate 'mstcnl' DB — not used here). The model's
        # save() generates invoice_no and defaults order_status to 'Pending'.
        today = now().date()
        # Header, lines and the invoiced-flips must land together — a partial
        # failure would leave a half-built invoice with unflipped timesheets.
        with transaction.atomic():
            invoice = SaleInvoiceOrders.objects.create(
                customer_id=customer,
                customer_address_id=billing_addr,            # may be None — that's fine
                bill_type='CREDIT',
                invoice_date=today,
                ref_date=today,
                tax='Exclusive',
                email=customer_email,
                billing_address=billing_address_text,
                shipping_address=shipping_address_text,
                item_value=item_value,
                discount=Decimal('0.00'),
                dis_amt=Decimal('0.00'),
                taxable=item_value,
                tax_amount=Decimal('0.00'),
                cess_amount=Decimal('0.00'),
                transport_charges=Decimal('0.00'),
                round_off=Decimal('0.00'),
                total_amount=item_value,
                paid_amount=Decimal('0.00'),
                pending_amount=item_value,
                remarks='Auto-generated from approved billable timesheets (HRMS).',
            )
            logger.info(f"Sale invoice {invoice.invoice_no} created from timesheets.")

            # ---- 5. Create one invoice line per timesheet -------------------
            for lp in line_payloads:
                SaleInvoiceItems.objects.create(
                    sale_invoice_id=invoice,
                    product_id=product,
                    quantity=lp['quantity'],
                    rate=lp['rate'],
                    amount=lp['amount'],
                    discount=Decimal('0.00'),
                    tax=Decimal('0.00'),
                    cgst=Decimal('0.00'),
                    sgst=Decimal('0.00'),
                    igst=Decimal('0.00'),
                    print_name=lp['print_name'],
                    remarks=lp['print_name'],
                )

            # ---- 6. Flip each timesheet to invoiced + link the invoice ------
            for ts in timesheets:
                ts.invoiced = 'YES'
                ts.sale_invoice_id = invoice
                ts.save()

        custom_data = {
            'sale_invoice_id': str(invoice.sale_invoice_id),
            'invoice_no':      invoice.invoice_no,
            'customer':        {'customer_id': str(customer.customer_id), 'name': customer.name},
            'total_amount':    str(item_value),
            'line_count':      len(timesheets),
            'timesheet_ids':   [str(ts.timesheet_id) for ts in timesheets],
        }
        return build_response(
            1, "Invoice created successfully from timesheets.", custom_data, status.HTTP_201_CREATED
        )
        
        
        
#employee portal login

# Add to your existing views.py
from django.conf import settings
from django.utils import timezone

class EmployeePortalLoginView(APIView):
    permission_classes = []  # Public access
    
    def post(self, request):
        try:
            # Get origin for CORS
            # Get origin for CORS
            origin = request.headers.get('Origin', '')
            allowed_origins = [
                "http://localhost:4200",
                "http://127.0.0.1:4200",
                "https://prod.cnlerp.com",
                "https://rudhra.cnlerp.com",
                "https://vasusri.cnlerp.com",  # ADD THIS
                "https://qa.cnlerp.com",       # ADD THIS
                "https://apicore.cnlerp.com",  # ADD THIS
                "https://dev.qodefarm.com",
            ]
            
            cors_origin = origin if origin in allowed_origins else "https://prod.cnlerp.com"
            
            print("="*50)
            print("🔐 EMPLOYEE LOGIN ATTEMPT")
            print(f"📍 Origin: {origin}")
            print("="*50)
            
            serializer = EmployeePortalLoginSerializer(data=request.data)
            
            if serializer.is_valid():
                employee = serializer.validated_data['employee']
                print(f"✅ Employee found: {employee.full_name}")
                
                # Update last login
                employee.last_login = timezone.now()
                employee.save()
                
                # Create session
                request.session.flush()
                request.session.cycle_key()
                
                # Set session data
                request.session['employee_id'] = str(employee.employee_id)
                request.session['employee_name'] = employee.full_name
                request.session['username'] = employee.username
                request.session['email'] = employee.email
                request.session['user_role'] = 'Employee'
                request.session['is_employee_portal'] = True
                request.session['designation'] = str(employee.designation_id.title) if employee.designation_id else None
                request.session['department'] = str(employee.department_id.name) if employee.department_id else None
                
                # Save session
                request.session.save()
                
                print(f"✅ Session created: {request.session.session_key}")
                
                # Create response
                response = Response({
                    'success': True,
                    'message': 'Login successful',
                    'employee': {
                        'id': str(employee.employee_id),
                        'name': employee.full_name,
                        'username': employee.username,
                        'email': employee.email,
                        'designation': employee.designation_id.title if employee.designation_id else None,
                        'department': employee.department_id.name if employee.department_id else None,
                        'picture': employee.picture
                    }
                })
                
                # Set cookie
                cookie_domain = settings.SESSION_COOKIE_DOMAIN if not settings.DEBUG else None
                
                response.set_cookie(
                    key='sessionid',
                    value=request.session.session_key,
                    max_age=settings.SESSION_COOKIE_AGE,
                    path='/',
                    domain=cookie_domain,
                    secure=settings.SESSION_COOKIE_SECURE,
                    httponly=settings.SESSION_COOKIE_HTTPONLY,
                    samesite=settings.SESSION_COOKIE_SAMESITE
                )
                
                # Set CORS headers
                response["Access-Control-Allow-Origin"] = cors_origin
                response["Access-Control-Allow-Credentials"] = "true"
                response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
                response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken, Authorization, X-Client-Domain"
                
                return response
            
            print(f"❌ Invalid serializer: {serializer.errors}")
            return Response(serializer.errors, status=400)
            
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({'success': False, 'message': 'Server error'}, status=500)


class EmployeePortalLogoutView(APIView):
    def post(self, request):
        try:
            request.session.flush()
            response = Response({'success': True, 'message': 'Logged out successfully'})
            response.delete_cookie('sessionid')
            return response
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=500)


class EmployeePortalProfileView(APIView):
    def get(self, request):
        if 'employee_id' not in request.session:
            return Response({'error': 'Not logged in'}, status=401)
        
        try:
            employee = Employees.objects.get(
                employee_id=request.session['employee_id'],
                is_deleted=False
            )
            
            serializer = EmployeesSerializer(employee)
            return Response({
                'success': True,
                'employee': serializer.data
            })
        except Employees.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=404)
        
# views.py - Add this simple API

from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework.response import Response

class GenerateEmployeeCredentials(APIView):
    def post(self, request):
        employees = Employees.objects.filter(is_portal_user=True, username__isnull=True)
        
        results = []
        for emp in employees:
            username = f"{emp.first_name.lower()}.{emp.last_name.lower()}"
            plain_password = "Welcome@123"  # Simple default password
            
            emp.username = username
            emp.password = make_password(plain_password)
            emp.save()
            
            results.append({
                'name': emp.full_name,
                'username': username,
                'password': plain_password
            })
        
        return Response({'credentials': results})
    
    
import logging
logger = logging.getLogger(__name__)

class GenerateEmployeeCredentialsView(APIView):
    """Generate username and password for employee"""
    
    def post(self, request, employee_id):
        try:
            employee = Employees.objects.get(employee_id=employee_id, is_deleted=False)
            
            # Generate credentials
            username = employee.generate_username()
            plain_password = employee.set_random_password()
            employee.is_portal_user = True
            employee.save()
            
            return Response({
                'success': True,
                'username': username,
                'password': plain_password,  # Only returned once!
                'message': 'Credentials generated successfully'
            }, status=status.HTTP_200_OK)
            
        except Employees.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Employee not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error generating credentials: {str(e)}")
            return Response({
                'success': False,
                'message': 'Error generating credentials'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
