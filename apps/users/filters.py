from django_filters import rest_framework as filters
from .models import RolePermissions
from config.utils_methods import filter_uuid
from django_filters import FilterSet, ChoiceFilter ,DateFromToRangeFilter
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
logger = logging.getLogger(__name__)

class RolePermissionsFilter(filters.FilterSet):
    
    role_id = filters.CharFilter(method=filter_uuid)

    # class Meta:
    #     model = RolePermissions
    #     fields =['role_id']
   
   