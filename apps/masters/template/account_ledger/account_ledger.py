import datetime
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from apps.customer.models import CustomerAddresses
from apps.finance.models import JournalEntryLines
from apps.company.models import Companies
from apps.masters.template.table_defination import doc_details, ledger_amount_summary, ledger_details_table, ledger_doc_details, ledger_period_details, return_company_header
from apps.masters.utils.docs_variables import doc_data
from apps.vendor.models import VendorAddress
from config.utils_methods import convert_amount_to_words


# def ledger_document_data(request, account_id, document_type):
#     """
#     Fetch ledger data from JournalEntryLines for Ledger document
#     """

#     model_data = doc_data.get(document_type)
#     print("-"*20)
    
#     print("model data : ", model_data)
    
#     print("-"*20)
#     if not model_data:
#         raise ValueError(f"Unknown document type: {document_type}")

#     # Fetch company
#     company = Companies.objects.first()

#     company_name = company.name if company else "N/A"
#     company_address = company.address if company and company.address else "Address Not Provided"
#     company_phone = company.phone if company else "N/A"
#     company_email = company.email if company else "N/A"

#     # Fetch journal entries for ledger
#     ledger_qs = JournalEntryLines.objects.filter(
#         ledger_account_id=account_id
#     ).order_by('created_at')

#     ledger_rows = []
#     debit_total = 0
#     credit_total = 0
#     running_balance = 0
    
#     print("ledger_qs : ", ledger_qs)

#     for row in ledger_qs:
#         debit = float(row.debit or 0)
#         credit = float(row.credit or 0)

#         running_balance += (debit - credit)

#         ledger_rows.append({
#             'date': row.created_at.strftime('%d/%m/%Y'),
#             'voucher_no': row.voucher_no,
#             'description': row.description,
#             'debit': debit,
#             'credit': credit,
#             'balance': running_balance
#         })

#         debit_total += debit
#         credit_total += credit

#     closing_balance = running_balance
    
#     from_date = request.GET.get('created_at_after'),
#     to_date = request.GET.get('created_at_before'),
#     period_name = request.GET.get('period_name'),

#     return {
#         # Company details
#         'company_name': company_name,
#         'company_address': company_address,
#         'company_phone': company_phone,
#         'company_email': company_email,

#         # Ledger details
#         'ledger_name': ledger_qs.first().ledger_account_id.name if ledger_qs.exists() else "N/A",
#         'ledger_data': ledger_rows,
        
#         'from_date': from_date,
#         'to_date': to_date,
#         # 'period_name': period_name,


#         # Totals
#         'debit_total': debit_total,
#         'credit_total': credit_total,
#         'closing_balance': closing_balance,
#         'amount_in_words': convert_amount_to_words(abs(closing_balance)),

#         # Document labels
#         'doc_header': model_data['Doc_Header'],
#         'number_lbl': model_data['number_lbl'],
#         'date_lbl': model_data['date_lbl'],
#         'doc_date': now().strftime('%d/%m/%Y'),
#     }

