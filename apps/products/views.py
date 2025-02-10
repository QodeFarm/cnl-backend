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
from config.utils_filter_methods import filter_response
from config.utils_variables import *
from config.utils_methods import *
from apps.inventory.serializers import WarehouseLocationsSerializer
from apps.inventory.models import WarehouseLocations
from .serializers import *
from .models import *
from .filters import ColorFilter, ProductGroupsFilter, ProductCategoriesFilter, ProductStockUnitsFilter, ProductGstClassificationsFilter, ProductSalesGlFilter, ProductPurchaseGlFilter, ProductsFilter, ProductItemBalanceFilter, ProductVariationFilter, SizeFilter

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)

# Create your views here.
class ProductGroupsViewSet(viewsets.ModelViewSet):
    queryset = ProductGroups.objects.all().order_by('-created_at')	
    serializer_class = ProductGroupsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductGroupsFilter
    ordering_fields = ['group_name','created_at']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class ProductCategoriesViewSet(viewsets.ModelViewSet):
    queryset = ProductCategories.objects.all().order_by('-created_at')	
    serializer_class = ProductCategoriesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductCategoriesFilter
    ordering_fields = ['category_name','code','created_at']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class ProductStockUnitsViewSet(viewsets.ModelViewSet):
    queryset = ProductStockUnits.objects.all().order_by('-created_at')	
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
    queryset = ProductGstClassifications.objects.all().order_by('-created_at')	
    serializer_class = ProductGstClassificationsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductGstClassificationsFilter
    ordering_fields = ['type','code','hsn_or_sac_code','created_at']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class ProductSalesGlViewSet(viewsets.ModelViewSet):
    queryset = ProductSalesGl.objects.all().order_by('-created_at')	
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
    queryset = ProductPurchaseGl.objects.all().order_by('-created_at')	
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
    queryset = Products.objects.all().order_by('-created_at')
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
    queryset = ProductItemBalance.objects.all().order_by('-created_at')	
    serializer_class = ProductItemBalanceSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductItemBalanceFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class SizeViewSet(viewsets.ModelViewSet):
    queryset = Size.objects.all().order_by('-created_at')	
    serializer_class = SizeSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = SizeFilter
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)    

class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all().order_by('-created_at')
    serializer_class = ColorSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ColorFilter
    ordering_fields = []


    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)    

