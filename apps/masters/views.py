from apps.masters.template.payment_receipt.payment_receipt import payment_receipt_data, payment_receipt_doc
from apps.products.models import Products
from apps.purchase.models import PurchaseInvoiceOrders, PurchaseOrders, PurchaseReturnOrders
from apps.sales.models import OrderShipments, PaymentTransactions, SaleCreditNotes, SaleDebitNotes, SaleInvoiceOrders, SaleOrder, SaleReturnOrders
from config.utils_filter_methods import list_filtered_objects
from config.utils_methods import send_pdf_via_email, list_all_objects, create_instance, update_instance, build_response, path_generate
from apps.masters.template.purchase.purchase_doc import purchase_doc, purchase_data
from apps.masters.template.sales.sales_doc import sale_order_sales_invoice_doc, sale_order_sales_invoice_data, sale_return_doc, sales_invoice_doc
from apps.masters.template.table_defination import doc_heading, payment_receipt_amount_section, payment_receipt_voucher_table
from django_filters.rest_framework import DjangoFilterBackend # type: ignore
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer, Image 
from rest_framework import viewsets
from config.utils_methods import *
from rest_framework import status
from django.conf import settings
from django.http import Http404, HttpResponse
from .serializers import *
from .filters import *
from .models import *
import os

class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        flag = request.data.get('flag')
        files = request.FILES.getlist('files')
        if flag == "remove_file":
            file_names = request.data.getlist('file_names')
            if len(file_names) != 0:
                for file_name in file_names:
                    file_path = os.path.join(settings.MEDIA_ROOT, file_name)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    else:
                        return Response({'count':0, 'msg':'Files Not Exist', 'data':[]}, status=status.HTTP_200_OK)
                return Response({'count':len(file_names), 'msg':'Files Removed', 'data':[file_names]}, status=status.HTTP_200_OK) 
            else:
                return Response({'count':len(files), 'msg':'No Files Selected', 'data':[]}, status=status.HTTP_400_BAD_REQUEST)  
        else:
            media_folder = settings.MEDIA_ROOT
            if not os.path.exists(media_folder):
                os.makedirs(media_folder)                
            if len(files) != 0:
                uploaded_files = []
                for file in files:
                    file_uuid = uuid.uuid4().hex[:6]
                    file_name, file_extension = os.path.splitext(file.name.replace(' ', '_'))
                    unique_file_name = f"{file_name}_{file_uuid}{file_extension}"
                    file_path = os.path.join(settings.MEDIA_ROOT, unique_file_name)
                    with open(file_path, 'wb+') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                    uploaded_files.append({
                        'attachment_name': file.name,
                        'file_size': file.size,
                        'attachment_path':unique_file_name 
                    })
                return Response({'count': len(files), 'msg': 'Files Uploaded Successfully', 'data': uploaded_files}, status=status.HTTP_201_CREATED)
            else:
                return Response({'count':len(files), 'msg':'No Files uploaded', 'data':[]}, status=status.HTTP_400_BAD_REQUEST) 

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all().order_by('-created_at')	
    serializer_class = CountrySerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = CountryFilters
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class StateViewSet(viewsets.ModelViewSet):
    queryset = State.objects.all().order_by('-created_at')	
    serializer_class = StateSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = StateFilters
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all().order_by('-created_at')	
    serializer_class = CitySerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = CityFilters
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class StatusesViewset(viewsets.ModelViewSet):
    queryset = Statuses.objects.all().order_by('-created_at')	
    serializer_class = StatusesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = StatusesFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Statuses,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class LedgerGroupsViews(viewsets.ModelViewSet):
    queryset = LedgerGroups.objects.all().order_by('-created_at')	
    serializer_class = LedgerGroupsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = LedgerGroupsFilters
    ordering_fields = ['name', 'created_at', 'updated_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, LedgerGroups,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class FirmStatusesViews(viewsets.ModelViewSet):
    queryset = FirmStatuses.objects.all().order_by('-created_at')	
    serializer_class = FirmStatusesSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = FirmStatusesFilters
    ordering_fields = ['name', 'created_at', 'updated_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, FirmStatuses,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class TerritoryViews(viewsets.ModelViewSet):
    queryset = Territory.objects.all().order_by('-created_at')	
    serializer_class = TerritorySerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = TerritoryFilters
    ordering_fields = ['name', 'created_at', 'updated_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Territory,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class CustomerCategoriesViews(viewsets.ModelViewSet):
    queryset = CustomerCategories.objects.all().order_by('-created_at')	
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
    queryset = GstCategories.objects.all().order_by('-created_at')	
    serializer_class = GstCategoriesSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = GstCategoriesFilters
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, GstCategories,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

  
class CustomerPaymentTermsViews(viewsets.ModelViewSet):
    queryset = CustomerPaymentTerms.objects.all().order_by('-created_at')	
    serializer_class = CustomerPaymentTermsSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = CustomerPaymentTermsFilters
    ordering_fields = ['name', 'created_at', 'updated_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, CustomerPaymentTerms,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
 

class PriceCategoriesViews(viewsets.ModelViewSet):
    queryset = PriceCategories.objects.all().order_by('-created_at')	
    serializer_class = PriceCategoriesSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = PriceCategoriesFilters
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, PriceCategories,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class TransportersViews(viewsets.ModelViewSet):
    queryset = Transporters.objects.all().order_by('-created_at')	
    serializer_class = TransportersSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = TransportersFilters
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Transporters,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class ProductTypesViewSet(viewsets.ModelViewSet):
    queryset = ProductTypes.objects.all().order_by('-created_at')	
    serializer_class = ProductTypesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductTypesFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, ProductTypes,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
	
class ProductUniqueQuantityCodesViewSet(viewsets.ModelViewSet):
    queryset = ProductUniqueQuantityCodes.objects.all().order_by('-created_at')	
    serializer_class = ProductUniqueQuantityCodesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductUniqueQuantityCodesFilter
    ordering_fields = ['quantity_code_name','created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, ProductUniqueQuantityCodes,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
	
class UnitOptionsViewSet(viewsets.ModelViewSet):
    queryset = UnitOptions.objects.all().order_by('-created_at')	
    serializer_class = UnitOptionsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = UnitOptionsFilter
    ordering_fields = ['unit_name','created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, UnitOptions,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class ProductDrugTypesViewSet(viewsets.ModelViewSet):
    queryset = ProductDrugTypes.objects.all().order_by('-created_at')	
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
    queryset = ProductItemType.objects.all().order_by('-created_at')	
    serializer_class = ProductItemTypeSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductItemTypeFilter
    ordering_fields = ['item_name','created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, ProductItemType,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
	
class BrandSalesmanViewSet(viewsets.ModelViewSet):
    queryset = BrandSalesman.objects.all().order_by('-created_at')	
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
    queryset = ProductBrands.objects.all().order_by('-created_at')	
    serializer_class = ProductBrandsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductBrandsFilter
    ordering_fields = ['brand_name','code','brand_salesman_id','created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, ProductBrands,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class PurchaseTypesViewSet(viewsets.ModelViewSet):
    queryset = PurchaseTypes.objects.all().order_by('-created_at')	
    serializer_class = PurchaseTypesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = PurchaseTypesFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, PurchaseTypes,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class ShippingCompaniesView(viewsets.ModelViewSet):
    queryset = ShippingCompanies.objects.all().order_by('-created_at')	
    serializer_class = ShippingCompaniesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class SaleTypesView(viewsets.ModelViewSet):
    queryset = SaleTypes.objects.all().order_by('-created_at')	
    serializer_class = SaleTypesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = SaleTypesFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, SaleTypes,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class GstTypesView(viewsets.ModelViewSet):
    queryset = GstTypes.objects.all().order_by('-created_at')	
    serializer_class = GstTypesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = GstTypesFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, GstTypes,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class ShippingModesView(viewsets.ModelViewSet):
    queryset = ShippingModes.objects.all().order_by('-created_at')	
    serializer_class = ShippingModesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class OrdersSalesmanView(viewsets.ModelViewSet):
    queryset = OrdersSalesman.objects.all().order_by('-created_at')	
    serializer_class = OrdersSalesmanSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    

class PaymentLinkTypesView(viewsets.ModelViewSet):
    queryset = PaymentLinkTypes.objects.all().order_by('-created_at')	
    serializer_class = PaymentLinkTypesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = PaymentLinkTypesFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, PaymentLinkTypes,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class OrderStatusesView(viewsets.ModelViewSet):
    queryset = OrderStatuses.objects.all().order_by('-created_at')	
    serializer_class = OrderStatusesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = OrderStatusesFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, OrderStatuses,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class OrderTypesView(viewsets.ModelViewSet):
    queryset = OrderTypes.objects.all().order_by('-created_at')	
    serializer_class = OrderTypesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = OrderTypesFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, OrderTypes,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


#-------------------------------------pavan-start---------------------------------------------
@api_view(['GET'])
def generate_order_number_view(request):
    """
    API endpoint to fetch the next order number based on the given type.
    The sequence is only incremented when a record is successfully created.
    """
    order_type_prefix = request.GET.get('type')

    if not order_type_prefix:
        return Response({"error": "Please pass the type param"}, status=status.HTTP_400_BAD_REQUEST)

    order_type_prefix = order_type_prefix.upper()
    valid_prefixes = ['SO', 'SOO', 'SO-INV', 'SOO-INV', 'SR', 'SHIP', 'PO', 'PO-INV', 'PR', 'PRD', 'CN', 'DN']

    if order_type_prefix not in valid_prefixes:
        return Response({"error": "Invalid prefix"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Get the next order number without incrementing
        order_number = get_next_order_number(order_type_prefix)
        response_data = {
            'msg': 'Next available order number (reserved but not yet saved)',
            'data': {'order_number': order_number}
        }
        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#-------------------------------------pavan-end---------------------------------------------------

ORDER_MODEL_MAPPING = {
    'SO': (SaleOrder, 'order_no'),
    'SOO': (SaleOrder, 'order_no'),
    'SO-INV': (SaleInvoiceOrders, 'invoice_no'),
    'SOO-INV': (SaleInvoiceOrders, 'invoice_no'),
    'SR': (SaleReturnOrders, 'return_no'),
    'PO': (PurchaseOrders, 'order_no'), #PurchaseInvoiceOrders
    'PO-INV': (PurchaseInvoiceOrders, 'invoice_no'), #PurchaseInvoiceOrders
    'PR': (PurchaseReturnOrders, 'return_no'),
    'CN': (SaleCreditNotes, 'credit_note_number'),
    'DN': (SaleDebitNotes, 'debit_note_number'),
    'SHIP': (OrderShipments, 'shipping_tracking_no'),
    'PRD': (Products, 'code'),
    'PTR': (PaymentTransactions, 'payment_receipt_no'),
    # Add others as needed
}

@api_view(['GET'])
def generate_order_number_view(request):
    order_type_prefix = request.GET.get('type')

    if not order_type_prefix:
        return Response({"error": "Please pass the type param"}, status=status.HTTP_400_BAD_REQUEST)

    order_type_prefix = order_type_prefix.upper()

    if order_type_prefix not in ORDER_MODEL_MAPPING:
        return Response({"error": f"Unsupported prefix: {order_type_prefix}"}, status=status.HTTP_400_BAD_REQUEST)

    model_class, field_name = ORDER_MODEL_MAPPING[order_type_prefix]

    try:
        order_number = generate_order_number(order_type_prefix, model_class, field_name)
        return Response({
            'msg': 'Next available order number',
            'data': {'order_number': order_number}
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def get_next_order_number(order_type_prefix):
    """
    Get the next order number without incrementing the sequence.

    Args:
        order_type_prefix (str): The prefix for the order type.

    Returns:
        str: The next order number.
    """
    if order_type_prefix == "PRD":
        key = f"{order_type_prefix}"
        sequence_number = cache.get(key, 0)
        sequence_number_str = f"{sequence_number + 1:05d}"
        return f"{order_type_prefix}-{sequence_number_str}"

    # For date-based prefixes
    current_date = timezone.now()
    date_str = current_date.strftime('%y%m')
    key = f"{order_type_prefix}-{date_str}"
    sequence_number = cache.get(key, 0)
    cache.set(key, sequence_number)  # UPDATE cache
    sequence_number_str = f"{sequence_number + 1:05d}"  # +1 for the next number
    return f"{order_type_prefix}-{date_str}-{sequence_number_str}"

    
class TaskPrioritiesViewSet(viewsets.ModelViewSet):
    queryset = TaskPriorities.objects.all().order_by('-created_at')	
    serializer_class = TaskPrioritiesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = TaskPrioritiesFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, TaskPriorities,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

#===============================================PDF_creation================================
class DocumentGeneratorView(APIView):
    def post(self, request, **kwargs):
        """ Retrieves a sale order and its related data. """

        try:
            flag = request.data.get('flag')
            format_value = request.data.get('format')
            print("format_value : ", format_value)
            pk = kwargs.get('pk')
            document_type = kwargs.get('document_type')
            doc_name, file_path, relative_file_path = path_generate(document_type)
            
#   #=======================================ReportLab Code Started============================          
            if document_type == "sale_order":
                pdf_data = sale_order_sales_invoice_data(pk, document_type, format_value)
                # Override doc_header based on sale_estimate directly in the view
                
                print("pdf_data.get('sale_estimate') : ", pdf_data.get('sale_estimate'))
                if pdf_data.get('sale_estimate') == 'Yes':
                    pdf_data['doc_header'] = "SALES QUOTATION"
                    
                print(f"Final confirmed doc_header: {pdf_data['doc_header']}") 

                elements, doc = doc_heading(file_path, pdf_data['doc_header'], 'BILL OF SUPPLY')
                sale_order_sales_invoice_doc(
                                   elements, doc, 
                                   pdf_data['cust_bill_dtl'], pdf_data['number_lbl'], pdf_data['number_value'], pdf_data['date_lbl'], pdf_data['date_value'],
                                   pdf_data['customer_name'], pdf_data['billing_address'], pdf_data['phone'], pdf_data['city'], 
                                   pdf_data['product_data'], 
                                   pdf_data['total_qty'], pdf_data['final_total'], pdf_data['total_amt'], pdf_data['total_cgst'], pdf_data['total_sgst'], pdf_data['total_igst'], 
                                   pdf_data['bill_amount_in_words'], pdf_data['itemstotal'], pdf_data['total_disc_amt'], pdf_data['finalDiscount'], pdf_data['round_0ff'], pdf_data['cess_amount'], 
                                   pdf_data['party_old_balance'], pdf_data['net_lbl'], pdf_data['net_value'], pdf_data['tax_type']
                                )
                
            if document_type == "sale_invoice":
                pdf_data = sale_order_sales_invoice_data(pk, document_type, format_value)  
                elements, doc = doc_heading(file_path, pdf_data['doc_header'], '')
                sales_invoice_doc(
                                   elements, doc, 
                                   pdf_data['company_logo'], pdf_data['company_name'], pdf_data['company_gst'], pdf_data['company_address'], pdf_data['company_phone'], pdf_data['company_email'],
                                   pdf_data['bank_name'], pdf_data['bank_acno'], pdf_data['bank_ifsc'], pdf_data['bank_branch'],
                                   pdf_data['number_lbl'], pdf_data['number_value'], pdf_data['date_lbl'], pdf_data['date_value'],
                                   pdf_data['customer_name'], pdf_data['city'], pdf_data['country'], pdf_data['phone'], pdf_data['dest'], pdf_data['shipping_address'],
                                   pdf_data['billing_address'],
                                   pdf_data['product_data'],
                                   pdf_data['total_qty'], pdf_data['final_total'], pdf_data['total_amt'], pdf_data['total_cgst'], pdf_data['total_sgst'], pdf_data['total_igst'], 
                                   pdf_data['bill_amount_in_words'], pdf_data['itemstotal'], pdf_data['total_disc_amt'],pdf_data['finalDiscount'], pdf_data['cess_amount'], pdf_data['round_0ff'], #finalDiscount
                                   pdf_data['party_old_balance'], pdf_data['net_lbl'], pdf_data['net_value'], pdf_data['tax_type']
                                )
            # Add this in the DocumentGeneratorView class after the sale_invoice condition
            if document_type == "sale_return":
                pdf_data = sale_order_sales_invoice_data(pk, document_type, format_value)
                elements, doc = doc_heading(file_path, "BILL OF SUPPLY", '')  # Modified header for returns
                sale_return_doc(
                    elements, doc, 
                    pdf_data['company_name'], pdf_data['company_address'], pdf_data['company_phone'],
                    pdf_data['cust_bill_dtl'], pdf_data['number_lbl'], pdf_data['final_invoice'],
                    pdf_data['date_lbl'], pdf_data['final_invoiceDate'],
                    pdf_data['customer_name'], pdf_data['billing_address'], pdf_data['phone'],
                    pdf_data['city'],
                    pdf_data['product_data'],
                    pdf_data['total_qty'], pdf_data['total_amt'], pdf_data['cess_amount'], pdf_data['total_cgst'], pdf_data['total_sgst'], pdf_data['total_igst'], pdf_data['itemstotal'],
                    pdf_data['finalDiscount'], pdf_data['bill_amount_in_words'],
                    pdf_data['round_0ff'],
                    pdf_data['party_old_balance'], pdf_data['net_lbl'], pdf_data['net_value'], pdf_data['tax_type']
                )
            if document_type == "purchase_order" or document_type == "purchase_return":
                pdf_data = purchase_data(pk, document_type)
                # sub_header = 'Receipt Voucher'
                elements, doc = doc_heading(file_path, "PURCHASE BILL", '')
                purchase_doc(elements, doc, 
                                   pdf_data['comp_name'], pdf_data['comp_address'], pdf_data['comp_phone'],
                                   pdf_data['cust_bill_dtl'], pdf_data['number_lbl'], pdf_data['number_value'], pdf_data['date_lbl'], pdf_data['date_value'],
                                   pdf_data['customer_name'], pdf_data['v_billing_address'], pdf_data['v_shipping_address_lbl'],  pdf_data['v_shipping_address'],
                                   pdf_data['product_data'],
                                   pdf_data['total_qty'], pdf_data['total_amt'],pdf_data['total_disc_amt'], pdf_data['total_txbl_amt'], pdf_data['total_sub_amt'], pdf_data['total_bill_amt'],
                                   pdf_data['destination'], pdf_data['tax_type'], pdf_data['shipping_mode_name'], pdf_data['port_of_landing'], pdf_data['port_of_discharge'],
                                   pdf_data['comp_name'],
                                   pdf_data['shipping_company_name'], pdf_data['shipping_tracking_no'], pdf_data['vehicle_vessel'],  pdf_data['no_of_packets'], pdf_data['shipping_date'], pdf_data['shipping_charges'], pdf_data['weight'],
                                   pdf_data['comp_address'], pdf_data['comp_phone'], pdf_data['comp_email']
                                )
                
            elif document_type == "payment_receipt":
                pdf_data = payment_receipt_data(pk, document_type)
                print("pdf_data--->>>", pdf_data)
                sub_header = 'Receipt Voucher'
                # Use same doc_heading pattern as sale order
                elements, doc = doc_heading(file_path, pdf_data['doc_header'], sub_header)
                
                # Generate payment receipt with same structure as sale order
                payment_receipt_doc(
                    elements, doc,
                    pdf_data['company_name'], pdf_data['company_address'], pdf_data['company_phone'],
                    pdf_data['cust_bill_dtl'], 
                    pdf_data['number_lbl'], 
                    pdf_data['invoice_no'], 
                    pdf_data['date_lbl'], 
                    pdf_data['receipt_date'],
                    pdf_data['customer_name'], 
                    pdf_data['billing_address'], 
                    pdf_data['phone'],
                    pdf_data['email'],
                    [{
                        'invoice_no': pdf_data['invoice_no'],
                        'invoice_date': pdf_data['invoice_date'],
                        'payment_method': pdf_data['payment_method'],
                        'cheque_no': pdf_data['cheque_no'],
                        'amount': pdf_data['amount']
                    }],  # Pass as list to match sale order's product_data structure
                    pdf_data['amount'],
                    pdf_data['outstanding'],
                    pdf_data['total'],
                    pdf_data['amount_in_words'],
                    pdf_data['receipt_no'],
                    # pdf_data['net_lbl'],
                    # pdf_data['amount']  # Using amount as net_value
                )
                
            if flag == 'email':
                pdf_send_response = send_pdf_via_email(pdf_data['email'], relative_file_path, document_type)
                
            if flag == 'print':
                # Add any print-specific modifications to your PDF here
                response = HttpResponse(pdf_data, content_type='application/pdf')
                response['Content-Disposition'] = 'inline; filename="document_to_print.pdf"'
                return response
            
            elif flag == 'preview':
                # Return the PDF file directly for preview
                with open(file_path, 'rb') as pdf_file:
                    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                    response['Content-Disposition'] = f'inline; filename="{doc_name}.pdf"'
                    return response
                
            # elif flag == 'whatsapp':
            #     pdf_send_response = send_whatsapp_message_via_wati(phone, cdn_path)

        except Http404:
            logger.error("pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("An error occurred while retrieving pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

        return build_response(1, pdf_send_response , [], status.HTTP_200_OK)

class ReturnOptionsViewset(viewsets.ModelViewSet):
    queryset = ReturnOptions.objects.all().order_by('-created_at')	
    serializer_class = ReturnOptionsSerializers

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class FieldTypeViewSet(viewsets.ModelViewSet):
    queryset = FieldType.objects.all().order_by('-created_at')	
    serializer_class = FieldTypeSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)    
    
class EntitiesViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on Entity model.
    """
    queryset = Entities.objects.all().order_by('-created_at')	
    serializer_class = EntitiesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class UserGroupsViewset(viewsets.ModelViewSet):
    queryset = UserGroups.objects.all().order_by('-created_at')	
    serializer_class = UserGroupsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = UserGroupsFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, UserGroups,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class UserGroupMembersViewset(viewsets.ModelViewSet):
    queryset = UserGroupMembers.objects.all().order_by('-created_at')	
    serializer_class = UserGroupMembersSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = UserGroupMembersFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, UserGroupMembers,*args, **kwargs)

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class PackageUnitViewSet(viewsets.ModelViewSet):
    queryset = PackageUnit.objects.all().order_by()
    serializer_class = PackageUnitSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = PackageUnitFilter
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, PackageUnit,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)    


class GPackageUnitViewSet(viewsets.ModelViewSet):
    queryset = GPackageUnit.objects.all().order_by()
    serializer_class = GPackageUnitSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = GPackageUnitFilter
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, GPackageUnit,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class FlowStatusViews(viewsets.ModelViewSet):
    queryset = FlowStatus.objects.all().order_by('-created_at')	
    serializer_class = FlowStatusSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = FlowStatusFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        response = create_instance(self, request, *args, **kwargs)
        return response

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

