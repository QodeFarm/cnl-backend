from decimal import Decimal
import logging
import re
import datetime
from django.forms import FloatField
from django.http import Http404
from django.db import transaction
from django.utils import timezone
from django.db.models import Q,Sum,F,Count,ExpressionWrapper,DecimalField,Value,IntegerField,OuterRef, Subquery, Max
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch
from rest_framework.filters import OrderingFilter
from apps.production.filters import BOMFilter, MachineFilter, MaterialFilter, MaterialIssueFilter, MaterialReceivedFilter, ProductionStatusFilter, StockJournalFilter, StockSummaryFilter, WorkOrderFilter,BOMReportFilter, BillOfMaterialsFilter, MachineFilter, MachineUtilizationReportFilter, MaterialFilter, ProductionCostReportFilter, ProductionStatusFilter, ProductionSummaryReportFilter, RawMaterialConsumptionReportFilter, WorkOrderFilter
from config.utils_db_router import set_db
from config.utils_filter_methods import filter_response, list_filtered_objects
from .models import *
from apps.products.models import Products, ProductVariation
from apps.products.serializers import ProductVariationSerializer, productsSerializer
from .serializers import *
from config.utils_methods import normalize_value, build_response, delete_multi_instance, soft_delete, generic_data_creation, get_related_data, list_all_objects, create_instance, product_stock_verification, update_instance, update_multi_instances, update_product_stock, validate_input_pk, validate_multiple_data, validate_order_type, validate_payload_data, validate_put_method_data
from django.db.models.functions import Coalesce,NullIf,Cast,ExtractSecond
from django.db.models import Avg
from rest_framework.views import APIView
from rest_framework import status
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from .models import MaterialIssue, MaterialIssueItem, MaterialIssueAttachment
from .serializers import MaterialIssueSerializer, MaterialIssueItemSerializer, MaterialIssueAttachmentSerializer
from config.utils_methods import build_response, generic_data_creation, get_related_data, update_multi_instances, soft_delete, validate_input_pk, validate_payload_data


# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)

class StockJournalViewSet(viewsets.ModelViewSet):
    queryset = StockJournal.objects.filter(is_deleted=False).order_by('-created_at')
    serializer_class = StockJournalsSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = StockJournalFilter
    
    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


# class StockSummaryViewSet(viewsets.ModelViewSet):
#     queryset = StockSummary.objects.filter(is_deleted=False).order_by('-period_end')
#     serializer_class = StockSummarySerializer
#     filter_backends = [DjangoFilterBackend, OrderingFilter]
#     filterset_class = StockSummaryFilter
#     ordering_fields = ['product_id__name', 'period_start', 'period_end', 'closing_quantity']
    
#     def list(self, request, *args, **kwargs):
#         return list_all_objects(self, request, *args, **kwargs)

#     def create(self, request, *args, **kwargs):
#         return create_instance(self, request, *args, **kwargs)

#     def update(self, request, *args, **kwargs):
#         return update_instance(self, request, *args, **kwargs)



class BOMViewSet(viewsets.ModelViewSet):
    queryset = BOM.objects.all().order_by('is_deleted', '-created_at')
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
    queryset = BillOfMaterials.objects.all().order_by('is_deleted', '-created_at')
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
    queryset = ProductionStatus.objects.all().order_by('is_deleted', '-created_at')
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
    queryset = WorkOrder.objects.all().order_by('is_deleted', '-created_at')
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
    queryset = Machine.objects.all().order_by('is_deleted', '-created_at')
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

