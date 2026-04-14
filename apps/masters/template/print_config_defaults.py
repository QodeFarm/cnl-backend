"""
Document Print Configuration Defaults
Enterprise-grade document template configuration system.
Defines all available columns, sections, styles, and paper sizes per document type.
"""

from reportlab.lib import colors as rl_colors
from reportlab.lib.pagesizes import inch

# ─────────────────────────────────────────────
# PAPER SIZES
# ─────────────────────────────────────────────
PAPER_SIZES = {
    'Custom_11x16': {'width': 11 * inch, 'height': 16 * inch, 'label': 'Custom 11×16 (Default)', 'usable_width': 10.0 * inch},
    'A4':           {'width': 8.27 * inch, 'height': 11.69 * inch, 'label': 'A4 Portrait', 'usable_width': 7.27 * inch},
    'A4_Landscape': {'width': 11.69 * inch, 'height': 8.27 * inch, 'label': 'A4 Landscape', 'usable_width': 10.69 * inch},
    'A5':           {'width': 5.83 * inch, 'height': 8.27 * inch, 'label': 'A5 Portrait', 'usable_width': 4.83 * inch},
    'Letter':       {'width': 8.5 * inch, 'height': 11 * inch, 'label': 'Letter Portrait', 'usable_width': 7.5 * inch},
}

# Width scale factor relative to Custom_11x16 (usable_width 10")
PAPER_WIDTH_SCALE = {
    'Custom_11x16': 1.0,
    'A4':           0.727,
    'A4_Landscape': 1.069,
    'A5':           0.483,
    'Letter':       0.75,
}

# ─────────────────────────────────────────────
# COLOR THEMES
# ─────────────────────────────────────────────
COLOR_THEMES = {
    'blue':   rl_colors.HexColor('#87CEEB'),  # skyblue — current default
    'green':  rl_colors.HexColor('#90EE90'),  # lightgreen
    'orange': rl_colors.HexColor('#FFDAB9'),  # peachpuff
    'grey':   rl_colors.HexColor('#D3D3D3'),  # lightgrey
    'purple': rl_colors.HexColor('#E6E6FA'),  # lavender
    'teal':   rl_colors.HexColor('#B2DFDB'),  # teal light
    'none':   rl_colors.HexColor('#FFFFFF'),  # white
}

# ─────────────────────────────────────────────
# COLUMN DEFINITIONS
# ─────────────────────────────────────────────
# data_index maps to the position in the product data list returned by extract_product_data()
# Format: [Idx, Product, Boxes, Qty, Unit Name, Rate, Amount, Disc(%), Disc(Rs), GST(Rs), Total Amount]

SALES_PURCHASE_COLUMN_DEFINITIONS = [
    # base_width = proportional width in inches on a 10" usable page (Custom_11x16)
    # Product name gets the most space; numeric/short cols get less
    {'key': 'serial_no',        'label': 'S.No',         'data_index': 0,  'required': True,  'default': True,  'base_width': 0.40},
    {'key': 'product_name',     'label': 'Product',      'data_index': 1,  'required': True,  'default': True,  'base_width': 2.80},
    {'key': 'boxes',            'label': 'Boxes',        'data_index': 2,  'required': False, 'default': True,  'base_width': 0.50},
    {'key': 'quantity',         'label': 'Qty',          'data_index': 3,  'required': True,  'default': True,  'base_width': 0.55},
    {'key': 'unit',             'label': 'Unit',         'data_index': 4,  'required': False, 'default': True,  'base_width': 0.60},
    {'key': 'rate',             'label': 'Rate',         'data_index': 5,  'required': True,  'default': True,  'base_width': 0.80},
    {'key': 'amount',           'label': 'Amount',       'data_index': 6,  'required': False, 'default': True,  'base_width': 0.85},
    {'key': 'discount_percent', 'label': 'Disc (%)',     'data_index': 7,  'required': False, 'default': True,  'base_width': 0.65},
    {'key': 'discount_amount',  'label': 'Disc (Rs)',    'data_index': 8,  'required': False, 'default': False, 'base_width': 0.65},
    {'key': 'gst_amount',       'label': 'GST (Rs)',     'data_index': 9,  'required': False, 'default': True,  'base_width': 0.75},
    {'key': 'total_amount',     'label': 'Total Amount', 'data_index': 10, 'required': True,  'default': True,  'base_width': 1.00},
]

PAYMENT_RECEIPT_COLUMN_DEFINITIONS = [
    {'key': 'invoice_no',      'label': 'Invoice No.',    'required': True,  'default': True},
    {'key': 'invoice_date',    'label': 'Invoice Date',   'required': False, 'default': True},
    {'key': 'payment_method',  'label': 'Payment Method', 'required': False, 'default': True},
    {'key': 'reference_no',    'label': 'Reference No.',  'required': False, 'default': True},
    {'key': 'amount_paid',     'label': 'Amount Paid',    'required': True,  'default': True},
    {'key': 'total_amount',    'label': 'Total Amount',   'required': True,  'default': True},
]

LEDGER_COLUMN_DEFINITIONS = [
    {'key': 'date',        'label': 'Date',        'required': True,  'default': True},
    {'key': 'voucher_no',  'label': 'Voucher No.', 'required': False, 'default': True},
    {'key': 'description', 'label': 'Description', 'required': True,  'default': True},
    {'key': 'debit',       'label': 'Debit',       'required': True,  'default': True},
    {'key': 'credit',      'label': 'Credit',      'required': True,  'default': True},
    {'key': 'balance',     'label': 'Balance',     'required': True,  'default': True},
]

