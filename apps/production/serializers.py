from rest_framework import serializers
from .models import *
from apps.products.serializers import ColorSerializer, ModColorSerializer, ModproductsSerializer, ModSizeSerializer
from apps.hrms.serializers import ModEmployeesSerializer
from apps.sales.serializers import ModFlowstatusSerializer


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
        fields = ['work_order_id','quantity','product','status','start_date','end_date']

class BOMSerializer(serializers.ModelSerializer):
    product = ModproductsSerializer(source='product_id', read_only=True)
    class Meta:
        model = BOM
        fields = '__all__'

class BillOfMaterialsSerializer(serializers.ModelSerializer):
    product = ModproductsSerializer(source='product_id', read_only=True)
    size = ModSizeSerializer(source='size_id',read_only=True)
    color = ModColorSerializer(source='color_id',read_only=True)
    class Meta:
        model = BillOfMaterials
        fields = '__all__'

class ProductionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionStatus
        fields = '__all__'

class WorkOrderSerializer(serializers.ModelSerializer):
    product = ModproductsSerializer(source='product_id', read_only=True)
    size = ModSizeSerializer(source='size_id',read_only=True)
    color = ColorSerializer(source='color_id',read_only=True)    
    status = ModProductionStatusSerializer(source='status_id', read_only=True)
    class Meta:
        model = WorkOrder
        fields = '__all__'
        read_only_fields = ['pending_qty']

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

class WorkOrderOptionsSerializer(serializers.ModelSerializer):
    product = ModproductsSerializer(source='product_id', read_only=True)
    quantity = serializers.IntegerField(read_only=True)
    sale_order_id = serializers.SerializerMethodField()
    flow_status = serializers.SerializerMethodField()
    status = ModProductionStatusSerializer(source='status_id', read_only=True)
    # work_order = ModWorkOrderSerializer(source='work_order_id', read_only=True)

    class Meta:
        model = WorkOrder
        fields = ['work_order_id', 'product', 'quantity', 'sale_order_id', 'flow_status', 'status' ,'start_date', 'end_date']

    def get_sale_order_id(self, obj):
        # Assuming there is a related SaleOrder and foreign key on WorkOrder model
        sale_order = SaleOrder.objects.filter(workorder=obj).first()
        return sale_order.sale_order_id if sale_order else None

    def get_flow_status(self, obj):
        # Access flow_status directly from sale_order_id to avoid additional query
        if obj.sale_order_id and obj.sale_order_id.flow_status_id:
            return ModFlowstatusSerializer(obj.sale_order_id.flow_status_id).data
        return None

    @staticmethod
    def get_work_order_summary(work_orders):
        serializer = WorkOrderOptionsSerializer(work_orders, many=True)
        return {
            "count": len(serializer.data),
            "msg": "SUCCESS",
            "data": serializer.data
        }