import json
import copy as _copy_module
import os
from django.conf import settings
from django.shortcuts import get_object_or_404
from reportlab.platypus import PageBreak
from apps.company.models import company_logos
from apps.company.serializers import CompaniesSerializer
from apps.customer.models import CustomerAddresses
from apps.finance.models import BankAccount
from apps.masters.template.print_config_defaults import get_default_template_config, resolve_print_config
from apps.masters.template.table_defination import *
from apps.masters.utils.docs_variables import doc_data
from config.utils_methods import convert_amount_to_words, extract_product_data, format_phone_number, get_related_data


def _copy_config_for(print_config, copy_index):
    """
    Return a shallow-cloned print_config where copy_config.copy_labels contains
    only the label for the given copy index.  Used to stamp each printed copy
    with the right label (e.g. "Original", "Duplicate", "Triplicate").
    """
    if not print_config:
        return None
    cfg = _copy_module.deepcopy(print_config)
    copy_cfg = cfg.get('copy_config') or {}
    labels = copy_cfg.get('copy_labels') or ['Original']
    label = labels[copy_index] if copy_index < len(labels) else f'Copy {copy_index + 1}'
    cfg['copy_config'] = {'num_copies': 1, 'copy_labels': [label]}
    return cfg


def _num_copies(print_config):
    """Return the configured number of copies (minimum 1)."""
    cfg = (print_config or {}).get('copy_config') or {}
    try:
        return max(1, int(cfg.get('num_copies', 1)))
    except (TypeError, ValueError):
        return 1


