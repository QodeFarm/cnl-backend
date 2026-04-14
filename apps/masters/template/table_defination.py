import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer, Image

from apps.company.models import Companies
from apps.masters.template.print_config_defaults import (
    SALES_PURCHASE_COLUMN_DEFINITIONS, COLOR_THEMES, PAPER_SIZES,
    get_header_color, get_width_scale, FONT_SIZE_MAP, PAPER_WIDTH_SCALE,
)


# ─────────────────────────────────────────────
# INTERNAL HELPERS
# ─────────────────────────────────────────────
def _resolve_product_columns(column_config, show_gst=True, print_config=None):
    """
    Returns an ordered list of column dicts from SALES_PURCHASE_COLUMN_DEFINITIONS
    that should be rendered, based on column_config (list of {key, visible, order}).
    Each returned dict includes 'base_width' for proportional sizing.
    Falls back to default behavior when column_config is None/empty.

    show_gst=False (Inclusive tax) ALWAYS removes the gst_amount column,
    regardless of what column_config says — GST is baked into the price.

    For small paper sizes (A5), auto-limits to essential columns so the table
    remains readable — this is standard ERP behavior for half-page formats.
    """
    if column_config:
        cfg_map = {c['key']: c for c in column_config}
        visible_cols = []
        for col_def in SALES_PURCHASE_COLUMN_DEFINITIONS:
            cfg = cfg_map.get(col_def['key'])
            if cfg is None:
                if col_def['required']:
                    visible_cols.append({**col_def, 'order': 99})
            elif cfg.get('visible', True) or col_def['required']:
                label = cfg.get('label') or col_def['label']
                visible_cols.append({**col_def, 'label': label, 'order': cfg.get('order', 99)})
        visible_cols.sort(key=lambda c: c.get('order', 99))
    else:
        visible_cols = list(SALES_PURCHASE_COLUMN_DEFINITIONS)

    # Always hide GST column for Inclusive tax — GST is baked into the price
    if not show_gst:
        visible_cols = [c for c in visible_cols if c['key'] != 'gst_amount']

    # ── Paper-size-aware auto-filtering ──────────────────────────
    # A5 (4.83" usable) cannot fit 8+ columns at any readable font size.
    # Auto-limit to essential columns — standard practice for half-page formats.
    paper_size = (print_config or {}).get('paper_size', 'Custom_11x16')
    s = PAPER_WIDTH_SCALE.get(paper_size, 1.0)
    if s <= 0.55:   # A5 (0.483) — essential columns only: S.No, Product, Qty, Rate, Total
        A5_KEEP = {'serial_no', 'product_name', 'quantity', 'rate', 'total_amount'}
        visible_cols = [c for c in visible_cols if c['key'] in A5_KEEP]
    elif s < 0.8:   # A4 (0.727), Letter (0.75) — drop decorative-only columns
        A4_DROP = {'boxes', 'discount_amount'}
        visible_cols = [c for c in visible_cols if c['key'] not in A4_DROP]

    return visible_cols


def _get_font_size(print_config, default=10):
    """Returns base font size from style_config: small=8, medium=10, large=12."""
    key = ((print_config or {}).get('style_config') or {}).get('font_size', 'medium')
    return FONT_SIZE_MAP.get(key, default)


def _effective_table_font_size(print_config):
    """
    Returns the font size to use inside the product table.
    Caps it based on paper size to prevent numeric column overflow:
      - A4 / Letter (s<0.9): max 10pt — 7.27" is too narrow for 12pt × 10 columns
      - A5 (s<0.6): max 9pt — 4.83" is very constrained
      - Custom_11x16 / A4_Landscape: allow up to large (12pt)
    """
    paper_size = (print_config or {}).get('paper_size', 'Custom_11x16')
    s = PAPER_WIDTH_SCALE.get(paper_size, 1.0)
    fs = _get_font_size(print_config)
    if s < 0.6:
        return min(fs, 9)
    elif s < 0.9:
        return min(fs, 10)
    return fs


def _compute_col_widths(visible_cols, total_width):
    """
    Compute per-column widths scaled to fill total_width proportionally,
    using each column's base_width as the ratio.
    """
    base_widths = [col.get('base_width', 0.8) for col in visible_cols]
    total_base = sum(base_widths)
    if total_base == 0:
        equal = total_width / len(visible_cols)
        return [equal] * len(visible_cols)
    return [(bw / total_base) * total_width for bw in base_widths]


def doc_heading(file_path, doc_header, sub_header, print_config=None):
    elements = []

    # Resolve paper size from config (defaults to Custom_11x16)
    paper_size_key = (print_config or {}).get('paper_size', 'Custom_11x16')
    paper_dims = PAPER_SIZES.get(paper_size_key, PAPER_SIZES['Custom_11x16'])
    page_width  = paper_dims['width']
    page_height = paper_dims['height']

    # Create the PDF document
    # Use 0.5" margins — matches usable_width values defined in PAPER_SIZES
    # (Default ReportLab margins are 1" which clips tables and causes page overflow)
    HALF_INCH = 0.5 * inch
    doc = SimpleDocTemplate(
        file_path,
        pagesize=(page_width, page_height),
        leftMargin=HALF_INCH,
        rightMargin=HALF_INCH,
        topMargin=HALF_INCH,
        bottomMargin=HALF_INCH,
    )
    
    # Get the default styles
    styles = getSampleStyleSheet()
    
    # For height-constrained paper sizes (A5, A4_Landscape) use smaller heading font
    # to save vertical space — both have only 7.27" usable height.
    _tight_height = paper_size_key in ('A5', 'A4_Landscape')
    _heading_fs  = 13 if _tight_height else 16
    _sub_fs      = 9  if _tight_height else 10

    def main_heading(doc_header):
        # Modify the heading style to be bold
        style_heading = ParagraphStyle(
            name='Heading1',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=_heading_fs,
            spaceAfter=2 if _tight_height else 3,
            spaceBefore=0,
            alignment=1,
        )
        elements.append(Paragraph(doc_header, style_heading))

    # Match exact header text (all uppercase as shown in your image)
    if doc_header.upper() == "SALES ORDER" or doc_header.upper() == "SALES QUOTATION":
        main_heading(doc_header.upper())  # Force uppercase to match your style

    elif doc_header == "TAX INVOICE":
        main_heading(doc_header)
        sub_style_heading = ParagraphStyle(
            name='Heading1Sub',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=_sub_fs,
            spaceAfter=2 if _tight_height else 3,
            spaceBefore=0,
            alignment=1,
        )
        elements.append(Paragraph(sub_header, sub_style_heading))
    elif doc_header.upper() in ("PURCHASE BILL", "PURCHASE RETURN"):
        # sub_header may be a list [name, address, phone, email] or a plain string.
        # Guard against both so we never crash with IndexError.
        if isinstance(sub_header, list) and len(sub_header) >= 4:
            styles = getSampleStyleSheet()
            bold_style = ParagraphStyle(
                    'BoldStyle',
                    parent=styles['Normal'],
                    fontName='Helvetica-Bold',
                    fontSize=14,
                    alignment=0,
                    textColor=colors.black
                )
            normal_style = ParagraphStyle(
                    'NormalStyle',
                    parent=styles['Normal'],
                    fontName='Helvetica',
                    fontSize=12,
                    alignment=0,
                    textColor=colors.black
                )
            elements.append(Paragraph(sub_header[0], bold_style))
            elements.append(Spacer(1, 2))
            elements.append(Paragraph(sub_header[1], normal_style))
            elements.append(Spacer(1, 1))
            elements.append(Paragraph('Phone No: ' + sub_header[2] + ' | ' + 'Email: ' + sub_header[3], normal_style))
            elements.append(Spacer(1, 18))
        main_heading(doc_header.upper())

    return elements, doc


def doc_details(cust_bill_dtl, sno_lbl, receipt_no, sdate_lbl, receipt_date, print_config=None):
    s = get_width_scale(print_config) if print_config else 1.0
    col_widths = [3.3*inch*s, 3.4*inch*s, 3.3*inch*s]

    # For A4 and smaller (s < 0.8): wrap cells in Paragraph so long SO numbers / dates
    # word-wrap instead of overflowing into adjacent cells on narrow paper sizes
    if s < 0.8:
        _styles = getSampleStyleSheet()
        _fs = max(7, _get_font_size(print_config) - 1)
        _cell_style = ParagraphStyle(
            'dd_cell_small', parent=_styles['Normal'],
            fontName='Helvetica-Bold', fontSize=_fs, leading=_fs + 2,
        )
        row = [
            Paragraph(cust_bill_dtl, _cell_style),
            Paragraph(f'{sno_lbl} : {receipt_no}', _cell_style),
            Paragraph(f'{sdate_lbl} : {receipt_date}', _cell_style),
        ]
    else:
        row = [cust_bill_dtl, f'{sno_lbl} : {receipt_no}', f'{sdate_lbl} : {receipt_date}']

    table_data_1 = [row]

    table = Table(table_data_1, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), get_header_color(print_config) if print_config else colors.skyblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, 0), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    return table

def customer_details(cust_name, billing_address, phone, city, print_config=None):
    styles = getSampleStyleSheet()
    fs = _get_font_size(print_config)
    style_normal = ParagraphStyle('cust_normal', parent=styles['Normal'], fontSize=fs)

    sec = (print_config or {}).get('section_config', {}) if print_config else {}
    show_billing  = sec.get('show_billing_address', True)
    show_shipping = sec.get('show_shipping_address', True)

    def _safe(val):
        """Return empty string for None/N/A values so PDF stays clean."""
        if val is None:
            return ''
        s = str(val).strip()
        return '' if s.lower() in ('none', 'n/a', 'null', '-') else s

    address_text = _safe(billing_address)
    phone_text   = _safe(phone)
    city_text    = _safe(city)

    billing_html = f"<b>{_safe(cust_name)}</b>"
    if show_billing and address_text:
        billing_html += f"<br/>{address_text}"

    shipping_parts = []
    if show_shipping:
        if phone_text:
            shipping_parts.append(f"<b>Mobile:</b> {phone_text}")
        if city_text:
            shipping_parts.append(f"<b>Destination:</b> {city_text}")
    shipping_html = "<br/>".join(shipping_parts)

    billing_content  = Paragraph(billing_html, style_normal)
    shipping_content = Paragraph(shipping_html, style_normal)

    table_data = [[billing_content, shipping_content]]

    s = get_width_scale(print_config) if print_config else 1.0
    table_col_widths = [6.7*inch*s, 3.3*inch*s]
    
    table = Table(table_data, colWidths=table_col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (1, 0), (1, -1), 'TOP'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, 0), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    return table

