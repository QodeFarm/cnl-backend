"""
Guard: every list that declares a document date must actually be able to filter by it.

The dangerous failure is silent. If a FilterSet says `document_date_field = 'invoice_date'`
but has no matching range filter, then `?invoice_date_after=...` is an unknown parameter,
django-filter ignores it, and the screen returns EVERY row while looking like it filtered.
No error, no empty list — just wrong data that looks right.

This test fails loudly instead. Run it after touching any filters.py:

    python config/test_document_date_wiring.py
"""
import os
import sys

import django

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import models
import django_filters

APPS = ['sales', 'purchase', 'finance', 'production', 'hrms', 'customer', 'vendor',
        'products', 'inventory', 'tasks', 'leads', 'reminders', 'masters', 'users',
        'assets', 'company', 'customfields', 'auditlogs']


def declared_filtersets():
    for app in APPS:
        try:
            mod = __import__(f'apps.{app}.filters', fromlist=['filters'])
        except Exception:
            continue
        for name in sorted(dir(mod)):
            obj = getattr(mod, name)
            if (isinstance(obj, type) and issubclass(obj, django_filters.FilterSet)
                    and obj is not django_filters.FilterSet
                    and getattr(obj, 'document_date_field', None)):
                yield app, name, obj


def test_every_document_date_has_a_range_filter():
    """Without the range filter the parameter is ignored and nothing is filtered."""
    broken = []
    for app, name, FS in declared_filtersets():
        field = FS.document_date_field
        try:
            base = FS.base_filters
        except Exception as e:
            broken.append(f'{app}.{name}: FilterSet fails to build ({type(e).__name__})')
            continue
        if not any(isinstance(f, django_filters.DateFromToRangeFilter)
                   and (f.field_name or key) == field
                   for key, f in base.items()):
            broken.append(f'{app}.{name}: document_date_field={field!r} has no matching '
                          f'DateFromToRangeFilter — the filter would silently match everything')
    assert not broken, 'Unwired document dates:\n  ' + '\n  '.join(broken)


def test_document_date_resolves_on_the_model():
    """A typo in the field name would also silently disable filtering."""
    broken = []
    for app, name, FS in declared_filtersets():
        model = getattr(getattr(FS, 'Meta', None), 'model', None)
        if not isinstance(model, type):
            continue
        current = model
        for part in FS.document_date_field.split('__'):
            try:
                f = current._meta.get_field(part)
            except Exception:
                broken.append(f'{app}.{name}: {FS.document_date_field!r} does not resolve on {model.__name__}')
                break
            current = f.related_model or current
    assert not broken, 'Unresolvable document dates:\n  ' + '\n  '.join(broken)


def test_document_date_is_a_date_column():
    """Guards against pointing at a name/number column by accident."""
    broken = []
    for app, name, FS in declared_filtersets():
        model = getattr(getattr(FS, 'Meta', None), 'model', None)
        if not isinstance(model, type):
            continue
        current, field = model, None
        try:
            for part in FS.document_date_field.split('__'):
                field = current._meta.get_field(part)
                current = field.related_model or current
        except Exception:
            continue
        if field is not None and not isinstance(field, (models.DateField, models.DateTimeField)):
            broken.append(f'{app}.{name}: {FS.document_date_field!r} is {type(field).__name__}, not a date')
    assert not broken, 'Non-date document dates:\n  ' + '\n  '.join(broken)


if __name__ == '__main__':
    total = len(list(declared_filtersets()))
    failed = 0
    for fn_name, fn in sorted(globals().items()):
        if not fn_name.startswith('test_'):
            continue
        try:
            fn()
            print(f'ok  {fn_name}')
        except AssertionError as e:
            failed += 1
            print(f'FAIL {fn_name}\n{e}')
    print(f'\n{total} FilterSets declare a document date; {failed} checks failed')
    sys.exit(1 if failed else 0)
