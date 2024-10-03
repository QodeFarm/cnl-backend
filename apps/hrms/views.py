from rest_framework import viewsets
from apps.hrms.filters import EmployeesFilter
from .models import *
from .serializers import *
from config.utils_filter_methods import list_filtered_objects
from config.utils_methods import list_all_objects, create_instance, update_instance
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import OrderingFilter

class DesignationsView(viewsets.ModelViewSet):
    queryset = Designations.objects.all()
    serializer_class = DesignationsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class DepartmentsView(viewsets.ModelViewSet):
    queryset = Departments.objects.all()
    serializer_class = DepartmentsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class EmployeesView(viewsets.ModelViewSet):
    queryset = Employees.objects.all()
    serializer_class = EmployeesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = EmployeesFilter
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Employees,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