def format_numeric(cell):
    try:
        return "{:,.2f}".format(float(cell))
    except (ValueError, TypeError):
        return str(cell)

# def product_details(data, show_gst=True):
#     style_normal = getSampleStyleSheet()['Normal']

#     tbl_3_col_widths = [
#         0.5 * inch, 2.0 * inch, 0.7 * inch, 0.7 * inch, 0.8 * inch,
#         1.0 * inch, 1.0 * inch, 0.7 * inch, 0.8 * inch
#     ]

#     table_3_heading = [["Idx", "Product", "Boxes", "Qty", "Unit Name", "Rate", "Amount", "Disc(%)", "Disc(Rs)"]]

#     if show_gst:
#         table_3_heading[0].append("GST(Rs)")
#         table_3_heading[0].append("Total Amount")
#         tbl_3_col_widths += [0.8 * inch, 1.0 * inch]
#     else:
#         table_3_heading[0].append("Total Amount")
#         tbl_3_col_widths += [1.0 * inch]

#     for index, item in enumerate(data):
#         if len(item) < 11:
#             continue

#         row = item[:9]  # First 9 fields are common

#         if show_gst:
#             row.append(format_numeric(item[9]))  # GST(Rs)
#             row.append(format_numeric(item[10]))  # Total Amount
#         else:
#             row.append(format_numeric(item[10]))  # Total Amount (shift left)

#         wrapped_row = [Paragraph(str(cell), style_normal) for cell in row]
#         table_3_heading.append(wrapped_row)

#     # Ensure minimum rows for spacing
#     while len(table_3_heading) < 6:
#         table_3_heading.append([" "] * len(table_3_heading[0]))

#     table = Table(table_3_heading, colWidths=tbl_3_col_widths)
#     # table = Table(table_3_heading, colWidths=tbl_3_col_widths)
#     table.setStyle(TableStyle([
#         # Basic styling
#         ('BACKGROUND', (0, 0), (-1, 0), colors.skyblue),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        
#         # Alignment
#         ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # Header alignment
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#         ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),  # Numeric columns right-aligned
#         ('ALIGN', (0, 1), (1, -1), 'LEFT'),    # Text columns left-aligned
        
#         # Vertical lines
#         ('LINEBEFORE', (0, 0), (-1, -1), 1, colors.black),  
#         ('LINEAFTER', (6, 0), (10, -1), 1, colors.black),   
        
#         # Horizontal lines
#         ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),  # Header top
#         ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),  # Header bottom
#         ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),  # Last row
        
#         # Increase row padding for spacing
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
#         ('TOPPADDING', (0, 0), (-1, -1), 12),
#         ('LEFTPADDING', (0, 0), (-1, -1), 6),
#         ('RIGHTPADDING', (0, 0), (-1, -1), 6),
#     ]))
    
#     return table

def product_details(data, show_gst=True, print_config=None):
    styles = getSampleStyleSheet()
    fs = _effective_table_font_size(print_config)
    style_normal = ParagraphStyle('prod_normal', parent=styles['Normal'], fontSize=fs)
    header_color = get_header_color(print_config) if print_config else colors.skyblue
    width_scale  = get_width_scale(print_config)  if print_config else 1.0

    BASE_TOTAL_WIDTH = 10.0 * inch  # usable width for Custom_11x16
    TOTAL_WIDTH = BASE_TOTAL_WIDTH * width_scale

    # Resolve visible columns
    col_config   = (print_config or {}).get('column_config') if print_config else None
    visible_cols = _resolve_product_columns(col_config, show_gst, print_config=print_config)

    headers    = [col['label'] for col in visible_cols]
    col_widths = _compute_col_widths(visible_cols, TOTAL_WIDTH)

    # Keys that should be right-aligned (numeric) and formatted
    NUMERIC_KEYS = {'quantity', 'rate', 'amount', 'discount_percent', 'discount_amount', 'gst_amount', 'total_amount', 'boxes'}

    table_data = [headers]

    for item in data:
        if not isinstance(item, (list, tuple)):
            continue
        row = []
        for col in visible_cols:
            idx = col.get('data_index', 0)
            raw = item[idx] if idx < len(item) else ''
            if col['key'] in NUMERIC_KEYS:
                # Plain string — ReportLab won't break mid-number (no space to break on)
                cell = format_numeric(raw)
            elif col['key'] == 'product_name':
                # Only product_name needs Paragraph for proper word-wrap
                cell = Paragraph(str(raw or ''), style_normal)
            elif col['key'] == 'unit':
                # Wrap unit name so multi-word names (e.g. "Stock Unit") word-wrap in narrow columns
                cell = Paragraph(str(raw or ''), style_normal) if raw not in (None, '', '-') else ''
            else:
                cell = str(raw) if raw not in (None, '', '-') else ''
            row.append(cell)
        table_data.append(row)

    num_columns = len(visible_cols)
    # A5 gets fewer padding rows — small page has limited height to spare
    min_total_rows = 4 if width_scale <= 0.55 else 6
    while len(table_data) < min_total_rows:
        table_data.append([' '] * num_columns)

    table = Table(table_data, colWidths=col_widths)

    NUMERIC_KEYS = {'quantity', 'rate', 'amount', 'discount_percent', 'discount_amount', 'gst_amount', 'total_amount'}
    # Reduce cell padding on narrow paper sizes to reclaim column width
    cell_pad = max(3, int(5 * width_scale))
    row_pad  = max(4, int(8 * width_scale))
    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), fs),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),           # header row: centre all
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),             # data rows default left
        ('LINEBEFORE', (0, 0), (-1, -1), 1, colors.black),
        ('LINEAFTER', (-1, 0), (-1, -1), 1, colors.black),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), row_pad),
        ('TOPPADDING', (0, 0), (-1, -1), row_pad),
        ('LEFTPADDING', (0, 0), (-1, -1), cell_pad),
        ('RIGHTPADDING', (0, 0), (-1, -1), cell_pad),
    ]
    # Right-align numeric data columns dynamically
    for ci, col in enumerate(visible_cols):
        if col['key'] in NUMERIC_KEYS:
            style_cmds.append(('ALIGN', (ci, 1), (ci, -1), 'RIGHT'))

    table.setStyle(TableStyle(style_cmds))
    return table



def _fmt_total(val):
    """Format a totals-row numeric value with commas and 2 decimal places."""
    if val is None or str(val).strip() in ('', '-'):
        return ''
    try:
        return '{:,.2f}'.format(round(float(val), 2))
    except (ValueError, TypeError):
        return str(val)


def product_total_details(ttl_Qty, final_Amount, ttl_Amount, total_disc, show_gst=False, print_config=None):
    """
    Renders the totals row below the product table.
    Dynamically matches visible columns from print_config so widths stay aligned.
    """
    width_scale  = get_width_scale(print_config) if print_config else 1.0
    TOTAL_WIDTH  = 10.0 * inch * width_scale
    fs           = _effective_table_font_size(print_config)

    col_config   = (print_config or {}).get('column_config') if print_config else None
    visible_cols = _resolve_product_columns(col_config, show_gst, print_config=print_config)
    col_widths   = _compute_col_widths(visible_cols, TOTAL_WIDTH)

    # Map column key → value to display in totals row (formatted)
    value_map = {
        'serial_no':        '',
        'product_name':     'Total',
        'boxes':            '',
        'quantity':         _fmt_total(ttl_Qty),
        'unit':             '',
        'rate':             '',
        'amount':           _fmt_total(final_Amount),
        'discount_percent': '',
        'discount_amount':  _fmt_total(total_disc),
        'gst_amount':       '',
        'total_amount':     _fmt_total(ttl_Amount),
    }

    row = [value_map.get(col['key'], '') for col in visible_cols]

    cell_pad = max(3, int(5 * width_scale))
    table = Table([row], colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), get_header_color(print_config) if print_config else colors.skyblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), fs),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), cell_pad),
        ('RIGHTPADDING', (0, 0), (-1, -1), cell_pad),
    ]))
    return table

def product_total_details_purchase(ttl_Qty, final_Amount, total_disc, ttl_Amount, show_gst=False, print_config=None):
    """
    Purchase totals row — mirrors product_total_details but purchase arg order differs.
    Dynamically matches visible columns from print_config.
    """
    width_scale  = get_width_scale(print_config) if print_config else 1.0
    TOTAL_WIDTH  = 10.0 * inch * width_scale
    fs           = _effective_table_font_size(print_config)

    col_config   = (print_config or {}).get('column_config') if print_config else None
    visible_cols = _resolve_product_columns(col_config, show_gst, print_config=print_config)
    col_widths   = _compute_col_widths(visible_cols, TOTAL_WIDTH)

    value_map = {
        'serial_no':        '',
        'product_name':     'Total',
        'boxes':            '',
        'quantity':         _fmt_total(ttl_Qty),
        'unit':             '',
        'rate':             '',
        'amount':           _fmt_total(final_Amount),
        'discount_percent': '',
        'discount_amount':  _fmt_total(total_disc),
        'gst_amount':       '',
        'total_amount':     _fmt_total(ttl_Amount),
    }

    row = [value_map.get(col['key'], '') for col in visible_cols]

    cell_pad = max(3, int(5 * width_scale))
    table = Table([row], colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), get_header_color(print_config) if print_config else colors.skyblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), fs),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), cell_pad),
        ('RIGHTPADDING', (0, 0), (-1, -1), cell_pad),
    ]))
    return table



