"""
Column sizing for every printed table: no value may ever be drawn outside its column.

Pure functions over reportlab metrics — no DB, no tenant:
    python apps/masters/template/test_col_widths.py
"""
import os
import sys

import django

# table_defination imports Django models at module level, so the app registry has to be
# up before it can be imported — even though nothing under test touches the database.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from reportlab.lib.pagesizes import inch
from reportlab.pdfbase.pdfmetrics import stringWidth

from apps.masters.template.print_config_defaults import get_default_template_config
from apps.masters.template.table_defination import (
    _compute_table_layout, _resolve_product_columns, _totals_probe_row, _is_wrappable,
    _proportional_col_widths, MIN_WRAPPABLE_WIDTH, MIN_TABLE_FONT_SIZE,
    product_details, product_total_details, ledger_details_table, payment_details_table,
    _COL_WIDTHS_CACHE_KEY,
)

TOTAL_WIDTH = 10.0 * inch
FS = 10
PAD = 5

ITEM_ROWS = [
    ['1', 'BJF KERALA 350 mL INJ MOULDING GLASS WITH PRINT', '9.00', '13,500.00', '-', '3.65', '49,275.00', '0.00', '0.00', '0.00', '49,275.00'],
    ['2', 'SMILEY FANCY LID RED', '-', '13,500.00', '-', '1.50', '20,250.00', '0.00', '0.00', '0.00', '20,250.00'],
    ['3', 'DOME LID RED', '-', '1,500.00', '-', '1.60', '2,400.00', '0.00', '0.00', '0.00', '2,400.00'],
]


def _assert_fits(cols, widths, rows, fs, pad=PAD):
    """Every cell that cannot wrap must draw inside its column, padding included."""
    for i, col in enumerate(cols):
        if _is_wrappable(col):
            continue
        for row in rows:
            if i >= len(row):
                continue
            drawn = stringWidth(str(row[i] or ''), 'Helvetica', fs) + 2 * pad
            assert drawn <= widths[i] + 0.01, (
                f"{col['key']}: '{row[i]}' needs {drawn:.1f}pt at {fs}pt, column is {widths[i]:.1f}pt"
            )


def test_wide_quantities_do_not_overflow():
    """The reported bug: 13,500.00 in a 0.55in Qty column painted over the ruling."""
    cols = _resolve_product_columns(None, show_gst=True)
    widths, fs = _compute_table_layout(cols, TOTAL_WIDTH, rows=ITEM_ROWS, fs=FS, cell_pad=PAD)
    _assert_fits(cols, widths, ITEM_ROWS, fs)
    assert fs == FS, 'this table fits at full size, nothing should have been shrunk'
    assert abs(sum(widths) - TOTAL_WIDTH) < 1, f'table must still fill the page, got {sum(widths)}'


def test_totals_row_is_measured_too():
    """The totals row is drawn by another function and is wider than any single line."""
    cols = _resolve_product_columns(None, show_gst=True)
    probe = _totals_probe_row(cols, ITEM_ROWS)
    widths, fs = _compute_table_layout(cols, TOTAL_WIDTH, rows=ITEM_ROWS + [probe], fs=FS, cell_pad=PAD)
    _assert_fits(cols, widths, ITEM_ROWS + [probe], fs)


def test_huge_numbers_squeeze_product_not_the_page():
    """Crore-scale values grow the numeric columns; Product gives up room, with a floor."""
    cols = _resolve_product_columns(None, show_gst=True)
    rows = [['1', 'A VERY LONG PRODUCT NAME THAT WILL WRAP', '1,234.00', '9,99,99,999.00',
             'Nos', '9,99,999.00', '9,99,99,99,999.00', '99.00', '9,99,999.00', '9,99,999.00', '9,99,99,99,999.00']]
    widths, fs = _compute_table_layout(cols, TOTAL_WIDTH, rows=rows, fs=FS, cell_pad=PAD)
    _assert_fits(cols, widths, rows, fs)
    name_i = next(i for i, c in enumerate(cols) if c['key'] == 'product_name')
    assert widths[name_i] >= MIN_WRAPPABLE_WIDTH - 0.01, 'product column starved below its floor'


def test_font_shrinks_rather_than_clipping():
    """
    Last resort: when the numbers cannot fit at the requested size even after squeezing
    the text columns, the font steps down. A clipped digit is a wrong number.
    """
    cols = _resolve_product_columns(None, show_gst=True)
    rows = [['999999', 'X', '9,99,99,999.00', '9,99,99,99,999.00', 'Nos', '9,99,99,99,999.00',
             '9,99,99,99,999.00', '9,999.00', '9,99,99,99,999.00', '9,99,99,99,999.00', '99,99,99,99,999.00']]
    widths, fs = _compute_table_layout(cols, TOTAL_WIDTH, rows=rows, fs=FS, cell_pad=PAD)
    assert fs < FS, 'should have shrunk the font to make these fit'
    assert fs >= MIN_TABLE_FONT_SIZE
    _assert_fits(cols, widths, rows, fs)
    assert sum(widths) <= TOTAL_WIDTH + 0.01


def test_no_rows_keeps_the_old_proportional_layout():
    cols = _resolve_product_columns(None, show_gst=True)
    widths, fs = _compute_table_layout(cols, TOTAL_WIDTH)
    assert widths == _proportional_col_widths(cols, TOTAL_WIDTH)
    assert fs == 10


