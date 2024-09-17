from apps.company.models import Companies
from apps.vendor.models import VendorAddress
from django.shortcuts import get_object_or_404
from apps.masters.template.table_defination import *
from apps.masters.utils.docs_variables import doc_data
from apps.company.serializers import CompaniesSerializer
from config.utils_methods import extract_product_data, format_phone_number,get_related_data

def purchase_data(pk, document_type):
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
            number_value = model_data.get('number_value')
            date_value = model_data.get('date_value')
        
        # Retrieve the PurchaseOrders instance
        obj = get_object_or_404(model, pk=pk)        
        
        # for extracting phone number, email from vendor_id
        vendor_id = list(model.objects.filter(**{item_model_pk : pk}).values_list('vendor_id', flat=True))
        filter_kwargs = {"vendor_id": vendor_id[0], "address_type": "Billing"}
        phone_number = str(list(VendorAddress.objects.filter(**filter_kwargs))[0].phone)
        email = (list(VendorAddress.objects.filter(**filter_kwargs))[0].email)
        phone = format_phone_number(phone_number)

        vendor = serializer(obj).data.get('vendor')      

        billing_address =  serializer(obj).data.get('billing_address')
        shipping_address =  serializer(obj).data.get('shipping_address')
        order_no =  serializer(obj).data.get(number_value)
        order_date =  serializer(obj).data.get(date_value)
        tax_type = serializer(obj).data.get('tax')

        
        # Retrieve related data
        items_data = get_related_data(item_model, items_serializer, item_model_pk, pk)
        shipments_data = get_related_data(related_model, related_serializer, related_filter_field , pk)
        shipments_data = shipments_data[0] if len(shipments_data)>0 else {}

        total_amt = total_qty = total_txbl_amt = total_disc_amt = total_sub_amt = total_bill_amt = net_value = 0.0

        for item in items_data:
            total_amt += float(item['amount']) if item['amount'] is not None else 0
            total_qty += float(item['quantity']) if item['quantity'] is not None else 0
            total_disc_amt += float(item['discount']) if item['discount'] is not None else 0
            total_txbl_amt += float(item['tax']) if item['tax'] is not None else 0

        total_sub_amt = total_amt - total_disc_amt  #Subtotal is the total amount before adding tax and after applying the discount.(Amount - Discount)

        total_bill_amt = total_sub_amt + total_txbl_amt #Bill Total is the final amount after adding the fixed tax.

        product_data = extract_product_data(items_data)

        # # Get the 'shipping_mode' dictionary or default to an empty dictionary
        # shipping_mode = shipments_data.get('shipping_mode', {})

        # # Safely get the 'name' from 'shipping_mode', or return an empty string if 'shipping_mode' is None or 'name' is not found
        # shipping_mode_name = shipping_mode.get('name', '') if shipping_mode is not None else ''
 
        return {
                'cust_bill_dtl' : 'Vendor Name & Address',
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
                
                'tax_type' : tax_type,
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
                'total_sub_amt'  : total_sub_amt,
                'total_bill_amt' : total_bill_amt,
                
                
                'destination'   : shipments_data.get('destination') or '',
                'shipping_mode_name': (shipments_data.get('shipping_mode') or {}).get('name', ''),
                'port_of_landing' : shipments_data.get('port_of_landing') or '',
                'port_of_discharge' :shipments_data.get('port_of_discharge') or '',
                'shipping_company_name' : (shipments_data.get('shipping_company') or {}).get('name', ''),
                'shipping_tracking_no' : shipments_data.get('shipping_tracking_no', ''),
                'vehicle_vessel' : shipments_data.get('vehicle_vessel') or '', 
                'no_of_packets' :  shipments_data.get('no_of_packets') or '', 
                'shipping_date' : shipments_data.get('shipping_date', ''),
                'shipping_charges' : shipments_data.get('shipping_charges', ''),
                'weight' :  shipments_data.get('weight') or '', 

                }


def purchase_doc(
         elements, doc, cust_bill_dtl, number_lbl, number_value, date_lbl, date_value,
         customer_name, v_billing_address, v_shipping_address_lbl, v_shipping_address,
         product_data,
         total_qty, total_amt, total_disc, total_txbl_amt, total_sub_amt, total_bill_amt,
         destination,tax_type, shipping_mode_name, port_of_landing, port_of_discharge,
         comp_name,
         shipping_company_name, shipping_tracking_no , vehicle_vessel, no_of_packets, shipping_date, shipping_charges, weight,
         comp_address, comp_phone, comp_email,
        ):

    # Append document details
    elements.append(doc_details(
       cust_bill_dtl, number_lbl, number_value, date_lbl, date_value
    ))

    # Append customer details
    elements.append(vendor_details(
        customer_name, v_billing_address, v_shipping_address_lbl, v_shipping_address
    ))
    
    elements.append(shipping_details(
        destination, tax_type,  shipping_mode_name, port_of_landing, port_of_discharge, date_value
    ))

    # Append product details
    elements.append(product_details(product_data))

    # Append product total details
    elements.append(product_total_details(
        total_qty, total_amt, total_disc, total_txbl_amt
    ))

    elements.append(narration_and_total(
        comp_name, date_value, total_sub_amt, total_bill_amt
    ))

    elements.append(logistics_info(
        shipping_company_name, shipping_tracking_no , vehicle_vessel, no_of_packets, shipping_date, shipping_charges, weight))

    elements.append(purchase_declaration(
        comp_name
    ))

    elements.append(comp_address_last_tbl(
        comp_address, comp_phone, comp_email
    ))
    
    # Build the PDF
    doc.build(elements)