@transaction.atomic
def update_product_stock_with_bom(work_order_id, completed_qty, using='default'):
    """
    Update product stock based on completed quantity and BOM calculations
    """
    try:
        # Get the work order
        work_order = WorkOrder.objects.using(using).get(work_order_id=work_order_id)
        product_id = work_order.product_id
        
        # Get all BOM items for this work order
        bom_items = BillOfMaterials.objects.using(using).filter(reference_id=work_order_id)
        
        # Update main product stock (add completed quantity)
        main_product = Products.objects.using(using).get(product_id=product_id)
        main_product.balance += completed_qty
        main_product.save(using=using)
        logger.info(f'Updated main product stock for Product ID: {product_id}, added: {completed_qty}')
        
        # Update each BOM component stock (subtract calculated quantity)
        for bom_item in bom_items:
            component_qty = completed_qty * bom_item.quantity
            component_product = Products.objects.using(using).get(product_id=bom_item.product_id)
            component_product.balance -= component_qty
            component_product.save(using=using)
            logger.info(f'Updated component stock for Product ID: {bom_item.product_id}, subtracted: {component_qty}')
            
    except Exception as e:
        logger.error(f'Error updating stock with BOM: {str(e)}')
        raise
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

            if request.query_params.get("summary", "false").lower() == "true" + "&":
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

        total_count = WorkOrder.objects.count() #queryset.count()
        # Apply pagination manually (if filter_response does not handle it)
        start = (page - 1) * limit
        end = start + limit
        page_queryset = queryset[start:end]
        
        serializer = WorkOrderSerializer(queryset, many=True)
        return filter_response(len(serializer.data), "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)
    # def get_work_orders(self, request):
    #     logger.info(f'We are in the method')
    #     queryset = WorkOrder.objects.annotate(pending_qty=F("quantity") - F("completed_qty"))
        
    #     # Apply filters
    #     filterset = WorkOrderFilter(request.GET, queryset=queryset)
    #     if filterset.is_valid():
    #         queryset = filterset.qs
            
    #     page, limit = self.get_pagination_params(request)
    #     total_count = WorkOrder.objects.count()  # <-- total number of matching records
    #     logger.info(f'We are in the method: {total_count}')
    #     # Apply pagination
    #     start = (page - 1) * limit
    #     end = start + limit
    #     page_queryset = queryset[start:end]

    #     serializer = WorkOrderSerializer(page_queryset, many=True)

    #     # Send correct totalCount
    #     return filter_response(
    #         len(serializer.data),            # total matching records
    #         "Success",
    #         serializer.data,
    #         page,
    #         limit,
    #         total_count,
    #         status.HTTP_200_OK
    #     )


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

    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        """
        Restores a soft-deleted WorkOrder record (is_deleted=True → is_deleted=False).
        """
        try:
            instance = WorkOrder.objects.get(pk=pk)

            if not instance.is_deleted:
                logger.info(f"WorkOrder with ID {pk} is already active.")
                return build_response(0, "Record is already active", [], status.HTTP_400_BAD_REQUEST)

            instance.is_deleted = False
            instance.save()

            logger.info(f"WorkOrder with ID {pk} restored successfully.")
            return build_response(1, "Record restored successfully", [], status.HTTP_200_OK)

        except WorkOrder.DoesNotExist:
            logger.warning(f"WorkOrder with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error restoring WorkOrder with ID {pk}: {str(e)}")
            return build_response(0, "Record restoration failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
            return build_response(0, "ValidationError: {errors}", errors, status.HTTP_400_BAD_REQUEST)

        # Stock Verification
        if bom_data:
            stock_error = product_stock_verification(Products, ProductVariation, bom_data)
            if stock_error:
                # Pick the first user-friendly error message
                # error_message = list(stock_error.values())[0] 
                # Build user-friendly messages including product name
                error_messages = [
                    f"{product}: {msg}" for product, msg in stock_error.items()
                ] 

                return build_response(
                    0,
                    error_messages[0],   # <-- directly show message like: "Insufficient stock..."
                    [],
                    status.HTTP_400_BAD_REQUEST
                )
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

# ---------------------working --------------------------------------
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
        work_order_error = None
        if work_order_data:
            work_order_error = validate_multiple_data(self, work_order_data , WorkOrderSerializer,[])
        
        # Validated BillOfMaterial Data
        bom_data = given_data.pop('bom', None)
        if bom_data:
            bom_error = validate_put_method_data(self, bom_data, BillOfMaterialsSerializer,['reference_id'], BillOfMaterials, current_model_pk_field='material_id')
        else:
            bom_error = []

        exclude_fields = ['work_order_id']
        # # Validated WorkOrderMachine Data
        # work_order_machines_data = given_data.pop('work_order_machines', None)
        # if work_order_machines_data:
        #     machinery_error = validate_put_method_data(self, work_order_machines_data, WorkOrderMachineSerializer, exclude_fields, WorkOrderMachine, current_model_pk_field='work_order_machines_id')
        # else:
        #     machinery_error = [] # Since 'default_machinery' is optional, so making an error is empty list
        # Validated WorkOrderMachine Data
        work_order_machines_data = normalize_value(given_data.pop('work_order_machines', None))
        if work_order_machines_data:
            work_order_machines_data = [d for d in work_order_machines_data if d.get("machine_id")]
            machinery_error = validate_multiple_data(self, work_order_machines_data, WorkOrderMachineSerializer, exclude_fields, using_db='default')
        else:
            machinery_error = []
            
        # # Validated ProductionWorker Data
        # workers_data = given_data.pop('workers', None)
        # if workers_data:
        #     workers_error = validate_put_method_data(self, workers_data, ProductionWorkerSerializer, exclude_fields, ProductionWorker, current_model_pk_field='worker_id')
        # else:
        #     workers_error = []
        
        # Validated ProductionWorker Data
        workers_data = normalize_value(given_data.pop('workers', None))
        if workers_data:
            workers_data = [d for d in workers_data if d.get("employee_id")]
            workers_error = validate_multiple_data(self, workers_data , ProductionWorkerSerializer,['work_order_id'], using_db='default')
        else:
            workers_error = []

        # Validated WorkOrderStage Data
        stages_data = normalize_value(given_data.pop('work_order_stages', None))
        if stages_data:
            stages_data = [d for d in stages_data if d.get("stage_id")]
            stages_error = validate_multiple_data(self, stages_data , WorkOrderStageSerializer,['work_order_id'], using_db='default')
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
        
        # Stock Verification
        if bom_data:
            stock_error = product_stock_verification(Products, ProductVariation, bom_data)
            if stock_error:
                # Pick the first user-friendly error message
                # error_message = list(stock_error.values())[0] 
                # Build user-friendly messages including product name
                error_messages = [
                    f"{product}: {msg}" for product, msg in stock_error.items()
                ] 

                return build_response(
                    0,
                    error_messages[0],   # <-- directly show message like: "Insufficient stock..."
                    [],
                    status.HTTP_400_BAD_REQUEST
                )
      
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

        # Get the work order instance after save
        work_order_instance = WorkOrder.objects.get(work_order_id=pk)
        
        # Get current values from request data
        current_sync_qty = work_order_data.get('sync_qty', None)
        current_completed_qty = int(work_order_data.get('completed_qty', 0) or 0)
        
        """Handle closed status"""
        pattern = r"(?i)\bclosed\b"
        order_status = work_order_data.get('status_id', None)
        if order_status:
            name = ProductionStatus.objects.get(status_id=order_status)
            if re.search(pattern, name.status_name):
                # Update inventory with completed_qty only (temp_quantity is already moved to completed_qty in save method)
                copy_data = work_order_data.copy()
                copy_data["quantity"] = work_order_instance.completed_qty or 0
                update_product_stock(Products, ProductVariation, [copy_data], 'add')
                logger.info('Stock Updated with completed quantity: %s', work_order_instance.completed_qty)
                
                return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

        # Handle inventory updates only when sync_qty is True
        if current_sync_qty:
            # Update inventory with the current completed_qty value
            copy_data = work_order_data.copy()
            copy_data["quantity"] = work_order_instance.completed_qty or 0
            update_product_stock(Products, ProductVariation, [copy_data], 'add')
            logger.info('Stock Updated with completed quantity: %s', work_order_instance.completed_qty)

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

    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        """
        Restores a soft-deleted BOM record (is_deleted=True → is_deleted=False).
        """
        try:
            instance = BOM.objects.get(pk=pk)

            if not instance.is_deleted:
                logger.info(f"BOM with ID {pk} is already active.")
                return build_response(0, "Record is already active", [], status.HTTP_400_BAD_REQUEST)

            instance.is_deleted = False
            instance.save()

            logger.info(f"BOM with ID {pk} restored successfully.")
            return build_response(1, "Record restored successfully", [], status.HTTP_200_OK)

        except BOM.DoesNotExist:
            logger.warning(f"BOM with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error restoring BOM with ID {pk}: {str(e)}")
            return build_response(0, "Record restoration failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        

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




class MaterialIssueView(APIView):
    """
    API View for handling Material Issue creation and related data.
    """

    def get_object(self, pk):
        try:
            return MaterialIssue.objects.get(pk=pk)
        except MaterialIssue.DoesNotExist:
            return None
        # return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk:
            result = validate_input_pk(self, pk)
            if result:
                return result
            return self.retrieve(request, pk)
        
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 10))

        queryset = MaterialIssue.objects.filter(is_deleted=False).order_by('-created_at')
        # Apply filters using RawMaterialConsumptionReportFilter
        if request.query_params:
            filterset = MaterialIssueFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs
        serializer = MaterialIssueSerializer(queryset, many=True)
        # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
        return filter_response( queryset.count(), "Success", serializer.data, page, limit, queryset.count(), status.HTTP_200_OK)

    def retrieve(self, request, pk):
        try:
            material_issue = get_object_or_404(MaterialIssue, pk=pk)
            serializer = MaterialIssueSerializer(material_issue)
            # Get related items and attachments
            items = get_related_data(MaterialIssueItem, MaterialIssueItemSerializer, 'material_issue_id', pk)
            attachments = get_related_data(MaterialIssueAttachment, MaterialIssueAttachmentSerializer, 'material_issue_id', pk)
            custom_data = {
                "material_issue": serializer.data,
                "items": items if items else [],
                "attachments": attachments if attachments else [],
            }
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)
        except Http404:
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        given_data = request.data
        errors = {}

        # Validate MaterialIssue Data
        material_issue_data = given_data.pop('material_issue', None)
        if not material_issue_data:
            return build_response(0, "material_issue data is mandatory", [], status.HTTP_400_BAD_REQUEST)
        issue_error = validate_payload_data(self, material_issue_data, MaterialIssueSerializer)
        if issue_error:
            errors["material_issue"] = issue_error

        # Validate items
        items_data = given_data.pop('items', [])
        items_error = validate_multiple_data(self, items_data, MaterialIssueItemSerializer, ['material_issue_id']) if items_data else None
        if items_error:
            errors["items"] = items_error

        # Validate attachments
        attachments_data = given_data.pop('attachments', [])
        attachments_error = validate_multiple_data(self, attachments_data, MaterialIssueAttachmentSerializer, ['material_issue_id']) if attachments_data else None
        if attachments_error:
            errors["attachments"] = attachments_error
        # ...existing code...    

        if errors:
            return build_response(0, "ValidationError", errors, status.HTTP_400_BAD_REQUEST)

        # Create MaterialIssue
        new_issue = generic_data_creation(self, [material_issue_data], MaterialIssueSerializer)[0]
        issue_id = new_issue.get("material_issue_id", None)

        # Create items
        new_items = []
        if items_data:
            new_items = generic_data_creation(self, items_data, MaterialIssueItemSerializer, {'material_issue_id': issue_id})

             
        for item in new_items:
            product_id = item.get('product_id')
            qty = Decimal(item.get('quantity', 0))
            try:
                product = Products.objects.get(product_id=product_id)
                # Reduce stock
                product.balance = product.balance - qty
                product.save()
                # --- Stock Journal Entry---
                StockJournal.objects.create(
                    product_id=product,
                    transaction_type='Issue',
                    quantity=qty,
                    reference_id=issue_id,
                    remarks='Material Issue to Production Floor'
                )
            except Products.DoesNotExist:
                logger.warning(f"Product {product_id} not found for inventory update.")

        # Create attachments
        new_attachments = []
        if attachments_data:
            new_attachments = generic_data_creation(self, attachments_data, MaterialIssueAttachmentSerializer, {'material_issue_id': issue_id})

        custom_data = {
            "material_issue": new_issue,
            "items": new_items,
            "attachments": new_attachments,
        }
        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)

    @transaction.atomic
    def put(self, request, pk, *args, **kwargs):
        return self.update(request, pk, *args, **kwargs)

    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):
        given_data = request.data
        errors = {}

        # Validate MaterialIssue Data
        # material_issue_data = given_data.pop('material_issue', None)
        # if material_issue_data:
        #     material_issue_data['material_issue_id'] = pk
        #     issue_error = validate_multiple_data(self, material_issue_data, MaterialIssueSerializer, [])
        #     if issue_error:
        #         errors["material_issue"] = issue_error

        material_issue_data = given_data.pop('material_issue', None)
        if material_issue_data:
            material_issue_data['material_issue_id'] = pk
            instance = MaterialIssue.objects.get(pk=pk)
            serializer = MaterialIssueSerializer(instance, data=material_issue_data, partial=False)
            if not serializer.is_valid():
                errors["material_issue"] = serializer.errors
            else:
                updated_issue = serializer.save()
        else:
            updated_issue = None
        # Validate items
        items_data = given_data.pop('items', [])
        items_error = validate_multiple_data(self, items_data, MaterialIssueItemSerializer, []) if items_data else None
        if items_error:
            errors["items"] = items_error

        # Validate attachments
        attachments_data = given_data.pop('attachments', [])
        attachments_error = validate_multiple_data(self, attachments_data, MaterialIssueAttachmentSerializer, []) if attachments_data else None
        if attachments_error:
            errors["attachments"] = attachments_error

        if errors:
            return build_response(0, "ValidationError", errors, status.HTTP_400_BAD_REQUEST)

        # Update MaterialIssue
        updated_issue = update_multi_instances(self, pk, [material_issue_data], MaterialIssue, MaterialIssueSerializer, [], main_model_related_field='material_issue_id', current_model_pk_field='material_issue_id')[0]

        # Inventory update BEFORE updating items
        for item_data in items_data:
            item_id = item_data.get('material_issue_item_id')
            print(23, item_id)
            new_qty = Decimal(item_data.get('quantity', 0))
            try:
                item_instance = MaterialIssueItem.objects.get(pk=item_id)
                old_qty = Decimal(item_instance.quantity)
                product = item_instance.product_id

                qty_diff = new_qty - old_qty
                if qty_diff != 0:
                    product.balance -= qty_diff
                    product.save()
                    # Instead of creating a new StockJournal entry, update the existing one:
                journal_entry = StockJournal.objects.filter(
                    reference_id=pk,
                    product_id=product,
                    transaction_type__in=['Issue', 'Receive']  # or match your types
                ).first()

                if journal_entry:
                    journal_entry.quantity = new_qty  # or the latest value
                    journal_entry.remarks = f'Material Issue quantity edited ({"Reduced" if qty_diff > 0 else "Returned"})'
                    journal_entry.save()
                else:
                    # If not found, create new (for legacy data)
                    StockJournal.objects.create(
                        product_id=product,
                        transaction_type='Issue',
                        quantity=new_qty,
                        reference_id=pk,
                        remarks='Material Issue to Production Floor'
                    )
            except MaterialIssueItem.DoesNotExist:
                continue


        # Update items
        updated_items = []
        if items_data:
            updated_items = update_multi_instances(self, pk, items_data, MaterialIssueItem, MaterialIssueItemSerializer, {'material_issue_id': pk}, main_model_related_field='material_issue_id', current_model_pk_field='material_issue_item_id')
            

        # Update attachments
        updated_attachments = []
        if attachments_data:
            updated_attachments = update_multi_instances(self, pk, attachments_data, MaterialIssueAttachment, MaterialIssueAttachmentSerializer, {'material_issue_id': pk}, main_model_related_field='material_issue_id', current_model_pk_field='attachment_id')

        custom_data = {
            "material_issue": updated_issue,
            "items": updated_items,
            "attachments": updated_attachments,
        }
        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

    # @transaction.atomic
    # def patch(self, request, pk, *args, **kwargs):
    #     try:
    #         material_issue = MaterialIssue.objects.filter(pk=pk).first()
    #         if not material_issue:
    #             return build_response(0, "Material Issue not found", [], status.HTTP_404_NOT_FOUND)
    #         serializer = MaterialIssueSerializer(material_issue, data=request.data, partial=True)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return build_response(1, "Material Issue updated successfully", serializer.data, status.HTTP_200_OK)
    #         return build_response(0, "Validation error", serializer.errors, status.HTTP_400_BAD_REQUEST)
    #     except Exception as e:
    #         return build_response(0, f"Error updating Material Issue: {str(e)}", [], status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        try:
            instance = MaterialIssue.objects.get(pk=pk)
            instance.is_deleted = True
            instance.save()
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except MaterialIssue.DoesNotExist:
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return build_response(0, f"Record deletion failed due to an error: {e}", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class MaterialReceivedView(APIView):
    """
    API View for handling Material Received creation and related data.
    """

    def get_object(self, pk):
        try:
            return MaterialReceived.objects.get(pk=pk)
        except MaterialReceived.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        if pk:
            result = validate_input_pk(self, pk)
            if result:
                return result
            return self.retrieve(request, pk)
        
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 10))

        queryset = MaterialReceived.objects.filter(is_deleted=False).order_by('-created_at')
         # Apply filters using RawMaterialConsumptionReportFilter
        if request.query_params:
            filterset = MaterialReceivedFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs
        # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)

        serializer = MaterialReceivedSerializer(queryset, many=True)
        return filter_response( queryset.count(), "Success", serializer.data, page, limit, queryset.count(), status.HTTP_200_OK)

    def retrieve(self, request, pk):
        try:
            material_received = get_object_or_404(MaterialReceived, pk=pk)
            serializer = MaterialReceivedSerializer(material_received)
            # Get related items and attachments
            items = get_related_data(MaterialReceivedItem, MaterialReceivedItemSerializer, 'material_received_id', pk)
            attachments = get_related_data(MaterialReceivedAttachment, MaterialReceivedAttachmentSerializer, 'material_received_id', pk)
            custom_data = {
                "material_received": serializer.data,
                "items": items if items else [],
                "attachments": attachments if attachments else [],
            }
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)
        except Http404:
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        given_data = request.data
        errors = {}

        # Validate MaterialReceived Data
        material_received_data = given_data.pop('material_received', None)
        if not material_received_data:
            return build_response(0, "material_received data is mandatory", [], status.HTTP_400_BAD_REQUEST)
        received_error = validate_payload_data(self, material_received_data, MaterialReceivedSerializer)
        if received_error:
            errors["material_received"] = received_error

        # Validate items
        items_data = given_data.pop('items', [])
        items_error = validate_multiple_data(self, items_data, MaterialReceivedItemSerializer, ['material_received_id']) if items_data else None
        if items_error:
            errors["items"] = items_error

        # Validate attachments
        attachments_data = given_data.pop('attachments', [])
        attachments_error = validate_multiple_data(self, attachments_data, MaterialReceivedAttachmentSerializer, ['material_received_id']) if attachments_data else None
        if attachments_error:
            errors["attachments"] = attachments_error

        if errors:
            return build_response(0, "ValidationError", errors, status.HTTP_400_BAD_REQUEST)

        # Create MaterialReceived
        new_received = generic_data_creation(self, [material_received_data], MaterialReceivedSerializer)[0]
        received_id = new_received.get("material_received_id", None)

        # Create items
        new_items = []
        if items_data:
            new_items = generic_data_creation(self, items_data, MaterialReceivedItemSerializer, {'material_received_id': received_id})

        # --- Inventory Update Logic ---
        for item in new_items:
            product_id = item.get('product_id')
            qty = Decimal(item.get('quantity', 0))
            try:
                product = Products.objects.get(product_id=product_id)
                # Increase stock
                product.balance = product.balance + qty
                product.save()
                # --- Stock Journal Entry (optional) ---
                StockJournal.objects.create(
                    product_id=product,
                    transaction_type='Receive',
                    quantity=qty,
                    reference_id=received_id,
                    remarks='Material Received from Production Floor'
                )
            except Products.DoesNotExist:
                logger.warning(f"Product {product_id} not found for inventory update.")
    

       
        # Create attachments
        new_attachments = []
        if attachments_data:
            new_attachments = generic_data_creation(self, attachments_data, MaterialReceivedAttachmentSerializer, {'material_received_id': received_id})

        custom_data = {
            "material_received": new_received,
            "items": new_items,
            "attachments": new_attachments,
        }
        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)

    @transaction.atomic
    def put(self, request, pk, *args, **kwargs):
        return self.update(request, pk, *args, **kwargs)

    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):
        given_data = request.data
        errors = {}

        # Validate MaterialReceived Data
        material_received_data = given_data.pop('material_received', None)
        if material_received_data:
            material_received_data['material_received_id'] = pk
            instance = MaterialReceived.objects.get(pk=pk)
            serializer = MaterialReceivedSerializer(instance, data=material_received_data, partial=False)
            if not serializer.is_valid():
                errors["material_received"] = serializer.errors
            else:
                updated_received = serializer.save()
        else:
            updated_received = None

        # Validate items
        items_data = given_data.pop('items', [])
        items_error = validate_multiple_data(self, items_data, MaterialReceivedItemSerializer, []) if items_data else None
        if items_error:
            errors["items"] = items_error

        # Validate attachments
        attachments_data = given_data.pop('attachments', [])
        attachments_error = validate_multiple_data(self, attachments_data, MaterialReceivedAttachmentSerializer, []) if attachments_data else None
        if attachments_error:
            errors["attachments"] = attachments_error

        if errors:
            return build_response(0, "ValidationError", errors, status.HTTP_400_BAD_REQUEST)

        # Update MaterialReceived
        updated_received = update_multi_instances(self, pk, [material_received_data], MaterialReceived, MaterialReceivedSerializer, [], main_model_related_field='material_received_id', current_model_pk_field='material_received_id')[0]

        # In MaterialReceivedView.update (inside the inventory update loop)
        for item_data in items_data:
            item_id = item_data.get('material_received_item_id')
            new_qty = Decimal(item_data.get('quantity', 0))
            try:
                item_instance = MaterialReceivedItem.objects.get(pk=item_id)
                old_qty = Decimal(item_instance.quantity)
                product = item_instance.product_id

                qty_diff = new_qty - old_qty
                if qty_diff != 0:
                    product.balance += qty_diff  # Add received difference to stock
                    product.save()
                    # Update existing StockJournal entry instead of creating a new one
                    journal_entry = StockJournal.objects.filter(
                        reference_id=pk,
                        product_id=product,
                        transaction_type__in=['Receive', 'Receive-Edit']
                    ).first()
                    if journal_entry:
                        journal_entry.quantity = new_qty
                        journal_entry.remarks = f'Material Received quantity edited ({"Increased" if qty_diff > 0 else "Reduced"})'
                        journal_entry.save()
                    else:
                        StockJournal.objects.create(
                            product_id=product,
                            transaction_type='Receive',
                            quantity=new_qty,
                            reference_id=pk,
                            remarks='Material Received from Production Floor'
                        )
            except MaterialReceivedItem.DoesNotExist:
                continue

        # Update items
        updated_items = []
        if items_data:
            updated_items = update_multi_instances(self, pk, items_data, MaterialReceivedItem, MaterialReceivedItemSerializer, {'material_received_id': pk}, main_model_related_field='material_received_id', current_model_pk_field='material_received_item_id')
          
        # Update attachments
        updated_attachments = []
        if attachments_data:
            updated_attachments = update_multi_instances(self, pk, attachments_data, MaterialReceivedAttachment, MaterialReceivedAttachmentSerializer, {'material_received_id': pk}, main_model_related_field='material_received_id', current_model_pk_field='material_received_attachment_id')

        custom_data = {
            "material_received": updated_received,
            "items": updated_items,
            "attachments": updated_attachments,
        }
        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

    # @transaction.atomic
    # def patch(self, request, pk, *args, **kwargs):
    #     try:
    #         material_received = MaterialReceived.objects.filter(pk=pk).first()
    #         if not material_received:
    #             return build_response(0, "Material Received not found", [], status.HTTP_404_NOT_FOUND)
    #         serializer = MaterialReceivedSerializer(material_received, data=request.data, partial=True)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return build_response(1, "Material Received updated successfully", serializer.data, status.HTTP_200_OK)
    #         return build_response(0, "Validation error", serializer.errors, status.HTTP_400_BAD_REQUEST)
    #     except Exception as e:
    #         return build_response(0, f"Error updating Material Received: {str(e)}", [], status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        try:
            instance = MaterialReceived.objects.get(pk=pk)
            instance.is_deleted = True
            instance.save()
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except MaterialReceived.DoesNotExist:
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return build_response(0, f"Record deletion failed due to an error: {e}", [], status.HTTP_500_INTERNAL_SERVER_ERROR)    




