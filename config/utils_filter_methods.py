import json
import logging
import django_filters
from django.db import models
from django.db.models import Q
from django.forms import ValidationError
from rest_framework.response import Response
from rest_framework import status
logger = logging.getLogger(__name__)
from django.utils import timezone
import datetime

PERIOD_NAME_CHOICES = [
    ('today', 'Today'),
    ('yesterday', 'Yesterday'),
    ('last_week', 'LastWeek'),
    ('current_month', 'CurrentMonth'),
    ('last_month', 'LastMonth'),
    ('last_six_months', 'LastSixMonths'),
    ('current_quarter', 'CurrentQuarter'),
    ('year_to_date', 'YearToDate'),
    ('last_year', 'LastYear'),
]

DEFAULT_DOCUMENT_DATE_FIELD = 'created_at'


class DocumentDateFromToRangeFilter(django_filters.DateFromToRangeFilter):
    """
    A from/to date range that is correct on BOTH DateField and DateTimeField columns.

    Django's DateFromToRangeFilter compares the upper bound as given, so on a DateTimeField
    `?payment_date_before=2026-07-31` becomes `<= 2026-07-31 00:00:00` and silently drops
    every payment recorded later that day — the record disappears from its own date. Here
    the upper bound is widened to the end of the day when the column stores a time.
    Use this instead of DateFromToRangeFilter for any document date.
    """

    def filter(self, qs, value):
        if value is not None and value.stop is not None and qs is not None:
            try:
                model_field = qs.model._meta.get_field(self.field_name.split('__')[0])
                is_datetime = isinstance(model_field, models.DateTimeField)
            except Exception:
                is_datetime = False
            if is_datetime and not isinstance(value.stop, datetime.datetime):
                value = slice(
                    value.start,
                    datetime.datetime.combine(value.stop, datetime.time.max),
                )
        return super().filter(qs, value)


def get_document_date_field(filter_set):
    """
    The column a list filters its dates on.

    A document carries two dates: the one the user chose (order_date, invoice_date) and
    the timestamp the row happened to be saved (created_at). Filters, reports and periods
    must use the FORMER — an order entered today but dated the 1st belongs to the 1st.
    A FilterSet opts in by declaring `document_date_field`; anything that does not is
    left on created_at, so existing screens keep their current behaviour.
    """
    return getattr(filter_set, 'document_date_field', DEFAULT_DOCUMENT_DATE_FIELD)


def _has_field(model, path):
    """True when the (possibly related) field path resolves on this model."""
    try:
        parts = path.split('__')
        current = model
        for part in parts:
            field = current._meta.get_field(part)
            current = field.related_model or current
        return True
    except Exception:
        return False


def build_default_ordering(model, date_field):
    """
    The order a list is shown in when the user has not clicked a column.

    Newest DOCUMENT first — the date on the document, matching the column on screen and
    the date filter — then deterministic tiebreakers. The tiebreakers are not cosmetic:
    many documents share a date, and with a non-deterministic order MySQL can return the
    same row on two pages while another row never appears at all.
    """
    order = []
    if any(f.name == 'is_deleted' for f in model._meta.fields):
        order.append('is_deleted')                      # deleted rows sink to the bottom
    if date_field and _has_field(model, date_field):
        order.append(f'-{date_field}')
    if date_field != 'created_at' and any(f.name == 'created_at' for f in model._meta.fields):
        order.append('-created_at')                     # same date -> most recently entered
    order.append(f'-{model._meta.pk.name}')             # absolute tiebreaker, stable paging
    return order


def apply_default_ordering(filter_set, queryset):
    """Order a queryset by its document date. Falls back to the queryset's own order."""
    try:
        return queryset.order_by(*build_default_ordering(
            queryset.model, get_document_date_field(filter_set)))
    except Exception as e:
        logger.debug(f"default ordering skipped: {e}")
        return queryset


def _date_bounds_for(queryset, date_field, start_date, end_date):
    """
    Bounds matching the column's type. A DateField compares against plain dates; a
    DateTimeField needs the whole day (00:00:00 → 23:59:59.999999), or documents saved
    later in the day fall outside their own date.
    """
    try:
        model_field = queryset.model._meta.get_field(date_field)
        is_datetime = isinstance(model_field, models.DateTimeField)
    except Exception:
        is_datetime = True

    if not is_datetime:
        return start_date, end_date
    return (datetime.datetime.combine(start_date, datetime.time.min),
            datetime.datetime.combine(end_date, datetime.time.max))


