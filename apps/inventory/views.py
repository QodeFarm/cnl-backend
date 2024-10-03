from django.shortcuts import render
from rest_framework import viewsets
<<<<<<< HEAD

from apps.inventory.filters import WareHouseLocationsFilter, WarehousesFilter
=======
from config.utils_filter_methods import list_filtered_objects
from apps.inventory.filters import WarehousesFilter
>>>>>>> 84a04a30e7a9c24423aeeac856039fa3bb46ac99
from .models import *
from .serializers import *
from config.utils_methods import *
from config.utils_variables import *
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import OrderingFilter


# Create your views here.
class WarehousesViewSet(viewsets.ModelViewSet):
    queryset = Warehouses.objects.all()
    serializer_class = WarehousesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = WarehousesFilter
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Warehouses,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class WarehouseLocationsViewSet(viewsets.ModelViewSet):
    queryset = WarehouseLocations.objects.all()
    serializer_class = WarehouseLocationsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = WareHouseLocationsFilter
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)