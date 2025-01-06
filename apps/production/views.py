import logging
import re
from django.http import Http404
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from apps.production.filters import BOMFilter, MaterialFilter, WorkOrderFilter
from config.utils_filter_methods import filter_response
from .models import *
from apps.products.models import Products, ProductVariation
from apps.products.serializers import ProductVariationSerializer, productsSerializer
from .serializers import *
from config.utils_methods import build_response, delete_multi_instance, generic_data_creation, get_related_data, list_all_objects, create_instance, product_stock_verification, update_instance, update_multi_instances, update_product_stock, validate_input_pk, validate_multiple_data, validate_order_type, validate_payload_data, validate_put_method_data

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)

class BOMViewSet(viewsets.ModelViewSet):
    queryset = BOM.objects.all().order_by('-created_at')
    serializer_class = BOMSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = BOMFilter

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class BillOfMaterialsViewSet(viewsets.ModelViewSet):
    queryset = BillOfMaterials.objects.all().order_by('-created_at')
    serializer_class = BillOfMaterialsSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = MaterialFilter

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
        
class ProductionStatusViewSet(viewsets.ModelViewSet):
    queryset = ProductionStatus.objects.all().order_by('-created_at')
    serializer_class = ProductionStatusSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all().order_by('-created_at')
    serializer_class = WorkOrderSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class CompletedQuantityViewSet(viewsets.ModelViewSet):
    queryset = CompletedQuantity.objects.all()
    serializer_class = CompletedQuantitySerializer  

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
        
