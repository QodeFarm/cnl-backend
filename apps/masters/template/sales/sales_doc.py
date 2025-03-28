import json
from django.conf import settings
from django.shortcuts import get_object_or_404
from apps.company.models import company_logos
from apps.company.serializers import CompaniesSerializer
from apps.customer.models import CustomerAddresses
from apps.finance.models import BankAccount
from apps.masters.template.table_defination import *
from apps.masters.utils.docs_variables import doc_data
from config.utils_methods import convert_amount_to_words, extract_product_data, format_phone_number,get_related_data

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
                # company_model = model_data.get('company_model')
                # company_serializer = model_data.get('company_serializers')
                # company_model_pk = model_data.get('company_model_pk')
                # net_value = model_data.get('total_amount')
               

            obj = get_object_or_404(model, pk=pk)
            customer_data_for_cust_data = serializer(obj).data
            itemstotal = customer_data_for_cust_data.get('item_value')
            # Access dictionary keys correctly
            shipping_address = customer_data_for_cust_data.get("shipping_address")
            billing_address = customer_data_for_cust_data.get("billing_address")
            net_value = customer_data_for_cust_data.get('total_amount')

            # Retrieve related data
            items_data = get_related_data(item_model, items_serializer, item_model_pk, pk)
            related_data = get_related_data(related_model, related_serializer, related_filter_field, pk)
            related_data = related_data[0] if len(related_data) > 0 else {}
            
            # ====== COMPLETE COMPANY DATA FETCH ======
            # Get the first company (you can modify this if you need specific company)
            company = Companies.objects.first()  # Get the first company
            company_name = company.name if company else "N/A"
            company_gst = company.gst_tin if company else "N/A"
            company_address = company.address if company else "N/A"
            company_phone = company.phone if company else "N/A"
            company_email = company.email if company else "N/A"
            company_logo = (
                company.logo[0]['attachment_path'] 
                if company and isinstance(company.logo, list) and company.logo else "N/A"
            )

            print("-" * 20)
            print("logo : ", company_logo)
            print("-" * 20)

            # company_logo = company.logo[0]['attachment_path'] if company and company.logo else "N/A"

            #fetching Bank details 
            bank = BankAccount.objects.first()
            bank_name = bank.bank_name if bank else "N/A"
            bank_branch = bank.branch_name if bank else "N/A"
            bank_ifsc = bank.ifsc_code if bank else "N/A"
            bank_acno = bank.account_number if bank else "N/A"
            bank_actype = bank.account_type if bank else "N/A"

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
            print("-"*20)
            print("items_data : ", items_data)
            print("-"*20)
            for item in items_data:
                total_amt += float(item['amount']) if item['amount'] is not None else 0
                total_qty += float(item['quantity']) if item['quantity'] is not None else 0
                total_disc_amt += float(item['discount']) if item['discount'] is not None else 0
                cgst = float(item['cgst']) if item['cgst'] else 0
                sgst = float(item['sgst']) if item['sgst'] else 0
                igst = float(item['igst']) if item['igst'] else 0
                item['tax'] = cgst + sgst + igst
                print("item['tax'] : ", item['tax'])
                total_txbl_amt += float(item['tax']) if item['tax'] is not None else 0


            bill_amount_in_words = convert_amount_to_words(total_amt)

            product_data = extract_product_data(items_data)

            return {
                #Company details
                'company_logo': company_logo,
                'company_name': company_name,
                'company_gst': company_gst,
                'company_address': company_address,
                'company_phone': company_phone,
                'company_email': company_email,
                
                #Bank details 
                'bank_name': bank_name,
                'bank_branch': bank_branch,
                'bank_acno': bank_acno,
                'bank_ifsc': bank_ifsc,
                'bank_actype': bank_actype,
                'cust_bill_dtl' : 'Customer Billing Detail',
                'number_lbl' : model_data.get('number_lbl'),
                'date_lbl' : model_data.get('date_lbl'),
                'doc_header' : model_data.get('Doc_Header'),
                'net_lbl' : model_data.get('net_lbl'),
                'number_value' : customer_data_for_cust_data[number_value],
                'date_value' :  customer_data_for_cust_data[date_value],
                'shipping_address' : shipping_address,
                'billing_address' : billing_address,

                'customer_name' : customer_data_for_cust_data['customer']['name'],
                'city' : city,
                'country' : country,
                'phone' : phone,
                'dest' : dest ,
                'email' : email,
                'bill_amount_in_words' : bill_amount_in_words,

                'product_data' : product_data,
                
                'itemstotal' : itemstotal,
                'total_amt' : total_amt,
                'total_qty' : total_qty,
                'total_txbl_amt' : total_txbl_amt,
                'total_disc_amt' : total_disc_amt,
                'round_0ff' : round_0ff,
                'party_old_balance' :  party_old_balance,
                'net_value' : net_value

                }



def sale_order_sales_invoice_doc(
    elements, doc,cust_bill_dtl, number_lbl, number_value, date_lbl, date_value,
    customer_name, billing_address, phone, city,
    product_data,
    total_qty, total_amt, total_txbl_amt,
    bill_amount_in_words, itemstotal, total_disc_amt, round_0ff, 
    party_old_balance, net_lbl, net_value
):  
    
    # Append document details
    elements.append(doc_details(
       cust_bill_dtl, number_lbl, number_value, date_lbl, date_value
    ))
    
    # Append customer details
    elements.append(customer_details(
        customer_name, billing_address, phone, city
    ))
    
    # Append product details
    elements.append(product_details(product_data))
    
    # Append product total details
    elements.append(product_total_details(
        total_qty, total_amt, total_disc_amt,  total_txbl_amt
    ))
    
    # Append product total details in words
    elements.append(product_total_details_inwords(
        bill_amount_in_words, itemstotal,total_disc_amt,
        total_txbl_amt, round_0ff, 
        party_old_balance, net_lbl, net_value
    ))
    
    # Append declaration
    elements.append(declaration())

    # Build the PDF
    doc.build(elements)
    
def sales_invoice_doc(
    elements, doc, company_logo, company_name, company_gst, company_address, company_phone, company_email, bank_name, bank_acno, bank_ifsc, bank_branch,
    cust_bill_dtl, number_lbl, number_value, date_lbl, date_value,
    customer_name, city, country, phone, dest, shipping_address, billing_address,
    product_data,
    total_qty, total_amt, total_txbl_amt,
    bill_amount_in_words, itemstotal, total_disc_amt, round_0ff, 
    party_old_balance, net_lbl, net_value
):  

    # Append document details
    elements.append(invoice_doc_details(
       company_logo, company_name, company_gst, company_address, company_phone, company_email, number_lbl, number_value, date_lbl, date_value
    ))
    
    # Append customer details
    elements.append(invoice_customer_details(
        customer_name, city, country, phone, dest, shipping_address, billing_address
    ))
    
    # Append product details
    elements.append(invoice_product_details(product_data))
    
    # Append product total details
    elements.append(invoice_product_total_details(
        total_qty, total_amt, total_disc_amt,  total_txbl_amt
    ))
    
    # Append product total details in words
    elements.append(product_total_details_inwords(
        bill_amount_in_words, itemstotal,
        total_disc_amt, total_txbl_amt, round_0ff,
        party_old_balance, net_lbl, net_value
    ))
    
    # Append declaration
    # elements.append(declaration())
    
    # Add to your PDF story just like other tables
    # elements.append(Spacer(1, 0.5*inch))  # Add some space first
    elements.append(create_footer_section(
        bank_name, bank_acno, bank_ifsc, bank_branch
    ))

    # Build the PDF
    doc.build(elements)