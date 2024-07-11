from django.shortcuts import render
from rest_framework import viewsets
from config.utils_methods import list_all_objects,create_instance,update_instance
from apps.asset.serializers import AssetStatusesSerializers, AssetCategoriesSerializers, LocationsSerializers, AssetsSerializer, AssetMaintenanceSerializer
from apps.asset.models import AssetStatuses, AssetCategories, Locations, Assets, AssetMaintenance


# Create your views here.
class AssetStatusesViewSet(viewsets.ModelViewSet):
    queryset = AssetStatuses.objects.all()
    serializer_class = AssetStatusesSerializers

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
		
class AssetCategoriesViewSet(viewsets.ModelViewSet):
    queryset = AssetCategories.objects.all()
    serializer_class = AssetCategoriesSerializers

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
		
class LocationsViewSet(viewsets.ModelViewSet):
    queryset = Locations.objects.all()
    serializer_class = LocationsSerializers

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class AssetsViewSet(viewsets.ModelViewSet):
    queryset = Assets.objects.all()
    serializer_class = AssetsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
		
class AssetMaintenanceViewSet(viewsets.ModelViewSet):
    queryset = AssetMaintenance.objects.all()
    serializer_class = AssetMaintenanceSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)