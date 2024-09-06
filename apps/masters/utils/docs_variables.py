import os
import random
import string
from django.conf import settings
from django.shortcuts import get_object_or_404
from apps.sales.models import SaleOrder, SaleOrderItems, SaleInvoiceOrders,SaleInvoiceItems, OrderShipments
from apps.sales.serializers import SaleOrderSerializer, SaleOrderItemsSerializer,SaleInvoiceOrdersSerializer, SaleInvoiceItemsSerializer, OrderShipmentsSerializer
from config.utils_methods import convert_amount_to_words, extract_product_data, format_phone_number,send_pdf_via_email, get_related_data
from apps.customer.models import CustomerAddresses

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
            }
        }


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