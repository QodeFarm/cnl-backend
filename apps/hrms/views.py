import logging
from rest_framework import viewsets, status
from django.db import transaction
from rest_framework.views import APIView
from django.http import  Http404
from django.shortcuts import get_object_or_404
from .models import JobTypes, Designations, JobCodes, Departments, Shifts, Employees, EmployeeSalary, SalaryComponents, EmployeeSalaryComponents, LeaveTypes, EmployeeLeaves, LeaveApprovals, EmployeeLeaveBalance, EmployeeAttendance, Swipes, Biometric
from .serializers import JobTypesSerializer, DesignationsSerializer, JobCodesSerializer, DepartmentsSerializer, ShiftsSerializer, EmployeesSerializer, EmployeeSalarySerializer, SalaryComponentsSerializer, EmployeeSalaryComponentsSerializer, LeavesTypesSerializer, EmployeeLeavesSerializer, LeaveApprovalsSerializer, EmployeeLeaveBalanceSerializer, EmployeeAttendanceSerializer, SwipesSerializer, BiometricSerializer
from config.utils_methods import build_response, generic_data_creation, get_object_or_none, get_related_data, list_all_objects, create_instance, update_instance, update_multi_instances, validate_input_pk, validate_multiple_data, validate_payload_data, validate_put_method_data
from config.utils_filter_methods import filter_response, list_filtered_objects
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import OrderingFilter
from apps.masters.models import Statuses
from apps.hrms.filters import DepartmentsFilter, DesignationsFilter, EmployeeSalaryComponentsFilter, EmployeesFilter, EmployeeSalaryFilter, EmployeeLeavesFilter, JobCodesFilter, JobTypesFilter, LeaveApprovalsFilter, EmployeeLeaveBalanceFilter, EmployeeAttendanceFilter, LeaveTypesFilter, SalaryComponentsFilter, ShiftsFilter, SwipesFilter
from django.utils.timezone import now
from datetime import datetime

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

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, JobTypes,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
		
class DesignationsViewSet(viewsets.ModelViewSet):
    queryset = Designations.objects.all().order_by('-created_at')
    serializer_class = DesignationsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = DesignationsFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Designations,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
		
class JobCodesViewSet(viewsets.ModelViewSet):
    queryset = JobCodes.objects.all().order_by('-created_at')
    serializer_class = JobCodesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = JobCodesFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, JobCodes,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs) 
		
class DepartmentsViewSet(viewsets.ModelViewSet):
    queryset = Departments.objects.all().order_by('-created_at')
    serializer_class = DepartmentsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = DepartmentsFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Departments,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)  
		
class ShiftsViewSet(viewsets.ModelViewSet):
    queryset = Shifts.objects.all().order_by('-created_at')
    serializer_class = ShiftsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ShiftsFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Shifts,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
		
class EmployeesViewSet(viewsets.ModelViewSet):
    queryset = Employees.objects.all().order_by('-created_at')	
    serializer_class = EmployeesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = EmployeesFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Employees,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
		
class EmployeeSalaryViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSalary.objects.all().order_by('-created_at')	
    serializer_class = EmployeeSalarySerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = EmployeeSalaryFilter
    ordering_fields = ['created_at']
    
    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, EmployeeSalary,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)		

class SalaryComponentsViewSet(viewsets.ModelViewSet):
    queryset = SalaryComponents.objects.all().order_by('-created_at')	
    serializer_class = SalaryComponentsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = SalaryComponentsFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, SalaryComponents,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)		

class EmployeeSalaryComponentsViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSalaryComponents.objects.all().order_by('-created_at')	
    serializer_class = EmployeeSalaryComponentsSerializer 
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = EmployeeSalaryComponentsFilter
    ordering_fields = ['created_at']

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

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, LeaveTypes,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class EmployeeLeavesViewSet(viewsets.ModelViewSet):
    queryset = EmployeeLeaves.objects.all().order_by('-created_at')	
    serializer_class = EmployeeLeavesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = EmployeeLeavesFilter
    ordering_fields = ['created_at']
    
    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, EmployeeLeaves,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class LeaveApprovalsViewSet(viewsets.ModelViewSet):
    queryset = LeaveApprovals.objects.all().order_by('-created_at')	
    serializer_class = LeaveApprovalsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = LeaveApprovalsFilter
    ordering_fields = ['created_at']
    
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
    
    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Swipes,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)    

class BiometricViewSet(viewsets.ModelViewSet):
    queryset = Biometric.objects.all().order_by('-created_at')
    serializer_class = BiometricSerializer

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
            instance.delete()

            logger.info(f"EmployeeLeaves with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except EmployeeLeaves.DoesNotExist:
            logger.warning(f"EmployeeLeaves with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting EmployeeLeaves with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
     
   
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
                return errors  # Return early if status is invalid

            manager_id = employee_leaves_data.get("employee", {}).get("manager_id", None)  # Get manager_id from employee_leaves

            # Ensure manager_id exists
            if not manager_id:
                errors["leave_approvals"] = {"approver_id": ["Manager not found."]}
                return errors  # Return early if manager_id is missing

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
            instance.delete()

            logger.info(f"Vendor with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except Employees.DoesNotExist:
            logger.warning(f"Employees with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting Employees with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
            'employee':{},
            'employee_leave_balance':[]
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
                "employee_id":employee_id,
                "leave_type_id":leave_type.get('leave_type_id'),
                "leave_balance":leave_type.get('max_days_allowed'),
                "year":get_current_year(),
                }

                employee_leave_balance = generic_data_creation(self, [balance_payload], EmployeeLeaveBalanceSerializer)
                # Append the created leave balance to custom_data
                custom_data["employee_leave_balance"].append(employee_leave_balance[0])

            logger.info('EmployeeLeaveBalance - created*')

        else:
            return build_response(0, "EmployeeLeaveBalance record creation failed.", [], status.HTTP_400_BAD_REQUEST)

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