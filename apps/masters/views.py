import random
import string
from django_filters.rest_framework import DjangoFilterBackend # type: ignore
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from config.utils_methods import *
from rest_framework import status
from django.conf import settings
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

#===============================================PDF_creation================================
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from apps.masters.utils.table_defination import create_table_1, create_table_2, create_table_3, create_table_4, create_table_5, create_table_6
from config.utils_methods import convert_amount_to_words, extract_product_data, format_phone_number,send_pdf_via_email, get_related_data, list_all_objects, create_instance, update_instance, build_response
from django.http import Http404
from apps.customer.models import CustomerAddresses
from .utils.docs_variables import doc_data
from reportlab.lib.pagesizes import inch

class DocumentGeneratorView(APIView):
    def post(self, request, **kwargs):
        """ Retrieves a sale order and its related data. """

        try:
            flag = request.data.get('flag')
            pk = kwargs.get('pk')
            document_type = kwargs.get('document_type')

            # Get the relevant data from the doc_data dictionary
            model_data = doc_data.get(document_type)
            if model_data:
                Model = model_data.get('Model')
                Serializer = model_data.get('Serializer')
                Item_Model = model_data.get('Item_Model')
                Items_Serializer = model_data.get('Items_Serializer')
                Item_Model_PK = model_data.get('Item_Model_PK')
                Related_Model = model_data.get('Related_Model')
                Related_Serializer = model_data.get('Related_Serializer')
                Related_filter_field = model_data.get('Related_filter_field')
                number_lbl = model_data.get('number_lbl')
                date_lbl = model_data.get('date_lbl')
                Doc_Header = model_data.get('Doc_Header')
                net_lbl = model_data.get('net_lbl')
                number_value = model_data.get('number_value')
                date_value = model_data.get('date_value')

            obj = get_object_or_404(Model, pk=pk)
            customer_data_for_cust_data = Serializer(obj).data
            # Retrieve related data
            items_data = get_related_data(Item_Model, Items_Serializer, Item_Model_PK, pk)
            related_data = get_related_data(Related_Model, Related_Serializer, Related_filter_field, pk)
            related_data = related_data[0] if len(related_data) > 0 else {}

            # extracting phone number from cust_address
            customer_id = list(Model.objects.filter(**{Item_Model_PK : pk}).values_list('customer_id', flat=True))
            

            filter_kwargs = {"customer_id": customer_id[0], "address_type": "Billing"}
            city = str(list(CustomerAddresses.objects.filter(**filter_kwargs))[0].city_id)
            country = str(list(CustomerAddresses.objects.filter(**filter_kwargs))[0].country_id)
            phone_number = str(list(CustomerAddresses.objects.filter(**filter_kwargs))[0].phone)
            phone = format_phone_number(phone_number)
            dest = str(related_data.get('destination', 'N/A'))
            email = customer_data_for_cust_data['email']

            total_amt = total_qty = total_txbl_amt = total_disc_amt =round_0ff = party_old_balance = net_value= 0.0
            for item in items_data:
                total_amt += float(item['amount']) if item['amount'] is not None else 0
                total_qty += float(item['quantity']) if item['quantity'] is not None else 0
                total_disc_amt += float(item['discount']) if item['discount'] is not None else 0
                total_txbl_amt += float(item['tax']) if item['tax'] is not None else 0

            bill_amount_in_words = convert_amount_to_words(total_amt)

            product_data = extract_product_data(items_data)

            Cust_data = {
                "{{number_lbl}}": number_lbl,
                "{{number_value}}": customer_data_for_cust_data[number_value],
                "{{date_lbl}}": date_lbl,
                "{{date_value}}": customer_data_for_cust_data[date_value],
                "{{cust_name}}": customer_data_for_cust_data['customer']['name'],
                "{{phone}}": phone,
                "{{dest}}": dest,
                "{{qty_ttl}}":  (total_qty),
                "{{amt_ttl}}":  (total_amt),
                "{{txbl_ttl}}": (total_txbl_amt),
                "{{discount}}": (total_disc_amt),
                "{{Rnd_off}}": "0.0",
                "{{Net_lbl}}": (net_lbl),
                "{{Net_Ttl}}": (net_value),
                "{{Party_Old_B}}": "0.0",
                "{{Bill_amt_wd}}": bill_amount_in_words,
                "{{Tax_amt_wd}}": bill_amount_in_words,
                "{{address}}": (city),
                "{{country}}": (country),
                "{{Doc Header}}": Doc_Header
            }

            # Generate a random filename
            unique_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) + '.pdf'
            doc_name = 'sale order_' + unique_code
            # Construct the full file path
            file_path = os.path.join(settings.MEDIA_ROOT, 'doc_generater', doc_name)
            # Ensure that the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

  #=======================================ReportLab Code Started============================          
            elements = []

            # Custom page size (11 inches wide, 10.5 inches high)
            page_width = 11 * inch
            page_height = 10.5 * inch

            # Create the PDF document
            doc = SimpleDocTemplate(file_path, pagesize=(page_width, page_height))
            

            # Get the default styles
            styles = getSampleStyleSheet()
            
            # Modify the heading style to be bold
            style_heading = ParagraphStyle(
                name='Heading1',
                parent=styles['Heading1'],
                fontName='Helvetica-Bold',  # Set font to Helvetica-Bold to make it bold
                fontSize=16,                # You can adjust the font size if needed
                spaceAfter=12,              # Adjust space after heading if needed
                alignment=1,                # Center align the text (0=left, 1=center, 2=right)
            )

           
            # Add a bold heading
            elements.append(Paragraph(Doc_Header, style_heading))

            # Add a spacer
            elements.append(Spacer(1, 12))
            
            # Add Table 1
            table_1 = create_table_1(customer_data_for_cust_data[number_value], customer_data_for_cust_data[date_value])
            elements.append(table_1)

            table_2 = create_table_2(customer_data_for_cust_data['customer']['name'], city, country, phone, dest)
            elements.append(table_2)

            table_3 = create_table_3(product_data)
            elements.append(table_3)

            table_4 = create_table_4(total_qty, total_amt, total_txbl_amt)
            elements.append(table_4)

            table_5 = create_table_5(bill_amount_in_words, bill_amount_in_words, customer_data_for_cust_data[number_value], total_qty, total_disc_amt, round_0ff, total_txbl_amt, party_old_balance, net_value)
            elements.append(table_5)

            table_6 = create_table_6()
            elements.append(table_6)

            # Build the PDF
            doc.build(elements)

 
            # Return the relative path to the file (relative to MEDIA_ROOT)
            relative_file_path = os.path.join('doc_generater', os.path.basename(doc_name))

            
            if flag == 'email':
                PDF_Send_Response = send_pdf_via_email(email, relative_file_path)
            # elif flag == 'whatsapp':
            #     PDF_Send_Response = send_whatsapp_message_via_wati(phone, cdn_path)

        except Http404:
            logger.error("pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("An error occurred while retrieving pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

        return build_response(1, PDF_Send_Response , [], status.HTTP_200_OK)

