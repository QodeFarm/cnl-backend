import logging
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from apps.purchase.filters import PurchaseInvoiceOrdersFilter, PurchaseOrdersFilter, PurchaseReturnOrdersFilter
from config.utils_filter_methods import filter_response
from .models import *
from .serializers import *
from config.utils_methods import *
from config.utils_variables import *
from config.utils_methods import update_multi_instances, validate_input_pk, delete_multi_instance, generic_data_creation, get_object_or_none, list_all_objects, create_instance, update_instance, build_response, validate_multiple_data, validate_order_type, validate_payload_data, validate_put_method_data
from uuid import UUID
from apps.products.models import Products, ProductVariation
from apps.sales.serializers import OrderAttachmentsSerializer,OrderShipmentsSerializer
from apps.sales.models import OrderAttachments,OrderShipments
from rest_framework import viewsets
from apps.masters.models import OrderTypes
from rest_framework.views import APIView
from django.db import transaction
from rest_framework.serializers import ValidationError
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import OrderingFilter

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)

# Create your views here.
class PurchaseOrdersViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrders.objects.all()
    serializer_class = PurchaseOrdersSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = PurchaseOrdersFilter
    ordering_fields = []
 
    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)
 
    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)
 
    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
 
class PurchaseorderItemsViewSet(viewsets.ModelViewSet):
    queryset = PurchaseorderItems.objects.all()
    serializer_class = PurchaseorderItemsSerializer
 
    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)
 
    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)
 
    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
 
class PurchaseInvoiceOrdersViewSet(viewsets.ModelViewSet):
    queryset = PurchaseInvoiceOrders.objects.all()
    serializer_class = PurchaseInvoiceOrdersSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = PurchaseInvoiceOrdersFilter
    ordering_fields = []
 
    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)
 
    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)
 
    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
 
class PurchaseInvoiceItemViewSet(viewsets.ModelViewSet):
    queryset = PurchaseInvoiceItem.objects.all()
    serializer_class = PurchaseInvoiceItemSerializer
 
    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)
 
    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)
 
    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
 
class PurchaseReturnOrdersViewSet(viewsets.ModelViewSet):
    queryset = PurchaseReturnOrders.objects.all()
    serializer_class = PurchaseReturnOrdersSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = PurchaseReturnOrdersFilter
    ordering_fields = []
 
    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)
 
    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)
 
    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
   
class PurchaseReturnItemsViewSet(viewsets.ModelViewSet):
    queryset = PurchaseReturnItems.objects.all()
    serializer_class = PurchaseReturnItemsSerializer
 
    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)
 
    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)
 
    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
 
class PurchasePriceListViewSet(viewsets.ModelViewSet):
    queryset = PurchasePriceList.objects.all()
    serializer_class = PurchasePriceListSerializer
 
    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)
 
    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)
 
    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
