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


def _fmt_date(value):
    """Format date/datetime to DD/MM/YYYY or DD/MM/YYYY HH:MM:SS.
    Time is only shown if it is not midnight (00:00:00)."""
    if not value:
        return ''
    s = str(value).strip().replace('T', ' ')
    parts = s.split(' ')
    date_part = parts[0]
    time_part = parts[1] if len(parts) > 1 else ''
    try:
        d = date_part.split('-')
        if len(d) == 3 and len(d[0]) == 4:
            formatted = f"{d[2]}/{d[1]}/{d[0]}"
            if time_part and time_part not in ('00:00:00', '00:00'):
                formatted += f" {time_part}"
            return formatted
    except Exception:
        pass
    return s


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
    company_name = (company.name or '') if company else ''
    company_address = (company.address or '') if company else ''
    company_phone = (company.phone or '') if company else ''
    company_email = (company.email or '') if company else ''

    # Get vendor details
    vendor = obj.vendor
    vendor_name = (vendor.name or '') if vendor else ''

    # Get billing address — guard against vendor being None
    billing_address = None
    if vendor:
        billing_address = VendorAddress.objects.filter(
            vendor_id=vendor.vendor_id,
            address_type="Billing"
        ).first()

    # Format amounts — use `or 0` so None values don't raise TypeError
    amount = float(payment_data.get('amount') or 0)
    outstanding = float(payment_data.get('outstanding_amount') or 0)
    total = float(payment_data.get('total_amount') or 0)

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
        'billing_address': (billing_address.address or '') if billing_address else '',
        'email': (billing_address.email or company_email) if billing_address else company_email,
        'phone': (billing_address.phone or '') if billing_address else '',
        
        # Payment details
        'invoice_no': payment_data.get('bill_no', ''),
        'invoice_date': _fmt_date(payment_data.get('bill_date')),
        'payment_method': payment_data.get('payment_method', ''),
        'cheque_no': payment_data.get('cheque_no') or '',
        'receipt_no': payment_data.get('payment_receipt_no', ''),
        'receipt_date': _fmt_date(payment_data.get('payment_date')),
        
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
        'cust_bill_dtl' : 'Vendor Name',
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
    amount_in_words, receipt_no, print_config=None
):
    elements.extend(return_company_header(company_name, company_address, company_phone))
    elements.append(doc_details(cust_bill_dtl, number_lbl, receipt_no, date_lbl, receipt_date, print_config=print_config))
    elements.append(payment_customer_details(vendor_name, billing_address, phone, email, print_config=print_config))
    elements.append(payment_details_table(payment_data, print_config=print_config))
    elements.append(payment_amount_summary(outstanding, amount_in_words, print_config=print_config))
    doc.build(elements)