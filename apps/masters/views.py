from apps.company.models import Companies
from apps.customer.models import Customer
from apps.documents.models import DocumentsGeneration
from apps.masters.template.print_config_defaults import (
    COLUMN_DEFINITIONS_BY_DOC_TYPE, DEFAULT_SECTION_CONFIG, DEFAULT_STYLE_CONFIG,
    DEFAULT_COPY_CONFIG, DEFAULT_CUSTOM_TEXT, PAPER_SIZES,
    get_default_template_config, resolve_print_config,
)
from apps.finance.models import JournalEntry, JournalVoucher
from apps.masters.template.account_ledger.account_ledger import ledger_document_data, ledger_document_doc
from apps.masters.template.billpayment_receipt.billpayment_receipt import billpayment_receipt_data, billpayment_receipt_doc
from apps.masters.template.payment_receipt.payment_receipt import payment_receipt_data, payment_receipt_doc
from apps.production.models import MaterialIssue, MaterialReceived
from apps.products.models import Products
from apps.purchase.models import BillPaymentTransactions, PurchaseInvoiceOrders, PurchaseOrders, PurchaseReturnOrders
from apps.sales.models import DeliveryChallans, OrderShipments, PaymentTransactions, SaleCreditNotes, SaleDebitNotes, SaleInvoiceOrders, SaleOrder, SaleReturnOrders
from apps.vendor.models import Vendor
from config.utils_filter_methods import list_filtered_objects
from config.utils_methods import send_pdf_via_email, list_all_objects, create_instance, update_instance, build_response, path_generate, soft_delete
from apps.masters.template.purchase.purchase_doc import purchase_doc, purchase_data
from apps.masters.template.sales.sales_doc import sale_order_sales_invoice_doc, sale_order_sales_invoice_data, sale_return_doc, sales_invoice_doc, delivery_challan_data, delivery_challan_doc
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
from django.db import transaction
from django.http import Http404, HttpResponse
from .serializers import *
from .filters import *
from .models import *
import os
import uuid

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


class ProductionFloorViewSet(viewsets.ModelViewSet):
    queryset = ProductionFloor.objects.all().order_by('-created_at')	
    serializer_class = ProductionFloorSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductionFloorFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Production Floor"
    log_pk_field = "production_floor_id"
    log_display_field = "code" 

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, ProductionFloor,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = CountrySerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = CountryFilters
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Country"
    log_pk_field = "country_id"
    log_display_field = "country_name" 

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

class StateViewSet(viewsets.ModelViewSet):
    queryset = State.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = StateSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = StateFilters
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "State"
    log_pk_field = "state_id"
    log_display_field = "state_name" 

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = CitySerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = CityFilters
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "City"
    log_pk_field = "city_id"
    log_display_field = "city_name" 

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)


class StatusesViewset(viewsets.ModelViewSet):
    queryset = Statuses.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = StatusesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = StatusesFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Statuses"
    log_pk_field = "status_id"
    log_display_field = "status_name" 

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Statuses,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

class LedgerGroupsViews(viewsets.ModelViewSet):
    queryset = LedgerGroups.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = LedgerGroupsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = LedgerGroupsFilters
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    #log actions
    log_actions = True
    log_module_name = "Ledger Groups"
    log_pk_field = "ledger_group_id"
    log_display_field = "code" 

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, LedgerGroups,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

class FirmStatusesViews(viewsets.ModelViewSet):
    queryset = FirmStatuses.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = FirmStatusesSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = FirmStatusesFilters
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    #log actions
    log_actions = True
    log_module_name = "Firm Status"
    log_pk_field = "firm_status_id"
    log_display_field = "name" 

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, FirmStatuses,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
    
class TerritoryViews(viewsets.ModelViewSet):
    queryset = Territory.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = TerritorySerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = TerritoryFilters
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    #log actions
    log_actions = True
    log_module_name = "Territory"
    log_pk_field = "territory_id"
    log_display_field = "name" 

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Territory,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
    
class CustomerCategoriesViews(viewsets.ModelViewSet):
    queryset = CustomerCategories.objects.all().order_by('is_deleted', '-created_at')	 #optional : CustomerCategories.objects.filter(is_deleted=False).order_by('is_deleted', '-created_at')
    serializer_class = CustomerCategoriesSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = CustomerCategoriesFilters
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    #log actions
    log_actions = True
    log_module_name = "Customer Categories"
    log_pk_field = "customer_category_id"
    log_display_field = "code"

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

class GstCategoriesViews(viewsets.ModelViewSet):
    queryset = GstCategories.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = GstCategoriesSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = GstCategoriesFilters
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    #log actions
    log_actions = True
    log_module_name = "GST Categories"
    log_pk_field = "gst_category_id"
    log_display_field = "name"
    
    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, GstCategories,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
  
class CustomerPaymentTermsViews(viewsets.ModelViewSet):
    queryset = CustomerPaymentTerms.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = CustomerPaymentTermsSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = CustomerPaymentTermsFilters
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    #log actions
    log_actions = True
    log_module_name = "Customer PaymentTerms"
    log_pk_field = "payment_term_id"
    log_display_field = "code"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, CustomerPaymentTerms,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
 
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

