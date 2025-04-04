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
            print("-"*20)
            print("model_data : ", model_data)
            print("-"*20)
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
            
            print("-"*20)
            print("customer_data_for_cust_data : ", customer_data_for_cust_data)
            print("-"*20)
            
            # Get the invoice OrderedDict
            InvoiceNo = customer_data_for_cust_data.get('sale_invoice')
            print("InvoiceNo : ", InvoiceNo)

            # Extract invoice_no and invoice_date
            final_invoice = InvoiceNo.get('invoice_no') if InvoiceNo else None
            final_invoiceDate = InvoiceNo.get('invoice_date') if InvoiceNo else None
            
            obj = get_object_or_404(model, pk=pk)
            is_estimate = getattr(obj, 'sale_estimate', 'No') == 'Yes'  # Safely get the attribute
            sale_estimate = customer_data_for_cust_data.get('sale_estimate')
            doc_header = "SALES QUOTATION" if is_estimate else "SALES ORDER"
            
            itemstotal=0 #making itemstotal value 0.            
            # itemstotal = customer_data_for_cust_data.get('item_value')
            itemstotal += float(customer_data_for_cust_data['item_value']) if customer_data_for_cust_data['item_value'] is not None else 0
        
            # Access dictionary keys correctly
            shipping_address = customer_data_for_cust_data.get("shipping_address")
            billing_address = customer_data_for_cust_data.get("billing_address")
            
            discountAmt = customer_data_for_cust_data.get("dis_amt")
            discountAmt = float(discountAmt) if discountAmt is not None else 0.0  # Convert to float
            print("billing_address : ", billing_address)
            if billing_address and 'Andhra Pradesh' in billing_address:
                print("Intra-state transaction (CGST + SGST)")
            net_value = customer_data_for_cust_data.get('total_amount')

            # Retrieve related data
            items_data = get_related_data(item_model, items_serializer, item_model_pk, pk)
            related_data = get_related_data(related_model, related_serializer, related_filter_field, pk)
            print("related_data : ", related_data)
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
            
            billing_state = list(CustomerAddresses.objects.filter(**filter_kwargs))[0].state_id
            print("billing_state : ", billing_state)
            
            print("Items data : ", items_data)

            total_amt = total_qty = cgst = sgst = igst = total_cgst = total_sgst= total_igst = total_disc_amt = round_0ff = party_old_balance = net_value = 0.0
            # Assuming cgst and sgst are not being mixed
            for item in items_data:
                total_amt += float(item['amount']) if item['amount'] is not None else 0
                total_qty += float(item['quantity']) if item['quantity'] is not None else 0
                cgst = float(item['cgst']) if item['cgst'] is not None else 0
                sgst = float(item['sgst']) if item['sgst'] is not None else 0
                igst = float(item['igst']) if item['igst'] is not None else 0

                # Handle intra-state or inter-state
                if billing_address and 'Andhra Pradesh' in billing_address:
                    print("-"*20)
                    print("we are in the method ...")
                    total_cgst += cgst  # Intra-state, split equally between CGST & SGST
                    print("total_cgst : ", total_cgst)
                    total_sgst += sgst
                    print("total_sgst : ", total_sgst)
                else:
                    total_igst += igst  # Inter-state, tax goes to IGST
                    print("total_igst : ", total_igst)
                    print("-"*20)

                total_disc_amt += float(item['quantity']) * float(item['rate']) * float(item['discount']) / 100



            
            bill_amount_in_words = convert_amount_to_words(total_amt)

            product_data = extract_product_data(items_data)
            
            # final_tax = total_cgst + total_sgst + total_igst
            finalDiscount = 0
            finalDiscount = discountAmt + total_disc_amt
            
            final_total = itemstotal + total_cgst + total_sgst + total_igst
            
            net_value = party_old_balance + final_total - finalDiscount

            return {
                'sale_estimate': sale_estimate,
                # Add the doc_header to the returned data
                'doc_header': doc_header,
                'final_invoice' : final_invoice, 
                'final_invoiceDate' : final_invoiceDate,
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
                'total_cgst' : total_cgst,
                'total_sgst' : total_sgst,
                'total_igst' : total_igst,
                
                'finalDiscount' : finalDiscount,
                # 'total_txbl_amt' : total_txbl_amt,
                'total_disc_amt' : total_disc_amt,
                'round_0ff' : round_0ff,
                'party_old_balance' :  party_old_balance,
                'net_value' : net_value

                }



def sale_order_sales_invoice_doc(
    elements, doc,cust_bill_dtl, number_lbl, number_value, date_lbl, date_value,
    customer_name, billing_address, phone, city,
    product_data,
    total_qty, total_amt, total_cgst, total_sgst, total_igst,
    bill_amount_in_words, itemstotal, total_disc_amt, finalDiscount, round_0ff, 
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
        total_qty, total_amt, total_disc_amt
    ))
    
    # Append product total details in words
    elements.append(product_total_details_inwords(
        bill_amount_in_words, itemstotal,finalDiscount,
        total_cgst, total_sgst, total_igst, round_0ff, 
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
    total_qty, total_amt, total_cgst, total_sgst, total_igst,
    bill_amount_in_words, itemstotal, total_disc_amt, finalDiscount, round_0ff, 
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
        total_qty, total_amt, total_disc_amt
    ))
    
    # Append product total details in words
    elements.append(product_total_details_inwords(
        bill_amount_in_words, itemstotal,
        finalDiscount, total_cgst, total_sgst, total_igst, round_0ff,
        party_old_balance, net_lbl, net_value
    ))
    
    # Add to your PDF story just like other tables
    # elements.append(Spacer(1, 0.5*inch))  # Add some space first
    elements.append(create_footer_section(
        bank_name, bank_acno, bank_ifsc, bank_branch
    ))

    # Build the PDF
    doc.build(elements)
    

def sale_return_doc(
    elements, doc, 
    company_name, company_address, company_phone,
    cust_bill_dtl, number_lbl, final_invoice, date_lbl, final_invoiceDate,
    customer_name, billing_address, phone, city,
    product_data,
    total_qty, total_amt, itemstotal, total_disc_amt,
    bill_amount_in_words, round_0ff,
    party_old_balance, net_lbl, net_value
):  
    # 1. Add company header
    elements.extend(
        return_company_header(company_name, company_address, company_phone)
    )
    
    # 2. Add document details (invoice no/date)
    elements.append(return_doc_details(
        cust_bill_dtl, number_lbl, final_invoice, date_lbl, final_invoiceDate
    ))
    
    # 3. Add customer details
    elements.append(return_customer_details(
        customer_name, billing_address, phone, city
    ))
    
    # 4. Add complete bordered table (products + financials)
    elements.append(return_complete_table(
        data=product_data,
        total_qty=format_numeric(total_qty),
        sub_total=format_numeric(itemstotal),
        discount_amt=format_numeric(total_disc_amt),
        bill_total=format_numeric(net_value),
        amount_in_words=bill_amount_in_words
    ))
    
    # 5. Build PDF
    doc.build(elements)