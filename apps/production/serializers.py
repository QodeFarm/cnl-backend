from rest_framework import serializers
from .models import BillOfMaterials, ProductionStatus, WorkOrder, Inventory, Machine, Labor
from apps.products.serializers import ModproductsSerializer
from apps.hrms.serializers import ModEmployeesSerializer

class ModProductionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionStatus
        fields = ['status_id','status_name']

class ModWorkOrderSerializer(serializers.ModelSerializer):
    product = ModproductsSerializer(source='product_id', read_only=True)
    status = ModProductionStatusSerializer(source='status_id', read_only=True)
    class Meta:
        model = WorkOrder
        fields = ['work_order_id','quantity','product','status']

class BillOfMaterialsSerializer(serializers.ModelSerializer):
    product = ModproductsSerializer(source='product_id', read_only=True)
    class Meta:
        model = BillOfMaterials
        fields = '__all__'

class ProductionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionStatus
        fields = '__all__'

class WorkOrderSerializer(serializers.ModelSerializer):
    product = ModproductsSerializer(source='product_id', read_only=True)
    status = ModProductionStatusSerializer(source='status_id', read_only=True)
    class Meta:
        model = WorkOrder
        fields = '__all__'

class InventorySerializer(serializers.ModelSerializer):
    product = ModproductsSerializer(source='product_id', read_only=True)
    class Meta:
        model = Inventory
        fields = '__all__'

class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = '__all__'

class LaborSerializer(serializers.ModelSerializer):
    work_order = ModWorkOrderSerializer(source='work_order_id', read_only=True)
    employee = ModEmployeesSerializer(source='employee_id', read_only=True)
    class Meta:
        model = Labor
        fields = '__all__'