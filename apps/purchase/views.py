import logging
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from .models import *
from .serializers import *
from config.utils_methods import *
from config.utils_variables import *
from config.utils_methods import validate_input_pk, delete_multi_instance, generic_data_creation, get_object_or_none, list_all_objects, create_instance, update_instance, build_response, update_multi_instance, validate_multiple_data, validate_payload_data
from uuid import UUID
from apps.sales.serializers import OrderAttachmentsSerializer,OrderShipmentsSerializer
from apps.sales.models import OrderAttachments,OrderShipments
from rest_framework import viewsets
from apps.masters.models import OrderTypes
from rest_framework.views import APIView
from django.db import transaction
from rest_framework.serializers import ValidationError

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)

# Create your views here.
class PurchaseOrdersViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrders.objects.all()
    serializer_class = PurchaseOrdersSerializer
 
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
            instance = PurchaseOrders.objects.all()
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

            # Customizing the response data
            custom_data = {
                "purchase_order": purchase_order_serializer.data,
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
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
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
        purchase_order_data = given_data.pop('purchase_order', None) # parent_data
        if purchase_order_data:
            order_error = validate_payload_data(self, purchase_order_data , PurchaseOrdersSerializer)

            # validate the order_type in 'purchase_order' data
            order_type = purchase_order_data.get('order_type',None) # 'order_type' is additonal Field and not defined in model
            if order_type is None and len(order_error) > 0:
                order_error[0]['order_type'] = ["Specify type of order"]
            elif order_type is None:
                order_error.append([{'order_type':"This field is required"}])
            else:
                order_type = get_object_or_none(OrderTypes, name=order_type)
                if order_type is None and len(order_error) > 0:
                    order_error[0]['order_type'] = ["Invalid order type"]
                elif order_type is None:
                    order_error.append([{'order_type':"Invalid order type"}])
                
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
            errors["purchase_order"] = order_error
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
        purchase_order_id = new_purchase_order_data[0].get("purchase_order_id",None) #Fetch purchase_order_id from mew instance
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
            logger.info('OrderShipments - created*')
        else:
            # Since OrderShipments Data is optional, so making it as an empty data list
            order_shipments = []

        custom_data = [
            {"purchase_order":new_purchase_order_data},
            {"purchase_order_items":items_data},
            {"order_attachments":order_attachments},
            {"order_shipments":order_shipments},
        ]

        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)

    def put(self, request, pk, *args, **kwargs):
        purchaseorder_data = items_data = attachments_data = shipments_data = response_data = None
        errors = []

        partial = kwargs.pop('partial', False)
        instance = self.get_object(pk)
        serializer = PurchaseOrdersSerializer(instance, data=request.data['purchase_order'], partial=partial)
        try:
            if serializer.is_valid(raise_exception=False):
                serializer.save()

        except Exception as e:
            logger.error("Validation error: %s", str(e))  # Log validation errors
            errors.append(str(e))  # Collect validation errors

        else:
            purchaseorder_data = serializer.data
            # Update purchase_order_items 
            purchase_order_items_data = request.data.pop('purchase_order_items')
            items_data, item_errors = update_multi_instance(pk, purchase_order_items_data, PurchaseorderItems, PurchaseorderItemsSerializer, filter_field_1='purchase_order_id')
            errors.extend(item_errors)
            # Update purchase_order_attachments
            order_attachments_data = request.data.pop('order_attachments')
            attachments_data, attachments_errors = update_multi_instance(pk, order_attachments_data, OrderAttachments, OrderAttachmentsSerializer, filter_field_1='order_id')
            errors.extend(attachments_errors)
            #  Update order_shipments
            order_shipments_data = request.data.pop('order_shipments')
            shipments_data, shipments_errors = update_multi_instance(pk, order_shipments_data, OrderShipments, OrderShipmentsSerializer, filter_field_1='order_id')
            errors.extend(shipments_errors)

            if errors:
                logger.warning("Record created with some errors: %s", errors)
                return build_response(1, "Record created with errors", response_data, status.HTTP_201_CREATED, errors)
            
        #  Here 'or' operator is used becaused data can be either empty list or filled with data. so that all the model data can be represented on output
        if purchaseorder_data or items_data or attachments_data or shipments_data:
            custom_data = {
                "purchase_order": purchaseorder_data,
                "purchase_order_items": items_data,
                "order_attachments":attachments_data,
                "order_shipments": shipments_data
            }
            response_data = build_response(1, "Record updated successfully", custom_data, status.HTTP_200_OK)
        else:
            logger.error("Error in PurchaseOrderViewSet")
            response_data = build_response(0, "Record updation failed", [serializer.errors], status.HTTP_400_BAD_REQUEST)
        
        return response_data