from decimal import Decimal
import logging
import re
from django.forms import FloatField
from django.http import Http404
from django.db import transaction
from django.db.models import Q,Sum,F,Count,ExpressionWrapper,DecimalField,Value,IntegerField,OuterRef, Subquery, Max
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch
from rest_framework.filters import OrderingFilter
from apps.production.filters import BOMFilter, MachineFilter, MaterialFilter, ProductionStatusFilter, StockJournalFilter, WorkOrderFilter,BOMReportFilter, BillOfMaterialsFilter, MachineFilter, MachineUtilizationReportFilter, MaterialFilter, ProductionCostReportFilter, ProductionStatusFilter, ProductionSummaryReportFilter, RawMaterialConsumptionReportFilter, WorkOrderFilter
from config.utils_db_router import set_db
from config.utils_filter_methods import filter_response, list_filtered_objects
from .models import *
from apps.products.models import Products, ProductVariation
from apps.products.serializers import ProductVariationSerializer, productsSerializer
from .serializers import *
from config.utils_methods import normalize_value, build_response, delete_multi_instance, soft_delete, generic_data_creation, get_related_data, list_all_objects, create_instance, product_stock_verification, update_instance, update_multi_instances, update_product_stock, validate_input_pk, validate_multiple_data, validate_order_type, validate_payload_data, validate_put_method_data
from django.db.models.functions import Coalesce,NullIf,Cast,ExtractSecond
from django.db.models import Avg

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
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductionStatusFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, ProductionStatus,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all().order_by('-created_at')
    serializer_class = WorkOrderSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = WorkOrderFilter

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
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = MachineFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Machine,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

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
        """Handles GET requests to retrieve Work Order data with optional filters and reports."""
        try:
            if "pk" in kwargs:
                result = validate_input_pk(self, kwargs["pk"])
                return result if result else self.retrieve(self, request, *args, **kwargs)

            if request.query_params.get("stock_journal", "false").lower() == "true":
                return self.get_stock_journal(request)
            
            if request.query_params.get("production_summary_report", "false").lower() == "true":
                return self.get_production_summary_report(request)
            
            if request.query_params.get("work_order_status_report", "false").lower() == "true":
                return self.get_work_order_status_report(request)

            if request.query_params.get("summary", "false").lower() == "true":
                return self.get_work_order_summary(request)
            
            # if request.query_params.get("work_order_status_report", "false").lower() == "true":
            #     return self.get_work_order_status_report(request)
            
            if request.query_params.get("finished_goods_report", "false").lower() == "true":
                return self.get_finished_goods_report(request)
            
            if request.query_params.get("production_cost_report", "false").lower() == "true":
                return self.get_production_cost_report(request)
            
            if request.query_params.get("machine_utilization_report", "false").lower() == "true":
                return self.get_machine_utilization_report(request)
            
            if request.query_params.get("wip_report", "false").lower() == "true":
                return self.get_wip_report(request)
            
            return self.get_work_orders(request)

        except WorkOrder.DoesNotExist:
            logger.error("WorkOrder does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_pagination_params(self, request):
        """Extracts pagination parameters from the request."""
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 10))
        return page, limit

    def get_work_orders(self, request):
        """Fetches paginated Work Order records with applied filters."""
        logger.info("Retrieving all Work Orders")

        page, limit = self.get_pagination_params(request)
        queryset = WorkOrder.objects.annotate(
        pending_qty=F("quantity") - F("completed_qty"))  #  Add pending_qty dynamically
        # total_count = queryset.count()  
        
       # Apply filters
        filterset = WorkOrderFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs

        total_count = queryset.count()
        serializer = WorkOrderSerializer(queryset, many=True)
        return filter_response(len(serializer.data), "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)

    def get_work_order_summary(self, request):
        """Fetches summarized Work Order data."""
        logger.info("Retrieving Work Order summary")

        page, limit = self.get_pagination_params(request)
        queryset = WorkOrder.objects.all().order_by("-created_at")
        
         # Apply filters
        if request.query_params:
            filterset = WorkOrderFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        total_count = queryset.count()  
        print("total_count===>> ",total_count)
        # queryset = self.apply_filters(request, queryset, WorkOrder)
        data = WorkOrderOptionsSerializer.get_work_order_summary(queryset)
        return filter_response(len(data), "Success", data, page, limit, total_count, status.HTTP_200_OK)

    def get_stock_journal(self, request):
        """Fetches stock journal data for Work Orders."""
        logger.info("Retrieving stock journal data")

        page, limit = self.get_pagination_params(request)
        queryset = WorkOrder.objects.all().order_by("-created_at")
        total_count = queryset.count() 
        if request.query_params:
            filterset = WorkOrderFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        serializer = StockJournalSerializer(queryset, many=True)
        return filter_response(len(serializer.data), "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)

    def get_production_summary_report(self, request, *args, **kwargs):
        """Fetches production summary report – overview of production output."""
        logger.info("Retrieving production summary report data")
        
        page, limit = self.get_pagination_params(request)
        
        # Annotate each WorkOrder with completion_percentage.
        queryset = WorkOrder.objects.all().annotate(
            completion_percentage=ExpressionWrapper(
                (F('completed_qty') * Value(100.0)) / Coalesce(F('quantity'), Value(1.0)),
                output_field=DecimalField(max_digits=5, decimal_places=2)
            )
        ).order_by('start_date')
        
        if request.query_params:
            filterset = ProductionSummaryReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs
                
        total_count = WorkOrder.objects.count()
        serializer = ProductionSummaryReportSerializer(queryset, many=True)
        
        return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

    
    def get_work_order_status_report(self, request):
        """Fetches the count of Work Orders grouped by status."""
        logger.info("Retrieving Work Order Status Report")

        page, limit = self.get_pagination_params(request)

        queryset = WorkOrder.objects.all().annotate(
        completion_percentage=ExpressionWrapper(
            (F('completed_qty') * Value(100.0)) / Coalesce(F('quantity'), Value(1.0)),
            output_field=DecimalField(max_digits=5, decimal_places=2)
        )
    ).order_by('-start_date')  # Sorting by latest work orders

      
        total_count = queryset.count()
        # queryset = self.apply_filters(request, queryset, WorkOrder)

        serializer = WorkOrderStatusReportSerializer(queryset, many=True)

        return filter_response(total_count, "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)
    
    def get_finished_goods_report(self, request):
        """Fetches Finished Goods Report (manufactured products ready for sale)."""
        logger.info("Retrieving Finished Goods Report")
        page, limit = self.get_pagination_params(request)
        
        # queryset = WorkOrder.objects.filter(status_id__status_name="closed" , completed_qty__gt=0)
        queryset = WorkOrder.objects.filter(completed_qty=F('quantity')).order_by('-end_date')

         # Apply filters
        if request.query_params:
            filterset = WorkOrderFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        total_count = WorkOrder.objects.count()   
        serializer = FinishedGoodsReportSerializer(queryset, many=True)
        return filter_response(queryset.count(),"Success",serializer.data,page,limit,queryset.count(),status.HTTP_200_OK)


    def get_production_cost_report(self, request):
        """Fetches breakdown of costs in manufacturing."""
        logger.info("Retrieving Production Cost Report")
        page, limit = self.get_pagination_params(request)
        
        queryset = BillOfMaterials.objects.values(
        product=F('product_id__name')
    ).annotate(
        total_quantity=Coalesce(Sum('quantity'), Value(0, output_field=IntegerField())),
        total_cost=Coalesce(Sum('total_cost'), Value(0, output_field=DecimalField(max_digits=18, decimal_places=2))),
        avg_unit_cost=Coalesce(Avg('unit_cost'), Value(0, output_field=DecimalField(max_digits=18, decimal_places=2)))
    ).order_by('product')
        
        #  Apply filters
        if request.query_params:
            filterset = ProductionCostReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        # Count the number of unique products after grouping rather than all BillOfMaterials records
        total_count = queryset.count()
        serializer = ProductionCostReportSerializer(queryset, many=True)
        return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)
    
    def get_machine_utilization_report(self, request):
        """Fetches machine utilization data including efficiency and downtime analysis."""
        logger.info("Retrieving Machine Utilization Report")

        page, limit = self.get_pagination_params(request)
        
        queryset = WorkOrderMachine.objects.values(
        machine_name=F('machine_id__machine_name')  # Get the machine name
            ).annotate(
                total_usage_hours=Coalesce(
                    Sum(F('work_order_id__completed_qty')), Value(0), output_field=DecimalField()
                ),
                total_work_orders=Coalesce(Count('work_order_id', distinct=True), Value(1)),  # Prevent division by zero
                avg_usage_per_work_order=ExpressionWrapper(
                    F('total_usage_hours') / F('total_work_orders'),
                    output_field=DecimalField()
                ),
                total_work_time=Coalesce(
                    Sum(
                        Cast(F('work_order_id__end_date'), output_field=IntegerField()) - 
                        Cast(F('work_order_id__start_date'), output_field=IntegerField())
                    ),
                    Value(0),
                    output_field=IntegerField()
                ),
                downtime_hours=ExpressionWrapper(
                    Value(168) - Cast(F('total_work_time'), output_field=IntegerField()),  # Assuming 168-hour work week
                    output_field=IntegerField()
                )
            ).order_by('-total_usage_hours')
         
        if request.query_params:
            filterset = MachineUtilizationReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        total_count = queryset.count()
        serializer = MachineUtilizationReportSerializer(queryset, many=True)
        return filter_response(total_count, "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)

    def get_wip_report(self, request):
        """Fetches Work in Progress (WIP) Report - Partially Completed Products."""
        logger.info("Retrieving WIP Report")

        page, limit = self.get_pagination_params(request)

        # Query work orders that are still in progress
        queryset = WorkOrder.objects.filter( completed_qty__gt=0,  # At least some work is done
            # completed_qty__lt=F('quantity'),  # But not fully completed
            status_id__status_name ="open"  # The order is still in progress
        )
         # Apply filters
        if request.query_params:
            filterset = WorkOrderFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        total_count = queryset.count()
        serializer = WorkOrderSerializer(queryset, many=True)

        return filter_response(total_count, "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)


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
            BillOfMaterials.objects.filter(reference_id=pk).update(is_deleted=True)

            # Delete the main WorkOrder instance
            # instance.delete()
            # Soft delete the main WorkOrder
            instance.is_deleted = True
            instance.save()

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

        db_name = set_db('default')
        # Validated WorkOrder Data
        work_order_data = given_data.pop('work_order', None) # parent_data
        if work_order_data:
            # Set default status to 'Open'
            id = ProductionStatus.objects.filter(status_name='open').values_list('status_id', flat=True).first()
            if id:
                work_order_data['status_id'] = id
            else:
                return build_response(0, " ValidationError: 'ProductionStatus' has no status named 'open'. ", [], status.HTTP_400_BAD_REQUEST)
            work_order_error = validate_multiple_data(self, work_order_data , WorkOrderSerializer, [], using_db=db_name)

        # Validated BillOfMaterial Data
        bom_data = normalize_value(given_data.pop('bom', None))
        if bom_data:
            bom_error = validate_multiple_data(self, bom_data, BillOfMaterialsSerializer, ['reference_id'], using_db=db_name)
        else:
            bom_error = []
            return build_response(0, "Bill Of Materials are required.", [], status.HTTP_400_BAD_REQUEST)

        # Validated WorkOrderMachine Data
        work_order_machines_data = normalize_value(given_data.pop('work_order_machines', None))
        if work_order_machines_data:
            machinery_error = validate_multiple_data(self, work_order_machines_data, WorkOrderMachineSerializer, ['work_order_id'], using_db=db_name)
        else:
            machinery_error = [] # Since 'default_machinery' is optional, so making an error is empty list

        # Validated ProductionWorker Data
        workers_data = normalize_value(given_data.pop('workers', None))
        if workers_data:
            workers_error = validate_multiple_data(self, workers_data , ProductionWorkerSerializer,['work_order_id'], using_db=db_name)
        else:
            workers_error = []

        # Validated WorkOrderStage Data
        stages_data = normalize_value(given_data.pop('work_order_stages', None))
        if stages_data:
            stages_error = validate_multiple_data(self, stages_data , WorkOrderStageSerializer,['work_order_id'], using_db=db_name)
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
        order_data = generic_data_creation(self, [work_order_data], WorkOrderSerializer, {}, using=db_name)
        new_work_order_data = order_data[0]
        work_order_id = new_work_order_data.get("work_order_id", None) #Fetch work_order_id from mew instance
        logger.info('WorkOrder - created*')
 
        # Create BillOfMaterials Data
        update_fields = {'reference_id': work_order_id}
        bom_data = generic_data_creation(self, bom_data, BillOfMaterialsSerializer, update_fields, using=db_name)
        logger.info('BillOfMaterials - created*')

        # Create WorkOrderMachine Data
        update_fields = {'work_order_id': work_order_id}
        work_order_machines_data = generic_data_creation(self, work_order_machines_data, WorkOrderMachineSerializer, update_fields, using=db_name)
        logger.info('DefaultMachinery - created*')

        # create ProductionWorker Data
        workers_data = generic_data_creation(self, workers_data, ProductionWorkerSerializer, update_fields, using=db_name)
        logger.info('ProductionWorker - created*')

        # create WorkOrderStage Data
        stages_data = generic_data_creation(self, stages_data, WorkOrderStageSerializer, update_fields, using=db_name)
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
            stages_error = validate_put_method_data(self, stages_data, WorkOrderStageSerializer, exclude_fields, ProductionWorker, current_model_pk_field='work_stage_id')
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
        """Handles GET requests to retrieve BOM data with optional filters and reports."""
        try:
            if "pk" in kwargs:
                result = validate_input_pk(self, kwargs["pk"])
                return result if result else self.retrieve(self, request, *args, **kwargs)
            
            if request.query_params.get("bom_records", "false").lower() == "true":
                return self.get_bom_records(request)
            
            if request.query_params.get("bom_report", "false").lower() == "true":
                return self.get_bom_report(request)
            
            if request.query_params.get("raw_material_consumption_report", "false").lower() == "true":
                return self.get_raw_material_consumption_report(request)

            return self.get_bom_records(request)

        except BOM.DoesNotExist:
            logger.error("BOM does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_pagination_params(self, request):
        """Extracts pagination parameters from the request."""
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 10))
        return page, limit

    def get_raw_material_consumption_report(self, request):
        """Fetches usage of raw materials in production."""
        logger.info("Retrieving Raw Material Consumption Report")

        page, limit = self.get_pagination_params(request)
        
        # Query to get raw material consumption data - grouped by product
        queryset = BillOfMaterials.objects.values(
            'product_id__name'  # Group by product name
        ).annotate(
            total_consumed_quantity=Sum('quantity', output_field=models.DecimalField()),
            total_cost=Sum(F('quantity') * F('unit_cost'), output_field=models.DecimalField()),
            last_consumption_date=Max('updated_at')  # Get the most recent usage date
        ).order_by('-total_consumed_quantity')  # Sort by consumption quantity in descending order

        total_count = queryset.count()
        
        # Apply filters using RawMaterialConsumptionReportFilter
        if request.query_params:
            filterset = RawMaterialConsumptionReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        serializer = RawMaterialConsumptionReportSerializer(queryset, many=True)
        return filter_response(total_count, "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)
    
    def get_bom_records(self, request):
        """Fetches paginated BOM records with applied filters."""
        logger.info("Retrieving all BOM records")
        page, limit = self.get_pagination_params(request)
        
        queryset = BOM.objects.all().order_by("-created_at")
        
        if request.query_params:
            filterset = BillOfMaterialsFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        total_count = BOM.objects.count()

        serializer = BOMSerializer(queryset, many=True)
        return filter_response(len(serializer.data), "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)
    
    def get_bom_report(self, request):
        """Fetches BOM details for products."""
        logger.info("Retrieving BOM report data")
        page, limit = self.get_pagination_params(request)
        queryset = BOM.objects.all().order_by('bom_name')
        if request.query_params:
            filterset = BOMReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        total_count = BOM.objects.count()
        serializer = BOMReportSerializer(queryset, many=True)
        
        return filter_response(len(serializer.data), "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)

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
            BillOfMaterials.objects.filter(reference_id=pk).update(is_deleted=True)

            # Delete the main WorkOrder instance
            # Soft delete the main WorkOrder
            instance.is_deleted = True
            instance.save()

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
