"""
Order Confirmation PDF Generator
Place this file in: apps/masters/template/sales/order_confirmation_pdf.py

Usage:
    from apps.masters.template.sales.order_confirmation_pdf import generate_order_confirmation_pdf
    
    file_path, cdn_path = generate_order_confirmation_pdf(sale_order_id)
"""

import os
import random
import string
from decimal import Decimal

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


# ─────────────────────────────────────────
# COLOR PALETTE
# ─────────────────────────────────────────
PRIMARY     = colors.HexColor('#1A73E8')   # blue header
DARK        = colors.HexColor('#1C1C1C')   # near black text
LIGHT_GRAY  = colors.HexColor('#F5F7FA')   # table row bg
MID_GRAY    = colors.HexColor('#9E9E9E')   # muted text
SUCCESS     = colors.HexColor('#34A853')   # green confirmed badge
WHITE       = colors.white


def _unique_filename(document_type):
    """Generate unique filename same way as path_generate()"""
    unique_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) + '.pdf'
    doc_name = f"{document_type}_confirm_{unique_code}"
    file_path = os.path.join(settings.MEDIA_ROOT, 'doc_generater', doc_name)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    relative_file_path = os.path.join('doc_generater', doc_name)
    cdn_path = f"{settings.MEDIA_URL}{relative_file_path}"
    return file_path, cdn_path


