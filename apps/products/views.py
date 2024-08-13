import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework import viewsets
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db import transaction
from config.utils_variables import *
from config.utils_methods import *
from apps.inventory.serializers import WarehouseLocationsSerializer
from apps.inventory.models import WarehouseLocations
from .serializers import *
from .models import *
from .filters import ProductGroupsFilter, ProductCategoriesFilter, ProductStockUnitsFilter, ProductGstClassificationsFilter, ProductSalesGlFilter, ProductPurchaseGlFilter, ProductsFilter, ProductItemBalanceFilter

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)

# Create your views here.
class ProductGroupsViewSet(viewsets.ModelViewSet):
    queryset = ProductGroups.objects.all()
    serializer_class = ProductGroupsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductGroupsFilter
    ordering_fields = ['group_name']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class ProductCategoriesViewSet(viewsets.ModelViewSet):
    queryset = ProductCategories.objects.all()
    serializer_class = ProductCategoriesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductCategoriesFilter
    ordering_fields = ['category_name','code']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class ProductStockUnitsViewSet(viewsets.ModelViewSet):
    queryset = ProductStockUnits.objects.all()
    serializer_class = ProductStockUnitsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductStockUnitsFilter
    ordering_fields = ['stock_unit_name','quantity_code_id']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
	
class ProductGstClassificationsViewSet(viewsets.ModelViewSet):
    queryset = ProductGstClassifications.objects.all()
    serializer_class = ProductGstClassificationsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductGstClassificationsFilter
    ordering_fields = ['type','code','hsn_or_sac_code']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class ProductSalesGlViewSet(viewsets.ModelViewSet):
    queryset = ProductSalesGl.objects.all()
    serializer_class = ProductSalesGlSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductSalesGlFilter
    ordering_fields = ['name','sales_accounts','code','type','account_no','rtgs_ifsc_code','address','pan','employee']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
	
class ProductPurchaseGlViewSet(viewsets.ModelViewSet):
    queryset = ProductPurchaseGl.objects.all()
    serializer_class = ProductPurchaseGlSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductPurchaseGlFilter
    ordering_fields = ['name','purchase_accounts','code','type','account_no','rtgs_ifsc_code','address','pan','employee']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

		
