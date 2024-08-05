from django_filters.rest_framework import DjangoFilterBackend # type: ignore
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from config.utils_methods import *
from rest_framework import status
from django.conf import settings
from .serializers import *
from .filters import *
from .models import *
import os

# Function to get the full path
def get_full_path(request, folder_path, file_name):
    return request.build_absolute_uri(f"{settings.MEDIA_URL}{folder_path}/{file_name}")

class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        flag = request.data.get('flag')
        files = request.FILES.getlist('files')
        folder_path = request.query_params.get('fp')
        if not folder_path:
            return Response({'count': 0, 'msg': 'Folder path not provided', 'data': []}, status=status.HTTP_400_BAD_REQUEST)
        target_folder = os.path.join(settings.MEDIA_ROOT, folder_path)
        if flag == "remove_file":
            file_names = request.data.getlist('file_names')
            if len(file_names) != 0:
                for file_name in file_names:
                    file_path = os.path.join(target_folder, file_name)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    else:
                        return Response({'count': 0, 'msg': 'Files Not Exist', 'data': []}, status=status.HTTP_200_OK)
                return Response({'count': len(file_names), 'msg': 'Files Removed', 'data': file_names}, status=status.HTTP_200_OK)
            else:
                return Response({'count': 0, 'msg': 'No Files Selected', 'data': []}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)

            if len(files) != 0:
                uploaded_files = []
                for file in files:
                    file_uuid = uuid.uuid4().hex[:6]
                    file_name, file_extension = os.path.splitext(file.name.replace(' ', '_'))
                    unique_file_name = f"{file_name}_{file_uuid}{file_extension}"
                    file_path = os.path.join(target_folder, unique_file_name)
                    with open(file_path, 'wb+') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                    full_path = get_full_path(request, folder_path, unique_file_name)
                    uploaded_files.append({
                        'file_size': file.size,
                        'attachment_name': file.name,
                        'attachment_path': unique_file_name,
                        'full_path': full_path
                    })
                return Response({'count': len(files), 'msg': 'Files Uploaded Successfully', 'data': uploaded_files}, status=status.HTTP_201_CREATED)
            else:
                return Response({'count': 0, 'msg': 'No Files uploaded', 'data': []}, status=status.HTTP_400_BAD_REQUEST)

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = CountryFilters
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class StateViewSet(viewsets.ModelViewSet):
    queryset = State.objects.all()
    serializer_class = StateSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = StateFilters
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = CityFilters
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class StatusesViewset(viewsets.ModelViewSet):
    queryset = Statuses.objects.all()
    serializer_class = StatusesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class LedgerGroupsViews(viewsets.ModelViewSet):
    queryset = LedgerGroups.objects.all()
    serializer_class = LedgerGroupsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = LedgerGroupsFilters
    ordering_fields = ['name', 'created_at', 'updated_at']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class FirmStatusesViews(viewsets.ModelViewSet):
    queryset = FirmStatuses.objects.all()
    serializer_class = FirmStatusesSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = FirmStatusesFilters
    ordering_fields = ['name', 'created_at', 'updated_at']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class TerritoryViews(viewsets.ModelViewSet):
    queryset = Territory.objects.all()
    serializer_class = TerritorySerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = TerritoryFilters
    ordering_fields = ['name', 'created_at', 'updated_at']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class CustomerCategoriesViews(viewsets.ModelViewSet):
    queryset = CustomerCategories.objects.all()
    serializer_class = CustomerCategoriesSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = CustomerCategoriesFilters
    ordering_fields = ['name', 'created_at', 'updated_at']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class GstCategoriesViews(viewsets.ModelViewSet):
    queryset = GstCategories.objects.all()
    serializer_class = GstCategoriesSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = GstCategoriesFilters
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

  
class CustomerPaymentTermsViews(viewsets.ModelViewSet):
    queryset = CustomerPaymentTerms.objects.all()
    serializer_class = CustomerPaymentTermsSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = CustomerPaymentTermsFilters
    ordering_fields = ['name', 'created_at', 'updated_at']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
 

