from django.shortcuts import render
from rest_framework import viewsets
from apps.assets.filters import AssetMaintenanceFilter, AssetsFilter
from config.utils_filter_methods import list_filtered_objects
from config.utils_methods import list_all_objects,create_instance,update_instance
from apps.assets.serializers import AssetStatusesSerializers, AssetCategoriesSerializers, LocationsSerializers, AssetsSerializer, AssetMaintenanceSerializer
from apps.assets.models import AssetStatuses, AssetCategories, Locations, Assets, AssetMaintenance
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import OrderingFilter

# Create your views here.
class AssetStatusesViewSet(viewsets.ModelViewSet):
    queryset = AssetStatuses.objects.all().order_by('-created_at')	
    serializer_class = AssetStatusesSerializers

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
		
class AssetCategoriesViewSet(viewsets.ModelViewSet):
    queryset = AssetCategories.objects.all().order_by('-created_at')	
    serializer_class = AssetCategoriesSerializers

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
		
class LocationsViewSet(viewsets.ModelViewSet):
    queryset = Locations.objects.all().order_by('-created_at')	
    serializer_class = LocationsSerializers

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class AssetsViewSet(viewsets.ModelViewSet):
    queryset = Assets.objects.all().order_by('-created_at')	
    serializer_class = AssetsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = AssetsFilter
    ordering_fields = ['created_at']


    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Assets, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
		
class AssetMaintenanceViewSet(viewsets.ModelViewSet):
    queryset = AssetMaintenance.objects.all().order_by('-created_at')	
    serializer_class = AssetMaintenanceSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = AssetMaintenanceFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, AssetMaintenance,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)