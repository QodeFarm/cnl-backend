import logging
from django.db import transaction
from django.forms import ValidationError
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.serializers import ValidationError
from uuid import UUID
from rest_framework.views import APIView
from config.utils_filter_methods import filter_response
from .filters import *
from apps.purchase.models import PurchaseOrders
from apps.purchase.serializers import PurchaseOrdersSerializer
from apps.products.models import Products, ProductVariation
from .serializers import *
from apps.masters.models import OrderTypes
from config.utils_methods import previous_product_instance_verification, product_stock_verification, update_multi_instances, update_product_stock, validate_input_pk, delete_multi_instance, generic_data_creation, get_object_or_none, list_all_objects, create_instance, update_instance, build_response, validate_multiple_data, validate_order_type, validate_payload_data, validate_put_method_data
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import OrderingFilter
from django.apps import apps


from datetime import datetime
from config.utils_methods import workflow_progression_dict 
workflow_progression_dict = {}
# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)


class SaleOrderView(viewsets.ModelViewSet):
    queryset = SaleOrder.objects.all()
    serializer_class = SaleOrderSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = SaleOrderFilter
    ordering_fields = ['num_employees', 'created_at', 'updated_at', 'name']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class PaymentTransactionsView(viewsets.ModelViewSet):
    queryset = PaymentTransactions.objects.all()
    serializer_class = PaymentTransactionsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class SaleInvoiceItemsView(viewsets.ModelViewSet):
    queryset = SaleInvoiceItems.objects.all()
    serializer_class = SaleInvoiceItemsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class SalesPriceListView(viewsets.ModelViewSet):
    queryset = SalesPriceList.objects.all()
    serializer_class = SalesPriceListSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class SaleOrderItemsView(viewsets.ModelViewSet):
    queryset = SaleOrderItems.objects.all()
    serializer_class = SaleOrderItemsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = SaleOrdersItemsilter

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class SaleInvoiceOrdersView(viewsets.ModelViewSet):
    queryset = SaleInvoiceOrders.objects.all()
    serializer_class = SaleInvoiceOrdersSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = SaleInvoiceOrdersFilter
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class SaleReturnOrdersView(viewsets.ModelViewSet):
    queryset = SaleReturnOrders.objects.all()
    serializer_class = SaleReturnOrdersSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = SaleReturnOrdersFilter
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class SaleReturnItemsView(viewsets.ModelViewSet):
    queryset = SaleReturnItems.objects.all()
    serializer_class = SaleReturnItemsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class OrderAttachmentsView(viewsets.ModelViewSet):
    queryset = OrderAttachments.objects.all()
    serializer_class = OrderAttachmentsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class OrderShipmentsView(viewsets.ModelViewSet):
    queryset = OrderShipments.objects.all()
    serializer_class = OrderShipmentsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class QuickPacksView(viewsets.ModelViewSet):
    queryset = QuickPacks.objects.all()
    serializer_class = QuickPackSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = QuickPacksFilter
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class QuickPacksItemsView(viewsets.ModelViewSet):
    queryset = QuickPackItems.objects.all()
    serializer_class = QuickPackItemSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class SaleCreditNoteViews(viewsets.ModelViewSet):
    queryset = SaleCreditNotes.objects.all()
    serializer_class = SaleCreditNoteSerializers

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        response = create_instance(self, request, *args, **kwargs)
        return response

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class SaleCreditNoteItemsViews(viewsets.ModelViewSet):
    queryset = SaleCreditNoteItems.objects.all()
    serializer_class = SaleCreditNoteItemsSerializers

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class SaleDebitNoteViews(viewsets.ModelViewSet):
    queryset = SaleDebitNotes.objects.all()
    serializer_class = SaleDebitNoteSerializers

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        response = create_instance(self, request, *args, **kwargs)
        return response

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class SaleDebitNoteItemsViews(viewsets.ModelViewSet):
    queryset = SaleDebitNoteItems.objects.all()
    serializer_class = SaleDebitNoteItemsSerializers

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        response = create_instance(self, request, *args, **kwargs)
        return response

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class SaleOrderViewSet(APIView):
    """
    API ViewSet for handling sale order creation and related data.
    """

    def get_object(self, pk):
        try:
            return SaleOrder.objects.get(pk=pk)
        except SaleOrder.DoesNotExist:
            logger.warning(f"SaleOrder with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            result = validate_input_pk(self, kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            summary = request.query_params.get("summary", "false").lower() == "true" + "&"
            if summary:
                logger.info("Retrieving Sale order summary")
                saleorders = SaleOrder.objects.all()
                data = SaleOrderOptionsSerializer.get_sale_order_summary(saleorders)
                return Response(data, status=status.HTTP_200_OK)

            logger.info("Retrieving all sale order")

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 

            queryset = SaleOrder.objects.all()

            # Apply filters manually
            if request.query_params:
                filterset = SaleOrderFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs   

            total_count = SaleOrder.objects.count()
        
            serializer = SaleOrderOptionsSerializer(queryset, many=True)
            logger.info("sale order data retrieved successfully.")
            # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
            return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a sale order and its related data (items, attachments, and shipments).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the SaleOrder instance
            sale_order = get_object_or_404(SaleOrder, pk=pk)
            sale_order_serializer = SaleOrderSerializer(sale_order)

            # Retrieve related data
            items_data = self.get_related_data(
                SaleOrderItems, SaleOrderItemsSerializer, 'sale_order_id', pk)
            attachments_data = self.get_related_data(
                OrderAttachments, OrderAttachmentsSerializer, 'order_id', pk)
            shipments_data = self.get_related_data(
                OrderShipments, OrderShipmentsSerializer, 'order_id', pk)
            shipments_data = shipments_data[0] if len(shipments_data)>0 else {}

            # Customizing the response data
            custom_data = {
                "sale_order": sale_order_serializer.data,
                "sale_order_items": items_data,
                "order_attachments": attachments_data,
                "order_shipments": shipments_data
            }
            logger.info("Sale order and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error("Sale order with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(
                "An error occurred while retrieving sale order with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_related_data(self, model, serializer_class, filter_field, filter_value):
        """
        Retrieves related data for a given model, serializer, and filter field.
        """
        try:
            related_data = model.objects.filter(**{filter_field: filter_value})
            serializer = serializer_class(related_data, many=True)
            logger.debug("Retrieved related data for model %s with filter %s=%s.",
                         model.__name__, filter_field, filter_value)
            return serializer.data
        except Exception as e:
            logger.exception("Error retrieving related data for model %s with filter %s=%s: %s",
                             model.__name__, filter_field, filter_value, str(e))
            return []

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a sale order and its related attachments and shipments.
        """
        try:
            # Get the SaleOrder instance
            instance = SaleOrder.objects.get(pk=pk)

            # Delete related OrderAttachments and OrderShipments
            if not delete_multi_instance(pk, SaleOrder, OrderAttachments, main_model_field_name='order_id'):
                return build_response(0, "Error deleting related order attachments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
            if not delete_multi_instance(pk, SaleOrder, OrderShipments, main_model_field_name='order_id'):
                return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Delete the main SaleOrder instance
            instance.delete()

            logger.info(f"SaleOrder with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except SaleOrder.DoesNotExist:
            logger.warning(f"SaleOrder with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting SaleOrder with ID {pk}: {str(e)}")
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

        # Vlidated SaleOrder Data
        sale_order_data = given_data.pop('sale_order', None)  # parent_data
        if sale_order_data:
            order_error = validate_payload_data(
                self, sale_order_data, SaleOrderSerializer)
            # validate the order_type in 'sale_order' data
            validate_order_type(sale_order_data, order_error,
                                OrderTypes, look_up='order_type')

        # Vlidated SaleOrderItems Data
        sale_order_items_data = given_data.pop('sale_order_items', None)
        if sale_order_items_data:
            item_error = validate_multiple_data(
                self, sale_order_items_data, SaleOrderItemsSerializer, ['sale_order_id'])

        # Vlidated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        if order_attachments_data:
            attachment_error = validate_multiple_data(
                self, order_attachments_data, OrderAttachmentsSerializer, ['order_id', 'order_type_id'])
        else:
            # Since 'order_attachments' is optional, so making an error is empty list
            attachment_error = []

        # Vlidated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if len(order_shipments_data) > 1 :  #handling validation error for shipments
            shipments_error = validate_multiple_data(
                self, [order_shipments_data], OrderShipmentsSerializer, ['order_id', 'order_type_id'])
        else:
            # Since 'order_shipments' is optional, so making an error is empty list
            shipments_error = []
            order_shipments_data = {} #handling validation error for shipments

        # Ensure mandatory data is present
        if not sale_order_data or not sale_order_items_data:
            logger.error(
                "Sale order and sale order items are mandatory but not provided.")
            return build_response(0, "Sale order and sale order items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if order_error:
            errors["sale_order"] = order_error
        if item_error:
            errors["sale_order_items"] = item_error
        if attachment_error:
            errors['order_attachments'] = attachment_error
        if shipments_error:
            errors['order_shipments'] = shipments_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """

        # Hence the data is validated , further it can be created.

        # Create SaleOrder Data
        new_sale_order_data = generic_data_creation(self, [sale_order_data], SaleOrderSerializer)
        new_sale_order_data = new_sale_order_data[0]
        sale_order_id = new_sale_order_data.get("sale_order_id", None)  # Fetch sale_order_id from mew instance
        logger.info('SaleOrder - created*')

        # Create SaleOrderItems Data
        update_fields = {'sale_order_id': sale_order_id}
        items_data = generic_data_creation(
            self, sale_order_items_data, SaleOrderItemsSerializer, update_fields)
        logger.info('SaleOrderItems - created*')

        # Get order_type_id from OrderTypes model
        order_type_val = sale_order_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Create OrderAttchments Data
        update_fields = {'order_id': sale_order_id, 'order_type_id': type_id}
        if order_attachments_data:
            order_attachments = generic_data_creation(
                self, order_attachments_data, OrderAttachmentsSerializer, update_fields)
            logger.info('OrderAttchments - created*')
        else:
            # Since OrderAttchments Data is optional, so making it as an empty data list
            order_attachments = []

        # create OrderShipments Data
        if order_shipments_data:
            order_shipments = generic_data_creation(
                self, [order_shipments_data], OrderShipmentsSerializer, update_fields)
            order_shipments = order_shipments[0]
            logger.info('OrderShipments - created*')
        else:
            # Since OrderShipments Data is optional, so making it as an empty data list
            order_shipments = {}

        custom_data = {
            "sale_order": new_sale_order_data,
            "sale_order_items": items_data,
            "order_attachments": order_attachments,
            "order_shipments": order_shipments,
        }

        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):

        # ----------------------------------- D A T A  V A L I D A T I O N -----------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        # Get the given data from request
        given_data = request.data

        # Vlidated SaleOrder Data
        sale_order_data = given_data.pop('sale_order', None)  # parent_data
        if sale_order_data:
            sale_order_data['sale_order_id'] = pk
            order_error = validate_multiple_data(
                self, [sale_order_data], SaleOrderSerializer, ['order_no'])
            # validate the 'order_type' in 'sale_order' data
            validate_order_type(sale_order_data, order_error,OrderTypes, look_up='order_type')

        # Vlidated SaleOrderItems Data
        sale_order_items_data = given_data.pop('sale_order_items', None)
        if sale_order_items_data:
            exclude_fields = ['sale_order_id']
            item_error = validate_put_method_data(self, sale_order_items_data, SaleOrderItemsSerializer,
                                                  exclude_fields, SaleOrderItems, current_model_pk_field='sale_order_item_id')

        # Vlidated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        exclude_fields = ['order_id', 'order_type_id']
        if order_attachments_data:
            attachment_error = validate_put_method_data(
                self, order_attachments_data, OrderAttachmentsSerializer, exclude_fields, OrderAttachments, current_model_pk_field='attachment_id')
        else:
            # Since 'order_attachments' is optional, so making an error is empty list
            attachment_error = []

        # Vlidated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_put_method_data(
                self, order_shipments_data, OrderShipmentsSerializer, exclude_fields, OrderShipments, current_model_pk_field='shipment_id')
        else:
            # Since 'order_shipments' is optional, so making an error is empty list
            shipments_error = []

        # Ensure mandatory data is present
        if not sale_order_data or not sale_order_items_data:
            logger.error(
                "Sale order and sale order items are mandatory but not provided.")
            return build_response(0, "Sale order and sale order items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if order_error:
            errors["sale_order"] = order_error
        if item_error:
            errors["sale_order_items"] = item_error
        if attachment_error:
            errors['order_attachments'] = attachment_error
        if shipments_error:
            errors['order_shipments'] = shipments_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#

        # update SaleOrder
        if sale_order_data:
            update_fields = []  # No need to update any fields
            saleorder_data = update_multi_instances(self, pk, [sale_order_data], SaleOrder, SaleOrderSerializer,
                                                    update_fields, main_model_related_field='sale_order_id', current_model_pk_field='sale_order_id')

        # Update the 'sale_order_items'
        update_fields = {'sale_order_id': pk}
        items_data = update_multi_instances(self, pk, sale_order_items_data, SaleOrderItems, SaleOrderItemsSerializer,
                                            update_fields, main_model_related_field='sale_order_id', current_model_pk_field='sale_order_item_id')

        # Get 'order_type_id' from 'OrderTypes' model
        order_type_val = sale_order_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Update the 'order_attchments'
        update_fields = {'order_id': pk, 'order_type_id': type_id}
        attachment_data = update_multi_instances(self, pk, order_attachments_data, OrderAttachments, OrderAttachmentsSerializer,
                                                 update_fields, main_model_related_field='order_id', current_model_pk_field='attachment_id')

        # Update the 'shipments'
        shipment_data = update_multi_instances(self, pk, order_shipments_data, OrderShipments, OrderShipmentsSerializer,
                                               update_fields, main_model_related_field='order_id', current_model_pk_field='shipment_id')

        custom_data = {
            "sale_order": saleorder_data[0] if saleorder_data else {},
            "sale_order_items": items_data if items_data else [],
            "order_attachments": attachment_data if attachment_data else [],
            "order_shipments": shipment_data[0] if shipment_data else {}
        }

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

class SaleInvoiceOrdersViewSet(APIView):
    """
    API ViewSet for handling sale invoice order creation and related data.
    """

    def get_object(self, pk):
        try:
            return SaleInvoiceOrders.objects.get(pk=pk)
        except SaleInvoiceOrders.DoesNotExist:
            logger.warning(f"SaleInvoiceOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            result =  validate_input_pk(self,kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs) 
        try:
            summary = request.query_params.get("summary", "false").lower() == "true" + "&"
            if summary:
                logger.info("Retrieving sale invoice order summary")
                saleinvoiceorder = SaleInvoiceOrders.objects.all()
                data = SaleInvoiceOrderOptionsSerializer.get_sale_invoice_order_summary(saleinvoiceorder)
                return build_response(len(data), "Success", data, status.HTTP_200_OK)
             
            logger.info("Retrieving all sale invoice orders")

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 

            queryset = SaleInvoiceOrders.objects.all()

            # Apply filters manually
            if request.query_params:
                filterset = SaleInvoiceOrdersFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs 

            total_count = SaleInvoiceOrders.objects.count()

            serializer = SaleInvoiceOrderOptionsSerializer(queryset, many=True)
            logger.info("sale order invoice data retrieved successfully.")
            # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
            return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a sale invoice order and its related data (items, attachments, and shipments).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the SaleInvoiceOrders instance
            sale_invoice_order = get_object_or_404(SaleInvoiceOrders, pk=pk)
            sale_invoice_order_serializer = SaleInvoiceOrdersSerializer(sale_invoice_order)

            # Retrieve related data
            items_data = self.get_related_data(SaleInvoiceItems, SaleInvoiceItemsSerializer, 'sale_invoice_id', pk)
            attachments_data = self.get_related_data(OrderAttachments, OrderAttachmentsSerializer, 'order_id', pk)
            shipments_data = self.get_related_data(OrderShipments, OrderShipmentsSerializer, 'order_id', pk)
            shipments_data = shipments_data[0] if len(shipments_data)>0 else {}

            # Customizing the response data
            custom_data = {
                "sale_invoice_order": sale_invoice_order_serializer.data,
                "sale_invoice_items": items_data,
                "order_attachments": attachments_data,
                "order_shipments": shipments_data
            }
            logger.info("Sale invoice order and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error("Sale invoice order with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(
                "An error occurred while retrieving sale invoice order with pk %s: %s", pk, str(e))
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
        Handles the deletion of a sale invoice order and its related attachments and shipments.
        """
        try:
            # Get the SaleInvoiceOrders instance
            instance = SaleInvoiceOrders.objects.get(pk=pk)

            # Delete related OrderAttachments and OrderShipments
            if not delete_multi_instance(pk, SaleInvoiceOrders, OrderAttachments, main_model_field_name='order_id'):
                return build_response(0, "Error deleting related order attachments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
            if not delete_multi_instance(pk, SaleInvoiceOrders, OrderShipments, main_model_field_name='order_id'):
                return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Delete the main SaleInvoiceOrders instance
            instance.delete()

            logger.info(f"SaleInvoiceOrders with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except SaleInvoiceOrders.DoesNotExist:
            logger.warning(f"SaleInvoiceOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting SaleInvoiceOrders with ID {pk}: {str(e)}")
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

        # Validate SaleInvoiceOrders Data
        sale_invoice_order_data = given_data.pop('sale_invoice_order', None)  # parent_data
        if sale_invoice_order_data:
            order_error = validate_payload_data(self, sale_invoice_order_data, SaleInvoiceOrdersSerializer)
            # validate the order_type in 'sale_invoice_order_data' data
            validate_order_type(sale_invoice_order_data, order_error, OrderTypes, look_up='order_type')

        # Validate SaleInvoiceItems Data
        sale_invoice_items_data = given_data.pop('sale_invoice_items', None)
        if sale_invoice_items_data:
            item_error = validate_multiple_data(self, sale_invoice_items_data, SaleInvoiceItemsSerializer, ['sale_invoice_id'])

        # Validate OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        if order_attachments_data:
            attachment_error = validate_multiple_data(self, order_attachments_data, OrderAttachmentsSerializer, ['order_id', 'order_type_id'])
        else:
            # Since 'order_attachments' is optional, so making an error is empty list
            attachment_error = []

        # Validate OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_multiple_data(self, [order_shipments_data], OrderShipmentsSerializer, ['order_id', 'order_type_id'])
        else:
            # Since 'order_shipments' is optional, so making an error is empty list
            shipments_error = []

        # Ensure mandatory data is present
        if not sale_invoice_order_data or not sale_invoice_items_data:
            logger.error(
                "Sale invoice order and sale invoice items are mandatory but not provided.")
            return build_response(0, "Sale invoice order and sale invoice items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if order_error:
            errors["sale_invoice_order"] = order_error
        if item_error:
            errors["sale_invoice_items"] = item_error
        if attachment_error:
            errors['order_attachments'] = attachment_error
        if shipments_error:
            errors['order_shipments'] = shipments_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # Stock verification
        stock_error = product_stock_verification(Products, ProductVariation, sale_invoice_items_data)
        if stock_error:
            return build_response(0, f"ValidationError :", stock_error, status.HTTP_400_BAD_REQUEST)          

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """

        # Hence the data is validated , further it can be created.

        # Create SaleInvoiceOrders Data
        new_sale_invoice_order_data = generic_data_creation(self, [sale_invoice_order_data], SaleInvoiceOrdersSerializer)
        new_sale_invoice_order_data = new_sale_invoice_order_data[0]
        sale_invoice_id = new_sale_invoice_order_data.get("sale_invoice_id", None)  # Fetch sale_invoice_id from mew instance
        logger.info('SaleInvoiceOrders - created*')

        # Create SaleInvoiceItems Data
        update_fields = {'sale_invoice_id': sale_invoice_id}
        items_data = generic_data_creation(self, sale_invoice_items_data, SaleInvoiceItemsSerializer, update_fields)
        logger.info('SaleInvoiceItems - created*')

        # Get order_type_id from OrderTypes model
        order_type_val = sale_invoice_order_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Create OrderAttchments Data
        update_fields = {'order_id': sale_invoice_id, 'order_type_id': type_id}
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
            "sale_invoice_order": new_sale_invoice_order_data,
            "sale_invoice_items": items_data,
            "order_attachments": order_attachments,
            "order_shipments": order_shipments,
        }

        # Update Product Stock
        update_product_stock(Products, ProductVariation, sale_invoice_items_data, 'subtract')

        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):

        # ----------------------------------- D A T A  V A L I D A T I O N -----------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        # Get the given data from request
        given_data = request.data

        # Validated SaleInvoiceOrders Data
        sale_invoice_order_data = given_data.pop('sale_invoice_order', None)  # parent_data
        if sale_invoice_order_data:
            sale_invoice_order_data['sale_invoice_id'] = pk
            order_error = validate_multiple_data(self, sale_invoice_order_data, SaleInvoiceOrdersSerializer, ['invoice_no'])
            # validate the 'order_type' in 'sale_order' data
            validate_order_type(sale_invoice_order_data, order_error, OrderTypes, look_up='order_type')

        # Vlidated SaleInvoiceItems Data
        sale_invoice_items_data = given_data.pop('sale_invoice_items', None)
        if sale_invoice_items_data:
            exclude_fields = ['sale_invoice_id']
            item_error = validate_put_method_data(self, sale_invoice_items_data, SaleInvoiceItemsSerializer, exclude_fields, SaleInvoiceItems, current_model_pk_field='sale_invoice_item_id')

        # Vlidated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        exclude_fields = ['order_id', 'order_type_id']
        if order_attachments_data:
            attachment_error = validate_put_method_data(self, order_attachments_data, OrderAttachmentsSerializer, exclude_fields, OrderAttachments, current_model_pk_field='attachment_id')
        else:
            # Since 'order_attachments' is optional, so making an error is empty list
            attachment_error = []

        # Vlidated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_put_method_data(self, order_shipments_data, OrderShipmentsSerializer, exclude_fields, OrderShipments, current_model_pk_field='shipment_id')
        else:
            # Since 'order_shipments' is optional, so making an error is empty list
            shipments_error = []

        # Ensure mandatory data is present
        if not sale_invoice_order_data or not sale_invoice_items_data:
            logger.error("Sale invoice order and sale invoice items are mandatory but not provided.")
            return build_response(0, "Sale order and sale order items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if order_error:
            errors["sale_invoice_order"] = order_error
        if item_error:
            errors["sale_invoice_items"] = item_error
        if attachment_error:
            errors['order_attachments'] = attachment_error
        if shipments_error:
            errors['order_shipments'] = shipments_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#

        # update SaleInvoiceOrders
        if sale_invoice_order_data:
            update_fields = []  # No need to update any fields
            saleinvoice_order_data = update_multi_instances(self, pk, sale_invoice_order_data, SaleInvoiceOrders, SaleInvoiceOrdersSerializer, update_fields, main_model_related_field='sale_invoice_id', current_model_pk_field='sale_invoice_id')
            saleinvoice_order_data = saleinvoice_order_data[0] if len(saleinvoice_order_data)==1 else saleinvoice_order_data

        # Update the 'sale_order_items'
        update_fields = {'sale_invoice_id': pk}
        invoice_items_data = update_multi_instances(self, pk, sale_invoice_items_data, SaleInvoiceItems, SaleInvoiceItemsSerializer, update_fields, main_model_related_field='sale_invoice_id', current_model_pk_field='sale_invoice_item_id')

        # Get 'order_type_id' from 'OrderTypes' model
        order_type_val = sale_invoice_order_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Update the 'order_attchments'
        update_fields = {'order_id': pk, 'order_type_id': type_id}
        attachment_data = update_multi_instances(self, pk, order_attachments_data, OrderAttachments, OrderAttachmentsSerializer, update_fields, main_model_related_field='order_id', current_model_pk_field='attachment_id')

        # Update the 'shipments'
        shipment_data = update_multi_instances(self, pk, order_shipments_data, OrderShipments, OrderShipmentsSerializer, update_fields, main_model_related_field='order_id', current_model_pk_field='shipment_id')
        shipment_data = shipment_data[0] if len(shipment_data)==1 else shipment_data
        

        custom_data = {
            "sale_invoice_order": saleinvoice_order_data,
            "sale_invoice_items": invoice_items_data if invoice_items_data else [],
            "order_attachments": attachment_data if attachment_data else [],
            "order_shipments": shipment_data if shipment_data else {}
        }

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

class SaleReturnOrdersViewSet(APIView):
    def get_object(self, pk):
        try:
            return SaleReturnOrders.objects.get(pk=pk)
        except SaleReturnOrders.DoesNotExist:
            logger.warning(f"SaleReturnOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            result =  validate_input_pk(self,kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs) 
        try:
            summary = request.query_params.get("summary", "false").lower() == "true" + "&"
            if summary:
                logger.info("Retrieving sale return orders summary")
                salereturnorders = SaleReturnOrders.objects.all()
                data = SaleReturnOrdersOptionsSerializer.get_sale_return_orders_summary(salereturnorders)
                return build_response(len(data), "Success", data, status.HTTP_200_OK)
             
            logger.info("Retrieving all sale return order")

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 
            
            queryset = SaleReturnOrders.objects.all()

            # Apply filters manually
            if request.query_params:
                filterset = SaleReturnOrdersFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs 

            total_count = SaleReturnOrders.objects.count()

            serializer = SaleReturnOrdersOptionsSerializer(queryset, many=True)
            logger.info("sale return order data retrieved successfully.")
            # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
            return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a sale return order and its related data (items, attachments, and shipments).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the SaleReturnOrders instance
            sale_return_order = get_object_or_404(SaleReturnOrders, pk=pk)
            sale_return_order_serializer = SaleReturnOrdersSerializer(sale_return_order)

            # Retrieve related data
            items_data = self.get_related_data(
                SaleReturnItems, SaleReturnItemsSerializer, 'sale_return_id', pk)
            attachments_data = self.get_related_data(
                OrderAttachments, OrderAttachmentsSerializer, 'order_id', pk)
            shipments_data = self.get_related_data(
                OrderShipments, OrderShipmentsSerializer, 'order_id', pk)
            shipments_data = shipments_data[0] if len(shipments_data)>0 else {}

            # Customizing the response data
            custom_data = {
                "sale_return_order": sale_return_order_serializer.data,
                "sale_return_items": items_data,
                "order_attachments": attachments_data,
                "order_shipments": shipments_data
            }
            logger.info("Sale return order and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error("Sale return order with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(
                "An error occurred while retrieving sale return order with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_related_data(self, model, serializer_class, filter_field, filter_value):
        """
        Retrieves related data for a given model, serializer, and filter field.
        """
        try:
            related_data = model.objects.filter(**{filter_field: filter_value})
            serializer = serializer_class(related_data, many=True)
            logger.debug("Retrieved related data for model %s with filter %s=%s.",
                         model.__name__, filter_field, filter_value)
            return serializer.data
        except Exception as e:
            logger.exception("Error retrieving related data for model %s with filter %s=%s: %s",
                             model.__name__, filter_field, filter_value, str(e))
            return []

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a sale return order and its related attachments and shipments.
        """
        try:
            # Get the SaleReturnOrders instance
            instance = SaleReturnOrders.objects.get(pk=pk)

            # Delete related OrderAttachments and OrderShipments
            if not delete_multi_instance(pk, SaleOrder, OrderAttachments, main_model_field_name='order_id'):
                return build_response(0, "Error deleting related order attachments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
            if not delete_multi_instance(pk, SaleOrder, OrderShipments, main_model_field_name='order_id'):
                return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Delete the main SaleOrder instance
            instance.delete()

            logger.info(f"SaleReturnOrders with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except SaleReturnOrders.DoesNotExist:
            logger.warning(f"SaleReturnOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting SaleReturnOrder with ID {pk}: {str(e)}")
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

        # Vlidated SaleReturnOrders Data
        sale_return_order_data = given_data.pop('sale_return_order', None)  # parent_data
        if sale_return_order_data:
            order_error = validate_payload_data(
                self, sale_return_order_data, SaleReturnOrdersSerializer)
            # validate the order_type in 'sale_return_order' data
            validate_order_type(sale_return_order_data, order_error,
                                OrderTypes, look_up='order_type')

        # Vlidated SaleReturnItems Data
        sale_return_items_data = given_data.pop('sale_return_items', None)
        if sale_return_items_data:
            item_error = validate_multiple_data(
                self, sale_return_items_data, SaleReturnItemsSerializer, ['sale_return_id'])

        # Vlidated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        if order_attachments_data:
            attachment_error = validate_multiple_data(
                self, order_attachments_data, OrderAttachmentsSerializer, ['order_id', 'order_type_id'])
        else:
            # Since 'order_attachments' is optional, so making an error is empty list
            attachment_error = []

        # Vlidated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_multiple_data(
                self, [order_shipments_data], OrderShipmentsSerializer, ['order_id', 'order_type_id'])
        else:
            # Since 'order_shipments' is optional, so making an error is empty list
            shipments_error = []

        # Ensure mandatory data is present
        if not sale_return_order_data or not sale_return_items_data:
            logger.error(
                "Sale return order and sale return items are mandatory but not provided.")
            return build_response(0, "Sale order and sale order items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if order_error:
            errors["sale_return_order"] = order_error
        if item_error:
            errors["sale_return_items"] = item_error
        if attachment_error:
            errors['order_attachments'] = attachment_error
        if shipments_error:
            errors['order_shipments'] = shipments_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        """
        Verifies if PREVIOUS PRODUCT INTANCE is available for the product.
        Raises a ValidationError if the product's instance is not present in database.
        """
        stock_error = previous_product_instance_verification(ProductVariation, sale_return_items_data)
        if stock_error:
            return build_response(0, f"ValidationError :", stock_error, status.HTTP_400_BAD_REQUEST)

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """

        # Hence the data is validated , further it can be created.

        # Create SaleReturnOrders Data
        new_sale_return_order_data = generic_data_creation(self, [sale_return_order_data], SaleReturnOrdersSerializer)
        new_sale_return_order_data = new_sale_return_order_data[0]
        sale_return_id = new_sale_return_order_data.get("sale_return_id", None)  # Fetch sale_return_id from mew instance
        logger.info('SaleReturnOrders - created*')

        # Create SaleReturnItems Data
        update_fields = {'sale_return_id': sale_return_id}
        items_data = generic_data_creation(
            self, sale_return_items_data, SaleReturnItemsSerializer, update_fields)
        logger.info('SaleReturnItems - created*')

        # Get order_type_id from OrderTypes model
        order_type_val = sale_return_order_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Create OrderAttchments Data
        update_fields = {'order_id': sale_return_id, 'order_type_id': type_id}
        if order_attachments_data:
            order_attachments = generic_data_creation(
                self, order_attachments_data, OrderAttachmentsSerializer, update_fields)
            logger.info('OrderAttchments - created*')
        else:
            # Since OrderAttchments Data is optional, so making it as an empty data list
            order_attachments = []

        # create OrderShipments Data
        if order_shipments_data:
            order_shipments = generic_data_creation(
                self, [order_shipments_data], OrderShipmentsSerializer, update_fields)
            order_shipments = order_shipments[0]
            logger.info('OrderShipments - created*')
        else:
            # Since OrderShipments Data is optional, so making it as an empty data list
            order_shipments = {}

        custom_data = {
            "sale_return_order": new_sale_return_order_data,
            "sale_return_items": items_data,
            "order_attachments": order_attachments,
            "order_shipments": order_shipments,
        }

        # Update the stock with returned products.
        update_product_stock(Products, ProductVariation, sale_return_items_data, 'add')

        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):

        # ----------------------------------- D A T A  V A L I D A T I O N -----------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        # Get the given data from request
        given_data = request.data

        # Vlidated SaleReturnOrders Data
        sale_return_order_data = given_data.pop('sale_return_order', None)  # parent_data
        if sale_return_order_data:
            sale_return_order_data['sale_return_id'] = pk
            order_error = validate_multiple_data(self, [sale_return_order_data], SaleReturnOrdersSerializer, ['return_no'])
            # validate the 'order_type' in 'sale_return_order' data
            validate_order_type(sale_return_order_data, order_error,OrderTypes, look_up='order_type')

        # Vlidated SaleReturnItems Data
        sale_return_items_data = given_data.pop('sale_return_items', None)
        if sale_return_items_data:
            exclude_fields = ['sale_return_id']
            item_error = validate_put_method_data(self, sale_return_items_data, SaleReturnItemsSerializer,
                                                  exclude_fields, SaleReturnItems, current_model_pk_field='sale_order_item_id')

        # Vlidated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        exclude_fields = ['order_id', 'order_type_id']
        if order_attachments_data:
            attachment_error = validate_put_method_data(
                self, order_attachments_data, OrderAttachmentsSerializer, exclude_fields, OrderAttachments, current_model_pk_field='attachment_id')
        else:
            # Since 'order_attachments' is optional, so making an error is empty list
            attachment_error = []

        # Vlidated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_put_method_data(
                self, order_shipments_data, OrderShipmentsSerializer, exclude_fields, OrderShipments, current_model_pk_field='shipment_id')
        else:
            # Since 'order_shipments' is optional, so making an error is empty list
            shipments_error = []

        # Ensure mandatory data is present
        if not sale_return_order_data or not sale_return_items_data:
            logger.error(
                "Sale return order and sale return items are mandatory but not provided.")
            return build_response(0, "Sale order and sale order items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if order_error:
            errors["sale_return_order"] = order_error
        if item_error:
            errors["sale_return_items"] = item_error
        if attachment_error:
            errors['order_attachments'] = attachment_error
        if shipments_error:
            errors['order_shipments'] = shipments_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#

        # update SaleReturnOrders
        if sale_return_order_data:
            update_fields = []  # No need to update any fields
            return_order_data = update_multi_instances(self, pk, sale_return_order_data, SaleReturnOrders, SaleReturnOrdersSerializer,update_fields, main_model_related_field='sale_return_id', current_model_pk_field='sale_return_id')
            return_order_data = return_order_data[0] if len(return_order_data)==1 else return_order_data

        # Update the 'sale_return_items'
        update_fields = {'sale_return_id': pk}
        items_data = update_multi_instances(self, pk, sale_return_items_data, SaleReturnItems, SaleReturnItemsSerializer,
                                            update_fields, main_model_related_field='sale_return_id', current_model_pk_field='sale_return_item_id')

        # Get 'order_type_id' from 'OrderTypes' model

        order_type_val = sale_return_order_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Update the 'order_attchments'
        update_fields = {'order_id': pk, 'order_type_id': type_id}
        attachment_data = update_multi_instances(self, pk, order_attachments_data, OrderAttachments, OrderAttachmentsSerializer,
                                                 update_fields, main_model_related_field='order_id', current_model_pk_field='attachment_id')

        # Update the 'shipments'
        shipment_data = update_multi_instances(self, pk, order_shipments_data, OrderShipments, OrderShipmentsSerializer,
                                               update_fields, main_model_related_field='order_id', current_model_pk_field='shipment_id')

        custom_data = {
            "sale_return_order": return_order_data,
            "sale_return_items": items_data if items_data else [],
            "order_attachments": attachment_data if attachment_data else [],
            "order_shipments": shipment_data[0] if shipment_data else {}
        }

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

class QuickPackCreateViewSet(APIView):
    """
    API ViewSet for handling Quick_Packs creation and related data.
    """
    def get_object(self, pk):
        try:
            return QuickPacks.objects.get(pk=pk)
        except QuickPacks.DoesNotExist:
            logger.warning(f"QuickPacks with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    # Get DB Objects
    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            result =  validate_input_pk(self,kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs) 
        try:
            logger.info("Retrieving all QuickPacks")

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10))   

            queryset = QuickPacks.objects.all()

            # Apply filters manually
            if request.query_params:
                filterset = QuickPacksFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs 

            total_count = QuickPacks.objects.count()
                     
            serializer = QuickPackSerializer(queryset, many=True)
            logger.info("QuickPacks data retrieved successfully.")
            # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
            return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a QuickPacks and its related data (items).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the SaleOrder instance
            quick_packs = get_object_or_404(QuickPacks, pk=pk)
            quick_packs_serializer = QuickPackSerializer(quick_packs)

            # Retrieve related data
            items_data = self.get_related_data(
                QuickPackItems, QuickPackItemSerializer, 'quick_pack_id', pk)
            
            # Customizing the response data
            custom_data = {
                "quick_pack_data": quick_packs_serializer.data,
                "quick_pack_data_items": items_data,                  
            }

            logger.info("quick_packs and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error("quick_packs with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(
                "An error occurred while retrieving quick_packs with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_related_data(self, model, serializer_class, filter_field, filter_value):
        """
        Retrieves related data for a given model, serializer, and filter field.
        """
        try:
            related_data = model.objects.filter(**{filter_field: filter_value})
            serializer = serializer_class(related_data, many=True)
            logger.debug("Retrieved related data for model %s with filter %s=%s.",
                         model.__name__, filter_field, filter_value)
            return serializer.data
        except Exception as e:
            logger.exception("Error retrieving related data for model %s with filter %s=%s: %s",
                             model.__name__, filter_field, filter_value, str(e))
            return []

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a Quick Packs.
        """
        try:
            # Get the QuickPacks instance
            instance = QuickPacks.objects.get(pk=pk)

           # Delete the main QuickPacks instance
            instance.delete()

            logger.info(f"QuickPacks with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except QuickPacks.DoesNotExist:
            logger.warning(f"QuickPacks with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting QuickPacks with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Handling POST requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

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

        # Vlidated quick_packs_data
        quick_packs_data = given_data.pop('quick_pack_data', None)  # parent_data
        if quick_packs_data:
            quick_packs_error = validate_payload_data(
                self, quick_packs_data, QuickPackSerializer)

        # Vlidated quick_pack_data_items Data
        quick_pack_items_data = given_data.pop('quick_pack_data_items', None)
        if quick_pack_items_data:
            item_error = validate_multiple_data(
                self, quick_pack_items_data, QuickPackItemSerializer, ['quick_pack_id'])

        # Ensure mandatory data is present
        if not quick_packs_data or not quick_pack_items_data:
            logger.error("Quick Packs and Quick Pack Items items are mandatory but not provided.")
            return build_response(0, "Quick Packs and Quick Pack items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if quick_packs_error:
            errors["quick_pack_data"] = quick_packs_error
        if item_error:
            errors["quick_pack_data_items"] = item_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """
        # Hence the data is validated , further it can be created.

        # Create quick_pack Data
        new_quick_pack_data = generic_data_creation(self, [quick_packs_data], QuickPackSerializer)
        new_quick_pack_data = new_quick_pack_data[0]
        quick_pack_id = new_quick_pack_data.get("quick_pack_id", None)  # Fetch quick_pack_id from mew instance
        logger.info('quick_pack - created*')

        # Create QuickPackItem Data
        update_fields = {'quick_pack_id': quick_pack_id}
        items_data = generic_data_creation(
            self, quick_pack_items_data, QuickPackItemSerializer, update_fields)
        logger.info('QuickPackItem - created*')

        custom_data = {
            "quick_pack_data": new_quick_pack_data,
            "quick_pack_data_items": items_data,            
        }

        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)

    def put(self, request, pk, *args, **kwargs):

        # ----------------------------------- D A T A  V A L I D A T I O N -----------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
         # Get the given data from request
        given_data = request.data
 
        # Vlidated Vendor Data
        quick_pack_data = given_data.pop('quick_pack_data', None)
        if quick_pack_data:
            order_error = validate_payload_data(self, quick_pack_data , QuickPackSerializer)

        # Vlidated QuickPackItems Data
        quick_pack_data_items = given_data.pop('quick_pack_data_items', None)
        if quick_pack_data_items:
            exclude_fields = ['quick_pack_id']
            item_error = validate_put_method_data(self, quick_pack_data_items, QuickPackItemSerializer,
                                    exclude_fields, QuickPackItems, current_model_pk_field='quick_pack_item_id')

      # Ensure mandatory data is present
        if not quick_pack_data or not quick_pack_data_items:
            logger.error("quick_pack and sale quick_pack_items are mandatory but not provided.")
            return build_response(0, "quick_pack and quick_pack_items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if order_error:
            errors["quick_pack"] = order_error
        if item_error:
            errors["quick_pack_items"] = item_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#

        # update QuickPacks
        if quick_pack_data:
            update_fields = []  # No need to update any fields
            quickpack_data = update_multi_instances(self, pk, [quick_pack_data], QuickPacks, QuickPackSerializer,
                                                    update_fields, main_model_related_field='quick_pack_id', current_model_pk_field='quick_pack_id')

        # Update the 'QuickPackItems'
        update_fields = {'quick_pack_id': pk}
        items_data = update_multi_instances(self, pk, quick_pack_data_items, QuickPackItems, QuickPackItemSerializer,
                                            update_fields, main_model_related_field='quick_pack_id', current_model_pk_field='quick_pack_item_id')

        custom_data = [
            {"quick_pack_data": quickpack_data},
            {"quick_pack_data_items": items_data if items_data else []}           
        ]

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

class SaleReceiptCreateViewSet(APIView):
    """
    API ViewSet for handling Lead creation and related data.
    """

    def get_object(self, pk):
        try:
            return SaleReceipt.objects.get(pk=pk)
        except SaleReceipt.DoesNotExist:
            logger.warning(f"SaleReceipt with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            result = validate_input_pk(self, kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            logger.info("Retrieving all sale_receipt")

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 

            queryset = SaleReceipt.objects.all()

            # Apply filters manually
            if request.query_params:
                filterset = SaleReceiptFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs 

            total_count = SaleInvoiceOrders.objects.count()

            serializer = SaleReceiptSerializer(queryset, many=True)
            logger.info("sale_receipt data retrieved successfully.")
            # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
            return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a sale_receipt and its related data (assignment_history, and Interaction).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the SaleReceipt instance
            sale_receipt = get_object_or_404(SaleReceipt, pk=pk)
            sale_receipt_serializer = SaleReceiptSerializer(sale_receipt)


            # Customizing the response data
            custom_data = {
                "sale_receipt": sale_receipt_serializer.data
                }
            logger.info("sale_receipt and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error("Lead record with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(
                "An error occurred while retrieving sale_receipt with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_related_data(self, model, serializer_class, filter_field, filter_value):
        """
        Retrieves related data for a given model, serializer, and filter field.
        """
        try:
            related_data = model.objects.filter(**{filter_field: filter_value})
            serializer = serializer_class(related_data, many=True)
            logger.debug("Retrieved related data for model %s with filter %s=%s.",
                         model.__name__, filter_field, filter_value)
            return serializer.data
        except Exception as e:
            logger.exception("Error retrieving related data for model %s with filter %s=%s: %s",
                             model.__name__, filter_field, filter_value, str(e))
            return []

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a sale_receipt and its related assignments and interactions.
        """
        try:
            # Get the SaleReceipt instance
            instance = SaleReceipt.objects.get(pk=pk)

            # Delete the main SaleReceipt instance
            '''
            All related instances will be deleted when parent record is deleted. all child models have foreignkey relation with parent table
            '''
            instance.delete()

            logger.info(f"SaleReceipt with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except SaleReceipt.DoesNotExist:
            logger.warning(f"SaleReceipt with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting SaleReceipt with ID {pk}: {str(e)}")
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

        # Validate SaleReceipt Data
        sale_receipt_data = given_data.pop('sale_receipt', None)  # parent_data
        if sale_receipt_data:
            sale_receipt_error = validate_payload_data(self, sale_receipt_data, SaleReceiptSerializer)

            if sale_receipt_error:
                errors["sale_receipt"] = sale_receipt_error

        # Ensure mandatory data is present
        if not sale_receipt_data:
            logger.error("Lead data is mandatory but not provided.")
            return build_response(0, "Lead data is mandatory", [], status.HTTP_400_BAD_REQUEST)

        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """

        # Hence the data is validated , further it can be created.
        custom_data = {
            'sale_receipt':{}
            }

        # Create SaleReceipt Data
        new_sale_receipt_data = generic_data_creation(self, [sale_receipt_data], SaleReceiptSerializer)
        new_sale_receipt_data = new_sale_receipt_data[0]
        custom_data["sale_receipt"] = new_sale_receipt_data
        sale_receipt_id = new_sale_receipt_data.get("sale_receipt_id", None)  # Fetch sale_receipt_id from mew instance
        logger.info('SaleReceipt - created*')

        #create History for Lead with assignemnt date as current and leave the end date as null.
        update_fields = {'sale_receipt_id':sale_receipt_id}

        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):

        # ----------------------------------- D A T A  V A L I D A T I O N -----------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        # Get the given data from request
        given_data = request.data
        errors = {}

        # Validate SaleReceipt Data
        sale_receipt_data = given_data.pop('sale_receipt', None)  # parent_data
        if sale_receipt_data:
            sale_receipt_data['sale_receipt_id'] = pk
            sale_receipt_error = validate_multiple_data(self, [sale_receipt_data], SaleReceiptSerializer, [])
            if sale_receipt_error:
                errors["sale_receipt"] = sale_receipt_error

        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#
        custom_data = {
            'sale_receipt':{}
            }
        

        if sale_receipt_data:
            # Fetch last record in 'SaleReceipt' | generally one recrd exists with one 'sale_receipt_id' (current Lead pk)
            sale_data_set = SaleReceipt.objects.filter(pk=pk).last()  # take the last instance in Lead data
            if sale_data_set is not None:
                previous_sale_receipt_id = str(sale_data_set.sale_receipt_id)
                current_sale_receipt_id = sale_receipt_data.get('sale_receipt_id')

        # update 'SaleReceipt'
        if sale_receipt_data:
            salereceiptdata = update_multi_instances(self, pk, sale_receipt_data, SaleReceipt, SaleReceiptSerializer,[], main_model_related_field='sale_receipt_id', current_model_pk_field='sale_receipt_id')
            custom_data["sale_receipt"] = salereceiptdata[0]

        # Update the 'LeadInteractions'
        update_fields = {'sale_receipt_id': pk}
        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

class WorkflowCreateViewSet(APIView):
    """
    API ViewSet for handling workflow creation and related data.
    """

    def get_object(self, pk):
        try:
            return Workflow.objects.get(pk=pk)
        except Workflow.DoesNotExist:
            logger.warning(f"Workflow with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            return self.retrieve(request, *args, **kwargs)
        try:
            logger.info("Retrieving all workflows")
            queryset = Workflow.objects.all()
            serializer = WorkflowSerializer(queryset, many=True)
            logger.info("Workflow data retrieved successfully.")
            return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a workflow and its related workflow stages.
        """
        pk = kwargs.get('pk')
        if not pk:
            logger.error("Primary key not provided in request.")
            return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the Workflow instance
            workflow = get_object_or_404(Workflow, pk=pk)
            workflow_serializer = WorkflowSerializer(workflow)

            # Retrieve associated workflow stages
            workflow_stages = WorkflowStage.objects.filter(workflow_id=pk)
            workflow_stages_serializer = WorkflowStageSerializer(workflow_stages, many=True)

            # Customizing the response data
            custom_data = {
                "workflow": workflow_serializer.data,
                "workflow_stages": workflow_stages_serializer.data,
            }
            logger.info("Workflow and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)
        except Http404:
            logger.error(f"Workflow with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(f"An error occurred while retrieving workflow with ID {pk}: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a workflow and its related workflow stages.
        """
        try:
            # Get the Workflow instance
            instance = Workflow.objects.get(pk=pk)
            instance.delete()

            logger.info(f"Workflow with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except Workflow.DoesNotExist:
            logger.warning(f"Workflow with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting Workflow with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        given_data = request.data

        # Extract and validate workflow data if provided
        workflow_data = given_data.get('workflow')
        workflow_instance = None

        if workflow_data:
            # Create a new workflow instance
            workflow_serializer = WorkflowSerializer(data=workflow_data)
            if not workflow_serializer.is_valid():
                return build_response(0, "ValidationError", workflow_serializer.errors, status.HTTP_400_BAD_REQUEST)
            
            # Save the workflow instance
            workflow_instance = workflow_serializer.save()

        if not workflow_instance:
            return build_response(0, "Workflow data is mandatory", [], status.HTTP_400_BAD_REQUEST)

        # Handle workflow stages data
        workflow_stage_data_list = given_data.get('workflow_stages')
        workflow_stage_instances = []

        if workflow_stage_data_list and isinstance(workflow_stage_data_list, list):
            for stage_data in workflow_stage_data_list:
                # Assign the newly created workflow's ID to each stage
                stage_data['workflow_id'] = workflow_instance.pk

                # Validate and save the workflow stage
                workflow_stage_serializer = WorkflowStageSerializer(data=stage_data)
                if not workflow_stage_serializer.is_valid():
                    return build_response(0, "ValidationError", workflow_stage_serializer.errors, status.HTTP_400_BAD_REQUEST)
                
                # Save the stage instance
                stage_instance = workflow_stage_serializer.save()
                workflow_stage_instances.append(stage_instance)

        # Prepare response data
        workflow_data_response = WorkflowSerializer(workflow_instance).data
        workflow_stage_data_response = WorkflowStageSerializer(workflow_stage_instances, many=True).data

        return build_response(1, "Record created successfully", {
            'workflow': workflow_data_response,
            'workflow_stages': workflow_stage_data_response
        }, status.HTTP_201_CREATED)


    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):
        given_data = request.data
        errors = {}

        # Update the Workflow data
        workflow_data = given_data.get('workflow')
        if workflow_data:
            try:
                workflow_instance = Workflow.objects.get(pk=pk)
                workflow_serializer = WorkflowSerializer(workflow_instance, data=workflow_data, partial=True)
                if not workflow_serializer.is_valid():
                    errors["workflow"] = workflow_serializer.errors
                else:
                    workflow_serializer.save()
            except Workflow.DoesNotExist:
                return build_response(0, f"Workflow with ID {pk} does not exist.", [], status.HTTP_404_NOT_FOUND)

        # Handle Workflow Stages
        workflow_stage_data_list = given_data.get('workflow_stages')
        existing_stage_ids = set()

        if workflow_stage_data_list and isinstance(workflow_stage_data_list, list):
            for stage_data in workflow_stage_data_list:
                stage_id = stage_data.get('workflow_stage_id')
                if stage_id:
                    # Update the existing workflow stage by ID
                    try:
                        stage_instance = WorkflowStage.objects.get(pk=stage_id, workflow_id=pk)
                        stage_serializer = WorkflowStageSerializer(stage_instance, data=stage_data, partial=True)

                        if not stage_serializer.is_valid():
                            errors[f"workflow_stage_{stage_id}"] = stage_serializer.errors
                        else:
                            stage_serializer.save()
                            existing_stage_ids.add(stage_id)
                    except WorkflowStage.DoesNotExist:
                        return build_response(0, f"WorkflowStage with ID {stage_id} does not exist.", [], status.HTTP_400_BAD_REQUEST)
                else:
                    # Create a new WorkflowStage if not found
                    stage_data['workflow_id'] = pk  # Attach the workflow ID to the new stage data
                    stage_serializer = WorkflowStageSerializer(data=stage_data)

                    if stage_serializer.is_valid():
                        new_stage = stage_serializer.save()
                        existing_stage_ids.add(new_stage.workflow_stage_id)
                    else:
                        errors["workflow_stage_creation"] = stage_serializer.errors

        # Optionally, remove stages that were not included in the update request
        WorkflowStage.objects.filter(workflow_id=pk).exclude(workflow_stage_id__in=existing_stage_ids).delete()

        if errors:
            return build_response(0, "ValidationError", errors, status.HTTP_400_BAD_REQUEST)

        # Prepare the response data
        workflow_data_response = WorkflowSerializer(Workflow.objects.get(pk=pk)).data
        workflow_stage_data_response = WorkflowStageSerializer(
            WorkflowStage.objects.filter(workflow_id=pk), many=True
        ).data

        return build_response(1, "Records updated successfully", {
            'workflow': workflow_data_response,
            'workflow_stages': workflow_stage_data_response
        }, status.HTTP_200_OK)

class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class WorkflowStageViewSet(viewsets.ModelViewSet):
    queryset = WorkflowStage.objects.all()
    serializer_class = WorkflowStageSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class SaleReceiptViewSet(viewsets.ModelViewSet):
    queryset = SaleReceipt.objects.all()
    serializer_class = SaleReceiptSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = SaleReceiptFilter
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
# created new view for this
# class ProgressWorkflowView(APIView):
#     """
#     API view to progress the workflow of a specific SaleOrder to the next stage.
#     This view is used to update the flow_status of a sale order, moving it from one stage to the next within its defined workflow.
#     """

#     def post(self, request, pk, format=None):
#         """
#         Handle POST requests to progress the workflow of the specified SaleOrder.
        
#         Parameters:
#         - request: The HTTP request object.
#         - pk: The primary key of the SaleOrder to be updated.
#         - format: An optional format specifier for content negotiation.

#         Returns:
#         - Custom JSON structure with 'count', 'message', and 'data'.
#         """
#         try:
#             # Attempt to retrieve the SaleOrder by its primary key (pk)
#             sale_order = SaleOrder.objects.get(pk=pk)

#             # Try to progress the workflow to the next stage
#             if sale_order.progress_workflow():
#                 response_data = {
#                     "count": 1,
#                     "message": "Success",
#                     "data": {"status": "Flow status updated successfully."}
#                 }
#                 return Response(response_data, status=status.HTTP_200_OK)
#             else:
#                 response_data = {
#                     "count": 1,
#                     "message": "Success",
#                     "data": {"status": "No further stages. Workflow is complete."}
#                 }
#                 return Response(response_data, status=status.HTTP_200_OK)
#         except SaleOrder.DoesNotExist:
#             response_data = {
#                 "count": 0,
#                 "message": "SaleOrder not found.",
#                 "data": None
#             }
#             return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        
class SaleCreditNoteViewset(APIView):
    
    def get_object(self, pk):
        try:
            return SaleCreditNotes.objects.get(pk=pk)
        except SaleCreditNotes.DoesNotExist:
            logger.warning(f"salecreditnote with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        
    def get(self, request, *args, **kwargs):
        print("Hello")
        if "pk" in kwargs:
            result = validate_input_pk(self, kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            logger.info("Retrieving all salecreditnote")
            print("try block is triggering")
            queryset = SaleCreditNotes.objects.all()
            serializer = SaleCreditNoteSerializers(queryset, many=True)
            logger.info("salecreditnote data retrieved successfully.")
            return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def retrieve(self, request, *args, **kwargs):
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the SaleOrder instance
            sale_credit_note = get_object_or_404(SaleCreditNotes, pk=pk)
            sale_credit_note_serializer = SaleCreditNoteSerializers(sale_credit_note)

            # Retrieve related data
            credit_items_data = self.get_related_data(
                SaleCreditNoteItems, SaleCreditNoteItemsSerializers, 'credit_note_id', pk)

            # Customizing the response data
            custom_data = {
                "sale_credit_note": sale_credit_note_serializer.data,
                "sale_credit_note_items": credit_items_data,
            }
            logger.info("salecreditnote and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error("salecreditnote with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(
                "An error occurred while retrieving salecreditnote with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get_related_data(self, model, serializer_class, filter_field, filter_value):
        """
        Retrieves related data for a given model, serializer, and filter field.
        """
        try:
            related_data = model.objects.filter(**{filter_field: filter_value})
            serializer = serializer_class(related_data, many=True)
            logger.debug("Retrieved related data for model %s with filter %s=%s.",
                         model.__name__, filter_field, filter_value)
            return serializer.data
        except Exception as e:
            logger.exception("Error retrieving related data for model %s with filter %s=%s: %s",
                             model.__name__, filter_field, filter_value, str(e))
            return []
        
    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a sale order and its related attachments and shipments.
        """
        try:
            # Get the SaleCreditNotes instance
            instance = SaleCreditNotes.objects.get(pk=pk)

            # Delete the main SaleCreditNotes instance
            instance.delete()

            logger.info(f"SaleCreditNotes with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except SaleCreditNotes.DoesNotExist:
            logger.warning(f"SaleCreditNotes with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting SaleCreditNotes with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Handling POST requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        print("Create is running now:")
        # Extracting data from the request
        given_data = request.data

        # ---------------------- D A T A   V A L I D A T I O N ----------------------------------#
        # Vlidated SaleOrder Data
        sale_credit_note_data = given_data.pop('sale_credit_note', None)  # parent_data
        if sale_credit_note_data:
            credit_note_error = validate_payload_data(
                self, sale_credit_note_data, SaleCreditNoteSerializers)

        # Vlidated SaleOrderItems Data
        sale_credit_items_data = given_data.pop('sale_credit_note_items', None)
        if sale_credit_items_data:
            item_error = validate_multiple_data(
                self, sale_credit_items_data, SaleCreditNoteItemsSerializers, ['credit_note_id'])

        # Ensure mandatory data is present
        if not sale_credit_note_data or not sale_credit_items_data:
            logger.error(
                "SaleCreditNote and SaleCreditNote items are mandatory but not provided.")
            return build_response(0, "SaleCreditNote and SaleCreditNote items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if credit_note_error:
            errors["sale_credit_note"] = credit_note_error
        if item_error:
            errors["sale_credit_note_items"] = item_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """

        # Hence the data is validated , further it can be created.

        # Create SaleCreditNotes Data
        new_sale_credit_note_data = generic_data_creation(self, [sale_credit_note_data], SaleCreditNoteSerializers)
        new_sale_credit_note_data = new_sale_credit_note_data[0]
        credit_note_id = new_sale_credit_note_data.get("credit_note_id", None)
        logger.info('SaleCreditNotes - created*')

        # Create SaleCreditNotesItems Data
        update_fields = {'credit_note_id': credit_note_id}
        items_data = generic_data_creation(
            self, sale_credit_items_data, SaleCreditNoteItemsSerializers, update_fields)
        logger.info('SaleCreditNotesItems - created*')


        custom_data = {
            "sale_credit_note": new_sale_credit_note_data,
            "sale_credit_note_items": items_data,
        }

        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):

        # ----------------------------------- D A T A  V A L I D A T I O N -----------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        # Get the given data from request
        given_data = request.data

        # Vlidated SaleOrder Data
        sale_credit_note_data = given_data.pop('sale_credit_note', None)  # parent_data
        if sale_credit_note_data:
            sale_credit_note_data['credit_note_id'] = pk
            credit_note_error = validate_multiple_data(
                self, [sale_credit_note_data], SaleCreditNoteSerializers, ['credit_note_number'])

        # Vlidated SaleOrderItems Data
        sale_credit_items_data = given_data.pop('sale_credit_note_items', None)
        if sale_credit_items_data:
            exclude_fields = ['credit_note_id']
            item_error = validate_put_method_data(self, sale_credit_items_data, SaleCreditNoteItemsSerializers,
                                                  exclude_fields, SaleCreditNoteItems, current_model_pk_field='credit_note_item_id')
        # Ensure mandatory data is present
        if not sale_credit_note_data or not sale_credit_items_data:
            logger.error(
                "SaleCreditNote and SaleCreditNote items are mandatory but not provided.")
            return build_response(0, "SaleCreditNote and SaleCreditNote items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if credit_note_error:
            errors["sale_credit_note"] = credit_note_error
        if item_error:
            errors["sale_credit_note_items"] = item_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#

        # update SaleOrder
        if sale_credit_note_data:
            update_fields = []  # No need to update any fields
            salecreditnote_data = update_multi_instances(self, pk, [sale_credit_note_data], SaleCreditNotes, SaleCreditNoteSerializers,
                                                    update_fields, main_model_related_field='credit_note_id', current_model_pk_field='credit_note_id')

        # Update the 'sale_order_items'
        update_fields = {'credit_note_id': pk}
        items_data = update_multi_instances(self, pk, sale_credit_items_data, SaleCreditNoteItems, SaleCreditNoteItemsSerializers,
                                            update_fields, main_model_related_field='credit_note_id', current_model_pk_field='credit_note_item_id')

        custom_data = {
            "sale_credit_note": salecreditnote_data[0] if salecreditnote_data else {},
            "sale_credit_note_items": items_data if items_data else []
        }

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)
    
    def patch(self, request, pk, format=None):
        sale_credit_note = self.get_object(pk)
        if sale_credit_note is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = SaleCreditNoteSerializers(sale_credit_note, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class SaleDebitNoteViewset(APIView):
    
    def get_object(self, pk):
        try:
            return SaleDebitNotes.objects.get(pk=pk)
        except SaleDebitNotes.DoesNotExist:
            logger.warning(f"salecreditnote with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        
    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            result = validate_input_pk(self, kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            logger.info("Retrieving all salecreditnote")
            print("try block is triggering")
            queryset = SaleDebitNotes.objects.all()
            serializer = SaleDebitNoteSerializers(queryset, many=True)
            logger.info("salecreditnote data retrieved successfully.")
            return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def retrieve(self, request, *args, **kwargs):
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the SaleOrder instance
            sale_debit_note = get_object_or_404(SaleDebitNotes, pk=pk)
            sale_debit_note_serializer = SaleDebitNoteSerializers(sale_debit_note)

            # Retrieve related data
            debit_items_data = self.get_related_data(
                SaleDebitNoteItems, SaleDebitNoteItemsSerializers, 'debit_note_id', pk)

            # Customizing the response data
            custom_data = {
                "sale_debit_note": sale_debit_note_serializer.data,
                "sale_debit_note_items": debit_items_data,
            }
            logger.info("salecreditnote and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error("salecreditnote with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(
                "An error occurred while retrieving salecreditnote with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get_related_data(self, model, serializer_class, filter_field, filter_value):
        """
        Retrieves related data for a given model, serializer, and filter field.
        """
        try:
            related_data = model.objects.filter(**{filter_field: filter_value})
            serializer = serializer_class(related_data, many=True)
            logger.debug("Retrieved related data for model %s with filter %s=%s.",
                         model.__name__, filter_field, filter_value)
            return serializer.data
        except Exception as e:
            logger.exception("Error retrieving related data for model %s with filter %s=%s: %s",
                             model.__name__, filter_field, filter_value, str(e))
            return []
        
    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a sale order and its related attachments and shipments.
        """
        try:
            # Get the SaleDebitNotes instance
            instance = SaleDebitNotes.objects.get(pk=pk)

            # Delete the main SaleDebitNotes instance
            instance.delete()

            logger.info(f"SaleDebitNotes with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except SaleDebitNotes.DoesNotExist:
            logger.warning(f"SaleDebitNotes with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting SaleDebitNotes with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Handling POST requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        print("Create is running now:")
        # Extracting data from the request
        given_data = request.data

        # ---------------------- D A T A   V A L I D A T I O N ----------------------------------#
        # Vlidated SaleOrder Data
        sale_debit_note_data = given_data.pop('sale_debit_note', None)  # parent_data
        if sale_debit_note_data:
            debit_note_error = validate_payload_data(
                self, sale_debit_note_data, SaleDebitNoteSerializers)

        # Vlidated SaleOrderItems Data
        sale_debit_items_data = given_data.pop('sale_debit_note_items', None)
        if sale_debit_items_data:
            item_error = validate_multiple_data(
                self, sale_debit_items_data, SaleDebitNoteItemsSerializers, ['debit_note_id'])

        # Ensure mandatory data is present
        if not sale_debit_note_data or not sale_debit_items_data:
            logger.error(
                "Saledebitnote and Saledebitnote items are mandatory but not provided.")
            return build_response(0, "Saledebitnote and Saledebitnote items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if debit_note_error:
            errors["sale_debit_note"] = debit_note_error
        if item_error:
            errors["sale_debit_note_items"] = item_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """

        # Hence the data is validated , further it can be created.

        # Create SaleDebitNotes Data
        new_sale_debit_note_data = generic_data_creation(self, [sale_debit_note_data], SaleDebitNoteSerializers)
        new_sale_debit_note_data = new_sale_debit_note_data[0]
        debit_note_id = new_sale_debit_note_data.get("debit_note_id", None)
        logger.info('SaleDebitNotes - created*')

        # Create SaleCreditNotesItems Data
        update_fields = {'debit_note_id': debit_note_id}
        items_data = generic_data_creation(
            self, sale_debit_items_data, SaleDebitNoteItemsSerializers, update_fields)
        logger.info('SaleCreditNotesItems - created*')


        custom_data = {
            "sale_debit_note": new_sale_debit_note_data,
            "sale_debit_note_items": items_data,
        }

        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):

        # ----------------------------------- D A T A  V A L I D A T I O N -----------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        # Get the given data from request
        given_data = request.data

        # Vlidated SaleOrder Data
        sale_debit_note_data = given_data.pop('sale_debit_note', None)  # parent_data
        if sale_debit_note_data:
            sale_debit_note_data['debit_note_id'] = pk
            debit_note_error = validate_multiple_data(
                self, [sale_debit_note_data], SaleDebitNoteSerializers, ['debit_note_number'])

        # Vlidated SaleOrderItems Data
        sale_debit_items_data = given_data.pop('sale_debit_note_items', None)
        if sale_debit_items_data:
            exclude_fields = ['debit_note_id']
            item_error = validate_put_method_data(self, sale_debit_items_data, SaleDebitNoteItemsSerializers,
                                                  exclude_fields, SaleDebitNoteItems, current_model_pk_field='debit_note_item_id')
        # Ensure mandatory data is present
        if not sale_debit_note_data or not sale_debit_items_data:
            logger.error(
                "Saledebitnote and Saledebitnote items are mandatory but not provided.")
            return build_response(0, "Saledebitnote and Saledebitnote items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if debit_note_error:
            errors["sale_debit_note"] = debit_note_error
        if item_error:
            errors["sale_debit_note_items"] = item_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#

        # update SaleOrder
        if sale_debit_note_data:
            update_fields = []  # No need to update any fields
            saledebitnote_data = update_multi_instances(self, pk, [sale_debit_note_data], SaleDebitNotes, SaleDebitNoteSerializers,
                                                    update_fields, main_model_related_field='debit_note_id', current_model_pk_field='debit_note_id')

        # Update the 'sale_order_items'
        update_fields = {'debit_note_id': pk}
        items_data = update_multi_instances(self, pk, sale_debit_items_data, SaleDebitNoteItems, SaleDebitNoteItemsSerializers,
                                            update_fields, main_model_related_field='debit_note_id', current_model_pk_field='debit_note_item_id')

        custom_data = {
            "sale_debit_note": saledebitnote_data[0] if saledebitnote_data else {},
            "sale_debit_note_items": items_data if items_data else []
        }

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)
        
    def patch(self, request, pk, format=None):
        sale_debit_note = self.get_object(pk)
        if sale_debit_note is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = SaleDebitNoteSerializers(sale_debit_note, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MoveToNextStageGenericView(APIView):
    """
    API endpoint to move any module (e.g., Sale Order, Purchase Order, etc.) to the next stage in its workflow.
    """

    def post(self, request, module_name, object_id):
        try:
            # Dynamically load the model based on module_name
            ModelClass = self.get_model_class(module_name)
            if not ModelClass:
                return Response({"error": f"Model {module_name} not found."}, status=status.HTTP_404_NOT_FOUND)

            # Fetch the object from the appropriate model
            obj = ModelClass.objects.get(pk=object_id)
            print(f"Current flow_status_id: {obj.flow_status_id}")

            # Find the current workflow stage based on the current flow_status_id
            current_stage = WorkflowStage.objects.filter(flow_status_id=obj.flow_status_id).first()
            if not current_stage:
                return Response({"error": "Current workflow stage not found."}, status=status.HTTP_404_NOT_FOUND)

            print(f"Current Stage: {current_stage}")

            # Check if the current stage is "Production"
            production_stage = WorkflowStage.objects.filter(
                workflow_id=current_stage.workflow_id_id,
                flow_status_id__flow_status_name="Production"  # Assuming "Production" stage has this name
            ).first()

            # Define the next stage logic
            if current_stage == production_stage:
                # If currently in "Production", move back to "Review Inventory" (Stage 1)
                next_stage = WorkflowStage.objects.filter(
                    workflow_id=current_stage.workflow_id_id,
                    stage_order=1  # Move back to stage 1
                ).first()
            else:
                # Otherwise, get the next stage in sequence
                next_stage = WorkflowStage.objects.filter(
                    workflow_id=current_stage.workflow_id_id,
                    stage_order__gt=current_stage.stage_order
                ).order_by('stage_order').first()

            if next_stage:
                # Update the object's flow_status_id to the next stage's flow_status_id
                obj.flow_status_id = next_stage.flow_status_id
                obj.save()

                # Log workflow progression details in the global dictionary
                workflow_progression_dict[obj.pk] = {
                    "current_stage": current_stage.flow_status_id.flow_status_name,
                    "next_stage": next_stage.flow_status_id.flow_status_name,
                    "timestamp": str(datetime.now())
                }

                return Response({
                    "message": f"{module_name} moved to the next stage.",
                    "current_stage": current_stage.flow_status_id.flow_status_name,
                    "next_stage": next_stage.flow_status_id.flow_status_name
                }, status=status.HTTP_200_OK)
            else:
                return Response({"message": f"{module_name} has reached the final stage."}, status=status.HTTP_200_OK)

        except ModelClass.DoesNotExist:
            return Response({"error": f"{module_name} object with ID {object_id} not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_model_class(self, module_name):
        """
        Helper method to dynamically load the model class.

        Parameters:
            - module_name (str): The name of the model (e.g., 'SaleOrder', 'PurchaseOrder').
        
        Returns:
            - Model class if found, otherwise None.
        """
        try:
            for model in apps.get_models():
                if model.__name__.lower() == module_name.lower():
                    return model
        except LookupError:
            print(f"Model {module_name} not found.")
            return None