# Add this class for a more flexible API approach
class StockSummaryAPIView(APIView):
    """
    API for generating and retrieving stock summary reports
    """
    
    def get_pagination_params(self, request):
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 10))
        return page, limit
    
    def get(self, request, *args, **kwargs):
        try:
            # Extract date range parameters
            from_date = request.query_params.get('from_date')
            to_date = request.query_params.get('to_date')
            
            if not from_date or not to_date:
                # Default to today only (for daily view)
                today = timezone.now().date()
                from_date = today.isoformat()
                to_date = today.isoformat()
            
            # Convert to datetime objects
            start_date = datetime.datetime.strptime(from_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(to_date, '%Y-%m-%d').date()
            
            # Get or generate stock summary for the period
            self.generate_stock_summary(start_date, end_date)
            
            page, limit = self.get_pagination_params(request)
            
            # Query the stock summary
            queryset = StockSummary.objects.filter(
                period_start=start_date,
                period_end=end_date,
                is_deleted=False
            ).order_by('product_id__product_group_id__group_name', 'product_id__name')
            
            # Apply filters if any
            if request.query_params:
                filterset = StockSummaryFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs
            
            total_count = queryset.count()
            serializer = StockSummarySerializer(queryset, many=True)
            
            return filter_response(
                queryset.count(), 
                "Success", 
                serializer.data, 
                page, 
                limit, 
                total_count, 
                status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error retrieving stock summary: {str(e)}")
            return build_response(
                0, 
                f"An error occurred: {str(e)}", 
                [], 
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def generate_stock_summary(self, start_date, end_date):
        """
        Generates stock summary for all products for the given period
        """
        with transaction.atomic():
            # Get all products
            products = Products.objects.filter(is_deleted=False)
            
            for product in products:
                # Find existing summary or create new
                summary, created = StockSummary.objects.get_or_create(
                    product_id=product,
                    period_start=start_date,
                    period_end=end_date,
                    defaults={
                        'unit_options_id': product.unit_options_id,
                        'mrp': product.mrp or 0,
                        'sales_rate': product.sales_rate or 0,
                        'purchase_rate': product.purchase_rate or 0,
                    }
                )
                
                # Calculate transactions within this period
                stock_movements = StockJournal.objects.filter(
                    product_id=product,
                    created_at__date__gte=start_date,
                    created_at__date__lte=end_date,
                    is_deleted=False
                )
                
                received_qty = stock_movements.filter(
                    transaction_type__in=['Receive', 'receive', 'RECEIVE', 'receive-edit']
                ).aggregate(Sum('quantity'))['quantity__sum'] or 0
                
                issued_qty = stock_movements.filter(
                    transaction_type__in=['Issue', 'issue', 'ISSUE', 'issue-edit']
                ).aggregate(Sum('quantity'))['quantity__sum'] or 0
                
                # IMPORTANT: Calculate opening balance by REMOVING the effect of current period transactions
                # Current balance minus (received minus issued) during period
                current_balance = product.balance
                opening_qty = current_balance - (received_qty - issued_qty)
                
                # Calculate closing stock (current balance)
                closing_qty = current_balance
                
                # Update the summary
                summary.opening_quantity = opening_qty
                summary.closing_quantity = closing_qty
                summary.received_quantity = received_qty
                summary.issued_quantity = issued_qty
                summary.save()