def sale_order_sales_invoice_data(pk, document_type, format_value=None):
    """Fetch all data for sales order/invoice with proper tax handling"""
    
    # Get the relevant data from the doc_data dictionary
    model_data = doc_data.get(document_type)
    print("-" * 20)
    print("model_data : ", model_data)
    print("-" * 20)
    
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

    obj = get_object_or_404(model, pk=pk)
    print("-" * 20)
    print("object data : ", obj)
    print("-" * 20)
    
    customer_data_for_cust_data = serializer(obj).data
    
    print("-" * 20)
    print("customer_data_for_cust_data : ", customer_data_for_cust_data)
    print("-" * 20)
    
    # Get the invoice OrderedDict
    InvoiceNo = customer_data_for_cust_data.get('sale_invoice')
    ReturnNo = customer_data_for_cust_data.get('return_no')
    
    print("customer_data_for_cust_data.get('sale_return') : ", customer_data_for_cust_data.get('sale_return'))
    print("customer_data_for_cust_data.get('return_no') : ", customer_data_for_cust_data.get('return_no'))
    print("ReturnNo : ", ReturnNo)

    # Extract invoice_no and invoice_date
    final_invoice = InvoiceNo.get('invoice_no') if InvoiceNo else None
    final_invoiceDate = InvoiceNo.get('invoice_date') if InvoiceNo else None
    
    final_return = ReturnNo if ReturnNo else None
    
    obj = get_object_or_404(model, pk=pk)
    is_estimate = getattr(obj, 'sale_estimate', 'No') == 'Yes'
    sale_estimate = customer_data_for_cust_data.get('sale_estimate')
    doc_header = "SALES QUOTATION" if is_estimate else "SALES ORDER"
    
    print("-" * 30)
    print("format_value check : ", format_value)
    print("-" * 30)
    
    # Determine tax type based on format selection
    if format_value == 'CNL_Standard_Incl':
        print("Using Inclusive tax mode")
        tax_type = 'Inclusive'
    else:
        print("Using Exclusive tax mode")
        tax_type = 'Exclusive'
    
    print("final tax type : ", tax_type)
    
    itemstotal = 0
    itemstotal += float(customer_data_for_cust_data['item_value']) if customer_data_for_cust_data['item_value'] is not None else 0

    # Access dictionary keys correctly
    shipping_address = customer_data_for_cust_data.get("shipping_address")
    print("shipping_address : ", shipping_address)
    billing_address = customer_data_for_cust_data.get("billing_address")
    print("billing_address : ", billing_address)

    discountAmt = customer_data_for_cust_data.get("dis_amt")
    discountAmt = float(discountAmt) if discountAmt is not None else 0.0

    # Fetch shipment record
    shipment_record = related_model.objects.filter(
        **{related_filter_field: pk}
    ).first()

    shipping_charges = 0.0
    shipping_gst = 0.0
    shipping_gst_amount = 0.0

    if shipment_record:
        shipping_charges = float(getattr(shipment_record, 'shipping_charges', 0) or 0)
        shipping_gst = float(getattr(shipment_record, 'shipping_gst', 0) or 0)
        
        # Calculate GST on shipping charges
        shipping_gst_amount = (shipping_charges * shipping_gst) / 100 if shipping_gst > 0 else 0.0

    shipping_charges = round(shipping_charges, 2)
    shipping_gst_amount = round(shipping_gst_amount, 2)
    
    if billing_address and 'Andhra Pradesh' in billing_address:
        print("Intra-state transaction (CGST + SGST)")
    
    net_value = customer_data_for_cust_data.get('total_amount')

    # Retrieve related data
    items_data = get_related_data(item_model, items_serializer, item_model_pk, pk)
    print("items_data : ", items_data)
    related_data = get_related_data(related_model, related_serializer, related_filter_field, pk)
    print("related_data : ", related_data)
    related_data = related_data[0] if len(related_data) > 0 else {}
    
    # ====== COMPLETE COMPANY DATA FETCH ======
    company = Companies.objects.first()
    print("company : ", company)
    company_name = (company.name or '') if company else ''
    print("company_name : ", company_name)
    company_gst = (company.gst_tin or '') if company else ''
    print("company_gst : ", company_gst)
    company_address = (company.address or '') if company else ''
    print("company_address : ", company_address)
    company_phone = (company.phone or '') if company else ''
    print("company_phone : ", company_phone)
    company_email = (company.email or '') if company else ''
    print("company_email : ", company_email)
    
    # Safe fallback for logo
    company_logo_path = None
    attachment_path = None

    if company and isinstance(company.logo, list) and company.logo:
        attachment_path = company.logo[0].get('attachment_path')
        if attachment_path:
            company_logo_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, attachment_path))

    print("company_logo_filename:", attachment_path)
    print("company_logo_path:", company_logo_path)
    print("Exists:", os.path.exists(company_logo_path) if company_logo_path else False)

    company_logo = company_logo_path
    
    # Fetching Bank details 
    bank = BankAccount.objects.first()
    bank_name = bank.bank_name if bank else "N/A"
    bank_branch = bank.branch_name if bank else "N/A"
    bank_ifsc = bank.ifsc_code if bank else "N/A"
    bank_acno = bank.account_number if bank else "N/A"
    bank_actype = bank.account_type if bank else "N/A"

    # Extracting phone number from cust_address
    customer_id = list(model.objects.filter(**{item_model_pk: pk}).values_list('customer_id', flat=True))
    
    filter_kwargs = {"customer_id": customer_id[0], "address_type": "Billing"}
    billing_addr = CustomerAddresses.objects.filter(**filter_kwargs).first()

    city = str(billing_addr.city_id) if billing_addr and billing_addr.city_id else 'N/A'
    country = str(billing_addr.country_id) if billing_addr and billing_addr.country_id else 'N/A'

    phone_number = str(billing_addr.phone) if billing_addr and billing_addr.phone else 'N/A'
    phone = format_phone_number(phone_number) if phone_number != 'N/A' else 'N/A'
    dest = str(related_data.get('destination', 'N/A'))

    email = billing_addr.email if billing_addr and billing_addr.email else 'N/A'
    billing_state = billing_addr.state_id if billing_addr and billing_addr.state_id else 'N/A'

    # Initialize totals
    total_amt = 0
    total_qty = 0
    total_cgst = 0
    total_sgst = 0
    total_igst = 0
    total_disc_amt = 0
    taxable_value_total = 0
    cessAmt = 0
    party_old_balance = 0
    
    # Process items with proper tax handling
    for item in items_data:
        # Get item values
        quantity = float(item.get('quantity', 0)) if item.get('quantity') is not None else 0
        rate = float(item.get('rate', 0)) if item.get('rate') is not None else 0
        discount = float(item.get('discount', 0)) if item.get('discount') is not None else 0
        tax_rate = float(item.get('tax', 0)) if item.get('tax') is not None else 0
        
        # Calculate base amount (quantity * rate)
        base_amount = quantity * rate
        
        # Calculate discount amount
        discount_amount = (base_amount * discount) / 100
        
        # Calculate amount after discount
        amount_after_discount = base_amount - discount_amount
        
        # Handle tax based on tax type
        if tax_type == 'Inclusive':
            # For Inclusive tax: Tax is included in the price
            if tax_rate > 0:
                # Taxable value = Price / (1 + tax_rate/100)
                taxable_value = base_amount / (1 + (tax_rate / 100))
                tax_amount = base_amount - taxable_value
            else:
                taxable_value = base_amount
                tax_amount = 0
            
            # For Inclusive: total amount is the base amount (includes tax)
            item_total = base_amount - discount_amount  # Discount on tax-inclusive price
            
        else:  # Exclusive
            # For Exclusive tax: Tax is added on top
            taxable_value = base_amount
            tax_amount = (base_amount * tax_rate) / 100
            item_total = base_amount - discount_amount + tax_amount
        
        print(f"Item: {item.get('name')}, Tax Type: {tax_type}")
        print(f"  Rate: {rate}, Qty: {quantity}, Tax: {tax_rate}%")
        print(f"  Base: {base_amount}, Tax Amount: {tax_amount}")
        print(f"  Total: {item_total}")
        
        # Accumulate totals
        total_amt += item_total
        total_qty += quantity
        total_disc_amt += discount_amount
        taxable_value_total += taxable_value
        
        # Determine GST split
        if billing_state is None or billing_state == 'N/A' or billing_state == 'Andhra Pradesh':
            # Intra-state transaction → CGST + SGST
            print(f"Intra-state: billing_state={billing_state} → CGST+SGST")
            cgst = tax_amount / 2
            sgst = tax_amount / 2
            total_cgst += cgst
            total_sgst += sgst
        else:
            # Inter-state transaction → IGST
            print(f"Inter-state: billing_state={billing_state} → IGST")
            total_igst += tax_amount

    print(f"Final totals - total_cgst: {total_cgst}, total_sgst: {total_sgst}, total_igst: {total_igst}")
    print(f"total_disc_amt: {total_disc_amt}")
    print(f"taxable_value_total: {taxable_value_total}")

    # Extract product data with tax handling
    product_data = extract_product_data(items_data, tax_type=tax_type)
    
    # Calculate final amounts
    finalDiscount = discountAmt + total_disc_amt
    
    cessAmt = customer_data_for_cust_data.get("cess_amount")
    cessAmt = round(float(cessAmt) if cessAmt is not None else 0.0, 2)
    
    # Calculate final totals based on tax type
    if tax_type == 'Inclusive':
        # For Inclusive: Tax is already in item total
        final_amount = round(itemstotal - total_disc_amt, 2)
        print(f"Inclusive mode - Final amount: {final_amount}")
    else:
        # For Exclusive: Add tax to the total
        final_amount = round(
            itemstotal - total_disc_amt + total_cgst + total_sgst + total_igst + cessAmt + shipping_gst_amount, 
            2
        )
        print(f"Exclusive mode - Final amount: {final_amount}")
    
    # Calculate net value
    net_value = round(party_old_balance + final_amount - finalDiscount + shipping_charges, 2)
    
    # Calculate round off
    round_0ff = round(net_value - (party_old_balance + final_amount - finalDiscount + shipping_charges), 2)
    
    # Convert to words
    bill_amount_in_words = convert_amount_to_words(net_value)
    
    # Combine Date + Time
    raw_date = getattr(obj, date_value, None)
    raw_time = getattr(obj, "created_at", None)

    if raw_date:
        date_part = raw_date.strftime("%d-%m-%Y")
    else:
        date_part = ""

    if raw_time:
        time_part = raw_time.strftime("%I:%M %p")
    else:
        time_part = ""

    combined_date_time = f"{date_part}  {time_part}".strip()

    return {
        'sale_estimate': sale_estimate,
        'doc_header': doc_header,
        'final_invoice': final_invoice,
        'final_invoiceDate': final_invoiceDate,
        'return_no': final_return,
        # Company details
        'company_logo': company_logo or '',
        'company_name': company_name or '',
        'company_gst': company_gst or '',
        'company_address': company_address or '',
        'company_phone': company_phone or '',
        'company_email': company_email or '',
        # Bank details
        'bank_name': bank_name,
        'bank_branch': bank_branch,
        'bank_acno': bank_acno,
        'bank_ifsc': bank_ifsc,
        'bank_actype': bank_actype,
        'cust_bill_dtl': 'Customer Billing Detail',
        'number_lbl': model_data.get('number_lbl'),
        'date_lbl': model_data.get('date_lbl'),
        'doc_header': model_data.get('Doc_Header'),
        'net_lbl': model_data.get('net_lbl'),
        'number_value': customer_data_for_cust_data[number_value],
        'date_value': combined_date_time,
        'shipping_address': shipping_address,
        'billing_address': billing_address,
        'customer_name': customer_data_for_cust_data['customer']['name'],
        'city': city,
        'country': country,
        'phone': phone,
        'dest': dest,
        'email': email,
        'bill_amount_in_words': bill_amount_in_words,
        'product_data': product_data,
        'tax_type': tax_type,
        'itemstotal': itemstotal,
        'final_total': round(taxable_value_total - total_disc_amt, 2),
        'total_amt': total_amt,
        'total_qty': total_qty,
        'total_cgst': round(total_cgst, 2),
        'total_sgst': round(total_sgst, 2),
        'total_igst': round(total_igst, 2),
        'finalDiscount': finalDiscount,
        'shipping_charges': shipping_charges,
        'shipping_gst': shipping_gst,
        'shipping_gst_amount': shipping_gst_amount,
        'total_disc_amt': total_disc_amt,
        'cess_amount': cessAmt,
        'round_0ff': round_0ff,
        'party_old_balance': party_old_balance,
        'net_value': round(net_value, 2),
        'remarks': customer_data_for_cust_data.get("remarks", ""),
        'return_reason': customer_data_for_cust_data.get("return_reason", "")
    }


