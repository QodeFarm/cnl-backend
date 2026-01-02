from django.shortcuts import render
from rest_framework import viewsets
from apps.assets.filters import AssetCategoriesFilter, AssetMaintenanceFilter, AssetStatusesFilter, AssetsFilter, LocationsFilter
from config.utils_filter_methods import list_filtered_objects
from config.utils_methods import list_all_objects,create_instance,update_instance, soft_delete
from apps.assets.serializers import AssetStatusesSerializers, AssetCategoriesSerializers, LocationsSerializers, AssetsSerializer, AssetMaintenanceSerializer
from apps.assets.models import AssetStatuses, AssetCategories, Locations, Assets, AssetMaintenance
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import OrderingFilter

# Create your views here.
class AssetStatusesViewSet(viewsets.ModelViewSet):
    queryset = AssetStatuses.objects.all().order_by('-created_at')	
    serializer_class = AssetStatusesSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = AssetStatusesFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Asset Statuses"
    log_pk_field = "asset_status_id"
    log_display_field = "status_name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, AssetStatuses,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
		
class AssetCategoriesViewSet(viewsets.ModelViewSet):
    queryset = AssetCategories.objects.all().order_by('-created_at')	
    serializer_class = AssetCategoriesSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = AssetCategoriesFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Asset Categories"
    log_pk_field = "asset_category_id"
    log_display_field = "category_name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, AssetCategories,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
		
class LocationsViewSet(viewsets.ModelViewSet):
    queryset = Locations.objects.all().order_by('-created_at')	
    serializer_class = LocationsSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = LocationsFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Locations"
    log_pk_field = "location_id"
    log_display_field = "location_name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Locations,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

class AssetsViewSet(viewsets.ModelViewSet):
    queryset = Assets.objects.all().order_by('-created_at')	
    serializer_class = AssetsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = AssetsFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Assets"
    log_pk_field = "asset_id"
    log_display_field = "name"


    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Assets, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
		
class AssetMaintenanceViewSet(viewsets.ModelViewSet):
    queryset = AssetMaintenance.objects.all().order_by('-created_at')	
    serializer_class = AssetMaintenanceSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = AssetMaintenanceFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Asset Maintenance"
    log_pk_field = "asset_maintenance_id"
    log_display_field = "asset_maintenance_id"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, AssetMaintenance,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)