def product_total_details_inwords(
    Bill_Amount_In_Words, SubTotal, Discount_Amt, shipping_charges,
    total_cgst, total_sgst, total_igst, cess_amount,
    round_off, Party_Old_Balance, net_lbl, net_value,
    tax_type='Exclusive', print_config=None
):
    styles = getSampleStyleSheet()
    fs = _get_font_size(print_config)
    normal_style  = ParagraphStyle('inwords_normal', parent=styles['Normal'], fontSize=fs)
    bold_style    = ParagraphStyle('inwords_bold', parent=normal_style, fontName='Helvetica-Bold', fontSize=fs)
    header_color  = get_header_color(print_config) if print_config else colors.skyblue

    sec = (print_config or {}).get('section_config', {}) if print_config else {}
    show_amount_in_words = sec.get('show_amount_in_words', True)
    show_subtotal        = sec.get('show_subtotal', True)
    show_discount        = sec.get('show_discount', True)
    show_shipping        = sec.get('show_shipping_charges', True)
    show_tax             = sec.get('show_tax_breakdown', True)
    show_cess            = sec.get('show_cess', True)
    show_round_off       = sec.get('show_round_off', True)
    show_party_balance   = sec.get('show_party_balance', True)

    def _fmt(val):
        """Format a numeric value: 2 decimal places, handle negative-zero, add commas."""
        try:
            f = round(float(val), 2)
            if f == 0.0:
                return '0.00'
            # Comma formatting with 2 decimals (Indian/International style)
            return '{:,.2f}'.format(f)
        except (ValueError, TypeError):
            return str(val)

    def _is_zero(val):
        if val is None:
            return True
        s = str(val).strip()
        if s in ('', 'None', 'N/A', 'null', '-'):
            return True
        try:
            return round(float(s), 2) == 0.0
        except (ValueError, TypeError):
            return False

    def _signed(val):
        """Show negative values with − prefix, positive as-is."""
        try:
            f = round(float(val), 2)
            if f == 0.0:
                return '0.00'
            if f < 0:
                return '-{:,.2f}'.format(abs(f))
            return '{:,.2f}'.format(f)
        except (ValueError, TypeError):
            return str(val)

    # ── Bill Amount In Words ─────────────────────────────────────
    bill_amount_paragraph = Paragraph(
        f"<b>Bill Amount In Words:</b><br/>{Bill_Amount_In_Words}" if show_amount_in_words else '',
        normal_style
    )

    # ── Financials rows ──────────────────────────────────────────
    # Each row: (label, value_str, is_net_total)
    rows = []

    if show_subtotal:
        rows.append(('Sub Total', _fmt(SubTotal), False))

    if show_discount and not _is_zero(Discount_Amt):
        disc_val = round(float(Discount_Amt), 2)
        disc_display = '-{:,.2f}'.format(abs(disc_val))
        rows.append(('Total Discount', disc_display, False))

    if show_shipping and not _is_zero(shipping_charges):
        rows.append(('Shipping Charges', _fmt(shipping_charges), False))

    if show_tax and tax_type != 'Inclusive':
        if not _is_zero(total_igst):
            rows.append(('IGST', _fmt(total_igst), False))
        else:
            if not _is_zero(total_cgst):
                rows.append(('CGST', _fmt(total_cgst), False))
            if not _is_zero(total_sgst):
                rows.append(('SGST', _fmt(total_sgst), False))

    if show_cess and not _is_zero(cess_amount):
        rows.append(('Cess Amt', _fmt(cess_amount), False))

    if show_round_off and not _is_zero(round_off):
        rows.append(('Round Off', _signed(round_off), False))

    if show_party_balance and not _is_zero(Party_Old_Balance):
        rows.append(('Party Old Balance', _fmt(Party_Old_Balance), False))

    # Net Total always shown
    rows.append((net_lbl or 'Net Total', _fmt(net_value), True))

    # ── Build table rows ────────────────────────────────────────
    s            = get_width_scale(print_config) if print_config else 1.0
    TOTAL_USABLE = 10.0 * inch * s
    # Scale minimum width with font size: "232,391.10" at 12pt needs ~1.2", at 10pt ~1.0"
    font_scale   = fs / 10.0
    LABEL_W      = max(1.5 * inch * font_scale, 2.2 * inch * s)
    VALUE_W      = max(1.0 * inch * font_scale, 1.1 * inch * s)
    LEFT_W       = TOTAL_USABLE - LABEL_W - VALUE_W

    financials_data = []
    net_row_index = None
    for i, (lbl, val, is_net) in enumerate(rows):
        if is_net:
            net_row_index = i
            financials_data.append([
                Paragraph(f"<b>{lbl}:</b>", bold_style),
                Paragraph(f"<b>{val}</b>", bold_style),
            ])
        else:
            financials_data.append([
                Paragraph(f"{lbl}:", normal_style),
                Paragraph(val, normal_style),
            ])

    if not financials_data:
        financials_data.append([Paragraph('', normal_style), Paragraph('', normal_style)])

    fin_style_cmds = [
        ('ALIGN',         (0, 0),  (-1, -1), 'LEFT'),
        ('ALIGN',         (1, 0),  (1, -1),  'RIGHT'),
        ('FONTNAME',      (0, 0),  (-1, -1), 'Helvetica'),
        ('FONTSIZE',      (0, 0),  (-1, -1), fs),
        ('TOPPADDING',    (0, 0),  (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0),  (-1, -1), 4),
        ('LEFTPADDING',   (0, 0),  (-1, -1), 6),
        ('RIGHTPADDING',  (0, 0),  (-1, -1), 6),
        # Thin separator line between rows
        ('LINEBELOW',     (0, 0),  (-1, -2), 0.3, colors.HexColor('#CCCCCC')),
    ]

    # Highlight Net Total row
    if net_row_index is not None:
        fin_style_cmds += [
            ('BACKGROUND',    (0, net_row_index), (-1, net_row_index), header_color),
            ('FONTNAME',      (0, net_row_index), (-1, net_row_index), 'Helvetica-Bold'),
            ('FONTSIZE',      (0, net_row_index), (-1, net_row_index), fs + 1),
            ('LINEABOVE',     (0, net_row_index), (-1, net_row_index), 1, colors.black),
        ]

    financials_table = Table(financials_data, colWidths=[LABEL_W, VALUE_W])
    financials_table.setStyle(TableStyle(fin_style_cmds))

    # ── Outer wrapper table ──────────────────────────────────────
    table = Table(
        [[bill_amount_paragraph, financials_table]],
        colWidths=[LEFT_W, (LABEL_W + VALUE_W)]
    )
    table.setStyle(TableStyle([
        ('BOX',      (0, 0), (-1, -1), 1, colors.black),
        ('LINEBEFORE',(1, 0), (1, 0),  1, colors.black),
        ('VALIGN',   (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING',  (0, 0), (0, 0), 8),
        ('RIGHTPADDING', (0, 0), (0, 0), 8),
        ('TOPPADDING',   (0, 0), (0, 0), 8),
        ('BOTTOMPADDING',(0, 0), (0, 0), 8),
        ('LEFTPADDING',  (1, 0), (1, 0), 0),
        ('RIGHTPADDING', (1, 0), (1, 0), 0),
        ('TOPPADDING',   (1, 0), (1, 0), 0),
        ('BOTTOMPADDING',(1, 0), (1, 0), 0),
    ]))

    return table



# def declaration():
#     table_data_6 = [['<b>Declaration:</b>\n' 'We declare that this invoice shows the actual price of the goods/services' '\n' 'described and that all particulars are true and correct.' '\n' 'Original For Recipient', 'Authorised Signatory']]
#     table_6_col_widths = [6.7*inch, 3.3*inch]
    
#     table = Table(table_data_6, colWidths=table_6_col_widths)
#     table.setStyle(TableStyle([
#     ('BACKGROUND', (0, 0), (-1, -1), colors.white),  # Background color for the entire table
#     ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),   # Text color for the entire table
#     ('ALIGN', (0, 0), (-1, -1), 'LEFT'),              # Left align all cells
#     ('VALIGN', (0, 0), (-1, -1), 'TOP'),              # Top align all cells
#     ('ALIGN', (1, 0), (1, 0), 'CENTER'),              # Center align text in the second column header cell
#     ('VALIGN', (1, 0), (1, 0), 'BOTTOM'),             # Bottom align text in the second column header cell
    
#     # Add border around header cells
#     ('GRID', (0, 0), (-1, 0), 1, colors.black),  # Add border around the header row
    
#     # Optional: Additional styling
#     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),  # Font for the header row
#     ('BOTTOMPADDING', (0, 0), (-1, 0), 10),       # Padding for the header row
#     ]))
#     return table

def declaration(print_config=None):
    styles = getSampleStyleSheet()
    sec = (print_config or {}).get('section_config', {}) if print_config else {}
    txt = (print_config or {}).get('custom_text', {}) if print_config else {}

    show_declaration = sec.get('show_declaration', True)
    show_signature   = sec.get('show_signature', True)
    decl_text = txt.get('declaration',
        'We declare that this invoice shows the actual price of the goods/services '
        'described and that all particulars are true and correct.'
    )

    fs = _get_font_size(print_config)
    styleN = ParagraphStyle(
        'normal_declaration', parent=styles['Normal'],
        fontSize=fs, leading=fs + 3, textColor=colors.black
    )

    # Use copy label from config, fall back to "Original For Recipient"
    copy_cfg    = (print_config or {}).get('copy_config', {}) if print_config else {}
    copy_labels = copy_cfg.get('copy_labels', ['Original For Recipient'])
    copy_label  = copy_labels[0] if copy_labels else 'Original For Recipient'

    left_text = Paragraph(
        (f"<b>Declaration:</b><br/><br/>{decl_text}<br/><br/>{copy_label}"
         if show_declaration else ''),
        styleN
    )
    right_text = Paragraph(
        ("<br/><br/><br/>__________________________<br/><b>Authorised Signatory</b>"
         if show_signature else ''),
        styleN
    )

    s = get_width_scale(print_config) if print_config else 1.0
    paper_size = (print_config or {}).get('paper_size', 'Custom_11x16')
    TOTAL_W = 10.0 * inch * s
    # A5 and smaller: shift to 60/40 so signature column has readable width
    left_w  = TOTAL_W * (0.60 if s <= 0.55 else 0.70)
    right_w = TOTAL_W - left_w
    # Reduce vertical padding for height-constrained sizes (A5, A4_Landscape)
    decl_pad = max(4, int(10 * min(s, 1.0))) if paper_size in ('A5', 'A4_Landscape') else 10
    table = Table([[left_text, right_text]], colWidths=[left_w, right_w])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), decl_pad),
        ('BOTTOMPADDING', (0, 0), (-1, -1), decl_pad),
        ('GRID', (0, 0), (-1, 0), 1, colors.black),
    ]))

    return table