def sale_order_sales_invoice_doc(
    elements, doc, cust_bill_dtl, number_lbl, number_value, date_lbl, date_value,
    customer_name, billing_address, phone, city,
    product_data,
    total_qty, final_total, total_amt, total_cgst, total_sgst, total_igst,
    bill_amount_in_words, itemstotal, total_disc_amt, finalDiscount, 
    shipping_charges, shipping_gst_amount, round_0ff, cess_amount,
    party_old_balance, net_lbl, net_value, tax_type, remarks, print_config=None
):
    """Generate sales order document with proper tax display"""
    copies = _num_copies(print_config)
    for i in range(copies):
        if i > 0:
            elements.append(PageBreak())
        cfg = _copy_config_for(print_config, i)
        elements.append(doc_details(cust_bill_dtl, number_lbl, number_value, date_lbl, date_value, print_config=cfg))
        elements.append(customer_details(customer_name, billing_address, phone, city, print_config=cfg))
        # Pass show_gst based on tax type
        elements.append(product_details(product_data, show_gst=(tax_type != 'Inclusive'), print_config=cfg))
        elements.append(product_total_details(
            total_qty, itemstotal, final_total, total_disc_amt,
            show_gst=(tax_type != 'Inclusive'), print_config=cfg
        ))
        elements.append(product_total_details_inwords(
            bill_amount_in_words, itemstotal, finalDiscount, shipping_charges, shipping_gst_amount,
            total_cgst, total_sgst, total_igst, cess_amount, round_0ff,
            party_old_balance, net_lbl, net_value, tax_type=tax_type, print_config=cfg
        ))
        elements.append(declaration(print_config=cfg))
    doc.build(elements)