def generate_order_confirmation_pdf(sale_order_id, format_value='CNL_Standard_Excl'):
    """
    Generate a clean order confirmation PDF.
    Returns: (file_path, cdn_path)
    """
    from apps.sales.models import SaleOrder, SaleOrderItems

    # ── Fetch Data ──────────────────────────────────────────────────────────
    sale_order = SaleOrder.objects.filter(sale_order_id=sale_order_id).first()
    if not sale_order:
        raise ValueError(f"SaleOrder {sale_order_id} not found")

    customer_name   = sale_order.customer_id.name if sale_order.customer_id else "Customer"
    order_no        = sale_order.order_no or "—"
    order_date      = str(sale_order.order_date) if sale_order.order_date else "—"
    total_amount    = Decimal(str(sale_order.total_amount or 0))
    billing_address = sale_order.billing_address or ""
    is_estimate     = str(sale_order.sale_estimate or "").lower() == "yes"
    doc_title       = "SALES QUOTATION" if is_estimate else "SALES ORDER"

    order_items = SaleOrderItems.objects.filter(sale_order_id=sale_order_id)

    # ── Company Info ─────────────────────────────────────────────────────────
    try:
        from apps.company.models import Companies
        company = Companies.objects.first()
        company_name  = company.name if company else "Rudhra Industries"
        company_phone = company.phone if hasattr(company, 'phone') and company.phone else "+91 95050 24999"
        company_email = company.email if hasattr(company, 'email') and company.email else "support@rudhra.com"
    except Exception:
        company_name  = "Rudhra Industries"
        company_phone = "+91 95050 24999"
        company_email = "support@rudhra.com"

    # ── File Setup ────────────────────────────────────────────────────────────
    file_path, cdn_path = _unique_filename("sale_order")

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        leftMargin=15*mm,
        rightMargin=15*mm,
        topMargin=15*mm,
        bottomMargin=15*mm,
    )

    styles = getSampleStyleSheet()
    elements = []

    # ── Styles ────────────────────────────────────────────────────────────────
    def style(name, **kwargs):
        return ParagraphStyle(name, **kwargs)

    s_company   = style('company',   fontSize=18, textColor=PRIMARY,   fontName='Helvetica-Bold', alignment=TA_LEFT)
    s_doc_title = style('doctitle',  fontSize=11, textColor=MID_GRAY,  fontName='Helvetica',      alignment=TA_LEFT)
    s_badge     = style('badge',     fontSize=10, textColor=SUCCESS,   fontName='Helvetica-Bold', alignment=TA_RIGHT)
    s_label     = style('label',     fontSize=8,  textColor=MID_GRAY,  fontName='Helvetica')
    s_value     = style('value',     fontSize=9,  textColor=DARK,      fontName='Helvetica-Bold')
    s_normal    = style('normal2',   fontSize=9,  textColor=DARK,      fontName='Helvetica')
    s_th        = style('th',        fontSize=9,  textColor=WHITE,     fontName='Helvetica-Bold', alignment=TA_CENTER)
    s_td_center = style('tdcenter',  fontSize=9,  textColor=DARK,      fontName='Helvetica',      alignment=TA_CENTER)
    s_td_right  = style('tdright',   fontSize=9,  textColor=DARK,      fontName='Helvetica',      alignment=TA_RIGHT)
    s_total_lbl = style('totallbl',  fontSize=10, textColor=DARK,      fontName='Helvetica-Bold', alignment=TA_RIGHT)
    s_total_val = style('totalval',  fontSize=11, textColor=PRIMARY,   fontName='Helvetica-Bold', alignment=TA_RIGHT)
    s_footer    = style('footer',    fontSize=8,  textColor=MID_GRAY,  fontName='Helvetica',      alignment=TA_CENTER)
    s_thanks    = style('thanks',    fontSize=13, textColor=PRIMARY,   fontName='Helvetica-Bold', alignment=TA_CENTER)

    PAGE_W = A4[0] - 30*mm  # usable width

    # ── HEADER ROW: Company name | Confirmed badge ────────────────────────────
    header_data = [[
        Paragraph(company_name, s_company),
        Paragraph('✔ ORDER CONFIRMED', s_badge),
    ]]
    header_table = Table(header_data, colWidths=[PAGE_W * 0.65, PAGE_W * 0.35])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(header_table)
    elements.append(Paragraph(doc_title, s_doc_title))
    elements.append(Spacer(1, 4*mm))
    elements.append(HRFlowable(width="100%", thickness=1, color=PRIMARY))
    elements.append(Spacer(1, 4*mm))

    # ── ORDER META: order no | date | customer ────────────────────────────────
    meta_data = [
        [
            Paragraph("Order No.", s_label),
            Paragraph("Order Date", s_label),
            Paragraph("Customer", s_label),
        ],
        [
            Paragraph(order_no, s_value),
            Paragraph(order_date, s_value),
            Paragraph(customer_name, s_value),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[PAGE_W/3]*3)
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), LIGHT_GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, 1), [WHITE]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#EEEEEE')),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 5*mm))

    # ── PRODUCT TABLE ─────────────────────────────────────────────────────────
    col_widths = [
        PAGE_W * 0.05,   # #
        PAGE_W * 0.45,   # Product
        PAGE_W * 0.15,   # Qty
        PAGE_W * 0.17,   # Rate
        PAGE_W * 0.18,   # Amount
    ]

    product_rows = [[
        Paragraph('#',        s_th),
        Paragraph('Product',  s_th),
        Paragraph('Qty',      s_th),
        Paragraph('Rate',     s_th),
        Paragraph('Amount',   s_th),
    ]]

    row_colors = []
    for idx, item in enumerate(order_items, start=1):
        product_name = item.product_id.name if item.product_id else "—"
        qty     = Decimal(str(item.quantity or 0))
        rate    = Decimal(str(item.rate or 0))
        amount  = Decimal(str(item.amount or qty * rate))

        bg = LIGHT_GRAY if idx % 2 == 0 else WHITE
        row_colors.append(('BACKGROUND', (0, idx), (-1, idx), bg))

        product_rows.append([
            Paragraph(str(idx), s_td_center),
            Paragraph(product_name, s_normal),
            Paragraph(str(int(qty)), s_td_center),
            Paragraph(f"₹{rate:,.2f}", s_td_right),
            Paragraph(f"₹{amount:,.2f}", s_td_right),
        ])

    product_table = Table(product_rows, colWidths=col_widths, repeatRows=1)
    ts = TableStyle([
        # Header
        ('BACKGROUND',    (0, 0), (-1, 0), PRIMARY),
        ('TEXTCOLOR',     (0, 0), (-1, 0), WHITE),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
        ('BOX',           (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        ('LINEBELOW',     (0, 0), (-1, 0),  0.5, colors.HexColor('#CCCCCC')),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
    ])
    for style_cmd in row_colors:
        ts.add(*style_cmd)
    product_table.setStyle(ts)
    elements.append(product_table)
    elements.append(Spacer(1, 3*mm))

    # ── GRAND TOTAL ───────────────────────────────────────────────────────────
    total_data = [[
        Paragraph("Grand Total", s_total_lbl),
        Paragraph(f"₹{total_amount:,.2f}", s_total_val),
    ]]
    total_table = Table(total_data, colWidths=[PAGE_W * 0.75, PAGE_W * 0.25])
    total_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), LIGHT_GRAY),
        ('TOPPADDING',    (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
        ('BOX',           (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 8*mm))

    # ── DIVIDER ───────────────────────────────────────────────────────────────
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#DDDDDD')))
    elements.append(Spacer(1, 5*mm))

    # ── THANK YOU MESSAGE ─────────────────────────────────────────────────────
    elements.append(Paragraph("Thank you for your order! 🎉", s_thanks))
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph(
        f"Need help? Contact us at <b>{company_email}</b> or <b>{company_phone}</b>",
        style('support', fontSize=9, textColor=MID_GRAY, fontName='Helvetica', alignment=TA_CENTER)
    ))
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph(
        f"© {company_name} — This is a system-generated document.",
        s_footer
    ))

    # ── BUILD ─────────────────────────────────────────────────────────────────
    doc.build(elements)
    print(f"✅ Order confirmation PDF generated: {file_path}")

    return file_path, cdn_path