import os
import random
import string
from django.conf import settings
from django.shortcuts import get_object_or_404
from apps.sales.models import SaleOrder, SaleOrderItems, SaleInvoiceOrders,SaleInvoiceItems, OrderShipments
from apps.sales.serializers import SaleOrderSerializer, SaleOrderItemsSerializer,SaleInvoiceOrdersSerializer, SaleInvoiceItemsSerializer, OrderShipmentsSerializer
from config.utils_methods import convert_amount_to_words, extract_product_data, format_phone_number,get_related_data
from apps.customer.models import CustomerAddresses
from apps.purchase.models import PurchaseOrders, PurchaseorderItems
from  apps.purchase.serializers import PurchaseOrdersSerializer, PurchaseorderItemsSerializer
from apps.company.models import Companies
from apps.company.serializers import CompaniesSerializer
from apps.sales.models import OrderShipments
from apps.sales.serializers import OrderShipmentsSerializer
from apps.vendor.models import VendorAddress


# needed for DocumentGeneratorView(present in sales.view) view for sending sales order rcpt, sales invoice rcpt etc 
doc_data = {
            'sale_order': {
                'Model': SaleOrder,
                'Serializer': SaleOrderSerializer,
                'Item_Model': SaleOrderItems,
                'Items_Serializer': SaleOrderItemsSerializer,
                'Item_Model_PK': 'sale_order_id',
                'Related_Model': OrderShipments,
                'Related_Serializer': OrderShipmentsSerializer,
                'Related_filter_field': 'order_id',

                'number_lbl': 'SO No.',
                'date_lbl': 'SO Date',
                'Doc_Header': 'SALES ORDER',
                'net_lbl': 'Net  Total',

                'number_value': 'order_no',
                'date_value': 'order_date',
            },

            'sale_invoice': {
                'Model': SaleInvoiceOrders,
                'Serializer': SaleInvoiceOrdersSerializer,
                'Item_Model': SaleInvoiceItems,
                'Items_Serializer': SaleInvoiceItemsSerializer,
                'Item_Model_PK': 'sale_invoice_id',
                'Related_Model': OrderShipments,
                'Related_Serializer': OrderShipmentsSerializer,
                'Related_filter_field': 'order_id',

                'number_lbl': 'Quotation No.',
                'date_lbl': 'Quote Date',
                'Doc_Header': 'SALES QUOTATION',
                'net_lbl': 'Net Amount',

                'number_value': 'invoice_no',
                'date_value': 'invoice_date',
            },
            'purchase_order': {
                'Model': PurchaseOrders,
                'Serializer': PurchaseOrdersSerializer,
                'Item_Model': PurchaseorderItems,
                'Items_Serializer': PurchaseorderItemsSerializer,
                'Item_Model_PK': 'purchase_order_id',
                'Related_Model': OrderShipments,
                'Related_Serializer': OrderShipmentsSerializer,
                'Related_filter_field': 'order_id',

                'number_lbl': 'Voucher No.',
                'date_lbl': 'Date',
                'Doc_Header': 'Purchase Bill',
                'net_lbl': 'Order Total',

                'number_value': 'invoice_no',
                'date_value': 'invoice_date',
            }
        }