def sales_invoice_doc(
    elements, doc, company_logo, company_name, company_gst, company_address, company_phone, company_email,
    bank_name, bank_acno, bank_ifsc, bank_branch,
    number_lbl, number_value, date_lbl, date_value,
    customer_name, city, country, phone, dest, shipping_address, billing_address,
    product_data,
    total_qty, final_total, total_amt, total_cgst, total_sgst, total_igst,
    bill_amount_in_words, itemstotal, total_disc_amt, finalDiscount, 
    shipping_charges, shipping_gst_amount, cess_amount, round_0ff,
    party_old_balance, net_lbl, net_value, tax_type, remarks, print_config=None
):
    """Generate sales invoice document with proper tax display"""
    copies = _num_copies(print_config)
    for i in range(copies):
        if i > 0:
            elements.append(PageBreak())
        cfg = _copy_config_for(print_config, i)
        elements.append(invoice_doc_details(
            company_logo, company_name, company_gst, company_address, company_phone, company_email,
            number_lbl, number_value, date_lbl, date_value, print_config=cfg
        ))
        elements.append(invoice_customer_details(customer_name, city, country, phone, dest, shipping_address, billing_address, print_config=cfg))
        # Pass show_gst based on tax type
        elements.append(invoice_product_details(product_data, show_gst=(tax_type != 'Inclusive'), print_config=cfg))
        elements.append(invoice_product_total_details(
            total_qty, itemstotal, final_total, total_disc_amt,
            show_gst=(tax_type != 'Inclusive'), print_config=cfg
        ))
        elements.append(product_total_details_inwords(
            bill_amount_in_words, itemstotal, finalDiscount, shipping_charges, shipping_gst_amount,
            total_cgst, total_sgst, total_igst, cess_amount, round_0ff,
            party_old_balance, net_lbl, net_value, tax_type=tax_type, print_config=cfg
        ))
        elements.append(create_footer_section(bank_name, bank_acno, bank_ifsc, bank_branch, remarks, print_config=cfg))
        elements.append(declaration(print_config=cfg))
    doc.build(elements)