class MachineViewSet(viewsets.ModelViewSet):
    queryset = Machine.objects.all().order_by('-created_at')
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
            instances = WorkOrder.objects.all().order_by('-created_at')	
            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 
            total_count = WorkOrder.objects.count()            

            #Added wokorder summary logic here(starts)
            summary = request.query_params.get("summary", "false").lower() == "true"
            stock_journal = request.query_params.get('stock_journal', 'false').lower() == 'true'
            if stock_journal:
                logger.info("Retrieving stock_journal")
                data = []
                for work_order in instances:
                    bom_data = BillOfMaterials.objects.filter(reference_id=work_order.pk).values()
                    data.append({
                        'work_order_id' : str(work_order.pk),
                        'finished_product' : str(work_order.product_id),
                        'quantity' : str(work_order.quantity),
                        'bom_components' : bom_data,
                        })
                    
                return filter_response(len(data),"Success", data, page, limit, total_count, status.HTTP_200_OK)
                    
            if summary:
                logger.info("Retrieving Work Order summary")
                
                # Apply filters to the queryset for the summary case
                workorders = WorkOrder.objects.all()	
                filterset = WorkOrderFilter(request.GET, queryset=workorders)
                if filterset.is_valid():
                    workorders = filterset.qs  # Filtered queryset for summary
                
                data = WorkOrderOptionsSerializer.get_work_order_summary(workorders)
                return filter_response(len(data),"Success", data, page, limit, total_count, status.HTTP_200_OK)

            # Apply filters manually
            if request.query_params:
                queryset = WorkOrder.objects.all().order_by('-created_at')
                filterset = WorkOrderFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs
                    data = WorkOrderSerializer(queryset, many=True).data
                    return filter_response(queryset.count(),"Success", data, page, limit, total_count, status.HTTP_200_OK)

        except WorkOrder.DoesNotExist:
            logger.error("WorkOrder does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        else:
            serializer = WorkOrderSerializer(instances, many=True)
            logger.info("WorkOrder data retrieved successfully.")
            return build_response(instances.count(), "Success", serializer.data, status.HTTP_200_OK)  

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
            bom_data = get_related_data(BillOfMaterials, BillOfMaterialsSerializer, 'reference_id', pk)
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
            BillOfMaterials.objects.filter(reference_id=pk).delete()

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
            # Set default status to 'Open'
            id = ProductionStatus.objects.filter(status_name='open').values_list('status_id', flat=True).first()
            if id:
                work_order_data['status_id'] = id
            else:
                return build_response(0, " ValidationError: 'ProductionStatus' has no status named 'open'. ", [], status.HTTP_400_BAD_REQUEST)
            work_order_error = validate_multiple_data(self, work_order_data , WorkOrderSerializer, [])

        # Validated BillOfMaterial Data
        bom_data = given_data.pop('bom', None)
        if bom_data:
            bom_error = validate_multiple_data(self, bom_data, BillOfMaterialsSerializer, ['reference_id'])
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

        # Stock Verification
        if bom_data:
            stock_error = product_stock_verification(Products, ProductVariation, bom_data)
            if stock_error:
                return build_response(0, f"ValidationError :", stock_error, status.HTTP_400_BAD_REQUEST)                

        #---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """
        # Hence the data is validated , further it can be created.
        # Create WorkOrder Data
        order_data = generic_data_creation(self, [work_order_data], WorkOrderSerializer, {})
        new_work_order_data = order_data[0]
        work_order_id = new_work_order_data.get("work_order_id", None) #Fetch work_order_id from mew instance
        logger.info('WorkOrder - created*')
 
        # Create BillOfMaterials Data
        update_fields = {'reference_id': work_order_id}
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
        logger.info('WorkOrderStage - created*')      

        custom_data = {
            "work_order":new_work_order_data,
            "bom":bom_data,
            "work_order_machines":work_order_machines_data,
            "workers":workers_data,
            "work_order_stages":stages_data
        }

        # Update Product Stock
        update_product_stock(Products, ProductVariation, bom_data, 'subtract')
        logger.info('Stock Updated Successfully.')

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
            bom_error = validate_put_method_data(self, bom_data, BillOfMaterialsSerializer,['reference_id'], BillOfMaterials, current_model_pk_field='material_id')
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
            updated_work_order_data = update_multi_instances(self, pk, work_order_data, WorkOrder, WorkOrderSerializer, update_fields,main_model_related_field='work_order_id', current_model_pk_field='work_order_id')
            work_order_data = work_order_data[0] if len(work_order_data)==1 else work_order_data

        # Update the 'BillOfMaterials'
        update_fields = {'reference_id':pk}
        bom_data = update_multi_instances(self, pk, bom_data, BillOfMaterials, BillOfMaterialsSerializer, update_fields, main_model_related_field='reference_id', current_model_pk_field='material_id')

        # Update the 'WorkOrderMachineSerializer'
        update_fields = {'work_order_id':pk}
        machines_data = update_multi_instances(self, pk, work_order_machines_data, WorkOrderMachine, WorkOrderMachineSerializer, update_fields, main_model_related_field='work_order_id', current_model_pk_field='work_order_machines_id')

        # Update the 'ProductionWorker'
        workers_data = update_multi_instances(self, pk, workers_data, ProductionWorker, ProductionWorkerSerializer, update_fields, main_model_related_field='work_order_id', current_model_pk_field='worker_id')

        # Update the 'ProductionWorker'
        stages_data = update_multi_instances(self, pk, stages_data, WorkOrderStage, WorkOrderStageSerializer, update_fields, main_model_related_field='work_order_id', current_model_pk_field='work_stage_id')

        custom_data = {
            "work_order" : updated_work_order_data,
            "bom" : bom_data if bom_data else [],
            "work_order_machines" : machines_data if machines_data else [],
            "workers" : workers_data if workers_data else [],
            "work_order_stages" : stages_data if stages_data else []
        }

        """This code searches 'closed' in production status. if matched it updates Inventory with unsynced quantity.
           And deletes the record in 'CompletedQuantity' """
        
        # Get 'sync_qty' status from WorkOrder
        sync_qty = work_order_data.get('sync_qty', None)

        pattern = r"(?i)\bclosed\b"
        order_status = work_order_data.get('status_id', None)
        name = ProductionStatus.objects.get(status_id=order_status)
        if re.search(pattern, name.status_name):
            # Update Product Stock
            try:
                unsync_qty = CompletedQuantity.objects.get(work_order_id=pk).quantity
            except CompletedQuantity.DoesNotExist:
                unsync_qty = 0
            copy_data = work_order_data.copy()
            copy_data["quantity"] = unsync_qty
            update_product_stock(Products, ProductVariation, [copy_data], 'add')
            logger.info('Stock Updated Successfully.')            
            # Delete the record.
            try:
                CompletedQuantity.objects.get(work_order_id=pk).delete()
            except CompletedQuantity.DoesNotExist:pass
            sync_qty = True

        if sync_qty:
            copy_data = work_order_data.copy()
            completed_qty = copy_data.pop('completed_qty')
            copy_data["quantity"] = completed_qty# Take completed quantity to update further
            logger.info('completed QTY : %s ', completed_qty)
            update_product_stock(Products, ProductVariation, [copy_data], 'add')
            logger.info('Stock Updated Successfully.')

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

#------------------- BILL OF MATERIAL API VIEW ------------------#
"""
API VIEW for BOM creation
"""
class BOMView(APIView):
    """
    API for handling Bill Of Material creation and related data.
    """
    def get_object(self, pk):
        try:
            return BOM.objects.get(pk=pk)
        except BOM.DoesNotExist:
            logger.warning(f"BOM with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:
           result =  validate_input_pk(self,kwargs['pk'])
           return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            instance = BOM.objects.all().order_by('-created_at')	


            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 
            total_count = BOM.objects.count()

            # Apply filters manually
            if request.query_params:
                queryset = BOM.objects.all().order_by('-created_at')	
                filterset = BOMFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs
                    serializer = BOMSerializer(queryset, many=True)
                    return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except BOM.DoesNotExist:
            logger.error("BOM does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        else:
            serializer = BOMSerializer(instance, many=True)
            logger.info("BOM data retrieved successfully.")
            return build_response(instance.count(), "Success", serializer.data, status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a BOM and its related data.
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the BOM instance
            instance = get_object_or_404(BOM, pk=pk)
            bom = BOMSerializer(instance)

            # Retrieve related data
            material_data = get_related_data(BillOfMaterials, BillOfMaterialsSerializer, 'reference_id', pk)

            # Customizing the response data
            custom_data = {
                "bom": bom.data,
                "bill_of_material": material_data
            }
            logger.info("BOM and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error("BOM with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("An error occurred while retrieving BOM with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a BOM and its related Bill of materials.
        """
        try:
            # Get the BOM instance
            instance = BOM.objects.get(pk=pk)

            # Delete the Child table instances from 'bill of materials'.
            BillOfMaterials.objects.filter(reference_id=pk).delete()

            # Delete the main WorkOrder instance
            instance.delete()

            logger.info(f"BOM with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except BOM.DoesNotExist:
            logger.warning(f"BOM with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting BOM with ID {pk}: {str(e)}")
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

        # Validated BOM Data
        bom_data = given_data.pop('bom', None) # parent_data
        # Ensure mandatory data is present
        if not bom_data:
            logger.error("BOM data are mandatory but not provided.")
            return build_response(0, "BOM data are mandatory but not provided.", [], status.HTTP_400_BAD_REQUEST)        
        else:
            bom_error = validate_multiple_data(self, [bom_data] , BOMSerializer, [])

        # Validated BillOfMaterial Data
        material_data = given_data.pop('bill_of_material', None)
        if material_data:
            material_error = validate_multiple_data(self, material_data, BillOfMaterialsSerializer, ['reference_id'])
        else:
            material_error = []

        errors = {
            "bom": bom_error,
            "bill_of_material": material_error
        }
        errors = {key: value for key, value in errors.items() if value}

        if errors:
            return build_response(0, "ValidationError:", errors, status.HTTP_400_BAD_REQUEST)

        #---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data created as new instances.
        """
        # Create BOM Data
        new_bom_data = generic_data_creation(self, [bom_data], BOMSerializer, {})[0]
        reference_id = new_bom_data.get("bom_id",None) #Fetch 'bom_id' as 'reference_id' from mew instance
        logger.info('BOM - created*')
 
        # Create BillOfMaterials Data
        new_material_data = generic_data_creation(self, material_data, BillOfMaterialsSerializer, {'reference_id': reference_id})
        logger.info('BillOfMaterials - created*')
       
        custom_data = {
            "bom":new_bom_data,
            "bill_of_material":new_material_data,
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

        # Validated BOM Data
        bom_data = given_data.pop('bom', None) # parent_data
        if not bom_data:
            logger.error("BOM data are mandatory but not provided.")
            return build_response(0, "BOM data are mandatory but not provided.", [], status.HTTP_400_BAD_REQUEST)        
        else:
            bom_error = validate_multiple_data(self, [bom_data] , BOMSerializer, [])        
        
        # Validated BillOfMaterial Data
        material_data = given_data.pop('bill_of_material', [])
        material_error = []
        if material_data:
            material_error = validate_multiple_data(self, material_data, BillOfMaterialsSerializer,['reference_id'])
        errors = {
            "bom":bom_error,
            "bill_of_material":material_error
        }
        errors = { key : value for key, value in errors.items() if value}
        if errors:
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)
      
        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#
        # update BOM
        new_bom_data = update_multi_instances(self, pk, [bom_data], BOM, BOMSerializer, [], main_model_related_field='bom_id', current_model_pk_field='bom_id')[0]

        # Update the 'BillOfMaterials'
        new_material_data = update_multi_instances(self, pk, material_data, BillOfMaterials, BillOfMaterialsSerializer, {'reference_id':pk}, main_model_related_field='reference_id', current_model_pk_field='material_id')

        custom_data = {
            "bom" : new_bom_data,
            "bill_of_material" : new_material_data
        }
        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)