from apps.masters.utils.table_defination import purchase_order_doc
def purchase_order_data(pk, document_type):
      #Companies Details
        company = Companies.objects.all()
        serializer = CompaniesSerializer(company, many=True)
        comp_data = serializer.data
         
        model_data = doc_data.get(document_type)
        if model_data:
            model = model_data.get('Model')
            serializer = model_data.get('Serializer')
            item_model = model_data.get('Item_Model')
            items_serializer = model_data.get('Items_Serializer')
            item_model_pk = model_data.get('Item_Model_PK')
            related_model = model_data.get('Related_Model')
            related_serializer = model_data.get('Related_Serializer')
            related_filter_field = model_data.get('Related_filter_field')
        
        # Retrieve the PurchaseOrders instance
        purchase_order = get_object_or_404(model, pk=pk)        
        
         # for extracting phone number, email from vendor_id
        vendor_id = list(model.objects.filter(**{item_model_pk : pk}).values_list('vendor_id', flat=True))
        filter_kwargs = {"vendor_id": vendor_id[0], "address_type": "Billing"}
        phone_number = str(list(VendorAddress.objects.filter(**filter_kwargs))[0].phone)
        email = (list(VendorAddress.objects.filter(**filter_kwargs))[0].email)
        phone = format_phone_number(phone_number)

        vendor = PurchaseOrdersSerializer(purchase_order).data.get('vendor')      
        billing_address =  PurchaseOrdersSerializer(purchase_order).data.get('billing_address')
        shipping_address =  PurchaseOrdersSerializer(purchase_order).data.get('shipping_address')
        order_no =  PurchaseOrdersSerializer(purchase_order).data.get('order_no')
        order_date =  PurchaseOrdersSerializer(purchase_order).data.get('order_date')

        
        # Retrieve related data
        items_data = get_related_data(item_model, items_serializer, item_model_pk, pk)
        shipments_data = get_related_data(related_model, related_serializer, related_filter_field , pk)
        shipments_data = shipments_data[0] if len(shipments_data)>0 else {}

        total_amt = total_qty = total_txbl_amt = total_disc_amt = round_0ff = party_old_balance = net_value = 0.0

        for item in items_data:
            total_amt += float(item['amount']) if item['amount'] is not None else 0
            total_qty += float(item['quantity']) if item['quantity'] is not None else 0
            total_disc_amt += float(item['discount']) if item['discount'] is not None else 0
            total_txbl_amt += float(item['tax']) if item['tax'] is not None else 0

        product_data = extract_product_data(items_data)
       
        return  {
                'cust_bill_dtl' : 'Vendor Name & Address ',
                'comp_name' : comp_data[0].get('name'),
                'comp_address' : comp_data[0].get('address'),
                'comp_phone' : comp_data[0].get('phone'),
                'comp_email' : comp_data[0].get('email'),

                'number_lbl' : model_data.get('number_lbl'),
                'date_lbl' : model_data.get('date_lbl'),
                'number_value' : order_no,
                'date_value' :  order_date,

                'doc_header' : model_data.get('Doc_Header'),
                'net_lbl' : model_data.get('net_lbl'),
                'net_value' :  total_amt,
                
                'v_billing_address' : billing_address,
                'v_shipping_address_lbl' :'Delivery Address',
                'v_shipping_address' : shipping_address,
                

                'customer_name' :vendor.get('name'),
                'email' : email,
                'phone' : phone,         
                

                'product_data' : product_data,

                'total_amt' : total_amt,
                'total_qty' : total_qty,
                'total_txbl_amt' : total_txbl_amt,
                'total_disc_amt' : total_disc_amt,
                'round_0ff' : round_0ff,
                'party_old_balance' :  party_old_balance,
                
                
                'destination'   : shipments_data.get('destination', ''),
                'shipping_mode_name' : shipments_data.get('shipping_mode', {}).get('name', ''),
                'port_of_landing' : shipments_data.get('port_of_landing', ''),
                'port_of_discharge' : shipments_data.get('port_of_discharge', ''),
                'shipping_company_name' : shipments_data.get('shipping_company', {}).get('name', ''),
                'shipping_tracking_no' : shipments_data.get('shipping_tracking_no', ''),
                'vehicle_vessel' : shipments_data.get('vehicle_vessel', ''),
                'no_of_packets' : shipments_data.get('no_of_packets', ''),
                'shipping_date' : shipments_data.get('shipping_date', ''),
                'shipping_charges' : shipments_data.get('shipping_charges', ''),
                'weight' : shipments_data.get('weight', '')

                }