def filter_by_period_name(self, queryset, name, value):
        today = timezone.now().date()
        start_date = None
        end_date = today

        # Check if custom from_date and to_date are provided in the URL. Read the screen's
        # own document-date params first, falling back to created_at_* for the screens
        # (and older callers) that still send those.
        date_field = get_document_date_field(self)
        from_date = self.data.get(f'{date_field}_after') or self.data.get('created_at_after')
        to_date = self.data.get(f'{date_field}_before') or self.data.get('created_at_before')

        if from_date and to_date:
            try:
                start_date = datetime.datetime.strptime(from_date, '%Y-%m-%d').date()
                end_date = datetime.datetime.strptime(to_date, '%Y-%m-%d').date()
            except ValueError:
                # Handle invalid date format
                print(f"Invalid date format: from_date={from_date}, to_date={to_date}")
                return queryset.none()
        else:
            # Determine the date range based on the period_name selected
            if value == 'today':
                start_date = end_date
            elif value == 'yesterday':
                start_date = end_date - datetime.timedelta(days=1)
                end_date = start_date
            elif value == 'last_week':
                start_date = today - datetime.timedelta(days=today.weekday() + 7)
                end_date = start_date + datetime.timedelta(days=6)
            elif value == 'current_month':
                start_date = today.replace(day=1)
            elif value == 'last_month':
                first_day_of_current_month = today.replace(day=1)
                last_day_of_last_month = first_day_of_current_month - datetime.timedelta(days=1)
                start_date = last_day_of_last_month.replace(day=1)
                end_date = last_day_of_last_month
            elif value == 'last_six_months':
                # Start of the month six months back — the same range the date picker
                # fills in on list screens. Using today-180d gave a different answer on
                # report screens, so "Last 6 Months" meant two things depending where you
                # asked. Plain month arithmetic, no extra dependency.
                month = today.month - 6
                year = today.year
                if month <= 0:
                    month += 12
                    year -= 1
                start_date = today.replace(year=year, month=month, day=1)
            elif value == 'current_quarter':
                quarter = (today.month - 1) // 3 + 1
                start_date = today.replace(month=(quarter - 1) * 3 + 1, day=1)
            elif value == 'year_to_date':
                # start_date = today.replace(month=1, day=1)
                start_date = today.replace(month=4, day=1)
            elif value == 'last_year':
                # start_date = today.replace(month=1, day=1) - datetime.timedelta(days=365)
                # end_date = today.replace(month=12, day=31)
                start_date = today.replace(month=4, day=1) - datetime.timedelta(days=365)
                end_date = today.replace(month=3, day=31)

  
        # Bound the range to the column's own type, then filter on the document date this
        # screen declared rather than a hardcoded created_at.
        if start_date and end_date:
            start_bound, end_bound = _date_bounds_for(queryset, date_field, start_date, end_date)
            queryset = queryset.filter(**{
                f'{date_field}__gte': start_bound,
                f'{date_field}__lte': end_bound,
            })

        return queryset

#=====================filter for page-limit-sort-search=======================================
def apply_sorting(self, queryset):
    sort_param = self.data.get('sort[0]')
    logger.debug(f"Sorting parameter: {sort_param}")

    if sort_param:
        try:
            sort_fields = sort_param.split(',')
            logger.debug(f"Sort fields: {sort_fields}")

            if len(sort_fields) != 2:
                raise ValueError("Sort parameter should be in the format 'field,DIRECTION'.")

            field, direction = sort_fields

            if field in self.filters:
                field_name = self.filters[field].field_name

                if direction.upper() == 'DESC':
                    field_name = f'-{field_name}'
                elif direction.upper() == 'ASC':
                    field_name = field_name
                else:
                    raise ValueError("Invalid sorting direction.")

                logger.debug(f"Sorting by field: {field_name} ({direction})")
                
                # Remove the 'is_deleted' ordering since it doesn't exist
                # Check if 'is_deleted' exists in the model before ordering
                if hasattr(queryset.model, 'is_deleted'):
                    queryset = queryset.order_by('is_deleted', field_name)
                else:
                    queryset = queryset.order_by(field_name)
                    
                logger.debug(f"Ordered queryset: {queryset.query}")
            else:
                raise ValueError(f"Field '{field}' is not a valid filter field.")

        except ValueError as e:
            logger.error(f"Sorting error: {e}")
            raise

    else:
        # No column chosen by the user: order by the DOCUMENT's own date, newest first.
        # This used to sort by whichever filter happened to be declared first (usually the
        # document number), so a backdated document jumped to the top of the list because
        # it had the newest number — contradicting the date column beside it.
        return apply_default_ordering(self, queryset)

    logger.debug(f"Sorting by field: {field_name}")
    
    # Final return with check
    if hasattr(queryset.model, 'is_deleted'):
        return queryset.order_by('is_deleted', field_name)
    else:
        return queryset.order_by(field_name)

