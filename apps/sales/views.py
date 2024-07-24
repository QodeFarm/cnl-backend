import logging
from django.db import transaction
from django.forms import ValidationError
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.serializers import ValidationError
from uuid import UUID
from rest_framework.views import APIView

from apps.purchase.models import PurchaseOrders
from apps.purchase.serializers import PurchaseOrdersSerializer
from .serializers import *
from apps.masters.models import OrderTypes
from config.utils_methods import update_multi_instances, validate_input_pk, delete_multi_instance, generic_data_creation, get_object_or_none, list_all_objects, create_instance, update_instance, build_response, validate_multiple_data, validate_order_type, validate_payload_data, validate_put_method_data

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)


class SaleOrderView(viewsets.ModelViewSet):
    queryset = SaleOrder.objects.all()
    serializer_class = SaleOrderSerializer

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

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class SaleInvoiceOrdersView(viewsets.ModelViewSet):
    queryset = SaleInvoiceOrders.objects.all()
    serializer_class = SaleInvoiceOrdersSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class SaleReturnOrdersView(viewsets.ModelViewSet):
    queryset = SaleReturnOrders.objects.all()
    serializer_class = SaleReturnOrdersSerializer

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
            summary = request.query_params.get("summary", "false").lower() == "true"
            if summary:
                logger.info("Retrieving Sale order summary")
                saleorders = SaleOrder.objects.all()
                data = SaleOrderOptionsSerializer.get_sale_order_summary(saleorders)
                return Response(data, status=status.HTTP_200_OK)

            logger.info("Retrieving all sale order")
            queryset = SaleOrder.objects.all()
            serializer = SaleOrderSerializer(queryset, many=True)
            logger.info("sale order data retrieved successfully.")
            return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)

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
        if order_shipments_data:
            shipments_error = validate_multiple_data(
                self, [order_shipments_data], OrderShipmentsSerializer, ['order_id', 'order_type_id'])
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
            summary = request.query_params.get("summary", "false").lower() == "true"
            if summary:
                logger.info("Retrieving sale invoice order summary")
                saleinvoiceorder = SaleInvoiceOrders.objects.all()
                data = SaleInvoiceOrderOptionsSerializer.get_sale_invoice_order_summary(saleinvoiceorder)
                return build_response(len(data), "Success", data, status.HTTP_200_OK)
             
            logger.info("Retrieving all sale invoice orders")
            queryset = SaleInvoiceOrders.objects.all()
            serializer = SaleInvoiceOrdersSerializer(queryset, many=True)
            logger.info("sale order invoice data retrieved successfully.")
            return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
 
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

        # Vlidated SaleInvoiceOrders Data
        sale_invoice_order_data = given_data.pop('sale_invoice_order', None)  # parent_data
        if sale_invoice_order_data:
            order_error = validate_payload_data(self, sale_invoice_order_data, SaleInvoiceOrdersSerializer)
            # validate the order_type in 'sale_invoice_order_data' data
            validate_order_type(sale_invoice_order_data, order_error, OrderTypes, look_up='order_type')

        # Validate SaleInvoiceItems Data
        sale_invoice_items_data = given_data.pop('sale_invoice_items', None)
        if sale_invoice_items_data:
            item_error = validate_multiple_data(self, sale_invoice_items_data, SaleInvoiceItemsSerializer, ['sale_invoice_id'])

        # Vlidated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        if order_attachments_data:
            attachment_error = validate_multiple_data(self, order_attachments_data, OrderAttachmentsSerializer, ['order_id', 'order_type_id'])
        else:
            # Since 'order_attachments' is optional, so making an error is empty list
            attachment_error = []

        # Vlidated OrderShipments Data
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
            summary = request.query_params.get("summary", "false").lower() == "true"
            if summary:
                logger.info("Retrieving sale return orders summary")
                salereturnorders = SaleReturnOrders.objects.all()
                data = SaleReturnOrdersOptionsSerializer.get_sale_return_orders_summary(salereturnorders)
                return build_response(len(data), "Success", data, status.HTTP_200_OK)
             
            logger.info("Retrieving all sale return order")
            queryset = SaleReturnOrders.objects.all()
            serializer = SaleReturnOrdersSerializer(queryset, many=True)
            logger.info("sale return order data retrieved successfully.")
            return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
 
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
            queryset = QuickPacks.objects.all()
            serializer = QuickPackSerializer(queryset, many=True)
            logger.info("QuickPacks data retrieved successfully.")
            return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
 
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