class PriceCategoriesViews(viewsets.ModelViewSet):
    queryset = PriceCategories.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = PriceCategoriesSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = PriceCategoriesFilters
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    #log actions
    log_actions = True
    log_module_name = "Price Categories"
    log_pk_field = "price_category_id"
    log_display_field = "code"
    
    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, PriceCategories,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
    
class TransportersViews(viewsets.ModelViewSet):
    queryset = Transporters.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = TransportersSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = TransportersFilters
    ordering_fields = ['name', 'created_at', 'updated_at']
    
    
    #log actions
    log_actions = True
    log_module_name = "Transporters"
    log_pk_field = "transporter_id"
    log_display_field = "code"
    
    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Transporters,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

class ProductTypesViewSet(viewsets.ModelViewSet):
    queryset = ProductTypes.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = ProductTypesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductTypesFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Product Types"
    log_pk_field = "type_id"
    log_display_field = "type_name"

    def list(self, request, *args, **kwargs):
        # Check if there's a mode_type filter applied
        mode_type = request.query_params.get('mode_type', None)
        
        # If mode_type is specified, filter queryset by it
        if mode_type:
            queryset = self.filter_queryset(
                ProductTypes.objects.filter(
                    models.Q(mode_type=mode_type) | models.Q(mode_type='All')
                ).order_by('is_deleted', '-created_at')
            )
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        
        # Otherwise use the default filtering
        return list_filtered_objects(self, request, ProductTypes, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
 
 
class ProductUniqueQuantityCodesViewSet(viewsets.ModelViewSet):
    queryset = ProductUniqueQuantityCodes.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = ProductUniqueQuantityCodesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductUniqueQuantityCodesFilter
    ordering_fields = ['quantity_code_name','created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Product Unique Quantity Codes"
    log_pk_field = "quantity_code_id"
    log_display_field = "quantity_code_name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, ProductUniqueQuantityCodes,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
	
class UnitOptionsViewSet(viewsets.ModelViewSet):
    queryset = UnitOptions.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = UnitOptionsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = UnitOptionsFilter
    ordering_fields = ['unit_name','created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Unit Options"
    log_pk_field = "unit_options_id"
    log_display_field = "unit_name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, UnitOptions,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

class ProductDrugTypesViewSet(viewsets.ModelViewSet):
    queryset = ProductDrugTypes.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = ProductDrugTypesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductDrugTypesFilter
    ordering_fields = ['drug_type_name']
    
    #log actions
    log_actions = True
    log_module_name = "Product Drug Types"
    log_pk_field = "drug_type_id"
    log_display_field = "drug_type_name"

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

class ProductItemTypeViewSet(viewsets.ModelViewSet):
    queryset = ProductItemType.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = ProductItemTypeSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductItemTypeFilter
    ordering_fields = ['item_name','created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Product Item Types"
    log_pk_field = "item_type_id"
    log_display_field = "item_name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, ProductItemType,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
	
class BrandSalesmanViewSet(viewsets.ModelViewSet):
    queryset = BrandSalesman.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = BrandSalesmanSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = BrandSalesmanFilter
    ordering_fields = ['code','name']
    
    #log actions
    log_actions = True
    log_module_name = "Brand Salesman"
    log_pk_field = "brand_salesman_id"
    log_display_field = "code"

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
	
class ProductBrandsViewSet(viewsets.ModelViewSet):
    queryset = ProductBrands.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = ProductBrandsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ProductBrandsFilter
    ordering_fields = ['brand_name','code','brand_salesman_id','created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Product Brands"
    log_pk_field = "brand_id"
    log_display_field = "brand_name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, ProductBrands,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

class PurchaseTypesViewSet(viewsets.ModelViewSet):
    queryset = PurchaseTypes.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = PurchaseTypesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = PurchaseTypesFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Purchase Types"
    log_pk_field = "purchase_type_id"
    log_display_field = "name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, PurchaseTypes,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

class ShippingCompaniesView(viewsets.ModelViewSet):
    queryset = ShippingCompanies.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = ShippingCompaniesSerializer
    
    #log actions
    log_actions = True
    log_module_name = "Shipping Companies"
    log_pk_field = "shipping_company_id"
    log_display_field = "code"

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)


class SaleTypesView(viewsets.ModelViewSet):
    queryset = SaleTypes.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = SaleTypesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = SaleTypesFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Sale Types"
    log_pk_field = "sale_type_id"
    log_display_field = "name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, SaleTypes,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

class GstTypesView(viewsets.ModelViewSet):
    queryset = GstTypes.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = GstTypesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = GstTypesFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "GST Types"
    log_pk_field = "gst_type_id"
    log_display_field = "name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, GstTypes,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

class ShippingModesView(viewsets.ModelViewSet):
    queryset = ShippingModes.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = ShippingModesSerializer
    
    #log actions
    log_actions = True
    log_module_name = "Shipping Modes"
    log_pk_field = "shipping_mode_id"
    log_display_field = "name"

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
    
class OrdersSalesmanView(viewsets.ModelViewSet):
    queryset = OrdersSalesman.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = OrdersSalesmanSerializer
    
    #log actions
    log_actions = True
    log_module_name = "Orders Salesman"
    log_pk_field = "order_salesman_id"
    log_display_field = "code"

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
    

class PaymentLinkTypesView(viewsets.ModelViewSet):
    queryset = PaymentLinkTypes.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = PaymentLinkTypesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = PaymentLinkTypesFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Payment Link Types"
    log_pk_field = "payment_link_type_id"
    log_display_field = "name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, PaymentLinkTypes,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
    
class OrderStatusesView(viewsets.ModelViewSet):
    queryset = OrderStatuses.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = OrderStatusesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = OrderStatusesFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Order Statuses"
    log_pk_field = "order_status_id"
    log_display_field = "status_name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, OrderStatuses,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
    
class OrderTypesView(viewsets.ModelViewSet):
    queryset = OrderTypes.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = OrderTypesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = OrderTypesFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Order Types"
    log_pk_field = "order_type_id"
    log_display_field = "name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, OrderTypes,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)


#-------------------------------------pavan-start---------------------------------------------
# @api_view(['GET'])
# def generate_order_number_view(request):
#     """
#     API endpoint to fetch the next order number based on the given type.
#     The sequence is only incremented when a record is successfully created.
#     """
#     order_type_prefix = request.GET.get('type')

#     if not order_type_prefix:
#         return Response({"error": "Please pass the type param"}, status=status.HTTP_400_BAD_REQUEST)

#     order_type_prefix = order_type_prefix.upper()
#     valid_prefixes = ['SO', 'SOO', 'SO-INV', 'SOO-INV', 'SR', 'SHIP', 'PO', 'PO-INV', 'PR', 'PRD', 'CN', 'DN']

#     if order_type_prefix not in valid_prefixes:
#         return Response({"error": "Invalid prefix"}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         # Get the next order number without incrementing
#         order_number = get_next_order_number(order_type_prefix)
#         response_data = {
#             'msg': 'Next available order number (reserved but not yet saved)',
#             'data': {'order_number': order_number}
#         }
#         return Response(response_data, status=status.HTTP_200_OK)
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    'DC': (DeliveryChallans, 'challan_no'),
    'SHIP': (OrderShipments, 'shipping_tracking_no'),
    'PRD': (Products, 'code'),
    'CUST': (Customer, 'code'),
    'VEND': (Vendor, 'code'),
    'PTR': (PaymentTransactions, 'payment_receipt_no'),
    'BPR': (BillPaymentTransactions, 'payment_receipt_no'),
    'MI' :(MaterialIssue, 'issue_no'),
    'MR' :(MaterialReceived, 'receipt_no'),
    'JE': (JournalEntry, 'voucher_no'),
    'JV': (JournalVoucher, 'voucher_no'),  # Journal Voucher
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


@api_view(['GET'])
def generate_ledger_code_view(request):
    """
    API endpoint to get the next available code for LedgerGroups or LedgerAccounts.
   
    """
    code_type = request.GET.get('type', '').lower()
    parent_id = request.GET.get('parent_id')
    
    if not code_type:
        return Response({
            "error": "Please pass the 'type' parameter ('group' or 'account')"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if code_type not in ['group', 'account']:
        return Response({
            "error": "Invalid type. Must be 'group' or 'account'"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        if code_type == 'group':
            from config.utils_methods import generate_ledger_group_code
            
            # Convert parent_id to UUID or None
            parent_uuid = None
            if parent_id:
                try:
                    parent_uuid = uuid.UUID(parent_id)
                except ValueError:
                    return Response({
                        "error": "Invalid parent_id format"
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            next_code = generate_ledger_group_code(parent_group_id=parent_uuid)
            
            return Response({
                'msg': 'Next available ledger group code',
                'data': {
                    'code': next_code,
                    'type': 'group',
                    'parent_id': parent_id
                }
            }, status=status.HTTP_200_OK)
            
        elif code_type == 'account':
            from config.utils_methods import generate_ledger_account_code
            
            if not parent_id:
                return Response({
                    "error": "parent_id (ledger_group_id) is required for accounts"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                parent_uuid = uuid.UUID(parent_id)
            except ValueError:
                return Response({
                    "error": "Invalid parent_id format"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            next_code = generate_ledger_account_code(ledger_group_id=parent_uuid)
            
            return Response({
                'msg': 'Next available ledger account code',
                'data': {
                    'code': next_code,
                    'type': 'account',
                    'ledger_group_id': parent_id
                }
            }, status=status.HTTP_200_OK)
            
    except ValueError as e:
        return Response({
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            "error": f"An error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_next_order_number(order_type_prefix):
    """
    Get the next order number without incrementing the sequence.

    Args:
        order_type_prefix (str): The prefix for the order type.

    Returns:
        str: The next order number.
    """
    if order_type_prefix == "CUST":
        key = f"{order_type_prefix}"
        sequence_number = cache.get(key, 0)
        sequence_number_str = f"{sequence_number + 1:05d}"
        return f"{order_type_prefix}-{sequence_number_str}"
    
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
    queryset = TaskPriorities.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = TaskPrioritiesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = TaskPrioritiesFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Task Priority"
    log_pk_field = "priority_id"
    log_display_field = "priority_name" 

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, TaskPriorities,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

#===============================================PDF_creation================================
class DocumentGeneratorView(APIView):
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]

    def _load_print_config(self, document_type):
        """
        Load the default DocumentPrintTemplate for the first company and given
        document_type, and resolve it into a config dict ready for PDF builders.
        Falls back to system defaults if no template is configured.
        """
        try:
            company = Companies.objects.first()
            template_obj = None
            if company:
                template_obj = DocumentPrintTemplate.objects.filter(
                    company=company,
                    document_type=document_type,
                    is_default=True,
                    is_deleted=False,
                    is_active=True,
                ).first()
            return resolve_print_config(template_obj, document_type)
        except Exception as e:
            logger.error("Failed to load print config for '%s': %s", document_type, str(e))
            return get_default_template_config(document_type)

    def post(self, request, **kwargs):
        """ Retrieves a sale order and its related data. """

        try:
            flag = request.data.get('flag')
            format_value = request.data.get('format')
            print("format_value : ", format_value)
            pk = kwargs.get('pk')
            document_type = kwargs.get('document_type')
            doc_name, file_path, relative_file_path = path_generate(document_type)

            # ========== LOAD PRINT CONFIG ==========
            print_config = self._load_print_config(document_type)
            print("print_config loaded for:", document_type)
            # ========== END PRINT CONFIG LOAD ==========

            # ========== CONSTRUCT FULL URL ==========
            relative_url = relative_file_path.replace('\\', '/')
            host = request.get_host().lower()
            if '127.0.0.1' in host or 'localhost' in host:
                full_pdf_url = f"http://127.0.0.1:8000/public/documents/{relative_url}"
            else:
                full_pdf_url = f"https://apicore.cnlerp.com/public/documents/{relative_url}"

            print(f"Request host: {host}")
            cdn_path = f"{settings.MEDIA_URL}{relative_file_path}"
            print(f"Full PDF URL: {full_pdf_url}")
            print(f"CDN PATH: {cdn_path}")
            # ========== END URL CONSTRUCTION ==========

#   #=======================================ReportLab Code Started============================
            if document_type == "sale_order":
                pdf_data = sale_order_sales_invoice_data(pk, document_type, format_value)
                # Override doc_header based on sale_estimate directly in the view
                
                print("pdf_data.get('sale_estimate') : ", pdf_data.get('sale_estimate'))
                if pdf_data.get('sale_estimate') == 'Yes':
                    pdf_data['doc_header'] = "SALES QUOTATION"
                    
                print(f"Final confirmed doc_header: {pdf_data['doc_header']}") 

                elements, doc = doc_heading(file_path, pdf_data['doc_header'], 'BILL OF SUPPLY', print_config=print_config)
                sale_order_sales_invoice_doc(
                                   elements, doc,
                                   pdf_data['cust_bill_dtl'], pdf_data['number_lbl'], pdf_data['number_value'], pdf_data['date_lbl'], pdf_data['date_value'],
                                   pdf_data['customer_name'], pdf_data['billing_address'], pdf_data['phone'], pdf_data['city'],
                                   pdf_data['product_data'],
                                   pdf_data['total_qty'], pdf_data['final_total'], pdf_data['total_amt'], pdf_data['total_cgst'], pdf_data['total_sgst'], pdf_data['total_igst'],
                                   pdf_data['bill_amount_in_words'], pdf_data['itemstotal'], pdf_data['total_disc_amt'], pdf_data['finalDiscount'], pdf_data['shipping_charges'], pdf_data['round_0ff'], pdf_data['cess_amount'],
                                   pdf_data['party_old_balance'], pdf_data['net_lbl'], pdf_data['net_value'], pdf_data['tax_type'], pdf_data['remarks'],
                                   print_config=print_config
                                )
                
            if document_type == "sale_invoice":
                pdf_data = sale_order_sales_invoice_data(pk, document_type, format_value)
                elements, doc = doc_heading(file_path, pdf_data['doc_header'], '', print_config=print_config)
                sales_invoice_doc(
                                   elements, doc,
                                   pdf_data['company_logo'], pdf_data['company_name'], pdf_data['company_gst'], pdf_data['company_address'], pdf_data['company_phone'], pdf_data['company_email'],
                                   pdf_data['bank_name'], pdf_data['bank_acno'], pdf_data['bank_ifsc'], pdf_data['bank_branch'],
                                   pdf_data['number_lbl'], pdf_data['number_value'], pdf_data['date_lbl'], pdf_data['date_value'],
                                   pdf_data['customer_name'], pdf_data['city'], pdf_data['country'], pdf_data['phone'], pdf_data['dest'], pdf_data['shipping_address'],
                                   pdf_data['billing_address'],
                                   pdf_data['product_data'],
                                   pdf_data['total_qty'], pdf_data['final_total'], pdf_data['total_amt'], pdf_data['total_cgst'], pdf_data['total_sgst'], pdf_data['total_igst'],
                                   pdf_data['bill_amount_in_words'], pdf_data['itemstotal'], pdf_data['total_disc_amt'], pdf_data['finalDiscount'], pdf_data['shipping_charges'], pdf_data['cess_amount'], pdf_data['round_0ff'],
                                   pdf_data['party_old_balance'], pdf_data['net_lbl'], pdf_data['net_value'], pdf_data['tax_type'], pdf_data['remarks'],
                                   print_config=print_config
                                )
            if document_type == "sale_return":
                pdf_data = sale_order_sales_invoice_data(pk, document_type, format_value)
                elements, doc = doc_heading(file_path, "BILL OF SUPPLY", '', print_config=print_config)
                sale_return_doc(
                    elements, doc,
                    pdf_data['company_name'], pdf_data['company_address'], pdf_data['company_phone'],
                    pdf_data['cust_bill_dtl'], pdf_data['number_lbl'], pdf_data['return_no'],
                    pdf_data['date_lbl'], pdf_data['date_value'],
                    pdf_data['customer_name'], pdf_data['billing_address'], pdf_data['phone'],
                    pdf_data['city'],
                    pdf_data['product_data'],
                    pdf_data['total_qty'], pdf_data['total_amt'], pdf_data['cess_amount'], pdf_data['total_cgst'], pdf_data['total_sgst'], pdf_data['total_igst'], pdf_data['itemstotal'],
                    pdf_data['finalDiscount'], pdf_data['bill_amount_in_words'],
                    pdf_data['round_0ff'],
                    pdf_data['party_old_balance'], pdf_data['net_lbl'], pdf_data['net_value'], pdf_data['tax_type'], pdf_data['return_reason'],
                    print_config=print_config
                )
            if document_type == "delivery_challan":
                pdf_data = delivery_challan_data(pk, format_value)
                elements, doc = doc_heading(file_path, "DELIVERY CHALLAN", '', print_config=print_config)
                delivery_challan_doc(
                    elements, doc,
                    pdf_data['company_logo'], pdf_data['company_name'], pdf_data['company_gst'], pdf_data['company_address'], pdf_data['company_phone'], pdf_data['company_email'],
                    pdf_data['number_lbl'], pdf_data['number_value'], pdf_data['date_lbl'], pdf_data['date_value'],
                    pdf_data['customer_name'], pdf_data['city'], pdf_data['country'], pdf_data['phone'], pdf_data['shipping_address'], pdf_data['billing_address'],
                    pdf_data['product_data'],
                    pdf_data['total_qty'], pdf_data['final_total'], pdf_data['total_amt'], pdf_data['total_cgst'], pdf_data['total_sgst'], pdf_data['total_igst'],
                    pdf_data['bill_amount_in_words'], pdf_data['itemstotal'], pdf_data['total_disc_amt'], pdf_data['finalDiscount'],
                    pdf_data['transport_charges'], pdf_data['cess_amount'], pdf_data['round_0ff'], pdf_data['net_value'], pdf_data['tax_type'],
                    pdf_data['vehicle_name'], pdf_data['driver_name'], pdf_data['lr_no'], pdf_data['total_boxes'], pdf_data['remarks'],
                    print_config=print_config
                )
            if document_type == "purchase_order" or document_type == "purchase_return":
                pdf_data = purchase_data(pk, document_type, format_value)
                elements, doc = doc_heading(file_path, "PURCHASE BILL", '', print_config=print_config)
                purchase_doc(elements, doc,
                                   pdf_data['comp_name'], pdf_data['comp_address'], pdf_data['comp_phone'],
                                   pdf_data['cust_bill_dtl'], pdf_data['number_lbl'], pdf_data['number_value'], pdf_data['date_lbl'], pdf_data['date_value'],
                                   pdf_data['customer_name'], pdf_data['v_billing_address'], pdf_data['v_shipping_address_lbl'], pdf_data['v_shipping_address'],
                                   pdf_data['product_data'],
                                   pdf_data['total_qty'], pdf_data['itemstotal'], pdf_data['total_disc_amt'], pdf_data['total_cgst'], pdf_data['total_sgst'], pdf_data['total_igst'], pdf_data['final_total'], pdf_data['final_total'], pdf_data['total_txbl_amt'], pdf_data['total_sub_amt'], pdf_data['total_bill_amt'],
                                   pdf_data['destination'], pdf_data['tax_type'], pdf_data['shipping_mode_name'], pdf_data['port_of_landing'], pdf_data['port_of_discharge'],
                                   pdf_data['comp_name'],
                                   pdf_data['shipping_company_name'], pdf_data['shipping_tracking_no'], pdf_data['vehicle_vessel'], pdf_data['no_of_packets'], pdf_data['shipping_date'], pdf_data['shipping_charges'], pdf_data['weight'],
                                   pdf_data['comp_address'], pdf_data['comp_phone'], pdf_data['comp_email'],
                                   print_config=print_config
                                )

            if document_type == "payment_receipt":
                pdf_data = payment_receipt_data(pk, document_type)
                print("pdf_data--->>>", pdf_data)
                sub_header = 'Receipt Voucher'
                elements, doc = doc_heading(file_path, pdf_data['doc_header'], sub_header, print_config=print_config)
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
                        'amount': pdf_data['amount'],
                        'total': pdf_data['total']
                    }],
                    pdf_data['amount'],
                    pdf_data['outstanding'],
                    pdf_data['total'],
                    pdf_data['amount_in_words'],
                    pdf_data['receipt_no'],
                    print_config=print_config
                )

            elif document_type == "bill_receipt":
                print("We entered in bill-receipt....")
                pdf_data = billpayment_receipt_data(pk, document_type)
                print("pdf_data--->>>", pdf_data)
                sub_header = 'Bill Payment Receipt Voucher'
                elements, doc = doc_heading(file_path, pdf_data['doc_header'], sub_header, print_config=print_config)
                billpayment_receipt_doc(
                    elements, doc,
                    pdf_data['company_name'], pdf_data['company_address'], pdf_data['company_phone'],
                    pdf_data['cust_bill_dtl'],
                    pdf_data['number_lbl'],
                    pdf_data['invoice_no'],
                    pdf_data['date_lbl'],
                    pdf_data['receipt_date'],
                    pdf_data['vendor_name'],
                    pdf_data['billing_address'],
                    pdf_data['phone'],
                    pdf_data['email'],
                    [{
                        'invoice_no': pdf_data['invoice_no'],
                        'invoice_date': pdf_data['invoice_date'],
                        'payment_method': pdf_data['payment_method'],
                        'cheque_no': pdf_data['cheque_no'],
                        'amount': pdf_data['amount'],
                        'total': pdf_data['total']
                    }],
                    pdf_data['amount'],
                    pdf_data['outstanding'],
                    pdf_data['total'],
                    pdf_data['amount_in_words'],
                    pdf_data['receipt_no'],
                    print_config=print_config
                )

            elif document_type == "account_ledger":
                print("We entered in account-ledger....")
                pdf_data = ledger_document_data(request, pk, document_type)
                print("pdf_data--->>>", pdf_data)
                sub_header = 'Account Ledger Statement'
                elements, doc = doc_heading(file_path, pdf_data['doc_header'], sub_header, print_config=print_config)
                ledger_document_doc(
                    elements, doc,
                    pdf_data['company_name'],
                    pdf_data['company_address'],
                    pdf_data['company_phone'],
                    pdf_data['from_date'],
                    pdf_data['to_date'],
                    pdf_data['ledger_name'],
                    pdf_data['number_lbl'],
                    pdf_data['date_lbl'],
                    pdf_data['doc_date'],
                    pdf_data['ledger_data'],
                    pdf_data['debit_total'],
                    pdf_data['credit_total'],
                    pdf_data['closing_balance'],
                    pdf_data['amount_in_words'],
                    print_config=print_config
                )

            # ========== DOCUMENT TRACKING (all document types) ==========
            try:
                file_size = os.path.getsize(file_path) if os.path.exists(file_path) else None
                customer_id = pdf_data.get('customer_id') if pdf_data else None
                customer_obj = None
                if customer_id:
                    try:
                        from apps.customer.models import Customer
                        customer_obj = Customer.objects.get(customer_id=customer_id)
                    except Exception:
                        pass
                DocumentsGeneration.objects.create(
                    document_type=document_type,
                    document_id=str(pk),
                    customer=customer_obj,
                    file_name=doc_name,
                    file_path=relative_file_path,
                    file_url=full_pdf_url,
                    file_size=file_size,
                )
            except Exception as e:
                logger.error("Failed to create DocumentsGeneration record: %s", str(e))
            # ========== END TRACKING ==========

            pdf_send_response = 'Document generated successfully'
            if flag == 'email':
                pdf_send_response = send_pdf_via_email(pdf_data['email'], relative_file_path, document_type)
                
            if flag == 'print':
                with open(file_path, 'rb') as pdf_file:
                    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                    response['Content-Disposition'] = f'inline; filename="{doc_name}"'
                    return response
            
            elif flag == 'preview':
                # Return the PDF file directly for preview
                with open(file_path, 'rb') as pdf_file:
                    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                    response['Content-Disposition'] = f'inline; filename="{doc_name}.pdf"'
                    return response
                
            # elif flag == 'whatsapp':
            #     pdf_send_response = send_whatsapp_message_via_wati(phone, cdn_path)
            elif flag == 'whatsapp':
                city_id = request.GET.get('city')
                
                # 1️⃣ Resolve phone
                phone = resolve_phone_from_document(
                    document_type=document_type,
                    pk=pk,
                    city_id=city_id,
                    request=request
                )
                
                if not phone:
                    return Response({
                        "status": 0,
                        "message": "Phone number not found in address"
                    }, status=400)
                
                # Get customer name
                customer_name = pdf_data.get("customer_name", "Customer")
                document_type_display = document_type.replace('_', ' ').title()
                
                # 2️⃣ WATI ENABLED
                if getattr(settings, 'ENABLE_WATI', False):
                    result = send_whatsapp_message_via_wati(
                        to_number=phone,
                        file_url=cdn_path,
                        document_type=document_type,
                        customer_name=customer_name
                    )
                    
                    return Response({
                        "status": 1 if result.get('sent') else 0,
                        "mode": result.get('mode', 'wati'),
                        "message": result,
                        "phone": phone
                    })
                
                # 3️⃣ LOCAL / DEV MODE (fallback)
                message = (
                    f"Hello {customer_name} 👋\n\n"
                    f"Please find your *{document_type_display}* below:\n\n"
                    f"{cdn_path}\n\n"
                    "Thank you.\n"
                    "Rudhra Industries"
                )
                
                whatsapp_url = build_whatsapp_click_url(phone, message)
                
                return Response({
                    "status": 1,
                    "mode": "click_to_chat",
                    "phone": phone,
                    "whatsapp_url": whatsapp_url
                })
            # elif flag == 'whatsapp':

            #     from django.conf import settings

            #     city_id = request.GET.get('city')

            #     # 1️⃣ Resolve phone
            #     phone = resolve_phone_from_document(
            #         document_type=document_type,
            #         pk=pk,
            #         city_id=city_id,
            #         request=request   # REQUIRED FOR LEDGER
            #     )

            #     if not phone:
            #         return Response({
            #             "status": 0,
            #             "message": "Phone number not found in address"
            #         }, status=400)

            #     # 2️⃣ WATI ENABLED (PROD)
            #     if getattr(settings, 'ENABLE_WATI', False):
            #         result = send_whatsapp_message_via_wati(phone, cdn_path)

            #         return Response({
            #             "status": 1,
            #             "mode": "wati",
            #             "message": result,                        
            #             "phone": phone
            #         })

            #     # 3️⃣ LOCAL / DEV MODE (NO LICENSE)
            #     customer_name = pdf_data.get("customer_name", "Customer")

            #     message = (
            #         f"Hello {customer_name} 👋\n\n"
            #         f"Please find your *{document_type.replace('_', ' ').title()}* below:\n\n"
            #         f"{cdn_path}\n\n"
            #         "Thank you.\n"
            #         "Rudhra Industries"
            #     )

            #     whatsapp_url = build_whatsapp_click_url(phone, message)

            #     return Response({
            #         "status": 1,
            #         "mode": "click_to_chat",
            #         "phone": phone,
            #         "whatsapp_url": whatsapp_url
            #     })



        except Http404:
            logger.error("pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("An error occurred while retrieving pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

        return build_response(1, pdf_send_response , [], status.HTTP_200_OK)

class ReturnOptionsViewset(viewsets.ModelViewSet):
    queryset = ReturnOptions.objects.exclude(name__iexact='Sale order').order_by('is_deleted', '-created_at')
    serializer_class = ReturnOptionsSerializers
    
    #log actions
    log_actions = True
    log_module_name = "Return Options"
    log_pk_field = "return_option_id"
    log_display_field = "name"

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
    
class FieldTypeViewSet(viewsets.ModelViewSet):
    queryset = FieldType.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = FieldTypeSerializer
    
    #log actions
    log_actions = True
    log_module_name = "Field Type"
    log_pk_field = "field_type_id"
    log_display_field = "field_type_name"

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)  
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)  
    
class EntitiesViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on Entity model.
    """
    queryset = Entities.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = EntitiesSerializer
    
    #log actions
    log_actions = True
    log_module_name = "Entities"
    log_pk_field = "entity_id"
    log_display_field = "entity_name"

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
    
class UserGroupsViewset(viewsets.ModelViewSet):
    queryset = UserGroups.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = UserGroupsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = UserGroupsFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "User Groups"
    log_pk_field = "group_id"
    log_display_field = "group_name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, UserGroups,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
    
class UserGroupMembersViewset(viewsets.ModelViewSet):
    queryset = UserGroupMembers.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = UserGroupMembersSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = UserGroupMembersFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "User Groups Members"
    log_pk_field = "member_id"
    log_display_field = "member_id"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, UserGroupMembers,*args, **kwargs)

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

class PackageUnitViewSet(viewsets.ModelViewSet):
    queryset = PackageUnit.objects.all().order_by('is_deleted')
    serializer_class = PackageUnitSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = PackageUnitFilter
    ordering_fields = []
    
    #log actions
    log_actions = True
    log_module_name = "Package Unit"
    log_pk_field = "pack_unit_id"
    log_display_field = "unit_name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, PackageUnit,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)  
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)  


class GPackageUnitViewSet(viewsets.ModelViewSet):
    queryset = GPackageUnit.objects.all().order_by('is_deleted')
    serializer_class = GPackageUnitSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = GPackageUnitFilter
    ordering_fields = []
    
    #log actions
    log_actions = True
    log_module_name = "G Package Unit"
    log_pk_field = "g_pack_unit_id"
    log_display_field = "unit_name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, GPackageUnit,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

class FlowStatusViews(viewsets.ModelViewSet):
    queryset = FlowStatus.objects.all().order_by('is_deleted', '-created_at')
    serializer_class = FlowStatusSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = FlowStatusFilter
    ordering_fields = ['created_at']

    #log actions
    log_actions = True
    log_module_name = "Flow Status"
    log_pk_field = "flow_status_id"
    log_display_field = "flow_status_name"

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        response = create_instance(self, request, *args, **kwargs)
        return response

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)


# ─────────────────────────────────────────────────────────────────
# DOCUMENT PRINT TEMPLATE — CRUD ViewSet
# ─────────────────────────────────────────────────────────────────
class DocumentPrintTemplateViewSet(viewsets.ModelViewSet):
    """
    CRUD for DocumentPrintTemplate.
    Supports per-company, per-document-type named print templates.
    Query params: ?company=<id>  ?document_type=<type>
    """
    from rest_framework.permissions import IsAuthenticated
    permission_classes   = [IsAuthenticated]
    serializer_class     = DocumentPrintTemplateSerializer
    filter_backends      = [DjangoFilterBackend, OrderingFilter]
    ordering_fields      = ['created_at', 'template_name']

    def get_queryset(self):
        qs = DocumentPrintTemplate.objects.filter(is_deleted=False)
        company       = self.request.query_params.get('company')
        document_type = self.request.query_params.get('document_type')
        if company:
            qs = qs.filter(company_id=company)
        if document_type:
            qs = qs.filter(document_type=document_type)
        return qs.order_by('-is_default', 'template_name')

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        If is_default=True, unset any existing default for the same (company, document_type).
        Wrapped in atomic so the unset + insert cannot interleave with a concurrent request.
        """
        data = request.data
        if data.get('is_default'):
            DocumentPrintTemplate.objects.select_for_update().filter(
                company_id=data.get('company'),
                document_type=data.get('document_type'),
                is_default=True,
            ).update(is_default=False)
        return create_instance(self, request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        if request.data.get('is_default'):
            instance = self.get_object()
            DocumentPrintTemplate.objects.select_for_update().filter(
                company_id=instance.company_id,
                document_type=instance.document_type,
                is_default=True,
            ).exclude(pk=instance.pk).update(is_default=False)
        return update_instance(self, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)


# ─────────────────────────────────────────────────────────────────
# DOCUMENT PRINT DEFAULTS — returns available columns/sections/options
# ─────────────────────────────────────────────────────────────────
class DocumentPrintDefaultsView(APIView):
    """
    GET /masters/document-print-defaults/?document_type=sale_invoice
    Returns available columns, sections, paper sizes, color themes
    for the given document type. Used to build the settings UI.
    """
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]

    def get(self, request):
        document_type = request.query_params.get('document_type', 'sale_invoice')
        col_defs = COLUMN_DEFINITIONS_BY_DOC_TYPE.get(document_type, [])

        # Build columns array — matches frontend PrintDefaultsResponse.columns
        columns = [
            {
                'key':           col['key'],
                'label':         col['label'],
                'default_visible': col.get('default', True),
                'required':      col.get('required', False),
                'order':         idx,
            }
            for idx, col in enumerate(col_defs)
        ]

        # Section group mapping for UI grouping
        SECTION_GROUPS = {
            'show_logo':             'Header',
            'show_company_name':     'Header',
            'show_company_address':  'Header',
            'show_company_phone':    'Header',
            'show_company_email':    'Header',
            'show_gstin':            'Header',
            'show_billing_address':  'Addresses',
            'show_shipping_address': 'Addresses',
            'show_subtotal':         'Totals',
            'show_discount':         'Totals',
            'show_shipping_charges': 'Totals',
            'show_cess':             'Totals',
            'show_round_off':        'Totals',
            'show_party_balance':    'Totals',
            'show_tax_breakdown':    'Totals',
            'show_amount_in_words':  'Totals',
            'show_bank_details':     'Footer',
            'show_terms':            'Footer',
            'show_notes':            'Footer',
            'show_signature':        'Footer',
            'show_declaration':      'Footer',
        }

        SECTION_LABELS = {
            'show_logo':             'Show Logo',
            'show_company_name':     'Show Company Name',
            'show_company_address':  'Show Company Address',
            'show_company_phone':    'Show Company Phone',
            'show_company_email':    'Show Company Email',
            'show_gstin':            'Show GSTIN',
            'show_billing_address':  'Show Billing Address',
            'show_shipping_address': 'Show Shipping Address',
            'show_subtotal':         'Show Subtotal',
            'show_discount':         'Show Discount',
            'show_shipping_charges': 'Show Shipping Charges',
            'show_cess':             'Show Cess',
            'show_round_off':        'Show Round Off',
            'show_party_balance':    'Show Party Balance',
            'show_tax_breakdown':    'Show Tax Breakdown (CGST/SGST/IGST)',
            'show_amount_in_words':  'Show Amount in Words',
            'show_bank_details':     'Show Bank Details',
            'show_terms':            'Show Terms & Conditions',
            'show_notes':            'Show Notes',
            'show_signature':        'Show Signature',
            'show_declaration':      'Show Declaration',
        }

        # Build sections array — matches frontend PrintDefaultsResponse.sections
        sections = [
            {
                'key':           key,
                'label':         SECTION_LABELS.get(key, key),
                'default_value': default_value,
                'group':         SECTION_GROUPS.get(key, 'General'),
            }
            for key, default_value in DEFAULT_SECTION_CONFIG.items()
        ]

        data = {
            'document_type': document_type,
            'columns':       columns,
            'sections':      sections,
            'paper_sizes': [
                {'value': k, 'label': v['label']}
                for k, v in PAPER_SIZES.items()
            ],
            'color_themes': [
                {'value': 'blue',   'label': 'Blue'},
                {'value': 'green',  'label': 'Green'},
                {'value': 'orange', 'label': 'Orange'},
                {'value': 'grey',   'label': 'Grey'},
                {'value': 'purple', 'label': 'Purple'},
                {'value': 'teal',   'label': 'Teal'},
                {'value': 'none',   'label': 'No Color'},
            ],
            'font_sizes': [
                {'value': 'small',  'label': 'Small'},
                {'value': 'medium', 'label': 'Medium'},
                {'value': 'large',  'label': 'Large'},
            ],
        }
        return build_response(1, "Document print defaults retrieved.", data, status.HTTP_200_OK)

