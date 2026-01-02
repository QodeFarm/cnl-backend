import datetime
import random
from django.shortcuts import get_object_or_404
from apps.vendor.models import VendorAddress
from apps.masters.template.table_defination import declaration, doc_details, payment_amount_summary, payment_customer_details, payment_details_table, return_company_header
from apps.masters.utils.docs_variables import doc_data
from apps.company.models import Companies
from apps.purchase.models import BillPaymentTransactions
from apps.sales.models import PaymentTransactions
from config.utils_methods import convert_amount_to_words
from django.utils.timezone import now


def billpayment_receipt_data(pk, document_type):
    """Extracts data needed for payment receipt generation"""
    model_data = doc_data.get(document_type)
    if not model_data:
        raise ValueError(f"Unknown document type: {document_type}")

    # Get the payment transaction
    obj = get_object_or_404(BillPaymentTransactions, transaction_id=pk)
    payment_data = model_data['Serializer'](obj).data
    print("-"*20)
    print("payment_data : ", payment_data)
    print("-"*20)
    # Get company details
    company = Companies.objects.first()
    company_name = company.name if company else "N/A"
    company_address = company.address if company and company.address else "Address\xa0Not\xa0Provided"
    company_phone = company.phone if company else "N/A"
    company_email = company.email if company else "N/A"
    
    # Get vendor details
    vendor = obj.vendor
    vendor_name = vendor.name if vendor else "N/A"
    
    # Get billing address
    billing_address = VendorAddress.objects.filter(
        vendor_id=vendor.vendor_id,
        address_type="Billing"
    ).first()
    
    # Format amounts
    amount = float(payment_data.get('amount', 0))
    outstanding = float(payment_data.get('outstanding_amount', 0))
    total = float(payment_data.get('total_amount', 0))
    
    # Generate voucher details
    current_date = now()
    voucher_no = f"{random.randint(100,999)}/{random.randint(1,12)}/{current_date.year}"
    voucher_date = current_date.strftime("%d/%m/%Y")
    transfer_date = (current_date - datetime.timedelta(days=1)).strftime("%d/%m/%Y")
    
    return {
        # Company details
        'company_name': company_name,
        'company_address': company_address,
        'company_phone': company_phone,
        'company_email': company_email,
        
        # vendor details
        'vendor_name': vendor_name,
        'billing_address': billing_address.address if billing_address else "N/A",
        'email': billing_address.email if billing_address else company_email,
        'phone': billing_address.phone if billing_address else "N/A",
        
        # Payment details
        'invoice_no': payment_data['bill_no'],
        'invoice_date': payment_data['bill_date'],
        'payment_method': payment_data['payment_method'],
        'cheque_no': payment_data.get('cheque_no', 'N/A'),
        'receipt_no': payment_data['payment_receipt_no'],
        'receipt_date': payment_data['payment_date'],
        
        # Amounts
        'amount': amount,
        'outstanding': outstanding,
        'total': total,
        'amount_in_words': convert_amount_to_words(amount),
        
        # Voucher details
        'voucher_no': voucher_no,
        'voucher_date': voucher_date,
        'transfer_name': "CAMARA BANK ODA",
        'transfer_date': transfer_date,
        
        # Labels from doc_data
        'cust_bill_dtl' : 'vendor Name',
        'number_lbl': model_data['number_lbl'],
        'date_lbl': model_data['date_lbl'],
        'doc_header': model_data['Doc_Header'],
    }
    
def billpayment_receipt_doc(
    elements, doc, company_name, company_address, company_phone,
    cust_bill_dtl, number_lbl, invoice_no, date_lbl, receipt_date,
    vendor_name, billing_address, phone, email,
    payment_data,
    amount, outstanding, total,
    amount_in_words,receipt_no
):
    
    # 1. Add company header
    elements.extend(
        return_company_header(company_name, company_address, company_phone)
    )
    # Append document details
    elements.append(doc_details(
        cust_bill_dtl, number_lbl, receipt_no, date_lbl, receipt_date
    ))
    
    # Append vendor details (modified for payment receipt)
    elements.append(payment_customer_details(
        vendor_name, billing_address, phone, email
    ))
    
    # Append payment details table
    elements.append(payment_details_table(payment_data))
    
    # Append amount summary
    elements.append(payment_amount_summary(
        outstanding, amount_in_words
    ))
    
    # Build the PDF
    doc.build(elements)