# def apply_sorting(self, queryset):
#     sort_param = self.data.get('sort[0]')
#     logger.debug(f"Sorting parameter: {sort_param}")

#     if sort_param:
#         try:
#             sort_fields = sort_param.split(',')
#             logger.debug(f"Sort fields: {sort_fields}")

#             if len(sort_fields) != 2:
#                 raise ValueError("Sort parameter should be in the format 'field,DIRECTION'.")

#             field, direction = sort_fields

#             if field in self.filters:
#                 field_name = self.filters[field].field_name

#                 if direction.upper() == 'DESC':
#                     field_name = f'-{field_name}'
#                 elif direction.upper() == 'ASC':
#                     field_name = field_name
#                 else:
#                     raise ValueError("Invalid sorting direction.")

#                 logger.debug(f"Sorting by field: {field_name} ({direction})")
#                 queryset = queryset.order_by('is_deleted', field_name)
#                 logger.debug(f"Ordered queryset: {queryset.query}")
#             else:
#                 raise ValueError(f"Field '{field}' is not a valid filter field.")

#         except ValueError as e:
#             logger.error(f"Sorting error: {e}")
#             raise

#     else:
#         default_field = list(self.filters.keys())[0]
#         field_name = f'-{self.filters[default_field].field_name}'

#     logger.debug(f"Sorting by field: {field_name}")
    return queryset.order_by('is_deleted', field_name)

def filter_by_pagination(queryset, page, limit):
    logger.debug(f"Pagination - page: {page}, limit: {limit}")

    # Every FilterSet exposing page/limit reaches pagination through here, so this is the
    # one place the ceiling has to hold. `limit` arrives straight from the query string:
    # without a clamp, ?limit=1000000 slices a million rows and then serializes them.
    from config.utils_methods import MAX_PAGE_LIMIT
    try:
        page = max(1, int(page or 1))
    except (TypeError, ValueError):
        page = 1
    try:
        limit = max(1, min(int(limit or 1), MAX_PAGE_LIMIT))
    except (TypeError, ValueError):
        limit = MAX_PAGE_LIMIT

    start = (page - 1) * limit
    end = start + limit

    # Apply slicing to the QuerySet to get the paginated results
    paginated_queryset = queryset[start:end]
    logger.debug(f"Paginated queryset from {start} to {end}: {paginated_queryset.query}")

    total_count = queryset.count()
    logger.debug(f"Total records in the database: {total_count}")
    return paginated_queryset, total_count

def search_queryset(queryset, search_params, filter_set):
    if search_params:
        search_query = Q()
        
        # Loop through the search parameters
        for param in search_params:
            for key, value in param.items():
                # Check if the key exists in the filter set
                if key in filter_set.filters:
                    # Get the actual field name in the model
                    field_name = filter_set.filters[key].field_name
                    # Build the Q object for filtering
                    search_query |= Q(**{f"{field_name}__icontains": value})
                else:
                    logger.warning(f"Field {key} not in filter fields; skipping.")
        
        # Apply the search query to the queryset
        queryset = queryset.filter(search_query)
    
    return queryset

def filter_by_search(queryset, filter_set, value):
    try:
        search_params = json.loads(value)
        filter_set.search_params = search_params  # Set the search_params as an instance attribute
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding search params: {e}")
        raise ValidationError("Invalid search parameter format.")
    
    return search_queryset(queryset, search_params, filter_set)