#====PURCHASE ORDER RELATED TBL
def shipping_details(destination, tax_type, shipping_mode_name, port_of_landing, port_of_discharge, sdate, print_config=None):
    s = get_width_scale(print_config)
    fs = _get_font_size(print_config)
    style_normal = ParagraphStyle('sd_normal', parent=getSampleStyleSheet()['Normal'], fontSize=fs)
    left_para = Paragraph(
        f"<b>Destination:</b> {destination}<br/>"
        f"<b>Shipping Mode:</b> {shipping_mode_name}<br/>"
        f"<b>Port of Loading:</b> {port_of_landing}<br/>"
        f"<b>Port of Discharge:</b> {port_of_discharge}",
        style_normal
    )
    right_para = Paragraph(
        f"<b>Tax Preference:</b> {tax_type}<br/>"
        f"<b>Ref Date:</b> {sdate}",
        style_normal
    )
    table = Table([[left_para, right_para]], colWidths=[5*inch*s, 5*inch*s])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), fs),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    return table


def vendor_details(customer_name, v_billing_address, v_shipping_address_lbl, v_shipping_address, print_config=None):
    s = get_width_scale(print_config)
    fs = _get_font_size(print_config)
    normal_style = ParagraphStyle('vd_normal', parent=getSampleStyleSheet()['Normal'], fontSize=fs)

    def _s(v):
        t = str(v).strip() if v is not None else ''
        return '' if t.lower() in ('none', 'n/a', 'null', '-') else t

    bill_html = f"<b>{_s(customer_name) or '—'}</b>"
    if _s(v_billing_address):
        bill_html += f"<br/>{_s(v_billing_address)}"

    ship_html = f"<b>{_s(v_shipping_address_lbl) or 'Delivery Address'}</b>"
    if _s(v_shipping_address):
        ship_html += f"<br/>{_s(v_shipping_address)}"

    cust_bill_paragraph = Paragraph(bill_html, normal_style)
    cust_ship_paragraph = Paragraph(ship_html, normal_style)

    table = Table([[cust_bill_paragraph, cust_ship_paragraph]], colWidths=[5*inch*s, 5*inch*s])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), fs),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    return table

def narration_and_total(comp_name, sdate, total_sub_amt, total_bill_amt, print_config=None):
    s = get_width_scale(print_config)
    fs = _get_font_size(print_config)
    normal_style = ParagraphStyle('nt_normal', parent=getSampleStyleSheet()['Normal'], fontSize=fs)

    def _f(v):
        try:
            return '{:,.2f}'.format(round(float(v), 2))
        except (ValueError, TypeError):
            return str(v)

    narration_paragraph = Paragraph(f"<b>Narration:</b> Being Goods Purchase From {comp_name} {sdate}", normal_style)
    total_paragraph = Paragraph(
        f"<b>Sub Total:</b> {_f(total_sub_amt)}<br/>"
        f"<b>Bill Total:</b> {_f(total_bill_amt)}",
        normal_style
    )

    table = Table([[narration_paragraph, total_paragraph]], colWidths=[5*inch*s, 5*inch*s])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), fs),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    return table

def logistics_info(shipping_company_name, shipping_tracking_no, vehicle_vessel, no_of_packets, shipping_date, shipping_charges, weight, print_config=None):
    s = get_width_scale(print_config)
    fs = _get_font_size(print_config)
    normal_style = ParagraphStyle('li_normal', parent=getSampleStyleSheet()['Normal'], fontSize=fs)

    logistics_para = Paragraph(
        f"<b>Logistics Info:</b><br/><br/>"
        f"Shipping Company: {shipping_company_name}<br/>"
        f"Tracking No: {shipping_tracking_no}<br/>"
        f"Vehicle/Vessel No.: {vehicle_vessel}<br/>"
        f"No of Packets: {no_of_packets}",
        normal_style
    )
    doc_extra_para = Paragraph(
        f"<b>Document Extra Info:</b><br/><br/>"
        f"Shipping Date: {shipping_date}<br/>"
        f"Charges Paid: {shipping_charges}<br/>"
        f"Weight: {weight}",
        normal_style
    )

    table = Table([[logistics_para, doc_extra_para]], colWidths=[5*inch*s, 5*inch*s])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), fs),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    return table

def purchase_declaration(comp_name, print_config=None):
    s = get_width_scale(print_config)
    fs = _get_font_size(print_config)

    table = Table([[f"For {comp_name}  \n\n\n\n  Authorised Signatory"]], colWidths=[10*inch*s])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), fs),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    return table

def comp_address_last_tbl(comp_address, comp_phone, comp_email, print_config=None):
    s = get_width_scale(print_config)
    fs = _get_font_size(print_config, default=8)

    table = Table([[f"{comp_address}  {comp_phone}  {comp_email}"]], colWidths=[10*inch*s])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), fs),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    return table

#Sale invoice logics ....
# def invoice_doc_details(company_logo, company_name, company_gst, company_address, company_phone, company_email, sno_lbl, sno, sdate_lbl, sdate): 
#     styles = getSampleStyleSheet()
#     style_normal = styles['Normal']
#     style_bold = styles['Heading4']

#     image_filename = "company_1_1afdb5.jpg"
#     media_folder = r"C:/Users/Pramod Kumar/CNL_Backend/document_format/cnl-backend/media/doc_generater"
#     image_path = os.path.join(media_folder, image_filename)

#     # Check if image exists
#     if not os.path.exists(image_path):
#         raise FileNotFoundError(f"Image file not found: {image_path}")

#     # Create an image object
#     company_logo = Image(image_path, width=60, height=60)

#     # Define company details as a Paragraph
#     company_details_content = Paragraph(
#         f"<b>{company_name}</b><br/>"
#         f"<b>GSTIN: {company_gst}</b><br/>"
#         f"{company_address}<br/>"
#         f"<b>Mobile:</b> {company_phone}<br/>"
#         f"<b>Email:</b> {company_email}",
#         style_normal
#     )

#     # Create a table with two columns: [Logo, Company Details]
#     col_widths = [1.2*inch, 3.8*inch, 2.5*inch, 2.5*inch]  # Adjust width for better spacing

#     table_data_1 = [
#         [company_logo, company_details_content, f'{sno_lbl} : \n{sno}', f'{sdate_lbl} : \n{sdate}']
#     ]
    
#     table = Table(table_data_1, colWidths=col_widths)
#     table.setStyle(TableStyle([
        
#         ('BACKGROUND', (0, 0), (-1, 0), colors.white),
#         ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
#         ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
#         ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
#         ('GRID', (2, 0), (-1, 0), 1, colors.black),  # Only add grid for Invoice No. and Invoice Date
#         ('BOX', (0, 0), (-1, 0), 1, colors.black),  # Full outer border
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#         ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
#     ]))
    
#     return table

def invoice_doc_details(company_logo, company_name, company_gst, company_address, company_phone, company_email, sno_lbl, sno, sdate_lbl, sdate, print_config=None):
    from reportlab.platypus import Image, Paragraph, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    import os

    styles = getSampleStyleSheet()
    s = get_width_scale(print_config) if print_config else 1.0
    paper_size = (print_config or {}).get('paper_size', 'Custom_11x16')

    # Scale font and logo for small / height-constrained paper sizes
    fs = _get_font_size(print_config)
    if s <= 0.55:       # A5 — very narrow, must compress aggressively
        fs = max(7, fs - 2)
        logo_w = logo_h = 35
    elif paper_size == 'A4_Landscape':  # landscape — height-constrained
        logo_w = logo_h = 55
    elif s < 0.85:      # A4, Letter
        logo_w = logo_h = 60
    else:               # Custom_11x16 default
        logo_w = logo_h = 80

    style_normal = ParagraphStyle('inv_normal', parent=styles['Normal'], fontSize=fs, leading=fs + 2)

    sec = (print_config or {}).get('section_config', {}) if print_config else {}
    show_logo         = sec.get('show_logo', True)
    show_company_name = sec.get('show_company_name', True)
    show_gstin        = sec.get('show_gstin', True)
    show_address      = sec.get('show_company_address', True)
    show_phone        = sec.get('show_company_phone', True)
    show_email        = sec.get('show_company_email', True)

    # Logo — scaled to fit the cell on small paper sizes
    if show_logo and company_logo and os.path.exists(company_logo):
        logo_cell = Image(company_logo, width=logo_w, height=logo_h)
    else:
        logo_cell = Paragraph('', style_normal)

    def _safe(val):
        return val if val and str(val).strip() not in ('None', 'N/A', '') else ''

    name_line    = f"<b>{company_name}</b><br/>"          if (show_company_name and _safe(company_name)) else ''
    gstin_line   = f"<b>GSTIN:</b> {company_gst}<br/>"   if (show_gstin   and _safe(company_gst))        else ''
    address_line = f"{company_address}<br/>"              if (show_address and _safe(company_address))    else ''
    mobile_line  = f"<b>Mobile:</b> {company_phone}<br/>" if (show_phone   and _safe(company_phone))     else ''
    email_line   = f"<b>Email:</b> {company_email}"       if (show_email   and _safe(company_email))     else ''

    company_details_content = Paragraph(
        f"{name_line}{gstin_line}{address_line}{mobile_line}{email_line}",
        style_normal
    )

    # For A5 the invoice/date labels also need Paragraph wrapping to word-wrap in narrow cells
    if s <= 0.55:
        sno_content   = Paragraph(f'<b>{sno_lbl}:</b><br/>{sno}',   style_normal)
        sdate_content = Paragraph(f'<b>{sdate_lbl}:</b><br/>{sdate}', style_normal)
    else:
        sno_content   = f'{sno_lbl} : \n{sno}'
        sdate_content = f'{sdate_lbl} : \n{sdate}'

    col_widths = [1.2*inch*s, 3.8*inch*s, 2.5*inch*s, 2.5*inch*s]
    table_data_1 = [[logo_cell, company_details_content, sno_content, sdate_content]]

    bottom_pad = max(4, int(10 * min(s, 1.0)))
    table = Table(table_data_1, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('GRID', (2, 0), (-1, 0), 1, colors.black),
        ('BOX', (0, 0), (-1, 0), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), fs),
        ('BOTTOMPADDING', (0, 0), (-1, 0), bottom_pad),
        ('TOPPADDING', (0, 0), (-1, 0), bottom_pad),
    ]))

    return table




