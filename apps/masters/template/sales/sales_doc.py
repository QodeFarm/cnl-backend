from apps.masters.template.table_defination import *
from django.shortcuts import get_object_or_404
from apps.customer.models import CustomerAddresses
from config.utils_methods import convert_amount_to_words, extract_product_data, format_phone_number,get_related_data
from apps.masters.utils.docs_variables import doc_data

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



def sale_order_sales_invoice_doc(
    elements, doc,cust_bill_dtl, number_lbl, number_value, date_lbl, date_value,
    customer_name, city, country, phone, dest,
    product_data,
    total_qty, total_amt, total_txbl_amt,
    bill_amount_in_words, total_disc_amt, round_off, 
    party_old_balance, net_lbl, net_value
):  
    
    # Append document details
    elements.append(doc_details(
       cust_bill_dtl, number_lbl, number_value, date_lbl, date_value
    ))
    
    # Append customer details
    elements.append(customer_details(
        customer_name, city, country, phone, dest
    ))
    
    # Append product details
    elements.append(product_details(product_data))
    
    # Append product total details
    elements.append(product_total_details(
        total_qty, total_amt, total_disc_amt,  total_txbl_amt
    ))
    
    # Append product total details in words
    elements.append(product_total_details_inwords(
        bill_amount_in_words, number_value,
        total_qty, total_disc_amt, round_off, total_txbl_amt,
        party_old_balance, net_lbl, net_value
    ))
    
    # Append declaration
    elements.append(declaration())

    # Build the PDF
    doc.build(elements)