# Map document_type -> column definitions
COLUMN_DEFINITIONS_BY_DOC_TYPE = {
    'sale_order':      SALES_PURCHASE_COLUMN_DEFINITIONS,
    'sale_invoice':    SALES_PURCHASE_COLUMN_DEFINITIONS,
    'sale_return':     SALES_PURCHASE_COLUMN_DEFINITIONS,
    'delivery_challan': SALES_PURCHASE_COLUMN_DEFINITIONS,
    'purchase_order':  SALES_PURCHASE_COLUMN_DEFINITIONS,
    'purchase_return': SALES_PURCHASE_COLUMN_DEFINITIONS,
    'payment_receipt': PAYMENT_RECEIPT_COLUMN_DEFINITIONS,
    'bill_receipt':    PAYMENT_RECEIPT_COLUMN_DEFINITIONS,
    'account_ledger':  LEDGER_COLUMN_DEFINITIONS,
}

# ─────────────────────────────────────────────
# SECTION DEFINITIONS
# ─────────────────────────────────────────────
DEFAULT_SECTION_CONFIG = {
    # Header
    'show_logo':             True,
    'show_company_name':     True,
    'show_company_address':  True,
    'show_company_phone':    True,
    'show_company_email':    True,
    'show_gstin':            True,
    # Customer/Vendor block
    'show_billing_address':  True,
    'show_shipping_address': True,
    # Financial summary
    'show_subtotal':         True,
    'show_discount':         True,
    'show_shipping_charges': True,
    'show_cess':             True,
    'show_round_off':        True,
    'show_party_balance':    True,
    'show_tax_breakdown':    True,   # CGST/SGST/IGST rows
    'show_amount_in_words':  True,
    # Footer
    'show_bank_details':     True,
    'show_terms':            True,
    'show_notes':            True,
    'show_signature':        True,
    'show_declaration':      True,
}

# ─────────────────────────────────────────────
# STYLE DEFAULTS
# ─────────────────────────────────────────────
DEFAULT_STYLE_CONFIG = {
    'color_theme': 'blue',   # key from COLOR_THEMES
    'font_size':   'medium', # small | medium | large
}

FONT_SIZE_MAP = {
    'small':  8,
    'medium': 10,
    'large':  12,
}

# ─────────────────────────────────────────────
# COPY DEFAULTS
# ─────────────────────────────────────────────
DEFAULT_COPY_CONFIG = {
    'num_copies':   1,
    'copy_labels':  ['ORIGINAL FOR RECIPIENT'],
}

# ─────────────────────────────────────────────
# CUSTOM TEXT DEFAULTS
# ─────────────────────────────────────────────
DEFAULT_CUSTOM_TEXT = {
    'terms_conditions': (
        "1. Goods once sold cannot be taken back\n"
        "2. Warranty as per manufacturer terms\n"
        "3. Interest @ 24% p.a. after 15 days\n"
        "4. Subject to local Jurisdiction"
    ),
    'notes':       'Thank you for the Business',
    'declaration': (
        'We declare that this invoice shows the actual price of the '
        'goods/services described and that all particulars are true and correct.'
    ),
    'header_note': '',
    'footer_note': '',
}

# ─────────────────────────────────────────────
# HELPER: build default column_config list
# ─────────────────────────────────────────────
def get_default_column_config(document_type):
    """
    Returns a list of column config dicts for the given document_type,
    using default visibility and order.
    """
    definitions = COLUMN_DEFINITIONS_BY_DOC_TYPE.get(document_type, SALES_PURCHASE_COLUMN_DEFINITIONS)
    return [
        {
            'key':     col['key'],
            'label':   col['label'],
            'visible': col['default'],
            'order':   idx + 1,
        }
        for idx, col in enumerate(definitions)
    ]


def get_default_template_config(document_type):
    """Returns a full default template config dict for the given document_type."""
    return {
        'paper_size':    'Custom_11x16',
        'column_config': get_default_column_config(document_type),
        'section_config': dict(DEFAULT_SECTION_CONFIG),
        'style_config':  dict(DEFAULT_STYLE_CONFIG),
        'copy_config':   dict(DEFAULT_COPY_CONFIG),
        'custom_text':   dict(DEFAULT_CUSTOM_TEXT),
    }


def resolve_print_config(template_obj, document_type):
    """
    Given a DocumentPrintTemplate ORM object (or None), returns a resolved
    config dict ready for use in PDF builders. Falls back to defaults gracefully.
    """
    default = get_default_template_config(document_type)

    if template_obj is None:
        return default

    return {
        'paper_size':     template_obj.paper_size or default['paper_size'],
        'column_config':  template_obj.column_config or default['column_config'],
        'section_config': {**default['section_config'], **(template_obj.section_config or {})},
        'style_config':   {**default['style_config'],   **(template_obj.style_config or {})},
        'copy_config':    {**default['copy_config'],     **(template_obj.copy_config or {})},
        'custom_text':    {**default['custom_text'],     **(template_obj.custom_text or {})},
    }


def get_header_color(config):
    """Returns the ReportLab color object for the given config's color_theme."""
    theme = (config.get('style_config') or {}).get('color_theme', 'blue')
    return COLOR_THEMES.get(theme, COLOR_THEMES['blue'])


def get_width_scale(config):
    """Returns the width scale factor for column width calculations."""
    paper_size = config.get('paper_size', 'Custom_11x16')
    return PAPER_WIDTH_SCALE.get(paper_size, 1.0)