def path_generate(document_type):
    # Generate a random filename
    unique_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) + '.pdf'
    doc_name = document_type + '_' + unique_code
    # Construct the full file path
    file_path = os.path.join(settings.MEDIA_ROOT, 'doc_generater', doc_name)
    # Ensure that the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Return the relative path to the file (relative to MEDIA_ROOT)
    relative_file_path = os.path.join('doc_generater', os.path.basename(doc_name))
    # cdn_path = os.path.join(MEDIA_URL, relative_file_path)
    # print(cdn_path)

    return doc_name, file_path, relative_file_path

def sale_order_sales_invoice_data(pk, document_type):
    # Get the relevant data from the doc_data dictionary
            model_data = doc_data.get(document_type)
            if model_data:
                model = model_data.get('Model')
                serializer = model_data.get('Serializer')
                item_model = model_data.get('Item_Model')
                items_serializer = model_data.get('Items_Serializer')
                item_model_pk = model_data.get('Item_Model_PK')
                related_model = model_data.get('Related_Model')
                related_serializer = model_data.get('Related_Serializer')
                related_filter_field = model_data.get('Related_filter_field')
                number_value =  model_data.get('number_value')
                date_value = model_data.get('date_value')
               

            obj = get_object_or_404(model, pk=pk)
            customer_data_for_cust_data = serializer(obj).data
            # Retrieve related data
            items_data = get_related_data(item_model, items_serializer, item_model_pk, pk)
            related_data = get_related_data(related_model, related_serializer, related_filter_field, pk)
            related_data = related_data[0] if len(related_data) > 0 else {}

            # extracting phone number from cust_address
            customer_id = list(model.objects.filter(**{item_model_pk : pk}).values_list('customer_id', flat=True))
            

            filter_kwargs = {"customer_id": customer_id[0], "address_type": "Billing"}
            city = str(list(CustomerAddresses.objects.filter(**filter_kwargs))[0].city_id)
            country = str(list(CustomerAddresses.objects.filter(**filter_kwargs))[0].country_id)
            phone_number = str(list(CustomerAddresses.objects.filter(**filter_kwargs))[0].phone)
            phone = format_phone_number(phone_number)
            dest = str(related_data.get('destination', 'N/A'))
            email = (list(CustomerAddresses.objects.filter(**filter_kwargs))[0].email) #customer_data_for_cust_data['email']

            total_amt = total_qty = total_txbl_amt = total_disc_amt = round_0ff = party_old_balance = net_value = 0.0
            for item in items_data:
                total_amt += float(item['amount']) if item['amount'] is not None else 0
                total_qty += float(item['quantity']) if item['quantity'] is not None else 0
                total_disc_amt += float(item['discount']) if item['discount'] is not None else 0
                total_txbl_amt += float(item['tax']) if item['tax'] is not None else 0

            bill_amount_in_words = convert_amount_to_words(total_amt)

            product_data = extract_product_data(items_data)

            return {
                'cust_bill_dtl' : 'Customer Billing Detail',
                'number_lbl' : model_data.get('number_lbl'),
                'date_lbl' : model_data.get('date_lbl'),
                'doc_header' : model_data.get('Doc_Header'),
                'net_lbl' : model_data.get('net_lbl'),
                'number_value' : customer_data_for_cust_data[number_value],
                'date_value' :  customer_data_for_cust_data[date_value],

                'customer_name' : customer_data_for_cust_data['customer']['name'],
                'city' : city,
                'country' : country,
                'phone' : phone,
                'dest' : dest ,
                'email' : email,
                'bill_amount_in_words' : bill_amount_in_words,

                'product_data' : product_data,

                'total_amt' : total_amt,
                'total_qty' : total_qty,
                'total_txbl_amt' : total_txbl_amt,
                'total_disc_amt' : total_disc_amt,
                'round_0ff' : round_0ff,
                'party_old_balance' :  party_old_balance,
                'net_value' :  net_value,

                }

