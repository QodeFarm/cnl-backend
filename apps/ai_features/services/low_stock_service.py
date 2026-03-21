from django.db.models import F, Value, CharField, IntegerField, Case, When, Q
from apps.products.models import Products


def get_low_stock_products(limit=500):
    """
    Returns products where current balance is below minimum_level.
    Only includes non-deleted products (active or no status set) that have a minimum_level set.
    """
    queryset = Products.objects.filter(
        is_deleted=False,
        minimum_level__isnull=False,
        balance__lt=F('minimum_level')
    ).exclude(
        status='Inactive'
    ).annotate(
        shortage=F('minimum_level') - F('balance'),
        reorder_qty=Case(
            When(maximum_level__isnull=False, then=F('maximum_level') - F('balance')),
            default=F('minimum_level') - F('balance'),
            output_field=IntegerField()
        ),
        severity=Case(
            When(balance=0, then=Value('critical')),
            When(balance__lt=F('minimum_level') / 2, then=Value('high')),
            default=Value('medium'),
            output_field=CharField()
        )
    ).select_related(
        'product_group_id',
        'category_id',
        'unit_options_id'
    ).order_by('balance')[:limit]

    return queryset