class ProductVariationViewSet(viewsets.ModelViewSet):
    queryset = ProductVariation.objects.all()
    serializer_class = ProductVariationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ProductVariationFilter
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
    def validate_sku(self,data):
        # Extract the list of SKUs from the product variations
        skus = [variation['sku'] for variation in data]

        # Find duplicates by comparing the length of the set and the list
        if len(skus) != len(set(skus)):
            logger.error('Error: Duplicate SKU found in product variations.')
            return False
        else:
            return True    

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
            summary = request.query_params.get('summary', 'false').lower() == 'true' + '&' 
            if summary:
                product = Products.objects.all().order_by('-created_at')	
                data = ProductOptionsSerializer.get_product_summary(product)
                return build_response(len(data), "Success", data, status.HTTP_200_OK)
            else:
                logger.info("Retrieving all products")
                queryset = Products.objects.all().order_by('-created_at')	

                page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
                limit = int(request.query_params.get('limit', 10)) 
                total_count = Products.objects.count()

                # Apply filters manuallys
                if request.query_params:
                    filterset = ProductsFilter(request.GET, queryset=queryset)
                    if filterset.is_valid():
                        queryset = filterset.qs 

                serializer = ProductOptionsSerializer(queryset, many=True)
                logger.info("product data retrieved successfully.")
                # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
                return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
            """
            Retrieves a products and its related data (ProductVariation)
            """
            try:
                pk = kwargs.get('pk')
                if not pk:
                    logger.error("Primary key not provided in request.")
                    return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

                # Retrieve the Products instance
                product = get_object_or_404(Products, pk=pk)
                products_serializer = productsSerializer(product)

                # Retrieve 'product_variations'
                product_variations_data = get_related_data(ProductVariation, ProductVariationSerializer, 'product_id', pk)

                # Retrieve 'product_item_balance'
                product_balance_data = get_related_data(ProductItemBalance, ProductItemBalanceSerializer, 'product_id', pk)

                # Customizing the response data
                custom_data = {
                    "products": products_serializer.data,
                    "product_variations":product_variations_data if product_variations_data else [],
                    "product_item_balance":product_balance_data if product_balance_data else [],
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

    # Handling POST requests for creating
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
            # Check if 'picture' exists in products_data and is a list
            picture_data = products_data.get('picture', None)
            if picture_data:
                if not isinstance(picture_data, list):
                    return build_response(0, "'picture' field in products_data must be a list.", [], status.HTTP_400_BAD_REQUEST)

                for attachment in picture_data:
                    if not all(key in attachment for key in ['uid', 'name', 'attachment_name', 'file_size', 'attachment_path']):
                        return build_response(0, "Missing required fields in some picture data.", [], status.HTTP_400_BAD_REQUEST)
            product_error = validate_payload_data(self, products_data, productsSerializer)
            if product_error:
                errors["products"] = product_error
        else:
            logger.error("products data is mandatory but not provided.")
            return build_response(0, "products data is mandatory", [], status.HTTP_400_BAD_REQUEST)

        # Validate 'product_variations' data
        product_variations_data = given_data.pop('product_variations', None)
        if product_variations_data:
            try:
                mark = self.validate_sku(product_variations_data)
                if mark==True:
                    variations_error = validate_multiple_data(self, product_variations_data, ProductVariationSerializer, ['product_id'])
                    if variations_error:
                        errors["product_variations"] = variations_error
                else:
                    return  build_response(0, "ValidationError", [], status.HTTP_400_BAD_REQUEST,errors='Check Duplicate SKU is entered.')
            except KeyError:
                product_variations_data = None
        # Validate product_item_balance Data
        product_item_balance_data = given_data.pop('product_item_balance', None)
        if product_item_balance_data:
            product_item_error = validate_multiple_data(self, product_item_balance_data, ProductItemBalanceSerializer, ['product_id'])
            if product_item_error:
                errors["product_item_balance"] = product_item_error

        if errors:
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)
        logger.info("*** (POST) Validation Passed***")

        # ---------------------- D A T A   C R E A T I O N ---------------------------- #
        """
        After the data is validated, this validated data is created as new instances.
        """

        # Hence the data is validated , further it can be created.
        custom_data = {
            'products':{},
            'product_variations':[],
            'product_item_balance':[]
            }

        # Create Products Data
        new_products_data = generic_data_creation(self, [products_data], productsSerializer)
        new_products_data = new_products_data[0]
        custom_data["products"] = new_products_data
        product_id = new_products_data.get("product_id", None)  # Fetch product_id from mew instance
        logger.info('Products - created*')

        # Create 'product_variations' data
        if product_variations_data:
            variations_data = generic_data_creation(self, product_variations_data, ProductVariationSerializer, {'product_id':product_id})
            custom_data["product_variations"] = variations_data
            logger.info('ProductVariation - created*')

        # Create 'product_item_balance' data
        if product_item_balance_data:
            update_fields = {'product_id':product_id}
            product_balance_data = generic_data_creation(self, product_item_balance_data, ProductItemBalanceSerializer, update_fields)
            custom_data["product_item_balance"] = product_balance_data
            logger.info('ProductItemBalance - created*') 

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

        # Validate 'products' Data
        products_data = given_data.pop('products', None)  # parent_data
        if products_data:
            products_data['product_id'] = pk
            products_error = validate_multiple_data(self, products_data, productsSerializer, [])
            if products_error:
                errors['products'] = products_error

        # Validate 'product_variations' data
        product_variations_data = given_data.pop('product_variations', None)
        if product_variations_data:
            mark = self.validate_sku(product_variations_data)
            if mark==True:
                variations_error = validate_multiple_data(self, product_variations_data, ProductVariationSerializer, ['product_id','sku'])
                if variations_error:
                    errors["product_variations"] = variations_error
            else:
                return  build_response(0, "ValidationError", [], status.HTTP_400_BAD_REQUEST,errors='Check Duplicate SKU is entered.')            
            variations_error = validate_multiple_data(self, product_variations_data, ProductVariationSerializer,['sku','product_id'])
            if variations_error:
                errors["product_variations"] = variations_error

        # Validate 'product_item_balance' Data
        product_balance_data = given_data.pop('product_item_balance', None)
        if product_balance_data:
            bal_error = validate_multiple_data(self, product_balance_data, ProductItemBalanceSerializer, [])
            if products_error:
                errors['product_item_balance'] = bal_error

        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#
        custom_data = {
            "products":{},
            "product_variations":[],
            "product_item_balance":[]
            }

        try:
            # update 'Products'
            product_data = update_multi_instances(self, pk, products_data, Products, productsSerializer, [], main_model_related_field='product_id', current_model_pk_field='product_id')
            product_data = product_data[0] if len(product_data)==1 else product_data
            custom_data['products'] = product_data

            update_fields = {'product_id':pk}

            # update 'product_variations'
            variations_data = update_multi_instances(self, pk, product_variations_data, ProductVariation, ProductVariationSerializer, update_fields, main_model_related_field='product_id', current_model_pk_field='product_variation_id')
            custom_data['product_variations'] = variations_data

            # update 'product_item_balance'
            item_bal_data = update_multi_instances(self, pk, product_balance_data, ProductItemBalance, ProductItemBalanceSerializer, update_fields, main_model_related_field='product_id', current_model_pk_field='product_item_balance_id')
            custom_data['product_item_balance'] = item_bal_data

        except Exception as e:
            logger.error(f'Error: {e}')
            return build_response(0, "An error occurred while updating the data. Please try again.", [], status.HTTP_400_BAD_REQUEST)
        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a lead and its related assignments and interactions.
        """
        try:
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
            return build_response(0, f"Record deletion failed due to an error : {e}", [], status.HTTP_500_INTERNAL_SERVER_ERROR)