#=======================PurchaseOrder=====================================================
class PurchaseOrderViewSet(APIView):
    """
    API ViewSet for handling purchase order creation and related data.
    """
    def get_object(self, pk):
        try:
            return PurchaseOrders.objects.get(pk=pk)
        except PurchaseOrders.DoesNotExist:
            logger.warning(f"PurchaseOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        
    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:
           result =  validate_input_pk(self,kwargs['pk'])
           return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            summary = request.query_params.get("summary", "false").lower() == "true"+ "&"
            if summary:
                logger.info("Retrieving Purchase order summary")
                purchaseorders = PurchaseOrders.objects.all().order_by('-created_at', '-updated_at')
                data = PurchaseOrdersOptionsSerializer.get_purchase_orders_summary(purchaseorders)
                return build_response(len(data), "Success", data, status.HTTP_200_OK)
            
            instance = PurchaseOrders.objects.all().order_by('-created_at', '-updated_at')
            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 
            total_count = PurchaseOrders.objects.count()

            # Apply filters manually
            if request.query_params:
                queryset = PurchaseOrders.objects.all()
                filterset = PurchaseOrdersFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs
                    serializer = PurchaseOrdersOptionsSerializer(queryset, many=True)
                    # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
                    return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except PurchaseOrders.DoesNotExist:
            logger.error("Purchase order does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        else:
            serializer = PurchaseOrdersSerializer(instance, many=True)
            logger.info("Purchase order data retrieved successfully.")
            return build_response(instance.count(), "Success", serializer.data, status.HTTP_200_OK)
        

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a purchase order and its related data (items, attachments, and shipments).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the PurchaseOrders instance
            purchase_order = get_object_or_404(PurchaseOrders, pk=pk)
            purchase_order_serializer = PurchaseOrdersSerializer(purchase_order)

            # Retrieve related data
            items_data = self.get_related_data(PurchaseorderItems, PurchaseorderItemsSerializer, 'purchase_order_id', pk)
            attachments_data = self.get_related_data(OrderAttachments, OrderAttachmentsSerializer, 'order_id', pk)
            shipments_data = self.get_related_data(OrderShipments, OrderShipmentsSerializer, 'order_id', pk)
            shipments_data = shipments_data[0] if len(shipments_data)>0 else {}
              
            # Customizing the response data
            custom_data = {
                "purchase_order_data": purchase_order_serializer.data,
                "purchase_order_items": items_data,
                "order_attachments": attachments_data,
                "order_shipments": shipments_data
            }
            logger.info("Purchase order and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)
        
        except Http404:
            logger.error("Purchase order with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("An error occurred while retrieving purchase order with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get_related_data(self, model, serializer_class, filter_field, filter_value):
        """
        Retrieves related data for a given model, serializer, and filter field.
        """
        try:
            related_data = model.objects.filter(**{filter_field: filter_value})
            serializer = serializer_class(related_data, many=True)
            logger.debug("Retrieved related data for model %s with filter %s=%s.", model.__name__, filter_field, filter_value)
            return serializer.data
        except Exception as e:
            logger.exception("Error retrieving related data for model %s with filter %s=%s: %s", model.__name__, filter_field, filter_value, str(e))
            return []

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a purchase order and its related attachments and shipments.
        """
        try:
            # Get the PurchaseOrders instance
            instance = PurchaseOrders.objects.get(pk=pk)

            # Delete related OrderAttachments and OrderShipments
            if not delete_multi_instance(pk, PurchaseOrders, OrderAttachments, main_model_field_name='order_id'):
                return build_response(0, "Error deleting related order attachments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
            if not delete_multi_instance(pk, PurchaseOrders, OrderShipments, main_model_field_name='order_id'):
                return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Delete the main PurchaseOrders instance
            instance.delete()

            logger.info(f"PurchaseOrders with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except PurchaseOrders.DoesNotExist:
            logger.warning(f"PurchaseOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting PurchaseOrders with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Handling POST requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
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

        # Validated PurchaseOrders Data
        purchase_order_data = given_data.pop('purchase_order_data', None) # parent_data
        if purchase_order_data:
            order_error = validate_payload_data(self, purchase_order_data , PurchaseOrdersSerializer)
            # validate the order_type in 'purchase_order' data
            validate_order_type(purchase_order_data, order_error, OrderTypes,look_up='order_type')


        # Validated PurchaseorderItems Data
        purchase_order_items_data = given_data.pop('purchase_order_items', None)
        if purchase_order_items_data:
            item_error = validate_multiple_data(self, purchase_order_items_data,PurchaseorderItemsSerializer,['purchase_order_id'])

        # Validated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        if order_attachments_data:
            attachment_error = validate_multiple_data(self, order_attachments_data ,OrderAttachmentsSerializer,['order_id','order_type_id'])
        else:
            attachment_error = [] # Since 'order_attachments' is optional, so making an error is empty list

        # Validated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_multiple_data(self, [order_shipments_data] , OrderShipmentsSerializer,['order_id','order_type_id'])
        else:
            shipments_error = [] # Since 'order_shipments' is optional, so making an error is empty list

        # Ensure mandatory data is present
        if not purchase_order_data or not purchase_order_items_data:
            logger.error("Purchase order and Purchase order items are mandatory but not provided.")
            return build_response(0, "Purchase order and Purchase order items are mandatory", [], status.HTTP_400_BAD_REQUEST)
        
        errors = {}
        if order_error:
            errors["purchase_order_data"] = order_error
        if item_error:
                errors["purchase_order_items"] = item_error
        if attachment_error:
                errors['order_attachments'] = attachment_error
        if shipments_error:
                errors['order_shipments'] = shipments_error
        if errors:
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)
        
        #---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """
            
        # Hence the data is validated , further it can be created.

        # Create PurchaseOrders Data
        new_purchase_order_data = generic_data_creation(self, [purchase_order_data], PurchaseOrdersSerializer)
        new_purchase_order_data = new_purchase_order_data[0]
        purchase_order_id = new_purchase_order_data.get("purchase_order_id",None) #Fetch purchase_order_id from mew instance
        logger.info('PurchaseOrders - created*')

        # Create PurchaseorderItems Data
        update_fields = {'purchase_order_id':purchase_order_id}
        items_data = generic_data_creation(self, purchase_order_items_data, PurchaseorderItemsSerializer, update_fields)
        logger.info('PurchaseorderItems - created*')

        # Get order_type_id from OrderTypes model
        order_type_val = purchase_order_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Create OrderAttchments Data
        update_fields = {'order_id':purchase_order_id, 'order_type_id':type_id}
        if order_attachments_data:
            order_attachments = generic_data_creation(self, order_attachments_data, OrderAttachmentsSerializer, update_fields)
            logger.info('OrderAttchments - created*')
        else:
            # Since OrderAttchments Data is optional, so making it as an empty data list
            order_attachments = []

        # create OrderShipments Data
        if order_shipments_data:
            order_shipments = generic_data_creation(self, [order_shipments_data], OrderShipmentsSerializer, update_fields)
            order_shipments = order_shipments[0]
            logger.info('OrderShipments - created*')
        else:
            # Since OrderShipments Data is optional, so making it as an empty data list
            order_shipments = {}

        custom_data = {
            "purchase_order":new_purchase_order_data,
            "purchase_order_items":items_data,
            "order_attachments":order_attachments,
            "order_shipments":order_shipments,
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

        # Validated PurchaseOrders Data
        purchase_order_data = given_data.pop('purchase_order_data', None) # parent_data
        if purchase_order_data:
            purchase_order_data['purchase_order_id'] = pk    
            order_error = validate_multiple_data(self, purchase_order_data , PurchaseOrdersSerializer,['order_no'])
            # validate the 'order_type' in 'purchase_order_data' data
            validate_order_type(purchase_order_data, order_error, OrderTypes,look_up='order_type')

        # Validated PurchaseorderItems Data
        purchase_order_items_data = given_data.pop('purchase_order_items', None)
        if purchase_order_items_data:
            exclude_fields = ['purchase_order_id']
            item_error = validate_put_method_data(self, purchase_order_items_data, PurchaseorderItemsSerializer, exclude_fields, PurchaseorderItems, current_model_pk_field='purchase_order_item_id')

        # Validated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        exclude_fields = ['order_id','order_type_id']
        if order_attachments_data:
            attachment_error = validate_put_method_data(self, order_attachments_data, OrderAttachmentsSerializer, exclude_fields, OrderAttachments, current_model_pk_field='attachment_id')
        else:
            attachment_error = [] # Since 'order_attachments' is optional, so making an error is empty list

        # Validated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_put_method_data(self, [order_shipments_data], OrderShipmentsSerializer, exclude_fields, OrderShipments, current_model_pk_field='shipment_id')
        else:
            shipments_error = [] # Since 'order_shipments' is optional, so making an error is empty list

        # Ensure mandatory data is present
        if not purchase_order_data or not purchase_order_items_data:
            logger.error("Purchase order and Purchase order items are mandatory but not provided.")
            return build_response(0, "Purchase order and Purchase order items are mandatory", [], status.HTTP_400_BAD_REQUEST)
        
        errors = {}
        if order_error:
            errors["purchase_order_data"] = order_error
        if item_error:
            errors["purchase_order_items"] = item_error
        if attachment_error:
            errors['order_attachments'] = attachment_error
        if shipments_error:
            errors['order_shipments'] = shipments_error
        if errors:
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)

        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#
        # update PurchaseOrders
        if purchase_order_data:
            update_fields = {} # No need to update any fields
            purchaseorder_data = update_multi_instances(self, pk, [purchase_order_data], PurchaseOrders, PurchaseOrdersSerializer, update_fields,main_model_related_field='purchase_order_id', current_model_pk_field='purchase_order_id')
            purchaseorder_data = purchaseorder_data[0] if len(purchaseorder_data)==1 else purchaseorder_data

        # Update the 'purchase_order_items'
        update_fields = {'purchase_order_id':pk}
        items_data = update_multi_instances(self, pk, purchase_order_items_data, PurchaseorderItems, PurchaseorderItemsSerializer, update_fields, main_model_related_field='purchase_order_id', current_model_pk_field='purchase_order_item_id')

        # Get 'order_type_id' from 'OrderTypes' model
        order_type_val = purchase_order_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Update the 'order_attchments'
        update_fields = {'order_id':pk, 'order_type_id':type_id}
        attachment_data = update_multi_instances(self, pk, order_attachments_data, OrderAttachments, OrderAttachmentsSerializer, update_fields, main_model_related_field='order_id', current_model_pk_field='attachment_id')

        # Update the 'shipments'
        shipment_data = update_multi_instances(self, pk, order_shipments_data, OrderShipments, OrderShipmentsSerializer, update_fields, main_model_related_field='order_id', current_model_pk_field='shipment_id')
        shipment_data = shipment_data[0] if len(shipment_data)==1 else shipment_data

        custom_data = {
            "purchase_order":purchaseorder_data,
            "purchase_order_items":items_data if items_data else [],
            "order_attachments":attachment_data if attachment_data else [],
            "order_shipments":shipment_data if shipment_data else {}
        }

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)
    
#=======================PurchaseInvoiceOrder==============================================

class PurchaseInvoiceOrderViewSet(APIView):
    """
    API ViewSet for handling Purchase Invoice Order creation and related data.
    """
    def get_object(self, pk):
        try:
            return PurchaseInvoiceOrders.objects.get(pk=pk)
        except PurchaseInvoiceOrders.DoesNotExist:
            logger.warning(f"PurchaseInvoiceOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)   
      
    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:
           result =  validate_input_pk(self,kwargs['pk'])
           return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            summary = request.query_params.get("summary", "false").lower() == "true"+ "&"
            if summary:
                logger.info("Retrieving Purchase Invoice orders summary")
                purchaseinvoiceorders = PurchaseInvoiceOrders.objects.all().order_by('-created_at', '-updated_at')
                data = PurchaseInvoiceOrdersOptionsSerializer.get_purchase_invoice_orders_summary(purchaseinvoiceorders)
                return build_response(len(data), "Success", data, status.HTTP_200_OK)
            
            instance = PurchaseInvoiceOrders.objects.all().order_by('-created_at', '-updated_at')

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 
            total_count = PurchaseInvoiceOrders.objects.count()

            # Apply filters manually
            if request.query_params:
                queryset = PurchaseInvoiceOrders.objects.all()
                filterset = PurchaseInvoiceOrdersFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs
                    serializer = PurchaseInvoiceOrdersOptionsSerializer(queryset, many=True)
                    # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
                    return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except PurchaseInvoiceOrders.DoesNotExist:
            logger.error("Purchase invoice order does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        else:
            serializer = PurchaseInvoiceOrdersSerializer(instance, many=True)
            logger.info("Purchase invoice order data retrieved successfully.")
            return build_response(instance.count(), "Success", serializer.data, status.HTTP_200_OK)      
     
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a Purchase Invoice Orders and its related data (Invoiceitems, attachments, and shipments).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the PurchaseInvoiceOrders instance
            purchase_invoice_order = get_object_or_404(PurchaseInvoiceOrders, pk=pk)
            purchase_invoice_order_serializer = PurchaseInvoiceOrdersSerializer(purchase_invoice_order)

            # Retrieve related data
            invoice_items_data = self.get_related_data(PurchaseInvoiceItem, PurchaseInvoiceItemSerializer, 'purchase_invoice_id', pk)
            attachments_data = self.get_related_data(OrderAttachments, OrderAttachmentsSerializer, 'order_id', pk)
            shipments_data = self.get_related_data(OrderShipments, OrderShipmentsSerializer, 'order_id', pk)
            shipments_data = shipments_data[0] if len(shipments_data)>0 else {}
                
            # Customizing the response data
            custom_data = {
                "purchase_invoice_orders": purchase_invoice_order_serializer.data,
                "purchase_invoice_items": invoice_items_data,
                "order_attachments": attachments_data,
                "order_shipments": shipments_data
            }
            logger.info("Purchase invoice Order and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)
        
        except Http404:
            logger.error("Purchase invoice order with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("An error occurred while retrieving purchase invoice order with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
      
    def get_related_data(self, model, serializer_class, filter_field, filter_value):
        """
        Retrieves related data for a given model, serializer, and filter field.
        """
        try:
            related_data = model.objects.filter(**{filter_field: filter_value})
            serializer = serializer_class(related_data, many=True)
            logger.debug("Retrieved related data for model %s with filter %s=%s.", model.__name__, filter_field, filter_value)
            return serializer.data
        except Exception as e:
            logger.exception("Error retrieving related data for model %s with filter %s=%s: %s", model.__name__, filter_field, filter_value, str(e))
            return []

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a Purchase Invoice Orders and its related attachments and shipments.
        """
        try:
            # Get the PurchaseInvoiceOrders instance
            instance = PurchaseInvoiceOrders.objects.get(pk=pk)

            # Delete related OrderAttachments and OrderShipments
            if not delete_multi_instance(pk, PurchaseInvoiceOrders, OrderAttachments, main_model_field_name='order_id'):
                return build_response(0, "Error deleting related order attachments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
            if not delete_multi_instance(pk, PurchaseInvoiceOrders, OrderShipments, main_model_field_name='order_id'):
                return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Delete the main PurchaseInvoiceOrders instance
            instance.delete()

            logger.info(f"PurchaseInvoiceOrders with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except PurchaseInvoiceOrders.DoesNotExist:
            logger.warning(f"PurchaseInvoiceOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting PurchaseInvoiceOrders with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Handling POST requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
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

        # Validated PurchaseInvoiceOrders Data
        purchase_invoice_orders_data = given_data.pop('purchase_invoice_orders', None) # parent_data
        if purchase_invoice_orders_data:
            invoice_order_error = validate_payload_data(self, purchase_invoice_orders_data , PurchaseInvoiceOrdersSerializer)
            # validate the order_type in 'PurchaseInvoiceOrders' data
            validate_order_type(purchase_invoice_orders_data, invoice_order_error, OrderTypes,look_up='order_type')
                
        # Validated PurchaseInvoiceItems Data
        purchase_invoice_items_data = given_data.pop('purchase_invoice_items', None)
        if purchase_invoice_items_data:
            invoice_item_error = validate_multiple_data(self, purchase_invoice_items_data,PurchaseInvoiceItemSerializer,['purchase_invoice_id'])

        # Validated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        if order_attachments_data:
            attachment_error = validate_multiple_data(self, order_attachments_data ,OrderAttachmentsSerializer,['order_id','order_type_id'])
        else:
            attachment_error = [] # Since 'order_attachments' is optional, so making an error is empty list

        # Validated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_multiple_data(self, [order_shipments_data] , OrderShipmentsSerializer,['order_id','order_type_id'])
        else:
            shipments_error = [] # Since 'order_shipments' is optional, so making an error is empty list

        # Ensure mandatory data is present
        if not purchase_invoice_orders_data or not purchase_invoice_items_data:
            logger.error("Purchase invoice order and Purchase invoice items are mandatory but not provided.")
            return build_response(0, "Purchase invoice order and Purchase invoice items are mandatory", [], status.HTTP_400_BAD_REQUEST)
        
        errors = {}
        if invoice_order_error:
            errors["purchase_invoice_orders"] = invoice_order_error
        if invoice_item_error:
                errors["purchase_invoice_items"] = invoice_item_error
        if attachment_error:
                errors['order_attachments'] = attachment_error
        if shipments_error:
                errors['order_shipments'] = shipments_error
        if errors:
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)
        
        # Stock verification
        stock_error = product_stock_verification(Products, ProductVariation, purchase_invoice_items_data)
        if stock_error:
            return build_response(0, f"ValidationError :", stock_error, status.HTTP_400_BAD_REQUEST)        
        
        #---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """
            
        # Hence the data is validated , further it can be created.

        # Create PurchaseInvoiceOrders Data
        new_purchase_invoice_orders_data = generic_data_creation(self, [purchase_invoice_orders_data], PurchaseInvoiceOrdersSerializer)
        new_purchase_invoice_orders_data = new_purchase_invoice_orders_data[0]
        purchase_invoice_id = new_purchase_invoice_orders_data.get("purchase_invoice_id",None) #Fetch purchase_invoice_id from mew instance
        logger.info('PurchaseInvoiceOrders - created*')

        # Create PurchaseInvoiceItem Data
        update_fields = {'purchase_invoice_id': purchase_invoice_id}
        invoice_items_data = generic_data_creation(self, purchase_invoice_items_data, PurchaseInvoiceItemSerializer, update_fields)
        logger.info('PurchaseInvoiceItem - created*')

        # Get order_type_id from OrderTypes model
        order_type_val = purchase_invoice_orders_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Create OrderAttchments Data
        update_fields = {'order_id':purchase_invoice_id, 'order_type_id':type_id}
        if order_attachments_data:
            order_attachments = generic_data_creation(self, order_attachments_data, OrderAttachmentsSerializer, update_fields)
            logger.info('OrderAttchments - created*')
        else:
            # Since OrderAttchments Data is optional, so making it as an empty data list
            order_attachments = []

        # create OrderShipments Data
        if order_shipments_data:
            order_shipments = generic_data_creation(self, [order_shipments_data], OrderShipmentsSerializer, update_fields)
            order_shipments = order_shipments[0]
            logger.info('OrderShipments - created*')
        else:
            # Since OrderShipments Data is optional, so making it as an empty data list
            order_shipments = {}

        custom_data = {
            "purchase_invoice_orders":new_purchase_invoice_orders_data,
            "purchase_invoice_items":invoice_items_data,
            "order_attachments":order_attachments,
            "order_shipments":order_shipments,
        }

        # Update Product Stock
        update_product_stock(Products, ProductVariation, purchase_invoice_items_data, 'subtract')        

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

        # Validated PurchaseInvoiceOrders Data
        purchase_invoice_orders_data = given_data.pop('purchase_invoice_orders', None) # parent_data
        if purchase_invoice_orders_data:
            purchase_invoice_orders_data['purchase_invoice_id'] = pk
            invoice_order_error = validate_multiple_data(self, purchase_invoice_orders_data , PurchaseInvoiceOrdersSerializer,['invoice_no'])
            # validate the 'order_type' in 'purchase_invoice_orders' data
            validate_order_type(purchase_invoice_orders_data, invoice_order_error, OrderTypes,look_up='order_type')

        # Validated PurchaseInvoiceItem Data
        purchase_invoice_items_data = given_data.pop('purchase_invoice_items', None)
        if purchase_invoice_items_data:
            exclude_fields = ['purchase_invoice_id']
            invoice_item_error = validate_put_method_data(self, purchase_invoice_items_data, PurchaseInvoiceItemSerializer, exclude_fields, PurchaseInvoiceItem, current_model_pk_field='purchase_invoice_item_id')

        # Validated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        exclude_fields = ['order_id','order_type_id']
        if order_attachments_data:
            attachment_error = validate_put_method_data(self, order_attachments_data, OrderAttachmentsSerializer, exclude_fields, OrderAttachments, current_model_pk_field='attachment_id')
        else:
            attachment_error = [] # Since 'order_attachments' is optional, so making an error is empty list

        # Validated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_put_method_data(self, order_shipments_data, OrderShipmentsSerializer, exclude_fields, OrderShipments, current_model_pk_field='shipment_id')
        else:
            shipments_error = [] # Since 'order_shipments' is optional, so making an error is empty list

        # Ensure mandatory data is present
        if not purchase_invoice_orders_data or not purchase_invoice_items_data:
            logger.error("Purchase invoice order and Purchase invoice items are mandatory but not provided.")
            return build_response(0, "Purchase invoice order and Purchase invoice items are mandatory", [], status.HTTP_400_BAD_REQUEST)
        
        errors = {}
        if invoice_order_error:
            errors["purchase_invoice_orders"] = invoice_order_error
        if invoice_item_error:
            errors["purchase_invoice_items"] = invoice_item_error
        if attachment_error:
            errors['order_attachments'] = attachment_error
        if shipments_error:
            errors['order_shipments'] = shipments_error
        if errors:
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)        
      
        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#
        # update PurchaseInvoiceOrders
        if purchase_invoice_orders_data:
            update_fields = [] # No need to update any fields
            purchaseinvoiceorder_data = update_multi_instances(self, pk, purchase_invoice_orders_data, PurchaseInvoiceOrders, PurchaseInvoiceOrdersSerializer, update_fields,main_model_related_field='purchase_invoice_id', current_model_pk_field='purchase_invoice_id')
            purchaseinvoiceorder_data = purchaseinvoiceorder_data[0] if len(purchaseinvoiceorder_data)==1 else purchaseinvoiceorder_data

        # Update the 'PurchaseInvoiceItem'
        update_fields = {'purchase_invoice_id':pk}
        invoice_items_data = update_multi_instances(self, pk, purchase_invoice_items_data, PurchaseInvoiceItem, PurchaseInvoiceItemSerializer, update_fields, main_model_related_field='purchase_invoice_id', current_model_pk_field='purchase_invoice_item_id')

        # Get 'order_type_id' from 'OrderTypes' model
        order_type_val = purchase_invoice_orders_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Update the 'order_attchments'
        update_fields = {'order_id':pk, 'order_type_id':type_id}
        attachment_data = update_multi_instances(self, pk, order_attachments_data, OrderAttachments, OrderAttachmentsSerializer, update_fields, main_model_related_field='order_id', current_model_pk_field='attachment_id')

        # Update the 'shipments'
        shipment_data = update_multi_instances(self, pk, order_shipments_data, OrderShipments, OrderShipmentsSerializer, update_fields, main_model_related_field='order_id', current_model_pk_field='shipment_id')
        shipment_data = shipment_data[0] if len(shipment_data)==1 else shipment_data

        custom_data = {
            "purchase_invoice_orders":purchaseinvoiceorder_data,
            "purchase_invoice_items":invoice_items_data if invoice_items_data else [],
            "order_attachments":attachment_data if attachment_data else [],
            "order_shipments":shipment_data if shipment_data else {}
        }

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

#=====================PurchaseReturnOrders========================================================
class PurchaseReturnOrderViewSet(APIView):
    """
    API ViewSet for handling Purchase Return Order creation and related data.
    """
    def get_object(self, pk):
        try:
            return PurchaseReturnOrders.objects.get(pk=pk)
        except PurchaseReturnOrders.DoesNotExist:
            logger.warning(f"PurchaseReturnOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)   
      
    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:
           result =  validate_input_pk(self,kwargs['pk'])
           return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            summary = request.query_params.get("summary", "false").lower() == "true"+ "&"
            if summary:
                logger.info("Retrieving Purchase return orders summary")
                purchasereturnorders = PurchaseReturnOrders.objects.all().order_by('-created_at', '-updated_at')
                data = PurchaseReturnOrdersOptionsSerializer.get_purchase_return_orders_summary(purchasereturnorders)
                return build_response(len(data), "Success", data, status.HTTP_200_OK)
            
            instance = PurchaseReturnOrders.objects.all().order_by('-created_at', '-updated_at')
            
            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 
            total_count = PurchaseReturnOrders.objects.count()            
            
            # Apply filters manually
            if request.query_params:
                queryset = PurchaseReturnOrders.objects.all()
                filterset = PurchaseReturnOrdersFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs
                    serializer = PurchaseReturnOrdersOptionsSerializer(queryset, many=True)
                    # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
                    return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except PurchaseReturnOrders.DoesNotExist:
            logger.error("Purchase return order does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        else:
            serializer = PurchaseReturnOrdersSerializer(instance, many=True)
            logger.info("Purchase return order data retrieved successfully.")
            return build_response(instance.count(), "Success", serializer.data, status.HTTP_200_OK)  
        
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a Purchase Return Orders and its related data (ReturnItems, attachments, and shipments).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the PurchaseReturnOrders instance
            purchase_return_order = get_object_or_404(PurchaseReturnOrders, pk=pk)
            purchase_return_order_serializer = PurchaseReturnOrdersSerializer(purchase_return_order)

            # Retrieve related data
            return_items_data = self.get_related_data(PurchaseReturnItems, PurchaseReturnItemsSerializer, 'purchase_return_id', pk)
            attachments_data = self.get_related_data(OrderAttachments, OrderAttachmentsSerializer, 'order_id', pk)
            shipments_data = self.get_related_data(OrderShipments, OrderShipmentsSerializer, 'order_id', pk)
            shipments_data = shipments_data[0] if len(shipments_data)>0 else {}
                
            # Customizing the response data
            custom_data = {
                "purchase_return_orders": purchase_return_order_serializer.data,
                "purchase_return_items": return_items_data,
                "order_attachments": attachments_data,
                "order_shipments": shipments_data
            }
            logger.info("Purchase return Order and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)
        
        except Http404:
            logger.error("Purchase return order with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("An error occurred while retrieving purchase return order with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    def get_related_data(self, model, serializer_class, filter_field, filter_value):
        """
        Retrieves related data for a given model, serializer, and filter field.
        """
        try:
            related_data = model.objects.filter(**{filter_field: filter_value})
            serializer = serializer_class(related_data, many=True)
            logger.debug("Retrieved related data for model %s with filter %s=%s.", model.__name__, filter_field, filter_value)
            return serializer.data
        except Exception as e:
            logger.exception("Error retrieving related data for model %s with filter %s=%s: %s", model.__name__, filter_field, filter_value, str(e))
            return []
        
    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a Purchase Return Orders and its related attachments and shipments.
        """
        try:
            # Get the PurchaseReturnOrders instance
            instance = PurchaseReturnOrders.objects.get(pk=pk)

            # Delete related OrderAttachments and OrderShipments
            if not delete_multi_instance(pk, PurchaseReturnOrders, OrderAttachments, main_model_field_name='order_id'):
                return build_response(0, "Error deleting related order attachments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
            if not delete_multi_instance(pk, PurchaseReturnOrders, OrderShipments, main_model_field_name='order_id'):
                return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Delete the main PurchaseReturnOrders instance
            instance.delete()

            logger.info(f"PurchaseReturnOrders with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except PurchaseReturnOrders.DoesNotExist:
            logger.warning(f"PurchaseReturnOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting PurchaseReturnOrders with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Handling POST requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
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

        # Validated PurchaseReturnOrders Data
        purchase_return_orders_data = given_data.pop('purchase_return_orders', None) # parent_data
        if purchase_return_orders_data:
            return_order_error = validate_payload_data(self, purchase_return_orders_data , PurchaseReturnOrdersSerializer)
            # validate the order_type in 'PurchaseReturnOrders' data
            validate_order_type(purchase_return_orders_data, return_order_error, OrderTypes,look_up='order_type')
                
        # Validated PurchaseInvoiceItems Data
        purchase_return_items_data = given_data.pop('purchase_return_items', None)
        if purchase_return_items_data:
            return_item_error = validate_multiple_data(self, purchase_return_items_data,PurchaseReturnItemsSerializer,['purchase_return_id'])

        # Validated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        if order_attachments_data:
            attachment_error = validate_multiple_data(self, order_attachments_data ,OrderAttachmentsSerializer,['order_id','order_type_id'])
        else:
            attachment_error = [] # Since 'order_attachments' is optional, so making an error is empty list

        # Validated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_multiple_data(self, [order_shipments_data] , OrderShipmentsSerializer,['order_id','order_type_id'])
        else:
            shipments_error = [] # Since 'order_shipments' is optional, so making an error is empty list

        # Ensure mandatory data is present
        if not purchase_return_orders_data or not purchase_return_items_data:
            logger.error("Purchase return order and Purchase return items are mandatory but not provided.")
            return build_response(0, "Purchase return order and Purchase return items are mandatory", [], status.HTTP_400_BAD_REQUEST)
        
        errors = {}
        if return_order_error:
            errors["purchase_return_orders"] = return_order_error
        if return_item_error:
                errors["purchase_return_items"] = return_item_error
        if attachment_error:
                errors['order_attachments'] = attachment_error
        if shipments_error:
                errors['order_shipments'] = shipments_error
        if errors:
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)
        
        """
        Verifies if PREVIOUS PRODUCT INTANCE is available for the product.
        Raises a ValidationError if the product's instance is not present in database.
        """
        stock_error = previous_product_instance_verification(ProductVariation, purchase_return_items_data)
        if stock_error:
            return build_response(0, f"ValidationError :", stock_error, status.HTTP_400_BAD_REQUEST)        

        #---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """
            
        # Hence the data is validated , further it can be created.

        # Create PurchaseReturnOrders Data
        new_purchase_return_orders_data = generic_data_creation(self, [purchase_return_orders_data], PurchaseReturnOrdersSerializer)
        new_purchase_return_orders_data = new_purchase_return_orders_data[0]
        purchase_return_id = new_purchase_return_orders_data.get("purchase_return_id",None) #Fetch purchase_return_id from mew instance
        logger.info('PurchaseReturnOrders - created*')

        # Create PurchaseReturnItems Data
        update_fields = {'purchase_return_id': purchase_return_id}
        return_items_data = generic_data_creation(self, purchase_return_items_data, PurchaseReturnItemsSerializer, update_fields)
        logger.info('PurchaseReturnItems - created*')

        # Get order_type_id from OrderTypes model
        order_type_val = purchase_return_orders_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Create OrderAttchments Data
        update_fields = {'order_id':purchase_return_id, 'order_type_id':type_id}
        if order_attachments_data:
            order_attachments = generic_data_creation(self, order_attachments_data, OrderAttachmentsSerializer, update_fields)
            logger.info('OrderAttchments - created*')
        else:
            # Since OrderAttchments Data is optional, so making it as an empty data list
            order_attachments = []

        # create OrderShipments Data
        if order_shipments_data:
            order_shipments = generic_data_creation(self, [order_shipments_data], OrderShipmentsSerializer, update_fields)
            order_shipments = order_shipments[0]
            logger.info('OrderShipments - created*')
        else:
            # Since OrderShipments Data is optional, so making it as an empty data list
            order_shipments = {}

        custom_data = {
            "purchase_return_orders":new_purchase_return_orders_data,
            "purchase_return_items":return_items_data,
            "order_attachments":order_attachments,
            "order_shipments":order_shipments,
        }

        # Update the stock with returned products.
        update_product_stock(Products, ProductVariation, purchase_return_items_data, 'add')

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

        # Validated PurchaseReturnOrders Data
        purchase_return_orders_data = given_data.pop('purchase_return_orders', None) # parent_data
        if purchase_return_orders_data:
            purchase_return_orders_data['purchase_return_id'] = pk
            return_order_error = validate_multiple_data(self, purchase_return_orders_data , PurchaseReturnOrdersSerializer,['return_no'])
            # validate the 'order_type' in 'purchase_return_orders' data
            validate_order_type(purchase_return_orders_data, return_order_error, OrderTypes,look_up='order_type')

        # Validated PurchaseReturnItems Data
        purchase_return_items_data = given_data.pop('purchase_return_items', None)
        if purchase_return_items_data:
            exclude_fields = ['purchase_return_id']
            return_item_error = validate_put_method_data(self, purchase_return_items_data, PurchaseReturnItemsSerializer, exclude_fields, PurchaseReturnItems, current_model_pk_field='purchase_return_item_id')

        # Validated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        exclude_fields = ['order_id','order_type_id']
        if order_attachments_data:
            attachment_error = validate_put_method_data(self, order_attachments_data, OrderAttachmentsSerializer, exclude_fields, OrderAttachments, current_model_pk_field='attachment_id')
        else:
            attachment_error = [] # Since 'order_attachments' is optional, so making an error is empty list

        # Validated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_put_method_data(self, order_shipments_data, OrderShipmentsSerializer, exclude_fields, OrderShipments, current_model_pk_field='shipment_id')
        else:
            shipments_error = [] # Since 'order_shipments' is optional, so making an error is empty list

        # Ensure mandatory data is present
        if not purchase_return_orders_data or not purchase_return_items_data:
            logger.error("Purchase return order and Purchase return items are mandatory but not provided.")
            return build_response(0, "Purchase return order and Purchase return items are mandatory", [], status.HTTP_400_BAD_REQUEST)
        
        errors = {}
        if return_order_error:
            errors["purchase_return_orders"] = return_order_error
        if return_item_error:
            errors["purchase_return_items"] = return_item_error
        if attachment_error:
            errors['order_attachments'] = attachment_error
        if shipments_error:
            errors['order_shipments'] = shipments_error
        if errors:
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)        
      
        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#
        # update PurchaseReturnOrders
        if purchase_return_orders_data:
            update_fields = [] # No need to update any fields
            purchasereturnorder_data = update_multi_instances(self, pk, purchase_return_orders_data, PurchaseReturnOrders, PurchaseReturnOrdersSerializer, update_fields,main_model_related_field='purchase_return_id', current_model_pk_field='purchase_return_id')
            purchasereturnorder_data = purchasereturnorder_data[0] if len(purchasereturnorder_data)==1 else purchasereturnorder_data

        # Update the 'PurchaseReturnItems'
        update_fields = {'purchase_return_id':pk}
        return_items_data = update_multi_instances(self, pk, purchase_return_items_data, PurchaseReturnItems, PurchaseReturnItemsSerializer, update_fields, main_model_related_field='purchase_return_id', current_model_pk_field='purchase_return_item_id')

        # Get 'order_type_id' from 'OrderTypes' model
        order_type_val = purchase_return_orders_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Update the 'order_attchments'
        update_fields = {'order_id':pk, 'order_type_id':type_id}
        attachment_data = update_multi_instances(self, pk, order_attachments_data, OrderAttachments, OrderAttachmentsSerializer, update_fields, main_model_related_field='order_id', current_model_pk_field='attachment_id')

        # Update the 'shipments'
        shipment_data = update_multi_instances(self, pk, order_shipments_data, OrderShipments, OrderShipmentsSerializer, update_fields, main_model_related_field='order_id', current_model_pk_field='shipment_id')
        shipment_data = shipment_data[0] if len(shipment_data)==1 else shipment_data

        custom_data = {
            "purchase_return_orders":purchasereturnorder_data,
            "purchase_return_items":return_items_data if return_items_data else [],
            "order_attachments":attachment_data if attachment_data else [],
            "order_shipments":shipment_data if shipment_data else {}
        }

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)
    