def sale_return_doc(
    elements, doc,
    company_name, company_address, company_phone,
    cust_bill_dtl, number_lbl, return_no, date_lbl, date_value,
    customer_name, billing_address, phone, city,
    product_data,
    total_qty, total_amt, cess_amount, total_cgst, total_sgst, total_igst, 
    itemstotal, finalDiscount, shipping_charges, shipping_gst_amount,
    bill_amount_in_words, round_0ff,
    party_old_balance, net_lbl, net_value, tax_type, return_reason, print_config=None
):
    """Generate sale return document with proper tax display"""
    heading_snapshot = list(elements)
    copies = _num_copies(print_config)
    elements.clear()

    for i in range(copies):
        if i > 0:
            elements.append(PageBreak())
        elements.extend(heading_snapshot)
        cfg = _copy_config_for(print_config, i)
        elements.append(return_doc_details(cust_bill_dtl, number_lbl, return_no, date_lbl, date_value, print_config=cfg))
        elements.append(return_customer_details_with_reason(customer_name, billing_address, phone, city, return_reason, print_config=cfg))
        elements.append(return_complete_table(
            data=product_data,
            total_qty=format_numeric(total_qty),
            sub_total=format_numeric(itemstotal),
            discount_amt=format_numeric(finalDiscount),
            shipping_charges=format_numeric(shipping_charges),
            shipping_gst=format_numeric(shipping_gst_amount),
            cess_amount=format_numeric(cess_amount),
            total_cgst=format_numeric(total_cgst),
            total_sgst=format_numeric(total_sgst),
            total_igst=format_numeric(total_igst),
            round_0ff=format_numeric(round_0ff),
            bill_total=format_numeric(net_value),
            amount_in_words=bill_amount_in_words,
            show_gst=(tax_type != 'Inclusive'),
            print_config=cfg
        ))
    doc.build(elements)