def invoice_customer_details(cust_name, city, country, phone, destination, shipping_address, billing_address, print_config=None):
    styles = getSampleStyleSheet()
    s = get_width_scale(print_config) if print_config else 1.0
    paper_size = (print_config or {}).get('paper_size', 'Custom_11x16')

    # Reduce font for A5 to fit narrow width and save vertical space
    fs = _get_font_size(print_config)
    if s <= 0.55:
        fs = max(7, fs - 2)
    elif paper_size == 'A4_Landscape':
        fs = max(8, fs - 1)

    style_normal = ParagraphStyle('inv_cust_normal', parent=styles['Normal'], fontSize=fs, leading=fs + 2)

    sec = (print_config or {}).get('section_config', {}) if print_config else {}
    show_billing  = sec.get('show_billing_address', True)
    show_shipping = sec.get('show_shipping_address', True)

    def _safe(v):
        sv = str(v).strip() if v is not None else ''
        return '' if sv.lower() in ('none', 'n/a', 'null', '', '-') else sv

    # Left: customer name always; billing address only when toggled on and non-empty
    billing_html = f"<b>Customer Details:</b><br/>{_safe(cust_name) or '—'}"
    if show_billing and _safe(billing_address):
        billing_html += f"<br/><b>Billing Address:</b><br/>{_safe(billing_address)}"
    billing_content = Paragraph(billing_html, style_normal)

    # Right: shipping address only when toggled on and non-empty
    if show_shipping and _safe(shipping_address):
        ship_html = f"<b>Shipping Address:</b><br/>{_safe(shipping_address)}"
    else:
        ship_html = ''
    shipping_content = Paragraph(ship_html, style_normal)

    table_data = [[billing_content, shipping_content]]
    table_col_widths = [5*inch*s, 5*inch*s]

    # Tighter cell padding for height-constrained sizes to reduce vertical space used
    cell_pad = max(2, int(4 * min(s, 1.0)))

    table = Table(table_data, colWidths=table_col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), fs),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), cell_pad),
        ('RIGHTPADDING', (0, 0), (-1, -1), cell_pad),
        ('TOPPADDING', (0, 0), (-1, -1), cell_pad),
        ('BOTTOMPADDING', (0, 0), (-1, -1), cell_pad),
    ]))

    return table

def invoice_product_details(data, show_gst=True, print_config=None):
    # Delegates to product_details — same logic, same config support
    return product_details(data, show_gst=show_gst, print_config=print_config)

def invoice_product_total_details(ttl_Qty, final_Amount, ttl_Amount, total_disc, show_gst=True, print_config=None):
    """
    Invoice totals row — dynamically matches visible columns from print_config.
    """
    width_scale  = get_width_scale(print_config) if print_config else 1.0
    TOTAL_WIDTH  = 10.0 * inch * width_scale
    fs           = _effective_table_font_size(print_config)

    col_config   = (print_config or {}).get('column_config') if print_config else None
    visible_cols = _resolve_product_columns(col_config, show_gst, print_config=print_config)
    col_widths   = _compute_col_widths(visible_cols, TOTAL_WIDTH)

    value_map = {
        'serial_no':        '',
        'product_name':     'Total',
        'boxes':            '',
        'quantity':         _fmt_total(ttl_Qty),
        'unit':             '',
        'rate':             '',
        'amount':           _fmt_total(final_Amount),
        'discount_percent': '',
        'discount_amount':  _fmt_total(total_disc),
        'gst_amount':       '',
        'total_amount':     _fmt_total(ttl_Amount),
    }

    row = [value_map.get(col['key'], '') for col in visible_cols]

    cell_pad = max(3, int(5 * width_scale))
    table = Table([row], colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), get_header_color(print_config) if print_config else colors.skyblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), fs),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), cell_pad),
        ('RIGHTPADDING', (0, 0), (-1, -1), cell_pad),
    ]))
    return table

def create_footer_section(bank_name, bank_acno, bank_ifsc, bank_branch, remarks="", print_config=None):
    styles = getSampleStyleSheet()
    s = get_width_scale(print_config) if print_config else 1.0
    paper_size = (print_config or {}).get('paper_size', 'Custom_11x16')

    # Height-constrained sizes: A5 (portrait) and A4_Landscape — only 7.27" usable height.
    # For these, collapse to a single row (bank + signature only) to prevent page overflow.
    is_tight_height = paper_size in ('A5', 'A4_Landscape')

    fs = _get_font_size(print_config)
    if s <= 0.55:       # A5 — aggressively compress
        fs = max(7, fs - 2)
    elif is_tight_height:  # A4_Landscape — slightly compress
        fs = max(8, fs - 1)

    style_normal = ParagraphStyle('footer_normal', parent=styles['Normal'], fontSize=fs, leading=fs + 2)
    sec = (print_config or {}).get('section_config', {}) if print_config else {}
    txt = (print_config or {}).get('custom_text', {}) if print_config else {}

    show_bank      = sec.get('show_bank_details', True)
    show_terms     = sec.get('show_terms', True)
    show_notes     = sec.get('show_notes', True)
    show_signature = sec.get('show_signature', True)

    notes_text = txt.get('notes', 'Thank you for the Business')
    terms_text = txt.get('terms_conditions',
        "1. Goods once sold cannot be taken back\n"
        "2. Warranty per manufacturer terms\n"
        "3. 24% p.a. interest after 15 days\n"
        "4. Subject to local Jurisdiction"
    )
    footer_note = txt.get('footer_note', '')

    # Bank details cell
    if show_bank:
        bank_content = Paragraph(
            f"<b>Bank Details:</b><br/>"
            f"Bank: <b>{bank_name}</b><br/>"
            f"A/C: <b>{bank_acno}</b>  IFSC: <b>{bank_ifsc}</b><br/>"
            f"Branch: <b>{bank_branch}</b>",
            style_normal
        )
    else:
        bank_content = Paragraph('', style_normal)

    # Signature cell — shorter on tight sizes to save height
    sig_spacer = '<br/>' if is_tight_height else '<br/><br/><br/>'
    signature_content = Paragraph(
        (f"{sig_spacer}__________________________<br/><b>Authorised Signatory</b>"
         if show_signature else ''),
        style_normal
    )

    col_widths = [7 * inch * s, 3 * inch * s]
    cell_pad = max(4, int(8 * min(s, 1.0)))

    if is_tight_height:
        # Single-row compact footer for height-constrained paper sizes.
        # Notes and Terms are merged into the left cell as compact inline text.
        inline_notes = ''
        if remarks and remarks.strip():
            inline_notes += f"<br/><b>Remarks:</b> {remarks}"
        if show_notes and notes_text:
            inline_notes += f"<br/><b>Note:</b> {notes_text}"
        if show_terms:
            terms_lines = terms_text.replace('\n', ' | ')
            inline_notes += f"<br/><b>Terms:</b> {terms_lines}"
        if footer_note:
            inline_notes += f"<br/>{footer_note}"
        bank_html = ''
        if show_bank:
            bank_html = (
                f"<b>Bank Details:</b> Bank: <b>{bank_name}</b>  "
                f"A/C: <b>{bank_acno}</b>  IFSC: <b>{bank_ifsc}</b>  "
                f"Branch: <b>{bank_branch}</b>"
            )
        bank_html += inline_notes
        left_cell = Paragraph(bank_html, style_normal)

        table_data = [[left_cell, signature_content]]
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), fs),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBEFORE', (1, 0), (1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ('VALIGN', (1, 0), (1, 0), 'BOTTOM'),
            ('LEFTPADDING', (0, 0), (-1, -1), cell_pad),
            ('RIGHTPADDING', (0, 0), (-1, -1), cell_pad),
            ('TOPPADDING', (0, 0), (-1, -1), cell_pad),
            ('BOTTOMPADDING', (0, 0), (-1, -1), cell_pad),
        ]))
        return table

    # Standard two-row footer for full-size paper (Custom_11x16, A4 portrait, Letter)
    notes_html = ''
    if remarks and remarks.strip():
        notes_html += f"<b>Remarks:</b> {remarks}<br/><br/>"
    if footer_note:
        notes_html += f"{footer_note}<br/><br/>"
    if show_notes:
        notes_html += f"<b>Notes:</b><br/>{notes_text}"
    notes_content = Paragraph(notes_html or '', style_normal)

    terms_lines = terms_text.replace('\n', '<br/>')
    terms_content = Paragraph(
        f"<b>Terms and Conditions:</b><br/>{terms_lines}" if show_terms else '',
        style_normal
    )

    table_data = [
        [bank_content, signature_content],
        [notes_content, terms_content]
    ]

    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), fs),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('LINEBEFORE', (1, 0), (1, -1), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('VALIGN', (1, 0), (1, 0), 'BOTTOM'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    return table


# Sale returns logic ...

def return_company_header(company_name, company_address, company_phone):
    styles = getSampleStyleSheet()

    def _s(v):
        """Return empty string for None/blank/sentinel values."""
        if v is None:
            return ''
        s = str(v).strip()
        return '' if s.lower() in ('none', 'n/a', 'null', '-', 'address not provided') else s

    company_style = ParagraphStyle(
        'CompanyStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        alignment=1,
        spaceAfter=6
    )
    address_style = ParagraphStyle(
        'AddressStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        spaceAfter=2
    )

    content = [Paragraph(f"<b>{_s(company_name) or 'Company'}</b>", company_style)]

    addr = _s(company_address)
    if addr:
        content.append(Paragraph(addr, address_style))

    phone = _s(company_phone)
    if phone:
        content.append(Paragraph(f"Phone No: {phone}", address_style))

    content += [Spacer(1, 12), Spacer(1, 12)]
    return content

def return_doc_details(cust_bill_dtl, sno_lbl, sno, sdate_lbl, sdate, print_config=None):
    s = get_width_scale(print_config) if print_config else 1.0
    col_widths = [3.3*inch*s, 2.8*inch*s, 3.9*inch*s]
    table_data = [
        [cust_bill_dtl, f'{sno_lbl} : {sno}', f'{sdate_lbl} : {sdate}'],
    ]

    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), get_header_color(print_config) if print_config else colors.skyblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('GRID', (0, 0), (-1, 0), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    return table

# def return_customer_details(cust_name, billing_address, phone, city):
#     styles = getSampleStyleSheet()
#     style_normal = styles['Normal']
    
#     content = Paragraph(
#         f"<b>{cust_name}</b><br/>"
#         f"{billing_address}<br/>"
#         f"Phone: {phone}<br/>"
#         f"Destination: {city}", 
#         style_normal
#     )
    
#     table_data = [[content]]
#     table = Table(table_data, colWidths=[10*inch])
#     table.setStyle(TableStyle([
#         ('BACKGROUND', (0, 0), (-1, -1), colors.white),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#         ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#     ]))
#     return table

def return_customer_details_with_reason(cust_name, billing_address, phone, city, return_reason, print_config=None):
    styles = getSampleStyleSheet()
    fs = _get_font_size(print_config)
    style_normal = ParagraphStyle('ret_cust_normal', parent=styles['Normal'], fontSize=fs)

    left_content = Paragraph(
        f"<b>{cust_name}</b><br/>"
        f"{billing_address}<br/>"
        f"Phone: {phone}<br/>"
        f"Destination: {city}",
        style_normal
    )
    right_content = Paragraph(
        f"<b>Return Reason:</b> {return_reason}",
        style_normal
    )

    # Table data: two columns
    table_data = [[left_content, right_content]]

    # Scale col widths for paper size
    s = get_width_scale(print_config) if print_config else 1.0
    col_widths = [6.1 * inch * s, 3.9 * inch * s]

    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('LINEBEFORE', (1, 0), (1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'LEFT'),
    ]))
    return table




