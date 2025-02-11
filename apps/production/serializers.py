from rest_framework import serializers
from .models import *
from apps.products.serializers import ColorSerializer, ModColorSerializer, ModStockJournalProductSerializer, ModproductsSerializer, ModSizeSerializer
from apps.hrms.serializers import ModEmployeesSerializer
from apps.sales.serializers import ModFlowstatusSerializer, UdfSaleOrderSerializer


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

class ModBillOfMaterialsSerializer(serializers.ModelSerializer):
    product = ModStockJournalProductSerializer(source='product_id', read_only=True)
    size = ModSizeSerializer(source='size_id',read_only=True)
    color = ModColorSerializer(source='color_id',read_only=True)
    class Meta:
        model = BillOfMaterials
        fields = ['material_id','product','size','color','quantity']

class ProductionStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionStatus
        fields = '__all__'

class WorkOrderSerializer(serializers.ModelSerializer):
    product = ModproductsSerializer(source='product_id', read_only=True)
    size = ModSizeSerializer(source='size_id',read_only=True)
    color = ColorSerializer(source='color_id',read_only=True)    
    status = ModProductionStatusSerializer(source='status_id', read_only=True)
    sale_order = UdfSaleOrderSerializer(source='sale_order_id', read_only=True)
    pending_qty = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrder
        fields = '__all__'
    
    def get_pending_qty(self, obj):
        return obj.quantity - obj.completed_qty
    
    def get_bom_data(pk, product_id):
        return {
            "work_order_id" : pk,
            "finished_product" : product_id.name,
            "bom": BOM.objects.filter(product_id=product_id.product_id).values(),
            "bom_components" : BillOfMaterials.objects.filter(reference_id=pk).values()
        }

class StockJournalSerializer(serializers.ModelSerializer):
    product = ModStockJournalProductSerializer(source='product_id', read_only=True)
    size = ModSizeSerializer(source='size_id',read_only=True)
    color = ColorSerializer(source='color_id',read_only=True)
    status = ModProductionStatusSerializer(source='status_id', read_only=True)
    material = serializers.SerializerMethodField()
    bom_name = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrder
        fields = ['work_order_id', 'quantity','product', 'size', 'color', 'status', 'material', 'bom_name']
    
    def get_material(self, obj):
        # Replace pk with the actual primary key of the instance, typically obj.pk
        materials = BillOfMaterials.objects.filter(reference_id=obj.pk)
        return ModBillOfMaterialsSerializer(materials, many=True).data
    
    def get_bom_name(self, obj):
        materials = BOM.objects.filter(product_id=obj.product_id_id).values_list('bom_name', flat=True) # Filter BOM objects for the given product_id
        # If there's at least one result, return the first bom_name as a string; otherwise, return None or an empty string
        return materials[0] if materials else None

    def get_bom_data(pk, product_id):
        return {
            "work_order_id" : pk,
            "finished_product" : product_id.name,
            "bom": BOM.objects.filter(product_id=product_id.product_id).values(),
            "bom_components" : BillOfMaterials.objects.filter(reference_id=pk).values()
        }

class CompletedQuantitySerializer(serializers.ModelSerializer):
    class Meta:
        model = CompletedQuantity
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
        return serializer.data
    
class WorkOrderStockJournalSerializer(serializers.ModelSerializer):
    product = ModproductsSerializer(source='product_id', read_only=True)
    bom_components = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrder
        fields = ['product', 'quantity', 'bom_components']

    def get_bom_components(self, obj):
        # Access pre-fetched BOM data
        return BillOfMaterials.objects.filter(reference_id=obj.pk).values()