def delivery_challan_doc(
    elements, doc,
    company_logo, company_name, company_gst, company_address, company_phone, company_email,
    number_lbl, number_value, date_lbl, date_value,
    customer_name, city, country, phone, shipping_address, billing_address,
    product_data,
    total_qty, final_total, total_amt, total_cgst, total_sgst, total_igst,
    bill_amount_in_words, itemstotal, total_disc_amt, finalDiscount,
    transport_charges, cess_amount, round_0ff, net_value, tax_type,
    vehicle_name, driver_name, lr_no, total_boxes, remarks, print_config=None
):
    """Generate delivery challan document with proper tax display"""
    heading_snapshot = list(elements)
    copies = _num_copies(print_config)
    elements.clear()

    for i in range(copies):
        if i > 0:
            elements.append(PageBreak())
        elements.extend(heading_snapshot)
        cfg = _copy_config_for(print_config, i)
        elements.append(invoice_doc_details(
            company_logo, company_name, company_gst, company_address, company_phone, company_email,
            number_lbl, number_value, date_lbl, date_value, print_config=cfg
        ))
        elements.append(invoice_customer_details(customer_name, city, country, phone, '', shipping_address, billing_address, print_config=cfg))
        # Pass show_gst based on tax type
        elements.append(invoice_product_details(product_data, show_gst=(tax_type != 'Inclusive'), print_config=cfg))
        elements.append(invoice_product_total_details(
            total_qty, itemstotal, final_total, total_disc_amt,
            show_gst=(tax_type != 'Inclusive'), print_config=cfg
        ))
        elements.append(dc_product_total_details_inwords(
            bill_amount_in_words, itemstotal, finalDiscount, transport_charges,
            total_cgst, total_sgst, total_igst, cess_amount, round_0ff, net_value,
            tax_type=tax_type, print_config=cfg
        ))
        elements.append(dc_footer_section(
            vehicle_name=vehicle_name, driver_name=driver_name,
            lr_no=lr_no, total_boxes=total_boxes, remarks=remarks, print_config=cfg
        ))
        elements.append(declaration(print_config=cfg))
    doc.build(elements)