def return_complete_table(data, total_qty, sub_total, discount_amt, cess_amount,
                          total_cgst, total_sgst, total_igst, round_0ff, bill_total,
                          amount_in_words, show_gst=False, print_config=None):
    styles = getSampleStyleSheet()
    fs = _effective_table_font_size(print_config)
    normal_style = ParagraphStyle('ret_tbl_normal', parent=styles['Normal'], fontSize=fs)
    header_color = get_header_color(print_config) if print_config else colors.HexColor('#f0f0f0')
    s = get_width_scale(print_config) if print_config else 1.0

    col_widths = [4.5*inch*s, 1.5*inch*s, 1.5*inch*s, 1.5*inch*s, 1.0*inch*s]

    table_data = [[
        Paragraph("<b>Description</b>", normal_style),
        Paragraph("<b>Qty</b>", normal_style),
        Paragraph("<b>MRP</b>", normal_style),
        Paragraph("<b>Amount</b>", normal_style),
        Paragraph("<b>Discount</b>", normal_style)
    ]]

    for item in data:
        table_data.append([
            Paragraph(str(item[1]), normal_style),   # Description — wraps
            format_numeric(item[3]),                 # Qty — plain string
            format_numeric(item[5]),                 # MRP — plain string
            format_numeric(item[6]),                 # Amount — plain string
            format_numeric(item[8]),                 # Discount — plain string
        ])

    # Fill with empty rows if less than 4 items (for layout consistency)
    while len(table_data) < 5:
        table_data.append(["", "", "", "", ""])

    def _fmtv(val):
        try:
            f = round(float(val), 2)
            return '0.00' if f == 0.0 else '{:,.2f}'.format(f)
        except (ValueError, TypeError):
            return str(val)

    def _is_zero_v(val):
        try:
            return round(float(val), 2) == 0.0
        except (ValueError, TypeError):
            return False

    # Add financial rows
    fin_rows = [["Total Quantity", "", "", "", _fmtv(total_qty)]]
    fin_rows.append(["Sub Total", "", "", "", _fmtv(sub_total)])
    if not _is_zero_v(discount_amt):
        disc_val = round(float(discount_amt), 2)
        fin_rows.append(["Total Discount", "", "", "", '-{:,.2f}'.format(abs(disc_val))])
    if not _is_zero_v(cess_amount):
        fin_rows.append(["Cess Amt", "", "", "", _fmtv(cess_amount)])
    table_data.extend(fin_rows)

    # GST handling based on tax type
    if show_gst:
        if float(total_igst) > 0:
            table_data.append(["IGST", "", "", "", format_numeric(total_igst)])
        else:
            if float(total_cgst) > 0:
                table_data.append(["CGST", "", "", "", format_numeric(total_cgst)])
            if float(total_sgst) > 0:
                table_data.append(["SGST", "", "", "", format_numeric(total_sgst)])

    # Round Off (hide if zero), Bill Total, Amount in Words
    if not _is_zero_v(round_0ff):
        r0ff = round(float(round_0ff), 2)
        r0ff_str = ('+' if r0ff > 0 else '') + '{:,.2f}'.format(r0ff)
        table_data.append(["Round Off", "", "", "", r0ff_str])
    table_data.extend([
        ["Bill Total", "", "", "", _fmtv(bill_total)],
        [Paragraph(f"<b>Amount in Words:</b> {amount_in_words}", normal_style), "", "", "", ""]
    ])

    # Create table
    table = Table(table_data, colWidths=col_widths)

    table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), fs),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEABOVE', (0, len(data)+1), (-1, len(data)+1), 1, colors.black),
        ('LINEABOVE', (0, -3), (-1, -3), 1, colors.black),
        ('LINEABOVE', (0, -2), (-1, -2), 0.5, colors.grey),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('SPAN', (0, -1), (-1, -1)),
        ('FONTNAME', (0, -2), (-1, -2), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    return table



# def return_complete_table(data, total_qty, sub_total, discount_amt, cess_amount, total_cgst, total_sgst, total_igst, round_0ff, bill_total, amount_in_words):
#     styles = getSampleStyleSheet()
#     normal_style = styles['Normal']
    
#     # Column widths
#     col_widths = [4.5*inch, 1.5*inch, 1.5*inch, 1.5*inch, 1*inch]
    
#     # Table data with headers
#     table_data = [
#         [
#             Paragraph("<b>Description</b>", normal_style),
#             Paragraph("<b>Qty</b>", normal_style),
#             Paragraph("<b>MRP</b>", normal_style),
#             Paragraph("<b>Amount</b>", normal_style),
#             Paragraph("<b>Discount</b>", normal_style)
#         ]
#     ]
    
#     # Add product rows
#     for item in data:
#         table_data.append([
#             Paragraph(str(item[1])),  # Description
#             Paragraph(format_numeric(item[3])),  # Qty
#             Paragraph(format_numeric(item[5])),  # MRP
#             Paragraph(format_numeric(item[6])),   # Amount
#             Paragraph(format_numeric(item[8]))   # Amount
#         ])
    
#     # Add empty rows if less than 4 products
#     while len(table_data) < 5:  # Header + min 3 products + empty row
#         table_data.append(["", "", "", ""])
    
#     # Add financial rows
#     table_data.extend([
#         ["Total Quantity", "", "", "", total_qty],
#         ["Sub Total", "", "", "", sub_total],
#         ["Total Discount", "", "", "", f"-{discount_amt}"],
#         ["Cess Amt", "", "", "", f"{cess_amount}"] #cess_amount
#     ])

#     if float(total_igst) > 0:
#         table_data.append(["IGST", "", "", "", f"{total_igst}"])
#     elif float(total_cgst) > 0 and float(total_sgst) > 0:
#         table_data.append(["CGST", "", "", "", f"{total_cgst}"])
#         table_data.append(["SGST", "", "", "", f"{total_sgst}"])

#     table_data.extend([
#         ["Round Off", "", "", "", round_0ff],
#         ["Bill Total", "", "", "", bill_total],
#         [Paragraph(f"<b>Amount in Words:</b> {amount_in_words}", normal_style), "", "", ""]
#     ])

    
#     # Create table
#     table = Table(table_data, colWidths=col_widths)
    
#     # Apply styling
#     table.setStyle(TableStyle([
#         # Outer border
#         ('BOX', (0, 0), (-1, -1), 1, colors.black),
        
#         # Header styling
#         ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
#         ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        
#         # Key dividers
#         ('LINEABOVE', (0, len(data)+1), (-1, len(data)+1), 1, colors.black),  # Above Total
#         ('LINEABOVE', (0, len(data)+3), (-1, len(data)+3), 1, colors.black),  # Above Bill Total
        
#         # Key dividers
#         ('LINEABOVE', (0, len(data)+1), (-1, len(data)+1), 1, colors.black),  # Above Total
#         ('LINEABOVE', (0, len(data)+3), (-1, len(data)+3), 1, colors.black),  # Above Bill Total
#         ('LINEABOVE', (0, -2), (-1, -2), 0.5, colors.grey),  # Line above Amount in Words
        
#         # Right-align numbers
#         ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        
       
#         # Span amount in words
#         ('SPAN', (0, -1), (-1, -1)),
        
#         # Bold important rows
#         ('FONTNAME', (0, -2), (-1, -2), 'Helvetica-Bold'),
#         ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
#     ]))
    
#     return table

#Payment receipt logic ...
def payment_receipt_header(company_name, company_address, company_phone, company_email):
    styles = getSampleStyleSheet()
    elements = []
    
    # Main header style
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading1'],
        fontSize=14,
        alignment=1,  # Center
        spaceAfter=12
    )
    
    # Subheader style
    subheader_style = ParagraphStyle(
        'SubheaderStyle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        spaceAfter=6
    )
    
    # Contact style
    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontSize=9,
        alignment=1,
        spaceAfter=12
    )
    
    elements.append(Paragraph(company_name.upper(), header_style))
    elements.append(Paragraph(company_address, subheader_style))
    elements.append(Paragraph(f"Phone: {company_phone} | Email: {company_email}", contact_style))
    
    return elements

