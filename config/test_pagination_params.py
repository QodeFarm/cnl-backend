"""
The pagination clamp — the guardrail every list endpoint inherits.

Pure function, no DB and no tenant needed:
    python config/test_pagination_params.py
"""
import os
import sys

import django

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from config.utils_methods import (
    get_pagination_params, MAX_PAGE_LIMIT, DEFAULT_PAGE_LIMIT,
)


def params(query=''):
    return get_pagination_params(Request(APIRequestFactory().get('/x' + query)))


def test_defaults_when_nothing_asked():
    page, limit, start, end = params()
    assert (page, limit, start, end) == (1, DEFAULT_PAGE_LIMIT, 0, DEFAULT_PAGE_LIMIT)


def test_normal_paging_maths():
    assert params('?page=3&limit=20') == (3, 20, 40, 60)


def test_hostile_limit_is_clamped():
    """?limit=1000000 previously went straight through to a slice."""
    page, limit, start, end = params('?limit=1000000')
    assert limit == MAX_PAGE_LIMIT
    assert end - start == MAX_PAGE_LIMIT


def test_page_size_dropdown_ceiling_fits_under_the_cap():
    """The UI offers up to 100; the server must not reject or truncate that."""
    assert params('?limit=100')[1] == 100
    assert 100 <= MAX_PAGE_LIMIT


def test_junk_and_out_of_range_values_do_not_explode():
    assert params('?page=abc&limit=xyz') == (1, DEFAULT_PAGE_LIMIT, 0, DEFAULT_PAGE_LIMIT)
    assert params('?page=0')[0] == 1        # no negative offset
    assert params('?page=-5')[0] == 1
    assert params('?limit=0')[1] == 1       # never a zero-width page
    assert params('?limit=-3')[1] == 1
    assert params('?page=&limit=')[1] == DEFAULT_PAGE_LIMIT


def test_start_is_never_negative():
    for q in ('?page=0&limit=10', '?page=-1&limit=10', '?page=1&limit=10'):
        assert params(q)[2] >= 0


if __name__ == '__main__':
    for name, fn in sorted(globals().items()):
        if name.startswith('test_'):
            fn()
            print(f'ok  {name}')
    print(f'\npagination clamp holds (default {DEFAULT_PAGE_LIMIT}, max {MAX_PAGE_LIMIT})')
