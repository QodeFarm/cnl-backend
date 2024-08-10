from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializers import *
from config.utils_methods import *
from config.utils_variables import *
from django_filters.rest_framework import DjangoFilterBackend # type: ignore
from rest_framework.filters import OrderingFilter
from .filters import ProductGroupsFilter, ProductCategoriesFilter, ProductStockUnitsFilter, ProductGstClassificationsFilter, ProductSalesGlFilter, ProductPurchaseGlFilter, ProductsFilter, ProductItemBalanceFilter
from rest_framework.response import Response
from rest_framework import status

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
        print("Product ID from request data: ", request_product_id)

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
                print("Using picture data: ", request.data['picture'])
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
        product_id = kwargs.get('pk')
        request_product_id = request.data.get('product_id')
        
        print("Product ID from request data: ", request_product_id)

        if request_product_id == product_id:
            # Fetch the existing record from the database
            try:
                instance = self.get_object()  # Assuming get_object() fetches the instance being updated
            except self.model.DoesNotExist:
                return build_response(0, "Record not found.", [], status.HTTP_404_NOT_FOUND)

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
                    print("Using picture data: ", request.data['picture'])
                else:
                    # Handle case where 'picture' list is empty
                    return build_response(0, "'picture' list is empty.", [], status.HTTP_400_BAD_REQUEST)
            else:
                # Handle the case where 'picture' is not provided or not a list
                return build_response(0, "'picture' field is required and should be a list.", [], status.HTTP_400_BAD_REQUEST)

            # Proceed with updating the instance
            try:
                response = super().update(request, *args, **kwargs)
                
                # Format the response to include the picture data
                if isinstance(response.data, dict):
                    picture_data = response.data.get('picture')
                    if picture_data:
                        response.data['picture'] = picture_data
                return response
            
            except ValidationError as e:
                return build_response(1, "Update failed due to validation errors.", e.detail, status.HTTP_400_BAD_REQUEST)
        else:
            return build_response(0, "Product ID does not match.", [], status.HTTP_400_BAD_REQUEST)


    
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