def payment_receipt_voucher_table(data):
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    bold_style = styles['Heading3']
    
    # Main voucher table data
    table_data = [
        [
            Paragraph(f"<b>Customer Name</b>", bold_style),
            Paragraph(f"Voucher No: {data['voucher_no']}", normal_style),
            Paragraph(f"Voucher Date: {data['voucher_date']}", normal_style)
        ],
        [
            Paragraph(data['customer_name'], normal_style),
            "Bills Ref",
            "-"
        ],
        [
            "",
            "Transfer No.",
            "-"
        ],
        [
            Paragraph(f"<b>Transfer Name</b>", bold_style),
            data['transfer_name'],
            Paragraph(f"<b>Transfer Date</b>", bold_style),
            data['transfer_date']
        ],
        [
            Paragraph(f"<b>Bill No:</b>", bold_style),
            "Bill Date",
            "D/C",
            "Transfer Amount",
            "Adjusted Amt (Cash Discount)",
            "Net Receipt"
        ],
        # Sample transaction rows (replace with actual data)
        [
            "09:45/24-25",
            "06/03/2025",
            "D",
            "31,216.00",
            "31,216.00",
            "0.00",
            "31,216.00"
        ],
        [
            "05/23/24-25",
            "06/03/2025",
            "D",
            "",
            "(1) 300.00",
            "0.00",
            "(1) 300.00"
        ],
        [
            "05/23/24-25",
            "07/03/2025",
            "D",
            "",
            "3,384.00",
            "0.00",
            "3,384.00"
        ]
    ]
    
    col_widths = [1.5*inch, 1*inch, 0.5*inch, 1*inch, 1.5*inch, 1*inch, 1*inch]
    
    table = Table(table_data, colWidths=col_widths, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('SPAN', (0, 1), (0, 2)),
        ('SPAN', (1, 1), (2, 1)),
        ('SPAN', (1, 2), (2, 2)),
        ('SPAN', (0, 3), (1, 3)),
        ('SPAN', (2, 3), (3, 3)),
        ('BACKGROUND', (0, 4), (-1, 4), colors.lightgrey),
    ]))
    
    return table

def payment_amount_section(amount, amount_in_words, outstanding, total):
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    bold_style = styles['Heading3']
    
    # Amount in words
    amount_words = Paragraph(
        f"<b>Amount:</b> {amount_in_words}", 
        normal_style
    )
    
    # Amount breakdown table
    amounts_data = [
        [Paragraph("<b>Amount Paid:</b>", bold_style), Paragraph(f"<b>{amount:,.2f}</b>", bold_style)],
        [Paragraph("<b>Outstanding:</b>", normal_style), Paragraph(f"{outstanding:,.2f}", normal_style)],
        [Paragraph("<b>Original Total:</b>", normal_style), Paragraph(f"{total:,.2f}", normal_style)],
    ]
    
    amounts_table = Table(amounts_data, colWidths=[3*inch, 2*inch])
    amounts_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    # Combine both in a single table
    combined_data = [[amount_words, amounts_table]]
    table = Table(combined_data, colWidths=[4*inch, 3*inch])
    table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    
    return table

def payment_approval_section():
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    
    table_data = [
        ["", "Authorized Signatory"],
        ["Prepared By:", ""],
        ["Approved By:", ""]
    ]
    
    table = Table(table_data, colWidths=[3*inch, 4*inch])
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
        ('LINEABOVE', (0, 1), (-1, 1), 1, colors.black),
        ('LINEABOVE', (0, 2), (-1, 2), 1, colors.black),
        ('SPAN', (1, 0), (1, 2)),
    ]))
    
    return table

def payment_receipt_amount_section(data):
    """Creates the amount section with amount in words and numeric breakdown"""
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    bold_style = styles['Heading3']
    
    # Amount in words
    amount_words = Paragraph(
        f"<b>Amount Paid:</b> {data['amount_in_words']}", 
        normal_style
    )
    
    # Amount breakdown table
    amounts_data = [
        [Paragraph("<b>Amount Paid:</b>", bold_style), f"{data['amount']:,.2f}"],
        [Paragraph("Outstanding:", normal_style), f"{data['outstanding']:,.2f}"],
        [Paragraph("Original Total:", normal_style), f"{data['total']:,.2f}"],
    ]
    
    amounts_table = Table(amounts_data, colWidths=[2.0*inch, 1.5*inch])
    amounts_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    
    # Combine both sections
    combined_table = Table([
        [amount_words, amounts_table]
    ], colWidths=[4.0*inch, 3.5*inch])
    
    combined_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    
    return combined_table

def payment_receipt_voucher_table(data):
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    bold_style = styles['Heading3']
    
    # Main voucher table data
    table_data = [
        [
            Paragraph(f"<b>Customer Name</b>", bold_style),
            Paragraph(f"Voucher No: {data['voucher_no']}", normal_style),
            Paragraph(f"Voucher Date: {data['voucher_date']}", normal_style)
        ],
        [
            Paragraph(data['customer_name'], normal_style),
            "Bills Ref",
            "-"
        ],
        [
            "",
            "Transfer No.",
            "-"
        ],
        [
            Paragraph(f"<b>Transfer Name</b>", bold_style),
            data['transfer_name'],
            Paragraph(f"<b>Transfer Date</b>", bold_style),
            data['transfer_date']
        ],
        [
            Paragraph(f"<b>Bill No:</b>", bold_style),
            "Bill Date",
            "D/C",
            "Transfer Amount",
            "Adjusted Amt (Cash Discount)",
            "Net Receipt"
        ],
        # Sample transaction rows (replace with actual data)
        [
            "09:45/24-25",
            "06/03/2025",
            "D",
            "31,216.00",
            "31,216.00",
            "0.00",
            "31,216.00"
        ],
        [
            "05/23/24-25",
            "06/03/2025",
            "D",
            "",
            "(1) 300.00",
            "0.00",
            "(1) 300.00"
        ],
        [
            "05/23/24-25",
            "07/03/2025",
            "D",
            "",
            "3,384.00",
            "0.00",
            "3,384.00"
        ]
    ]
    
    col_widths = [1.5*inch, 1*inch, 0.5*inch, 1*inch, 1.5*inch, 1*inch, 1*inch]
    
    table = Table(table_data, colWidths=col_widths, hAlign='LEFT')
    table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        
        # Vertical lines only
        ('LINEBEFORE', (0, 0), (0, -1), 1, colors.black),  # First column
        ('LINEBEFORE', (1, 0), (1, -1), 1, colors.black),  # Second column
        ('LINEBEFORE', (2, 0), (2, -1), 1, colors.black),  # Third column
        ('LINEBEFORE', (3, 0), (3, -1), 1, colors.black),  # Fourth column
        ('LINEBEFORE', (4, 0), (4, -1), 1, colors.black),  # Fifth column
        ('LINEBEFORE', (5, 0), (5, -1), 1, colors.black),  # Sixth column
        ('LINEBEFORE', (6, 0), (6, -1), 1, colors.black),  # Seventh column
        
        # Remove all horizontal lines by removing GRID and LINEABOVE/BELOW
        ('SPAN', (0, 1), (0, 2)),
        ('SPAN', (1, 1), (2, 1)),
        ('SPAN', (1, 2), (2, 2)),
        ('SPAN', (0, 3), (1, 3)),
        ('SPAN', (2, 3), (3, 3)),
        ('BACKGROUND', (0, 4), (-1, 4), colors.lightgrey),
        
        # Right align numeric columns
        ('ALIGN', (3, 5), (6, -1), 'RIGHT'),
    ]))
    
    return table

def payment_customer_details(cust_name, billing_address, phone, email, print_config=None):
    styles = getSampleStyleSheet()
    fs = _get_font_size(print_config)
    style_normal = ParagraphStyle('pay_cust_normal', parent=styles['Normal'], fontSize=fs)
    s = get_width_scale(print_config) if print_config else 1.0

    def _s(v):
        if v is None:
            return ''
        t = str(v).strip()
        return '' if t.lower() in ('none', 'n/a', 'null', '-') else t

    lines = [f"<b>{_s(cust_name) or '—'}</b>"]
    if _s(billing_address):
        lines.append(_s(billing_address))
    if _s(phone):
        lines.append(f"<b>Phone:</b> {_s(phone)}")
    if _s(email):
        lines.append(f"<b>Email:</b> {_s(email)}")

    customer_content = Paragraph('<br/>'.join(lines), style_normal)

    table = Table([[customer_content]], colWidths=[10 * inch * s])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    return table

def payment_details_table(payment_data, print_config=None):
    styles = getSampleStyleSheet()
    fs = _get_font_size(print_config)
    style_normal = ParagraphStyle('pay_normal', parent=styles['Normal'], fontSize=fs)
    header_color = get_header_color(print_config) if print_config else colors.skyblue
    s = get_width_scale(print_config) if print_config else 1.0

    col_config = (print_config or {}).get('column_config') if print_config else None
    col_keys = ['invoice_no', 'invoice_date', 'payment_method', 'reference_no', 'amount_paid', 'total_amount']
    col_labels = {
        'invoice_no': 'Invoice No.', 'invoice_date': 'Invoice Date',
        'payment_method': 'Payment Method', 'reference_no': 'Reference No.',
        'amount_paid': 'Amount Paid', 'total_amount': 'Total Amount',
    }
    NUMERIC_KEYS = {'amount_paid', 'total_amount'}

    if col_config:
        cfg_map = {c['key']: c for c in col_config}
        visible_keys = [k for k in col_keys if cfg_map.get(k, {}).get('visible', True)]
        required = {'invoice_no', 'amount_paid', 'total_amount'}
        for k in required:
            if k not in visible_keys:
                visible_keys.append(k)
        for c in col_config:
            if c['key'] in col_keys:
                col_labels[c['key']] = c.get('label') or col_labels[c['key']]
    else:
        visible_keys = col_keys

    num_cols   = len(visible_keys)
    total_w    = 10.0 * inch * s
    col_widths = [total_w / num_cols] * num_cols

    table_data = [[Paragraph(f"<b>{col_labels[k]}</b>", style_normal) for k in visible_keys]]

    def _fmt_date(v):
        """Convert ISO datetime to DD/MM/YYYY or DD/MM/YYYY HH:MM:SS.
        Time is only shown if it is not midnight (00:00:00)."""
        if not v:
            return ''
        s = str(v).strip().replace('T', ' ')
        p = s.split(' ')
        date_part, time_part = p[0], (p[1] if len(p) > 1 else '')
        try:
            d = date_part.split('-')
            if len(d) == 3 and len(d[0]) == 4:
                out = f"{d[2]}/{d[1]}/{d[0]}"
                if time_part and time_part not in ('00:00:00', '00:00'):
                    out += f" {time_part}"
                return out
        except Exception:
            pass
        return s

    def _cell(payment, key):
        mapping = {
            'invoice_no':     payment.get('invoice_no', ''),
            'invoice_date':   _fmt_date(payment.get('invoice_date', '')),
            'payment_method': payment.get('payment_method', ''),
            'reference_no':   payment.get('cheque_no') or '',
            'amount_paid':    format_numeric(payment.get('amount', 0)),
            'total_amount':   format_numeric(payment.get('total', 0)),
        }
        val = str(mapping.get(key, ''))
        # Numeric cells as plain strings (no mid-number wrap)
        if key in NUMERIC_KEYS:
            return val
        return Paragraph(val, style_normal)

    for payment in payment_data:
        table_data.append([_cell(payment, k) for k in visible_keys])

    while len(table_data) < 7:
        table_data.append([' '] * num_cols)

    table = Table(table_data, colWidths=col_widths)

    # Build vertical lines dynamically (one per column)
    line_cmds = [('LINEBEFORE', (i, 0), (i, -1), 1, colors.black) for i in range(num_cols)]
    line_cmds.append(('LINEAFTER', (num_cols - 1, 0), (num_cols - 1, -1), 1, colors.black))

    style_cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), fs),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 1, colors.black),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
    ] + line_cmds

    # Right-align numeric columns dynamically
    for ci, key in enumerate(visible_keys):
        if key in NUMERIC_KEYS:
            style_cmds.append(('ALIGN', (ci, 1), (ci, -1), 'RIGHT'))

    table.setStyle(TableStyle(style_cmds))
    return table