def delivery_challan_data(pk, format_value=None):
    """Fetch all data needed to generate a Delivery Challan PDF with proper tax handling"""
    from apps.sales.models import DeliveryChallans, DeliveryChallanItems
    from apps.sales.serializers import DeliveryChallansSerializer, DeliveryChallanItemsSerializer

    obj = get_object_or_404(DeliveryChallans, pk=pk)
    data = DeliveryChallansSerializer(obj).data

    # Determine tax type based on format selection
    if format_value == 'CNL_Standard_Incl':
        tax_type = 'Inclusive'
    else:
        tax_type = 'Exclusive'

    billing_address = data.get('billing_address') or ''
    shipping_address = data.get('shipping_address') or ''

    # Company
    company = Companies.objects.first()
    company_name = (company.name or '') if company else ''
    company_gst = (company.gst_tin or '') if company else ''
    company_address = (company.address or '') if company else ''
    company_phone = (company.phone or '') if company else ''
    company_email = (company.email or '') if company else ''
    company_logo = None
    if company and isinstance(company.logo, list) and company.logo:
        attachment_path = company.logo[0].get('attachment_path')
        if attachment_path:
            company_logo = os.path.normpath(os.path.join(settings.MEDIA_ROOT, attachment_path))

    # Bank
    bank = BankAccount.objects.first()
    bank_name = bank.bank_name if bank else 'N/A'
    bank_branch = bank.branch_name if bank else 'N/A'
    bank_ifsc = bank.ifsc_code if bank else 'N/A'
    bank_acno = bank.account_number if bank else 'N/A'

    # Customer billing address details
    customer_raw_id = list(
        DeliveryChallans.objects.filter(delivery_challan_id=pk).values_list('customer_id', flat=True)
    )
    billing_addr = CustomerAddresses.objects.filter(
        customer_id=customer_raw_id[0], address_type='Billing'
    ).first() if customer_raw_id else None

    city = str(billing_addr.city_id) if billing_addr and billing_addr.city_id else 'N/A'
    country = str(billing_addr.country_id) if billing_addr and billing_addr.country_id else 'N/A'
    phone_number = str(billing_addr.phone) if billing_addr and billing_addr.phone else 'N/A'
    phone = format_phone_number(phone_number) if phone_number != 'N/A' else 'N/A'
    email = billing_addr.email if billing_addr and billing_addr.email else 'N/A'

    # Items with proper tax handling
    items_data = get_related_data(DeliveryChallanItems, DeliveryChallanItemsSerializer, 'delivery_challan_id', pk)

    itemstotal = float(data.get('item_value') or 0)
    discount_amt = float(data.get('dis_amt') or 0)
    total_qty = 0
    total_cgst = 0
    total_sgst = 0
    total_igst = 0
    total_disc_amt = 0
    
    # Get billing state for tax calculation
    billing_state = billing_addr.state_id if billing_addr and billing_addr.state_id else 'N/A'

    for item in items_data:
        quantity = float(item.get('quantity') or 0)
        rate = float(item.get('rate') or 0)
        discount = float(item.get('discount') or 0)
        tax_rate = float(item.get('tax') or 0)
        
        total_qty += quantity
        
        # Calculate discount amount
        discount_amount = (quantity * rate * discount) / 100
        total_disc_amt += discount_amount
        
        # Calculate tax based on type
        base_amount = quantity * rate
        
        if tax_type == 'Inclusive':
            # For Inclusive: Tax is in the price
            if tax_rate > 0:
                taxable_value = base_amount / (1 + (tax_rate / 100))
                tax_amount = base_amount - taxable_value
            else:
                tax_amount = 0
        else:
            # For Exclusive: Tax is added
            tax_amount = (base_amount * tax_rate) / 100
        
        # Determine GST split
        if billing_state is None or billing_state == 'N/A' or billing_state == 'Andhra Pradesh':
            # Intra-state
            total_cgst += tax_amount / 2
            total_sgst += tax_amount / 2
        else:
            # Inter-state
            total_igst += tax_amount

    product_data = extract_product_data(items_data, tax_type=tax_type)

    transport_charges = round(float(data.get('transport_charges') or 0), 2)
    cess_amount = round(float(data.get('cess_amount') or 0), 2)
    
    # Calculate final totals based on tax type
    if tax_type == 'Inclusive':
        final_amount = round(itemstotal - total_disc_amt, 2)
    else:
        final_amount = round(itemstotal - total_disc_amt + total_cgst + total_sgst + total_igst + cess_amount, 2)
    
    final_discount = discount_amt + total_disc_amt
    net_value = round(final_amount - final_discount + transport_charges, 2)
    round_off = round(net_value - (final_amount - final_discount + transport_charges), 2)
    bill_amount_in_words = convert_amount_to_words(net_value)

    # Date + Time
    raw_date = obj.challan_date
    raw_time = obj.created_at
    date_part = raw_date.strftime('%d-%m-%Y') if raw_date else ''
    time_part = raw_time.strftime('%I:%M %p') if raw_time else ''
    combined_date_time = f'{date_part}  {time_part}'.strip()

    # Append dispatch info to remarks
    dispatch_parts = []
    if obj.vehicle_name:
        dispatch_parts.append(f'Vehicle: {obj.vehicle_name}')
    if obj.driver_name:
        dispatch_parts.append(f'Driver: {obj.driver_name}')
    if obj.lr_no:
        dispatch_parts.append(f'LR No: {obj.lr_no}')
    if obj.total_boxes:
        dispatch_parts.append(f'Boxes: {obj.total_boxes}')
    remarks = data.get('remarks') or ''
    if dispatch_parts:
        remarks = (remarks + ' | ' if remarks else '') + ', '.join(dispatch_parts)

    return {
        'company_logo': company_logo or '',
        'company_name': company_name,
        'company_gst': company_gst,
        'company_address': company_address,
        'company_phone': company_phone,
        'company_email': company_email,
        'bank_name': bank_name,
        'bank_acno': bank_acno,
        'bank_ifsc': bank_ifsc,
        'bank_branch': bank_branch,
        'number_lbl': 'Challan No.',
        'date_lbl': 'Challan Date',
        'number_value': data.get('challan_no'),
        'date_value': combined_date_time,
        'customer_name': data['customer']['name'],
        'city': city,
        'country': country,
        'phone': phone,
        'dest': 'N/A',
        'email': email,
        'billing_address': billing_address,
        'shipping_address': shipping_address,
        'product_data': product_data,
        'tax_type': tax_type,
        'itemstotal': itemstotal,
        'final_total': round(itemstotal - total_disc_amt, 2),
        'total_amt': itemstotal,
        'total_qty': total_qty,
        'total_cgst': round(total_cgst, 2),
        'total_sgst': round(total_sgst, 2),
        'total_igst': round(total_igst, 2),
        'finalDiscount': final_discount,
        'transport_charges': transport_charges,
        'total_disc_amt': total_disc_amt,
        'cess_amount': cess_amount,
        'round_0ff': round_off,
        'net_value': net_value,
        'bill_amount_in_words': bill_amount_in_words,
        'remarks': data.get('remarks') or '',
        'vehicle_name': obj.vehicle_name or '',
        'driver_name': obj.driver_name or '',
        'lr_no': obj.lr_no or '',
        'total_boxes': obj.total_boxes,
    }