class productsViewSet(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = productsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductsFilter
    ordering_fields = ['name','code','barcode','category_id','product_group_id','type_id','gst_classification_id','created_at']

    def list(self, request, *args, **kwargs):
        summary = request.query_params.get('summary', 'false').lower() == 'true'
        if summary:
            products = self.filter_queryset(self.get_queryset())
            data = ProductOptionsSerializer.get_product_summary(products)
            result = Response(data, status=status.HTTP_200_OK)
        else:
            result = list_all_objects(self, request, *args, **kwargs)
        
        return result
    
    def create(self, request, *args, **kwargs):
        # Extract the product ID from the request if needed
        request_product_id = request.data.get('product_id')

        # Check if 'picture' exists in request data and is a list
        if 'picture' in request.data and isinstance(request.data['picture'], list):
            attachment_data_list = request.data['picture']
            if attachment_data_list:
                # Ensure all items in the list have the required fields
                for attachment in attachment_data_list:
                    if not all(key in attachment for key in ['uid', 'name', 'attachment_name', 'file_size', 'attachment_path']):
                        return build_response(0, "Missing required fields in some picture data.", [], status.HTTP_400_BAD_REQUEST)
                
                # Set the picture field in request data as a list of objects
                request.data['picture'] = attachment_data_list

            else:
                # Handle case where 'picture' list is empty
                return build_response(0, "'picture' list is empty.", [], status.HTTP_400_BAD_REQUEST)
        else:
            # Handle the case where 'picture' is not provided or not a list
            return build_response(0, "'picture' field is required and should be a list.", [], status.HTTP_400_BAD_REQUEST)

        # Proceed with creating the instance
        try:
            response = super().create(request, *args, **kwargs)
            
            # Format the response to include the picture data
            if isinstance(response.data, dict):
                picture_data = response.data.get('picture')
                if picture_data:
                    response.data['picture'] = picture_data
            return response
        
        except ValidationError as e:
            return build_response(1, "Creation failed due to validation errors.", e.detail, status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

    
class ProductItemBalanceViewSet(viewsets.ModelViewSet):
    queryset = ProductItemBalance.objects.all()
    serializer_class = ProductItemBalanceSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductItemBalanceFilter
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


#--------------------P R O D U C T - A P I-----------------------#

class ProductViewSet(APIView):
    """
    API ViewSet for handling Lead creation and related data.
    """

    def get_object(self, pk):
        try:
            return Products.objects.get(pk=pk)
        except Products.DoesNotExist:
            logger.warning(f"Products with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            result = validate_input_pk(self, kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            summary = request.query_params.get('summary', 'false').lower() == 'true'
            if summary:
                salereturnorders = Products.objects.all()
                data = ProductOptionsSerializer.get_product_summary(salereturnorders)
                return build_response(len(data), "Success", data, status.HTTP_200_OK)                

            logger.info("Retrieving all products")
            queryset = Products.objects.all()
            serializer = productsSerializer(queryset, many=True)
            logger.info("product data retrieved successfully.")
            return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def retrieve(self, request, *args, **kwargs):
            """
            Retrieves a products and its related data (warehouse_locations, and product_item_balance).
            """
            try:
                pk = kwargs.get('pk')
                if not pk:
                    logger.error("Primary key not provided in request.")
                    return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

                # Retrieve the Leads instance
                lead = get_object_or_404(Products, pk=pk)
                products_serializer = productsSerializer(lead)

                # Retrieve product_item_balance
                product_item_balance_data = self.get_related_data(ProductItemBalance, ProductItemBalanceSerializer, 'product_id', pk)
                product_item_balance_data = product_item_balance_data if product_item_balance_data else []
                if product_item_balance_data:
                    # get all location IDs in loop
                    location_ids = []
                    for data in product_item_balance_data:
                        location_id = data.get('location_id', None)
                        location_ids.append(location_id)

                    # Retrieve warehouse_locations
                    warehouse_locations_data = []
                    for id in location_ids:
                        warehouse_data = self.get_related_data( WarehouseLocations, WarehouseLocationsSerializer, 'location_id', id)
                        if len(warehouse_data) > 0:
                            warehouse_locations_data.append(warehouse_data[0])
                else:
                    warehouse_locations_data = []

                # Customizing the response data
                custom_data = {
                    "products": products_serializer.data,
                    "product_item_balance":product_item_balance_data,
                    "warehouse_locations": warehouse_locations_data
                    }
                logger.info("product and related data retrieved successfully.")
                return build_response(1, "Success", custom_data, status.HTTP_200_OK)

            except Http404:
                logger.error("product record with pk %s does not exist.", pk)
                return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
            except Exception as e:
                logger.exception(
                    "An error occurred while retrieving product with pk %s: %s", pk, str(e))
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

        # Validate products Data
        products_data = given_data.pop('products', None)  # parent_data
        if products_data:
            product_error = validate_payload_data(self, products_data, productsSerializer)
            if product_error:
                errors["products"] = product_error
        else:
            logger.error("products data is mandatory but not provided.")
            return build_response(0, "products data is mandatory", [], status.HTTP_400_BAD_REQUEST)            

        # Validate warehouse_locations Data
        warehouse_locations_data = given_data.pop('warehouse_locations', None)
        if warehouse_locations_data:
            location_error = validate_multiple_data(self, warehouse_locations_data, WarehouseLocationsSerializer,[])
            if location_error:
                errors["warehouse_locations"] = location_error

        # Validate product_item_balance Data
        product_item_balance_data = given_data.pop('product_item_balance', None)
        if product_item_balance_data:
            product_item_error = validate_multiple_data(self, product_item_balance_data, ProductItemBalanceSerializer, ['product_id'])
            if product_item_error:
                errors["product_item_balance"] = product_item_error

        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)
        logger.info("***Validation Passed***")

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """

        # Hence the data is validated , further it can be created.
        custom_data = {
            'products':{},
            'product_item_balance':[],
            'warehouse_locations':[]
            }

        # Create Products Data
        new_products_data = generic_data_creation(self, [products_data], productsSerializer)
        new_products_data = new_products_data[0]
        custom_data["products"] = new_products_data
        product_id = new_products_data.get("product_id", None)  # Fetch product_id from mew instance
        logger.info('Products - created*')

        # Create warehouse_locations Data
        if warehouse_locations_data:
            warehouse_location_data = generic_data_creation(self, warehouse_locations_data, WarehouseLocationsSerializer)
            warehouse_location_data = warehouse_location_data[0]
            custom_data["warehouse_locations"] = warehouse_location_data
            logger.info('WarehouseLocations - created*')

            # Get 'location_id' from new 'warehouse_location_data'
            if warehouse_location_data:
                location_id = warehouse_location_data.get('location_id')

        # Create product_item_balance Data
        if product_item_balance_data:
            update_fields = {'product_id':product_id, 'location_id':location_id}
            product_balance_data = generic_data_creation(self, product_item_balance_data, ProductItemBalanceSerializer, update_fields)
            custom_data["product_item_balance"] = product_balance_data
            logger.info('ProductItemBalance - created*')
        logger.info("***Creation Completed***")

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

        # Validate products Data
        products_data = given_data.pop('products', None)  # parent_data
        if products_data:
            products_data['product_id'] = pk
            order_error = validate_multiple_data(self, products_data, productsSerializer, [])
            if order_error:
                errors['products'] = order_error

        # Validate warehouse_locations Data
        warehouse_locations_data = given_data.pop('warehouse_locations', None)
        if warehouse_locations_data:
            location_error = validate_put_method_data(self, warehouse_locations_data, WarehouseLocationsSerializer, [], WarehouseLocations, current_model_pk_field='location_id')
            if location_error:
                errors['warehouse_locations'] = location_error

        # Validate product_item_balance Data
        product_item_balance_data = given_data.pop('product_item_balance', None)
        if product_item_balance_data:
            exclude_fields = ['product_id']
            # add product_id
            for data in product_item_balance_data:
                if 'product_balance_id' not in data:
                    data['product_id'] = pk

            product_item_error = validate_put_method_data(self, product_item_balance_data, ProductItemBalanceSerializer, exclude_fields, ProductItemBalance, current_model_pk_field='product_balance_id')
            if product_item_error:
                errors['product_item_balance'] = product_item_error
        

        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)
        logger.info("***Validation Passed***")

        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#
        custom_data = {
            "products":{},
            "product_item_balance":[],
            "warehouse_locations":[]
            }

        # update Products
        update_fields = []  # No need to update any fields
        product_data = update_multi_instances(self, pk, products_data, Products, productsSerializer, update_fields, main_model_related_field='product_id', current_model_pk_field='product_id')
        product_data = product_data[0] if len(product_data)==1 else product_data
        custom_data['products'] = product_data

        if warehouse_locations_data:
            # get pk for 'warehouse_locations' from previous instance
            for data in warehouse_locations_data:
                if 'location_id' in data:
                    warehouse_pk = data.get('location_id',None)

            # Update the 'warehouse_locations'
            update_fields = {}
            warehouse_location_data = update_multi_instances(self, warehouse_pk, warehouse_locations_data, WarehouseLocations, WarehouseLocationsSerializer, update_fields, main_model_related_field='location_id', current_model_pk_field='location_id')
            warehouse_location_data = warehouse_location_data if warehouse_location_data else []
            custom_data['warehouse_locations'] = warehouse_location_data

        # Update the 'product_item_balance'
        if product_item_balance_data:
            update_fields = {'product_id':pk}
            product_balance_data = update_multi_instances(self, pk, product_item_balance_data, ProductItemBalance, ProductItemBalanceSerializer, update_fields, main_model_related_field='product_id', current_model_pk_field='product_balance_id')
            product_balance_data = product_balance_data if product_balance_data else []
            custom_data['product_item_balance'] = product_balance_data

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a lead and its related assignments and interactions.
        """
        try:

            ids_list = []
            item_instances = ProductItemBalance.objects.filter(product_id=pk)
            if item_instances:
                for id in item_instances:
                    ids_list.append(id.location_id_id)
            if ids_list:
                for id in ids_list:
                    if id:
                        instance = WarehouseLocations.objects.get(location_id=id)
                        instance.delete()
                        logger.info(f"WarehouseLocation instances with pk={id} deleted successfully")

            # delete the main instance
            instance = Products.objects.get(pk=pk) # Get the Products instance
            instance.delete() # Delete the main Products instance
            logger.info(f"Products with ID {pk} deleted successfully.")

            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except Products.DoesNotExist:
            logger.warning(f"Products with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting Leads with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR) 