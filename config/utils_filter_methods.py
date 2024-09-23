import json
import logging
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

def filter_by_period_name(self, queryset, name, value):
        today = timezone.now().date()
        start_date = None
        end_date = today

        # Check if custom from_date and to_date are provided in the URL
        from_date = self.data.get('created_at_after')
        to_date = self.data.get('created_at_before')

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
                start_date = today - datetime.timedelta(days=180)
                # six_months_ago = today - relativedelta(months=6)
                # start_date = six_months_ago.replace(day=1)
                # end_date = today
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

  
        # Convert start_date and end_date to datetime objects with min and max times
        if start_date:
            start_datetime = datetime.datetime.combine(start_date, datetime.time.min)
        if end_date:
            end_datetime = datetime.datetime.combine(end_date, datetime.time.max)

        # Apply filters
        if start_datetime and end_datetime:
            queryset = queryset.filter(created_at__gte=start_datetime, created_at__lte=end_datetime)

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
                queryset = queryset.order_by(field_name)
                logger.debug(f"Ordered queryset: {queryset.query}")
            else:
                raise ValueError(f"Field '{field}' is not a valid filter field.")

        except ValueError as e:
            logger.error(f"Sorting error: {e}")
            raise

    else:
        default_field = list(self.filters.keys())[0]
        field_name = f'-{self.filters[default_field].field_name}'

    logger.debug(f"Sorting by field: {field_name}")
    return queryset.order_by(field_name)

def filter_by_pagination(queryset, page, limit):
    logger.debug(f"Pagination - page: {page}, limit: {limit}")

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

def filter_by_sort(filter_set, queryset, value):
    return apply_sorting(filter_set, queryset)

def filter_by_page(filter_set, queryset, value):
    filter_set.page_number = int(value)
    return queryset

def filter_by_limit(filter_set, queryset, value):
    filter_set.limit = int(value)
    queryset = apply_sorting(filter_set, queryset)
    paginated_queryset, total_count = filter_by_pagination(queryset, filter_set.page_number, filter_set.limit)
    filter_set.total_count = total_count
    return paginated_queryset

#========================Filter Response==================================

def filter_response(count, message, data,page, limit,total_count,status_code):
    """
    Builds a standardized API response.
    """
    response = {
        'count': count,
        'message': message,
        'data': data,
        'page': page,
        'limit': limit,
        'totalCount': total_count
    }
    return Response(response, status=status_code)

def list_filtered_objects(self, request, model_name,*args, **kwargs):
    queryset = self.filter_queryset(self.get_queryset())
    # Pagination handling
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    total_count = model_name.objects.count()
    start = (page - 1) * limit
    end = start + limit
    paginated_queryset = queryset[start:end]
    serializer = self.get_serializer(paginated_queryset, many=True)
    message = "NO RECORDS INSERTED" if not serializer.data else None
    status_code = status.HTTP_201_CREATED if not serializer.data else status.HTTP_200_OK
    return filter_response(count=len(paginated_queryset),message=message,data=serializer.data,page=page,limit=limit,total_count=total_count,status_code=status_code)

# def create_filtered_instance(self, request, *args, **kwargs):
#     serializer = self.get_serializer(data=request.data)
    
#     if serializer.is_valid():
#         serializer.save()
#         data = serializer.data
#         return filter_response(count=1,message="Record created successfully",data=data,page=None,limit=None,total_count=None,status_code=status.HTTP_201_CREATED)
#     else:
#         errors_str = json.dumps(serializer.errors, indent=2)
#         logger.error("Serializer validation error: %s", errors_str)
#         return filter_response(count=0,message="Form validation failed",data=[],page=None,limit=None,total_count=None,status_code=status.HTTP_400_BAD_REQUEST)

# def update_filtered_instance(self, request, *args, **kwargs):
#     partial = kwargs.pop('partial', False)
#     instance = self.get_object()
#     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    
#     if serializer.is_valid():
#         self.perform_update(serializer)
#         data = serializer.data
#         return filter_response(count=1,message="Record updated successfully",data=data,page=None,limit=None,total_count=None,status_code=status.HTTP_200_OK)
#     else:
#         errors_str = json.dumps(serializer.errors, indent=2)
#         logger.error("Serializer validation error: %s", errors_str)
#         return filter_response(count=0,message="Update failed",data=[],page=None,limit=None,total_count=None,status_code=status.HTTP_400_BAD_REQUEST)

#========================Filter Response==================================