def filter_by_simple_search(queryset, value, search_fields, filter_set=None):
    """
    Global simple text search utility for dropdown/autocomplete use-cases.
    Searches across multiple fields using OR logic with icontains.
    
    Args:
        queryset: The queryset to filter
        value: The search text
        search_fields: List of field names to search in (e.g., ['name', 'print_name', 'code'])
        filter_set: Optional filter_set instance to store search params for deferred execution
    
    Returns:
        Filtered queryset
    
    Usage in FilterSet:
        search = filters.CharFilter(method='filter_by_search_dropdown', label="Search")
        
        def filter_by_search_dropdown(self, queryset, name, value):
            return filter_by_simple_search(queryset, value, ['name', 'print_name', 'code'], self)
    """
    if not value or not search_fields:
        return queryset
    
    # Store search params for deferred execution (before pagination)
    if filter_set is not None:
        filter_set._simple_search_value = value
        filter_set._simple_search_fields = search_fields
        return queryset  # Don't filter yet, will be applied before pagination
    
    # Direct filtering (when no filter_set provided)
    search_query = Q()
    for field in search_fields:
        search_query |= Q(**{f"{field}__icontains": value})
    
    return queryset.filter(search_query)


def apply_simple_search(filter_set, queryset):
    """
    Apply deferred simple search filter before pagination.
    Called internally by filter_by_limit.
    """
    if hasattr(filter_set, '_simple_search_value') and hasattr(filter_set, '_simple_search_fields'):
        value = filter_set._simple_search_value
        search_fields = filter_set._simple_search_fields
        if value and search_fields:
            search_query = Q()
            for field in search_fields:
                search_query |= Q(**{f"{field}__icontains": value})
            queryset = queryset.filter(search_query)
    return queryset

def filter_by_sort(filter_set, queryset, value):
    return apply_sorting(filter_set, queryset)

def filter_by_page(filter_set, queryset, value):
    try:
        filter_set.page_number = int(value)
        logger.debug(f"Setting page number to {filter_set.page_number}")
        # Initialize limit if not set yet
        if not hasattr(filter_set, 'limit'):
            filter_set.limit = 10  # Default limit
        return queryset
    except (ValueError, TypeError) as e:
        logger.error(f"Error parsing page value: {e}")
        filter_set.page_number = 1  # Default to first page on error
        return queryset

def filter_by_limit(filter_set, queryset, value):
    try:
        filter_set.limit = int(value)
        logger.debug(f"Setting limit to {filter_set.limit}")
        # Initialize page if not set yet
        if not hasattr(filter_set, 'page_number'):
            filter_set.page_number = 1  # Default page
        
        # Apply simple search filter BEFORE pagination (if deferred)
        queryset = apply_simple_search(filter_set, queryset)
            
        # Apply sorting first
        queryset = apply_sorting(filter_set, queryset)
        
        # Apply pagination
        paginated_queryset, total_count = filter_by_pagination(queryset, filter_set.page_number, filter_set.limit)
        filter_set.total_count = total_count
        return paginated_queryset
    except (ValueError, TypeError) as e:
        logger.error(f"Error parsing limit value: {e}")
        filter_set.limit = 10  # Default to 10 items on error
        # Apply simple search filter BEFORE pagination (if deferred)
        queryset = apply_simple_search(filter_set, queryset)
        # Apply default pagination
        paginated_queryset, total_count = filter_by_pagination(queryset, getattr(filter_set, 'page_number', 1), filter_set.limit)
        filter_set.total_count = total_count
        return paginated_queryset

#========================Filter Response==================================

# def filter_response(count, message, data,page, limit,total_count,status_code):
#     """
#     Builds a standardized API response.
#     """
#     response = {
#         'count': count,
#         'message': message,
#         'data': data,
#         'page': page,
#         'limit': limit,
#         'totalCount': total_count
#     }
#     return Response(response, status=status_code)

def filter_response(count, message, data, page, limit, total_count, status_code):
    response = {
        'count': count,
        'message': message,
        'data': data,
        'page': page,
        'limit': limit,
        'totalCount': total_count   # camelCase only in JSON
    }
    return Response(response, status=status_code)



