from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import BillOfMaterials, ProductionStatus, WorkOrder, Inventory, Machine, Labor
from .serializers import BillOfMaterialsSerializer, ProductionStatusSerializer, WorkOrderSerializer, InventorySerializer, MachineSerializer, LaborSerializer
from config.utils_methods import list_all_objects, create_instance, update_instance

class BillOfMaterialsViewSet(viewsets.ModelViewSet):
    queryset = BillOfMaterials.objects.all()
    serializer_class = BillOfMaterialsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
        
class ProductionStatusViewSet(viewsets.ModelViewSet):
    queryset = ProductionStatus.objects.all()
    serializer_class = ProductionStatusSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
        
class MachineViewSet(viewsets.ModelViewSet):
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
        
class LaborViewSet(viewsets.ModelViewSet):
    queryset = Labor.objects.all()
    serializer_class = LaborSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)