def test_narrow_paper_still_fits_the_page():
    """
    A5 is the tightest shape. It works because _resolve_product_columns drops to the
    essential columns first — that column-dropping is the pressure valve that keeps the
    measured fit reachable, so resolve columns the way the real render does.
    """
    a5_width = 4.83 * inch
    cols = _resolve_product_columns(None, show_gst=True, print_config={'paper_size': 'A5'})
    assert len(cols) == 5, 'A5 should have been reduced to the essential columns'
    # S.No, Product, Qty, Rate, Total Amount — the five A5 keeps.
    rows = [[r[0], r[1], r[3], r[5], r[10]] for r in ITEM_ROWS]
    widths, fs = _compute_table_layout(cols, a5_width, rows=rows, fs=9, cell_pad=3)
    _assert_fits(cols, widths, rows, fs, pad=3)
    assert sum(widths) <= a5_width + 0.01, f'overflowed the sheet: {sum(widths)} > {a5_width}'


def test_impossible_layout_stays_inside_the_page():
    """
    More columns than any font can serve (11 crore-scale numbers on A5) is physically
    unsatisfiable. The contract there is narrower: the table still fits the sheet at the
    floor font rather than running off it. Reaching this means columns should have been
    dropped upstream — which is exactly what _resolve_product_columns does for A5.
    """
    a5_width = 4.83 * inch
    cols = _resolve_product_columns(None, show_gst=True)  # deliberately NOT reduced
    widths, fs = _compute_table_layout(cols, a5_width, rows=ITEM_ROWS, fs=9, cell_pad=3)
    assert fs == MIN_TABLE_FONT_SIZE
    assert sum(widths) <= a5_width + 0.01, f'overflowed the sheet: {sum(widths)} > {a5_width}'


def test_items_table_and_totals_row_share_one_grid():
    """A totals row on a different grid shows up as a broken, misaligned ruling."""
    cfg = get_default_template_config('sale_order')
    data = [
        ['1', 'BJF KERALA 350 mL INJ MOULDING GLASS WITH PRINT', '9.00', '13500', '-', '3.65', '49275', '0', '0', '0', '49275'],
        ['2', 'SMILEY FANCY LID RED', '-', '13500', '-', '1.50', '20250', '0', '0', '0', '20250'],
    ]
    items  = product_details(data, show_gst=True, print_config=cfg)
    totals = product_total_details(30000, 77400, 77400, 0, show_gst=True, print_config=cfg)
    assert _COL_WIDTHS_CACHE_KEY in cfg
    assert [round(w, 3) for w in items._argW] == [round(w, 3) for w in totals._argW]


def test_ledger_balances_fit_their_columns():
    """A running balance grows without bound — the widest one still has to fit."""
    cols = [
        {'key': 'date',        'label': 'Date',        'base_width': 1.2, 'wrappable': True},
        {'key': 'voucher_no',  'label': 'Voucher No',  'base_width': 1.7, 'wrappable': True},
        {'key': 'description', 'label': 'Description', 'base_width': 3.0, 'wrappable': True},
        {'key': 'debit',       'label': 'Debit',       'base_width': 1.2},
        {'key': 'credit',      'label': 'Credit',      'base_width': 1.2},
        {'key': 'balance',     'label': 'Balance',     'base_width': 1.7},
    ]
    rows = [
        ['30-07-2026', 'SO-INV-2607-00925', 'Sales against invoice for BJF KERALA 350 mL',
         '9,99,99,999.00', '0.00', '12,34,56,789.00'],
    ]
    widths, fs = _compute_table_layout(cols, TOTAL_WIDTH, rows=rows, fs=10, cell_pad=6)
    _assert_fits(cols, widths, rows, fs, pad=6)

    # And through the real builder, which must not raise and must fill the page.
    table = ledger_details_table(
        [{'date': r[0], 'voucher_no': r[1], 'description': r[2],
          'debit': 99999999, 'credit': 0, 'balance': 123456789} for r in rows],
        print_config=get_default_template_config('account_ledger'),
    )
    assert abs(sum(table._argW) - TOTAL_WIDTH) < 1


def test_payment_receipt_amounts_fit_their_columns():
    """Same defect as the ledger: the receipt table equal-split the page."""
    table = payment_details_table(
        [{'invoice_no': 'SO-INV-2607-00925', 'invoice_date': '2026-07-30',
          'payment_method': 'Credit Card', 'cheque_no': '',
          'amount': 123456789.5, 'total': 987654321.75}],
        print_config=get_default_template_config('payment_receipt'),
    )
    widths = table._argW
    assert abs(sum(widths) - TOTAL_WIDTH) < 1
    # Amount Paid and Total Amount are the last two columns and are drawn as plain strings.
    for i, value in ((len(widths) - 2, '12,34,56,789.50'), (len(widths) - 1, '98,76,54,321.75')):
        needed = stringWidth(value, 'Helvetica', 10) + 12
        assert needed <= widths[i] + 0.01, f"'{value}' needs {needed:.1f}pt, column is {widths[i]:.1f}pt"


if __name__ == '__main__':
    for name, fn in sorted(globals().items()):
        if name.startswith('test_'):
            fn()
            print(f'ok  {name}')
    print('\nall column-width checks passed')