# def list_filtered_objects(viewset, request, model_name, *args, **kwargs):
#     """
#     Handles filtered listing of objects with pagination for ModelViewSet.
#     """
#     queryset = viewset.filter_queryset(viewset.get_queryset())

#     # Pagination handling
#     paginator = viewset.paginator
#     if paginator:
#         paginated_queryset = paginator.paginate_queryset(queryset, request, view=viewset)
#         serializer = viewset.get_serializer(paginated_queryset, many=True)
#         return paginator.get_paginated_response(serializer.data)

#     # Fallback if no pagination is configured
#     serializer = viewset.get_serializer(queryset, many=True)
#     message = "NO RECORDS INSERTED" if not serializer.data else None
#     status_code = status.HTTP_201_CREATED if not serializer.data else status.HTTP_200_OK
#     # Use filtered queryset count instead of counting all records in the model
#     total_count = queryset.count()
#     return filter_response(count=len(serializer.data),message=message,data=serializer.data,page=1,limit=len(serializer.data),total_count=total_count,status_code=status_code)

# def list_filtered_objects(viewset, request, model_name, *args, **kwargs):
#     """
#     Handles filtered listing of objects with pagination for ModelViewSet.
#     """
#     # queryset = viewset.filter_queryset(viewset.get_queryset())
    
#     # # ✅ Apply ordering only if field exists in model
#     # field_names = [f.name for f in model_name._meta.get_fields()]
#     # if "is_deleted" in field_names:
#     #     queryset = queryset.order_by("is_deleted", "-created_at")
#     queryset = viewset.get_queryset()

#     # ✅ Apply custom ordering first (before pagination / slicing)
#     field_names = [f.name for f in model_name._meta.get_fields()]
#     if "is_deleted" in field_names:
#         queryset = queryset.order_by("is_deleted", "-created_at")

#     # ✅ Now apply filters (safe after ordering)
#     queryset = viewset.filter_queryset(queryset)


#     # Pagination handling
#     paginator = viewset.paginator
#     if paginator:
#         paginated_queryset = paginator.paginate_queryset(queryset, request, view=viewset)
#         serializer = viewset.get_serializer(paginated_queryset, many=True)
#         return paginator.get_paginated_response(serializer.data)

#     # Fallback if no pagination is configured
#     serializer = viewset.get_serializer(queryset, many=True)
#     message = "NO RECORDS INSERTED" if not serializer.data else None
#     status_code = status.HTTP_201_CREATED if not serializer.data else status.HTTP_200_OK
    
#     # ✅ Total count from full model, not queryset
#     total_count = model_name.objects.count()

#     return filter_response(
#         count=len(serializer.data),
#         message=message,
#         data=serializer.data,
#         page=1,
#         limit=len(serializer.data),
#         total_count=total_count,
#         status_code=status_code
#     )

def list_filtered_objects(viewset, request, model_name, *args, **kwargs):
    """
    Handles filtered listing of objects with pagination for ModelViewSet.
    """
    # ✅ force ordering by is_deleted first, then created_at desc
    # Join whatever the serializer will read, exactly as list_all_objects does — this is
    # the other shared list path, and without it these screens pay a query per row.
    from config.utils_methods import optimize_list_queryset
    _serializer_class = viewset.get_serializer_class() if hasattr(viewset, 'get_serializer_class') else None
    queryset = viewset.filter_queryset(
        optimize_list_queryset(viewset.get_queryset(), _serializer_class)
    )

    # Pagination handling
    paginator = viewset.paginator
    if paginator:
        paginated_queryset = paginator.paginate_queryset(queryset, request, view=viewset)
        serializer = viewset.get_serializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    # Fallback if no pagination is configured
    serializer = viewset.get_serializer(queryset, many=True)
    message = "NO RECORDS INSERTED" if not serializer.data else None
    status_code = status.HTTP_201_CREATED if not serializer.data else status.HTTP_200_OK
    
    # ✅ Total count from full model, not queryset
    total_count = model_name.objects.count()

    return filter_response(
        count=len(serializer.data),
        message=message,
        data=serializer.data,
        page=1,
        limit=len(serializer.data),
        total_count=total_count,
        status_code=status_code
    )


#========================Filter Response==================================