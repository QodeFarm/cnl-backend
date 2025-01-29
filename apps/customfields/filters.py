from django_filters import rest_framework as filters
import uuid
from django.db.models import Q
from apps.customer.models import Customer
from config.utils_methods import filter_uuid


class CustomFieldValuesFilters(filters.FilterSet):
    entity_data_id = filters.CharFilter(field_name='entity_data_id', lookup_expr='exact')
    entity_id = filters.CharFilter(field_name='entity_id', lookup_expr='exact')