# Helpers
def num_val(value):
    """Return safe numeric value"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def str_val(value):
    """Return safe string value"""
    return str(value) if value not in [None, '', []] else 'N/A'


def generate_sale_order_pdf(sale_order_id):
    """Generate PDF for a specific sale order and return file_path and cdn_path"""
    from reportlab.platypus import SimpleDocTemplate
    from reportlab.lib.pagesizes import letter
    from apps.company.models import Companies
    from apps.masters.models import DocumentPrintTemplate
    import uuid
    
    # Create directory if it doesn't exist
    doc_generater_dir = os.path.join(settings.MEDIA_ROOT, 'doc_generater')
    os.makedirs(doc_generater_dir, exist_ok=True)
    
    # Get order details for filename
    from apps.sales.models import SaleOrder
    sale_order = SaleOrder.objects.filter(sale_order_id=sale_order_id).first()
    order_no = sale_order.order_no if sale_order else str(sale_order_id)[:8]
    
    filename = f"sale_order_{order_no}_{uuid.uuid4().hex[:4]}.pdf"
    file_path = os.path.join(doc_generater_dir, filename)
    cdn_path = f"/cdn/doc_generater/{filename}"
    
    # Load print config
    try:
        company = Companies.objects.first()
        template_obj = None
        if company:
            template_obj = DocumentPrintTemplate.objects.filter(
                company=company,
                document_type="sale_order",
                is_default=True,
                is_deleted=False,
                is_active=True,
            ).first()
        print_config = resolve_print_config(template_obj, "sale_order")
    except Exception as e:
        print_config = get_default_template_config("sale_order")
    
    # Generate PDF in Exclusive mode
    pdf_data = sale_order_sales_invoice_data(sale_order_id, "sale_order", 'CNL_Standard_Excl')
    
    # Determine doc header
    doc_header = "SALES QUOTATION" if pdf_data.get('sale_estimate') == 'Yes' else "SALES ORDER"
    
    # Generate PDF with doc_heading
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    elements = []
    
    # from apps.masters.template.doc_heading import doc_heading
    elements, doc = doc_heading(file_path, doc_header, 'BILL OF SUPPLY', print_config=print_config)
    
    sale_order_sales_invoice_doc(
        elements, doc,
        pdf_data['cust_bill_dtl'], pdf_data['number_lbl'], pdf_data['number_value'],
        pdf_data['date_lbl'], pdf_data['date_value'],
        pdf_data['customer_name'], pdf_data['billing_address'], pdf_data['phone'], pdf_data['city'],
        pdf_data['product_data'],
        pdf_data['total_qty'], pdf_data['final_total'], pdf_data['total_amt'],
        pdf_data['total_cgst'], pdf_data['total_sgst'], pdf_data['total_igst'],
        pdf_data['bill_amount_in_words'], pdf_data['itemstotal'], pdf_data['total_disc_amt'],
        pdf_data['finalDiscount'], pdf_data['shipping_charges'], pdf_data.get('shipping_gst_amount', 0.0), 
        pdf_data['round_0ff'], pdf_data['cess_amount'],
        pdf_data['party_old_balance'], pdf_data['net_lbl'], pdf_data['net_value'],
        pdf_data['tax_type'], pdf_data['remarks'],
        print_config=print_config
    )
    
    return file_path, cdn_path