def payment_amount_summary(outstanding, amount_in_words, print_config=None):
    styles = getSampleStyleSheet()
    fs = _get_font_size(print_config)
    normal_style = ParagraphStyle('pay_summary_normal', parent=styles['Normal'], fontSize=fs)
    s = get_width_scale(print_config) if print_config else 1.0

    # Format outstanding as proper currency (not raw float)
    try:
        outstanding_fmt = '{:,.2f}'.format(round(float(outstanding), 2))
    except (ValueError, TypeError):
        outstanding_fmt = str(outstanding)

    amount_paragraph = Paragraph(
        f"<b>Paid Amount in Words:</b> {amount_in_words}",
        normal_style
    )
    outstanding_paragraph = Paragraph(
        f"<b>Outstanding Balance:</b> {outstanding_fmt}",
        normal_style
    )

    combined = Table(
        [[amount_paragraph, outstanding_paragraph]],
        colWidths=[6 * inch * s, 4 * inch * s]
    )
    combined.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('LINEBEFORE', (1, 0), (1, -1), 1, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    return combined

from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch


def ledger_details_table(ledger_data, print_config=None):
    styles = getSampleStyleSheet()
    fs = _get_font_size(print_config)
    normal = ParagraphStyle('ledger_normal', parent=styles['Normal'], fontSize=fs)
    bold   = ParagraphStyle('ledger_bold',   parent=styles['Normal'], fontSize=fs, fontName='Helvetica-Bold')
    header_color = get_header_color(print_config) if print_config else colors.HexColor('#f0f0f0')
    s = get_width_scale(print_config) if print_config else 1.0

    # Column widths scale with paper size
    # voucher_no needs 1.7" to fit "SO-INV-XXXX-XXXXX" without wrapping
    col_widths = [1.2*inch*s, 1.7*inch*s, 3.0*inch*s, 1.2*inch*s, 1.2*inch*s, 1.7*inch*s]

    table_data = [[
        Paragraph("<b>Date</b>", bold),
        Paragraph("<b>Voucher No</b>", bold),
        Paragraph("<b>Description</b>", bold),
        Paragraph("<b>Debit</b>", bold),
        Paragraph("<b>Credit</b>", bold),
        Paragraph("<b>Balance</b>", bold),
    ]]

    for row in ledger_data:
        table_data.append([
            Paragraph(row.get('date', ''), normal),
            Paragraph(row.get('voucher_no', ''), normal),
            Paragraph(row.get('description', ''), normal),
            # Numeric cells as plain strings — no mid-number wrap
            f"{(row.get('debit') or 0):,.2f}",
            f"{(row.get('credit') or 0):,.2f}",
            f"{(row.get('balance') or 0):,.2f}",
        ])

    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), fs),
        ('LINEBEFORE', (0, 0), (-1, -1), 0.8, colors.black),
        ('LINEAFTER', (-1, 0), (-1, -1), 0.8, colors.black),
        ('LINEABOVE', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
        ('LINEBELOW', (0, -1), (-1, -1), 0.8, colors.black),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),  # Debit/Credit/Balance right-aligned
        ('ALIGN', (0, 0), (2, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    return table


def ledger_amount_summary(total_debit, total_credit, closing_balance, balance_in_words, print_config=None):
    styles = getSampleStyleSheet()
    fs = _get_font_size(print_config)
    normal_style = ParagraphStyle('ledger_sum_normal', parent=styles['Normal'], fontSize=fs)
    s = get_width_scale(print_config) if print_config else 1.0

    debit_para   = Paragraph(f"<b>Total Debit:</b> {total_debit:,.2f}", normal_style)
    credit_para  = Paragraph(f"<b>Total Credit:</b> {total_credit:,.2f}", normal_style)
    balance_para = Paragraph(f"<b>Closing Balance:</b> {closing_balance:,.2f}", normal_style)
    words_para   = Paragraph(f"<b>Balance in Words:</b> {balance_in_words}", normal_style)

    summary_table = Table(
        [[debit_para, credit_para], [balance_para, words_para]],
        colWidths=[5 * inch * s, 5 * inch * s]
    )
    summary_table.setStyle(TableStyle([
        ('BOX',    (0, 0), (-1, -1), 1, colors.black),
        ('LINEBEFORE', (1, 0), (1, -1), 1, colors.black),
        ('LINEBELOW',  (0, 0), (-1, 0), 0.5, colors.HexColor('#CCCCCC')),
        ('LEFTPADDING',  (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING',   (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    return summary_table

def ledger_period_details(from_date, to_date, print_config=None):
    fs = _get_font_size(print_config)
    style = ParagraphStyle(
        'PeriodStyle',
        parent=getSampleStyleSheet()['Normal'],
        fontSize=fs,
        alignment=1,  # Center
        spaceAfter=10
    )

    if from_date and to_date:
        text = f"<b>Period : {from_date} &nbsp; to &nbsp; {to_date} </b>"
    else:
        text = "<b>Period:</b> All Dates"

    return Paragraph(text, style)

def ledger_doc_details(ledgername, ledger_name, number_lbl, date_lbl, doc_date, print_config=None):
    s = get_width_scale(print_config) if print_config else 1.0
    col_widths = [5*inch*s, 5*inch*s]
    table_data_1 = [
        [f'{ledger_name} : {number_lbl}', f'{date_lbl} : {doc_date}'],
    ]

    table = Table(table_data_1, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), get_header_color(print_config) if print_config else colors.skyblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 1), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, 0), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
    ]))
    return table

# ─── Delivery Challan specific functions ─────────────────────────────────────

def dc_product_total_details_inwords(
    Bill_Amount_In_Words, SubTotal, Discount_Amt, transport_charges,
    total_cgst, total_sgst, total_igst, cess_amount,
    round_off, net_value, tax_type='Exclusive', print_config=None
):
    """Totals section for Delivery Challan — no Party Old Balance, Transport Charges label."""
    # Reuse the main totals function with Party_Old_Balance=0 and net_lbl='Net Amount'
    return product_total_details_inwords(
        Bill_Amount_In_Words=Bill_Amount_In_Words,
        SubTotal=SubTotal,
        Discount_Amt=Discount_Amt,
        shipping_charges=transport_charges,
        total_cgst=total_cgst,
        total_sgst=total_sgst,
        total_igst=total_igst,
        cess_amount=cess_amount,
        round_off=round_off,
        Party_Old_Balance=0,
        net_lbl='Net Amount',
        net_value=net_value,
        tax_type=tax_type,
        print_config=print_config,
    )


def dc_footer_section(vehicle_name='', driver_name='', lr_no='', total_boxes=None, remarks='', print_config=None):
    """Footer for Delivery Challan — dispatch details + dual signatory. No bank details."""
    s = get_width_scale(print_config)
    styles = getSampleStyleSheet()
    style_normal = styles['Normal']

    dispatch_lines = []
    if vehicle_name:
        dispatch_lines.append(f"<b>Vehicle:</b> {vehicle_name}")
    if driver_name:
        dispatch_lines.append(f"<b>Driver:</b> {driver_name}")
    if lr_no:
        dispatch_lines.append(f"<b>LR No:</b> {lr_no}")
    if total_boxes is not None:
        dispatch_lines.append(f"<b>Total Boxes:</b> {total_boxes}")

    if dispatch_lines:
        dispatch_html = "<b>Dispatch Details:</b><br/>" + "<br/>".join(dispatch_lines)
    else:
        dispatch_html = ""

    notes_html = ""
    if remarks and remarks.strip():
        notes_html += f"<b>Remarks:</b> {remarks}<br/><br/>"
    notes_html += "<b>Notes:</b><br/>Goods dispatched in good condition. Please verify count on receipt."

    left_body = (dispatch_html + "<br/><br/>" + notes_html) if dispatch_html else notes_html
    left_content = Paragraph(left_body, style_normal)

    # Signature blocks — mini-table with LINEABOVE border as the signature line
    sig_style = ParagraphStyle(
        'sig_label',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica-Bold',
        alignment=1,  # CENTER
    )

    def _sig_cell(label_text):
        label_para = Paragraph(label_text, sig_style)
        inner = Table(
            [[''], [label_para]],
            colWidths=[1.8 * inch * s],
            rowHeights=[0.02 * inch, 0.3 * inch]
        )
        inner.setStyle(TableStyle([
            ('LINEABOVE', (0, 1), (0, 1), 0.8, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        return inner

    table = Table(
        [[left_content, _sig_cell('Authorised Signatory'), _sig_cell("Receiver's Signature")]],
        colWidths=[5.6 * inch * s, 2.2 * inch * s, 2.2 * inch * s],
        rowHeights=[2.5 * inch]
    )
    table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('LINEBEFORE', (1, 0), (1, -1), 1, colors.black),
        ('LINEBEFORE', (2, 0), (2, -1), 1, colors.black),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (2, 0), 'CENTER'),
        ('VALIGN', (0, 0), (0, 0), 'TOP'),
        ('VALIGN', (1, 0), (2, 0), 'BOTTOM'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ]))
    return table