class PriceCategoriesViews(viewsets.ModelViewSet):
    queryset = PriceCategories.objects.all()
    serializer_class = PriceCategoriesSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = PriceCategoriesFilters
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class TransportersViews(viewsets.ModelViewSet):
    queryset = Transporters.objects.all()
    serializer_class = TransportersSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = TransportersFilters
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class ProductTypesViewSet(viewsets.ModelViewSet):
    queryset = ProductTypes.objects.all()
    serializer_class = ProductTypesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductTypesFilter
    ordering_fields = ['type_name']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
	
class ProductUniqueQuantityCodesViewSet(viewsets.ModelViewSet):
    queryset = ProductUniqueQuantityCodes.objects.all()
    serializer_class = ProductUniqueQuantityCodesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductUniqueQuantityCodesFilter
    ordering_fields = ['quantity_code_name']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
	
class UnitOptionsViewSet(viewsets.ModelViewSet):
    queryset = UnitOptions.objects.all()
    serializer_class = UnitOptionsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = UnitOptionsFilter
    ordering_fields = ['unit_name']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class ProductDrugTypesViewSet(viewsets.ModelViewSet):
    queryset = ProductDrugTypes.objects.all()
    serializer_class = ProductDrugTypesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductDrugTypesFilter
    ordering_fields = ['drug_type_name']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class ProductItemTypeViewSet(viewsets.ModelViewSet):
    queryset = ProductItemType.objects.all()
    serializer_class = ProductItemTypeSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductItemTypeFilter
    ordering_fields = ['item_name']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
	
class BrandSalesmanViewSet(viewsets.ModelViewSet):
    queryset = BrandSalesman.objects.all()
    serializer_class = BrandSalesmanSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = BrandSalesmanFilter
    ordering_fields = ['code','name']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
	
class ProductBrandsViewSet(viewsets.ModelViewSet):
    queryset = ProductBrands.objects.all()
    serializer_class = ProductBrandsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductBrandsFilter
    ordering_fields = ['brand_name','code','brand_salesman_id']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class PurchaseTypesViewSet(viewsets.ModelViewSet):
    queryset = PurchaseTypes.objects.all()
    serializer_class = PurchaseTypesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class ShippingCompaniesView(viewsets.ModelViewSet):
    queryset = ShippingCompanies.objects.all()
    serializer_class = ShippingCompaniesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class SaleTypesView(viewsets.ModelViewSet):
    queryset = SaleTypes.objects.all()
    serializer_class = SaleTypesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class GstTypesView(viewsets.ModelViewSet):
    queryset = GstTypes.objects.all()
    serializer_class = GstTypesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class ShippingModesView(viewsets.ModelViewSet):
    queryset = ShippingModes.objects.all()
    serializer_class = ShippingModesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class OrdersSalesmanView(viewsets.ModelViewSet):
    queryset = OrdersSalesman.objects.all()
    serializer_class = OrdersSalesmanSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    

class PaymentLinkTypesView(viewsets.ModelViewSet):
    queryset = PaymentLinkTypes.objects.all()
    serializer_class = PaymentLinkTypesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class OrderStatusesView(viewsets.ModelViewSet):
    queryset = OrderStatuses.objects.all()
    serializer_class = OrderStatusesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class OrderTypesView(viewsets.ModelViewSet):
    queryset = OrderTypes.objects.all()
    serializer_class = OrderTypesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

@api_view(['GET'])
def generate_order_number_view(request):
    """
    API endpoint to generate an order number based on the given type.

    Args:
        request (HttpRequest): The request object containing the query parameter 'type'.

    Returns:
        Response: A JSON response containing the generated order number or an error message.
    """
    order_type_prefix = request.GET.get('type')
    
    if not order_type_prefix:
        return Response({"error": "Please pass the type param"}, status=status.HTTP_400_BAD_REQUEST)
    
    order_type_prefix = order_type_prefix.upper()
    valid_prefixes = ['SO', 'SO-INV', 'SR', 'SHIP', 'PO', 'PO-INV', 'PR', 'PRD']
    
    if order_type_prefix not in valid_prefixes:
        return Response({"error": "Invalid prefix"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        order_number = generate_order_number(order_type_prefix)
        response_data = {
            'count': 1,
            'msg': None,
            'data': {'order_number': order_number}
        }
        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class TaskPrioritiesViewSet(viewsets.ModelViewSet):
    queryset = TaskPriorities.objects.all()
    serializer_class = TaskPrioritiesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
