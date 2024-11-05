import logging
from rest_framework import viewsets, status
from django.db import transaction
from rest_framework.views import APIView
from django.http import  Http404
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
from config.utils_methods import build_response, generic_data_creation, get_related_data, list_all_objects, create_instance, update_instance, update_multi_instances, validate_input_pk, validate_multiple_data, validate_payload_data, validate_put_method_data
from config.utils_filter_methods import filter_response, list_filtered_objects
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import OrderingFilter
from apps.hrms.filters import EmployeesFilter, EmployeeSalaryFilter, EmployeeSalaryComponentsFilter, EmployeeLeavesFilter, LeaveApprovalsFilter, EmployeeLeaveBalanceFilter, AttendanceFilter, SwipesFilter

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)

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
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = EmployeesFilter
    ordering_fields = []

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

class EmployeeSalaryViewSet(viewsets.ModelViewSet):
    queryset = EmployeeSalary.objects.all()
    serializer_class = EmployeeSalarySerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = EmployeeSalaryFilter
    ordering_fields = []
    
    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, EmployeeSalary,*args, **kwargs)

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
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = EmployeeSalaryComponentsFilter
    ordering_fields = []
    
    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, EmployeeSalaryComponents,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)  
		
# //=====================leaves====================================      

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
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = EmployeeLeavesFilter
    ordering_fields = []
    
    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, EmployeeLeaves,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
 
class LeaveApprovalsViewSet(viewsets.ModelViewSet):
    queryset = LeaveApprovals.objects.all()
    serializer_class = LeaveApprovalsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = LeaveApprovalsFilter
    ordering_fields = []
    
    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, LeaveApprovals,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs) 
        
class EmployeeLeaveBalanceViewSet(viewsets.ModelViewSet):
    queryset = EmployeeLeaveBalance.objects.all()
    serializer_class = EmployeeLeaveBalanceSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = EmployeeLeaveBalanceFilter
    ordering_fields = []
    
    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, EmployeeLeaveBalance,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
         
# =====================attendance====================================      

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = AttendanceFilter
    ordering_fields = []
    
    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Attendance,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)    

class SwipesViewSet(viewsets.ModelViewSet):
    queryset = Swipes.objects.all()
    serializer_class = SwipesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = SwipesFilter
    ordering_fields = []
    
    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Swipes,*args, **kwargs)

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


#------------  API --------------  

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

            queryset = Employees.objects.all()

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

            # Retrieve EmployeeDetails data
            employee_details_data = get_related_data(EmployeeDetails, EmployeeDetailsSerializer, 'employee_id', pk)
            emp_details_data = employee_details_data[0] if employee_details_data else {}

            # Customizing the response data
            custom_data = {
                "employee": employee_serializer.data,
                "employee_details": emp_details_data
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

        # Validate EmployeeDetails Data
        employee_details_data = given_data.pop('employee_details',None)
        if employee_details_data:
            employee_details_error = validate_multiple_data(self, [employee_details_data], EmployeeDetailsSerializer,['employee_id'])

            if employee_details_error:
                errors["employee_details"] = employee_details_error

        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """

        # Hence the data is validated , further it can be created.
        custom_data = {
            'employee':{},
            'employee_details':{}
            }

        # Create Employees Data
        new_employee_data = generic_data_creation(self, [employee_data], EmployeesSerializer)
        employee_data = new_employee_data[0]
        custom_data["employee"] = employee_data
        logger.info('Employee - created*')

        employee_id = employee_data.get("employee_id", None)  # Fetch journal_entry_id from mew instance

        #create EmployeeDetails
        if employee_details_data:
            update_fields = {'employee_id':employee_id}
            emp_details_data = generic_data_creation(self, [employee_details_data], EmployeeDetailsSerializer, update_fields)
            emp_details_data = emp_details_data[0] 
            custom_data["employee_details"] = emp_details_data
            logger.info('EmployeeDetails - created*')

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
            employee_error = validate_payload_data(self, employee_data , EmployeesSerializer)

        # Validated EmployeeDetails Data
        employee_details_data = given_data.pop('employee_details', None)
        if employee_details_data:
            exclude_fields = ['employee_id']
            employee_details_error = validate_put_method_data(self, employee_details_data,EmployeeDetailsSerializer, exclude_fields, EmployeeDetails,current_model_pk_field='employee_detail_id')
        else:
            employee_details_error = [] # Since 'JournalEntryLines' is optional, so making an error is empty list

        # Ensure mandatory data is present
        if not employee_data:
            logger.error("Employee data mandatory but not provided.")
            return build_response(0, "Employee data mandatory but not provided.", [], status.HTTP_400_BAD_REQUEST)
        
        errors = {}
        if employee_error:
            errors["employee"] = employee_error
        if employee_details_error:
            errors["employee_details"] = employee_details_error
        if errors:
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)
            
            # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#
        try:
            # Update the 'Employees'
            if employee_data:
                update_fields = []# No need to update any fields
                emp_data = update_multi_instances(self, pk, [employee_data], Employees, EmployeesSerializer, update_fields,main_model_related_field='employee_id', current_model_pk_field='employee_id')

            # Update EmployeeDetails Data
            update_fields = {'employee_id':pk}
            emp_details_data = update_multi_instances(self,pk, employee_details_data, EmployeeDetails, EmployeeDetailsSerializer, update_fields, main_model_related_field='employee_id', current_model_pk_field='employee_detail_id')

            custom_data = [
                {"employee":emp_data[0]},
                {"employee_details":emp_details_data[0] if emp_details_data else {}}
            ]

            return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)
        except Exception:
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)