def ledger_document_data(request, pk, document_type):
    """
    pk = filter type (customer_id / vendor_id / ledger_account_id / city_id)
    actual UUID comes from request.GET
    """

    model_data = doc_data.get(document_type)
    if not model_data:
        raise ValueError(f"Unknown document type: {document_type}")

    # ---------------------------
    # Company
    # ---------------------------
    company = Companies.objects.first()

    company_name = company.name if company else "N/A"
    company_address = company.address if company and company.address else "Address Not Provided"
    company_phone = company.phone if company else "N/A"
    company_email = company.email if company else "N/A"

    # ---------------------------
    # Base queryset
    # ---------------------------
    ledger_qs = JournalEntryLines.objects.all()

    # ---------------------------
    # Apply ACTIVE FILTER (pk)
    # ---------------------------
    filter_value = request.GET.get(pk)

    if filter_value:
        ledger_qs = ledger_qs.filter(**{pk: filter_value})
        
    # ---------------------------
    # ✅ CITY-BASED FILTER (FIX)
    # ---------------------------
    city_id = request.GET.get('city')

    if city_id:
        if pk == 'customer_id':
            ledger_qs = ledger_qs.filter(
                customer_id__in=CustomerAddresses.objects.filter(
                    city_id=city_id
                ).values_list('customer_id', flat=True)
            )

        elif pk == 'vendor_id':
            ledger_qs = ledger_qs.filter(
                vendor_id__in=VendorAddress.objects.filter(
                    city_id=city_id
                ).values_list('vendor_id', flat=True)
        )


    # ---------------------------
    # Date filters
    # ---------------------------
    from_date = request.GET.get('created_at_after')
    to_date = request.GET.get('created_at_before')

    if from_date:
        ledger_qs = ledger_qs.filter(created_at__date__gte=from_date)

    if to_date:
        ledger_qs = ledger_qs.filter(created_at__date__lte=to_date)

    ledger_qs = ledger_qs.order_by('created_at')

    # ---------------------------
    # Ledger calculations
    # ---------------------------
    ledger_rows = []
    debit_total = 0
    credit_total = 0
    running_balance = 0

    for row in ledger_qs:
        debit = float(row.debit or 0)
        credit = float(row.credit or 0)

        running_balance += (debit - credit)

        ledger_rows.append({
            'date': row.created_at.strftime('%d/%m/%Y'),
            'voucher_no': row.voucher_no,
            'description': row.description,
            'debit': debit,
            'credit': credit,
            'balance': running_balance
        })

        debit_total += debit
        credit_total += credit

    closing_balance = running_balance

    # ---------------------------
    # Ledger name (dynamic)
    # ---------------------------
    ledger_name = "Account Ledger"

    if pk == "ledger_account_id" and ledger_qs.exists():
        ledger_name = ledger_qs.first().ledger_account_id.name
    elif pk == "customer_id":
        ledger_name = "Customer Ledger"
    elif pk == "vendor_id":
        ledger_name = "Vendor Ledger"
    elif pk == "city_id":
        ledger_name = "City Ledger"

    return {
        # Company
        'company_name': company_name,
        'company_address': company_address,
        'company_phone': company_phone,
        'company_email': company_email,

        # Period
        'from_date': from_date,
        'to_date': to_date,

        # Ledger
        'ledger_name': ledger_name,
        'ledger_data': ledger_rows,

        # Totals
        'debit_total': debit_total,
        'credit_total': credit_total,
        'closing_balance': closing_balance,
        'amount_in_words': convert_amount_to_words(abs(closing_balance)),

        # Labels
        'doc_header': model_data['Doc_Header'],
        'number_lbl': model_data['number_lbl'],
        'date_lbl': model_data['date_lbl'],
        'doc_date': now().strftime('%d/%m/%Y'),
    }



def ledger_document_doc(
    elements, doc,
    company_name, company_address, company_phone, from_date, to_date, 
    ledger_name, number_lbl, date_lbl, doc_date,
    ledger_data,
    debit_total, credit_total, closing_balance,
    amount_in_words
):

    # 1. Company Header
    elements.extend(
        return_company_header(company_name, company_address, company_phone)
    )
    
    # ✅ 2.1 Period line (BEST PLACE)
    elements.append(
        ledger_period_details(from_date, to_date)
    )

    # 2. Document Details
    elements.append(
        ledger_doc_details(
            'Ledger Name',
            number_lbl,
            ledger_name,
            date_lbl,
            doc_date
        )
    )
    

    # 3. Ledger Transactions Table
    elements.append(
        ledger_details_table(ledger_data)
    )

    # 4. Ledger Summary
    elements.append(
        ledger_amount_summary(
            debit_total,
            credit_total,
            closing_balance,
            amount_in_words
        )
    )

    # 5. Declaration (optional – same pattern)
    # elements.append(declaration())

    doc.build(elements)
