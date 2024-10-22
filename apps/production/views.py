import logging
from django.http import Http404
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.views import APIView

from apps.production.filters import WorkOrderFilter
from config.utils_filter_methods import filter_response
from .models import *
from .serializers import *
from config.utils_methods import build_response, delete_multi_instance, generic_data_creation, get_related_data, list_all_objects, create_instance, update_instance, update_multi_instances, validate_input_pk, validate_multiple_data, validate_payload_data, validate_put_method_data

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)

class BillOfMaterialsViewSet(viewsets.ModelViewSet):
    queryset = BillOfMaterials.objects.all()
    serializer_class = BillOfMaterialsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
        
class ProductionStatusViewSet(viewsets.ModelViewSet):
    queryset = ProductionStatus.objects.all()
    serializer_class = ProductionStatusSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
        
class MachineViewSet(viewsets.ModelViewSet):
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class DefaultMachineryViewSet(viewsets.ModelViewSet):
    queryset = DefaultMachinery.objects.all()
    serializer_class = DefaultMachinerySerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class WorkOrderStageViewSet(viewsets.ModelViewSet):
    queryset = WorkOrderStage.objects.all()
    serializer_class = WorkOrderStageSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class WorkOrderMachineViewSet(viewsets.ModelViewSet):
    queryset = WorkOrderMachine.objects.all()
    serializer_class = WorkOrderMachineSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class RawMaterialViewSet(viewsets.ModelViewSet):
    queryset = RawMaterial.objects.all()
    serializer_class = RawMaterialSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class ProductionWorkerViewSet(viewsets.ModelViewSet):
    queryset = ProductionWorker.objects.all()
    serializer_class = ProductionWorkerSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs) 


