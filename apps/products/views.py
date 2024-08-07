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
        # Check if profile_picture_url is in data and it's a list
        if 'picture' in request.data and isinstance(request.data['picture'], list):
            # Assuming the first item in the list contains the attachment data
            attachment_data_list = request.data['picture']
            if attachment_data_list:
                first_attachment = attachment_data_list[0]
                request.data['picture'] = first_attachment.get('attachment_path', None)
        
        try:
            # Call the superclass's create method
            response = super().create(request, *args, **kwargs)
            result = Response({
                'count': '1',
                'msg': 'Success! Your user account has been created. Please check your mailbox',
                'data': [response.data]
            }, status=status.HTTP_201_CREATED)
        
        except ValidationError as e:
            result = Response({
                'count': '1',
                'msg': 'User creation failed due to validation errors.',
                'data': [e.detail]
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return result

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