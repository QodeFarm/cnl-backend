from rest_framework import serializers
from .models import *
from apps.products.serializers import ModproductsSerializer
from apps.hrms.serializers import ModEmployeesSerializer

class ModProductionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionStatus
        fields = ['status_id','status_name']

class ModRawMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawMaterial
        fields = ['raw_material_id','name']

class ModMachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ['machine_id','machine_name']

class ModWorkOrderSerializer(serializers.ModelSerializer):
    product = ModproductsSerializer(source='product_id', read_only=True)
    status = ModProductionStatusSerializer(source='status_id', read_only=True)
    class Meta:
        model = WorkOrder
        fields = ['work_order_id','quantity','product','status']

class BillOfMaterialsSerializer(serializers.ModelSerializer):
    product = ModproductsSerializer(source='product_id', read_only=True)
    raw_material = ModRawMaterialSerializer(source='raw_material_id', read_only=True)
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

class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = '__all__'

class DefaultMachinerySerializer(serializers.ModelSerializer):
    product = ModproductsSerializer(source='product_id', read_only=True)
    machine = ModMachineSerializer(source='machine_id', read_only=True)
    class Meta:
        model = DefaultMachinery
        fields = '__all__'

class WorkOrderMachineSerializer(serializers.ModelSerializer):
    work_order = ModWorkOrderSerializer(source='work_order_id', read_only=True)
    machine = ModMachineSerializer(source='machine_id', read_only=True)
    class Meta:
        model = WorkOrderMachine
        fields = '__all__'

class WorkOrderStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrderStage
        fields = '__all__'

class RawMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawMaterial
        fields = '__all__'

class ProductionWorkerSerializer(serializers.ModelSerializer):
    work_order = ModWorkOrderSerializer(source='work_order_id', read_only=True)
    employee = ModEmployeesSerializer(source='employee_id', read_only=True)    
    class Meta:
        model = ProductionWorker
        fields = '__all__' 