class WorkOrderAPIView(APIView):
    """
    API ViewSet for handling Purchase Return Order creation and related data.
    """

    def get_object(self, pk):
        try:
            return WorkOrder.objects.get(pk=pk)
        except WorkOrder.DoesNotExist:
            logger.warning(f"WorkOrder with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)   

    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:
           result =  validate_input_pk(self,kwargs['pk'])
           return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            instance = WorkOrder.objects.all()

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 
            total_count = WorkOrder.objects.count()

            # Apply filters manually
            if request.query_params:
                queryset = WorkOrder.objects.all()
                filterset = WorkOrderFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs
                    serializer = WorkOrderSerializer(queryset, many=True)
                    # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
                    return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except WorkOrder.DoesNotExist:
            logger.error("WorkOrder does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        else:
            serializer = WorkOrderSerializer(instance, many=True)
            logger.info("WorkOrder data retrieved successfully.")
            return build_response(instance.count(), "Success", serializer.data, status.HTTP_200_OK)  

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a WorkOrder and its related data.
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the WorkOrder instance
            instance = get_object_or_404(WorkOrder, pk=pk)
            work_order = WorkOrderSerializer(instance)

            # Retrieve related data
            bom_data = get_related_data(BillOfMaterials, BillOfMaterialsSerializer, 'order_id', pk)
            machines_data = get_related_data(WorkOrderMachine, WorkOrderMachineSerializer, 'work_order_id', pk)
            workers_data = get_related_data(ProductionWorker, ProductionWorkerSerializer, 'work_order_id', pk)
            stages_data = get_related_data(WorkOrderStage, WorkOrderStageSerializer, 'work_order_id', pk)

            # Customizing the response data
            custom_data = {
                "work_order": work_order.data,
                "bom": bom_data,
                "work_order_machines": machines_data,
                "workers": workers_data,
                "work_order_stages": stages_data
            }
            logger.info("WorkOrder and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error("WorkOrder with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("An error occurred while retrieving WorkOrder with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a WorkOrder and its related BOM, WorkOrderMachine, ProductionWorker and WorkOrderStage.
        """
        try:
            # Get the WorkOrder instance
            instance = WorkOrder.objects.get(pk=pk)

            # Delete related BillOfMaterials.
            if not delete_multi_instance(pk, WorkOrder, BillOfMaterials, main_model_field_name='order_id'):
                return build_response(0, "Error deleting related BillOfMaterials", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Delete the main WorkOrder instance
            instance.delete()

            logger.info(f"WorkOrder with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except WorkOrder.DoesNotExist:
            logger.warning(f"WorkOrder with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting WorkOrder with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Handling POST requests for creating
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Extracting data from the request
        given_data = request.data

        #---------------------- D A T A   V A L I D A T I O N ----------------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """

        # Validated WorkOrder Data
        work_order_data = given_data.pop('work_order', None) # parent_data
        if work_order_data:
            work_order_error = validate_multiple_data(self, work_order_data , WorkOrderSerializer, ['status_id'])

        # Validated BillOfMaterial Data
        bom_data = given_data.pop('bom', None)
        if bom_data:
            bom_error = validate_multiple_data(self, bom_data, BillOfMaterialsSerializer, ['work_order_id'])
        else:
            bom_error = []

        # Validated WorkOrderMachine Data
        work_order_machines_data = given_data.pop('work_order_machines', None)
        if work_order_machines_data:
            machinery_error = validate_multiple_data(self, work_order_machines_data, WorkOrderMachineSerializer, ['work_order_id'])
        else:
            machinery_error = [] # Since 'default_machinery' is optional, so making an error is empty list

        # Validated ProductionWorker Data
        workers_data = given_data.pop('workers', None)
        if workers_data:
            workers_error = validate_multiple_data(self, workers_data , ProductionWorkerSerializer,['work_order_id'])
        else:
            workers_error = []

        # Validated WorkOrderStage Data
        stages_data = given_data.pop('work_order_stages', None)
        if stages_data:
            stages_error = validate_multiple_data(self, stages_data , WorkOrderStageSerializer,['work_order_id'])
        else:
            stages_error = []

        # Ensure mandatory data is present
        if not work_order_data:
            logger.error("WorkOrder data are mandatory but not provided.")
            return build_response(0, "WorkOrder data are mandatory but not provided.", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if work_order_error:
            errors["work_order"] = work_order_error
        if bom_error:
                errors["bom"] = bom_error
        if machinery_error:
                errors['default_machinery'] = machinery_error
        if workers_error:
                errors['workers'] = workers_error
        if stages_error:
                errors['work_order_stages'] = stages_error
        if errors:
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)

        #---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """

        # Hence the data is validated , further it can be created.

        # get default status_id
        '''
        try:
            status_name = ProductionStatus.objects.get(status_name='work in progress')
            status_id = status_name.status_id
        except ProductionStatus.DoesNotExist:
            return build_response(0, "No matching status found.", status.HTTP_400_BAD_REQUEST)
        '''

        # Create WorkOrder Data
        # update_fields = {'status_id': status_id}
        order_data = generic_data_creation(self, [work_order_data], WorkOrderSerializer, {})
        new_work_order_data = order_data[0]
        work_order_id = new_work_order_data.get("work_order_id",None) #Fetch work_order_id from mew instance
        logger.info('WorkOrder - created*')
 
        # Create BillOfMaterials Data
        update_fields = {'order_id': work_order_id}
        bom_data = generic_data_creation(self, bom_data, BillOfMaterialsSerializer, update_fields)
        logger.info('BillOfMaterials - created*')

        # Create WorkOrderMachine Data
        update_fields = {'work_order_id': work_order_id}
        work_order_machines_data = generic_data_creation(self, work_order_machines_data, WorkOrderMachineSerializer, update_fields)
        logger.info('DefaultMachinery - created*')

        # create ProductionWorker Data
        workers_data = generic_data_creation(self, workers_data, ProductionWorkerSerializer, update_fields)
        logger.info('ProductionWorker - created*')

        # create WorkOrderStage Data
        stages_data = generic_data_creation(self, stages_data, WorkOrderStageSerializer, update_fields)
        # logger.info('WorkOrderStage - created*')        

        custom_data = {
            "work_order":new_work_order_data,
            "bom":bom_data,
            "work_order_machines":work_order_machines_data,
            "workers":workers_data,
            "work_order_stages":stages_data
        }
        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)

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

        # Validated WorkOrder Data
        work_order_data = given_data.pop('work_order', None) # parent_data
        if work_order_data:
            work_order_error = validate_multiple_data(self, work_order_data , WorkOrderSerializer,[])
        
        # Validated BillOfMaterial Data
        bom_data = given_data.pop('bom', None)
        if bom_data:
            bom_error = validate_put_method_data(self, bom_data, BillOfMaterialsSerializer, [], BillOfMaterials, current_model_pk_field='bom_id')
        else:
            bom_error = []

        exclude_fields = ['work_order_id']
        # Validated WorkOrderMachine Data
        work_order_machines_data = given_data.pop('work_order_machines', None)
        if work_order_machines_data:
            machinery_error = validate_put_method_data(self, work_order_machines_data, WorkOrderMachineSerializer, exclude_fields, WorkOrderMachine, current_model_pk_field='work_order_machines_id')
        else:
            machinery_error = [] # Since 'default_machinery' is optional, so making an error is empty list

        # Validated ProductionWorker Data
        workers_data = given_data.pop('workers', None)
        if workers_data:
            workers_error = validate_put_method_data(self, workers_data, ProductionWorkerSerializer, exclude_fields, ProductionWorker, current_model_pk_field='worker_id')
        else:
            workers_error = []

        # Validated WorkOrderStage Data
        stages_data = given_data.pop('work_order_stages', None)
        if stages_data:
            stages_error = validate_put_method_data(self, stages_data, WorkOrderStageSerializer, exclude_fields, WorkOrderStage, current_model_pk_field='work_stage_id')
        else:
            stages_error = []
        
        errors = {}
        if work_order_error:
            errors["work_order"] = work_order_error
        if bom_error:
                errors["bom"] = bom_error
        if machinery_error:
                errors['default_machinery'] = machinery_error
        if workers_error:
                errors['workers'] = workers_error
        if stages_error:
                errors['work_order_stages'] = stages_error
        if errors:
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)
      
        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#
        # update WorkOrder
        if work_order_data:
            update_fields = [] # No need to update any fields
            work_order_data = update_multi_instances(self, pk, work_order_data, WorkOrder, WorkOrderSerializer, update_fields,main_model_related_field='work_order_id', current_model_pk_field='work_order_id')
            work_order_data = work_order_data[0] if len(work_order_data)==1 else work_order_data

        # Get 'product_id' from WorkOrder
        product_id = work_order_data.get('product_id',None)            

        # Update the 'BillOfMaterials'
        update_fields = {'order_id':pk}
        bom_data = update_multi_instances(self, pk, bom_data, BillOfMaterials, BillOfMaterialsSerializer, update_fields, main_model_related_field='order_id', current_model_pk_field='bom_id')

        # Update the 'WorkOrderMachineSerializer'
        update_fields = {'work_order_id':pk}
        machines_data = update_multi_instances(self, pk, work_order_machines_data, WorkOrderMachine, WorkOrderMachineSerializer, update_fields, main_model_related_field='work_order_id', current_model_pk_field='work_order_machines_id')

        # Update the 'ProductionWorker'
        workers_data = update_multi_instances(self, pk, workers_data, ProductionWorker, ProductionWorkerSerializer, update_fields, main_model_related_field='work_order_id', current_model_pk_field='worker_id')

        # Update the 'ProductionWorker'
        stages_data = update_multi_instances(self, pk, stages_data, WorkOrderStage, WorkOrderStageSerializer, update_fields, main_model_related_field='work_order_id', current_model_pk_field='work_stage_id')

        custom_data = {
            "work_order" : work_order_data,
            "bom" : bom_data if bom_data else [],
            "work_order_machines" : machines_data if machines_data else [],
            "workers" : workers_data if workers_data else [],
            "work_order_stages" : stages_data if stages_data else []
        }

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)
