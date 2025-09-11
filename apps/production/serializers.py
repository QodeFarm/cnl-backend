from rest_framework import serializers

from apps.masters.serializers import ModOrderStatusesSerializer, ModProductionFloorSerializer, ModUnitOptionsSerializer
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
        fields = ['material_id','product','size','color','quantity', 'original_quantity']

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
    

class ProductionSummaryReportSerializer(serializers.ModelSerializer):
    product = ModproductsSerializer(source='product_id', read_only=True)
    status = ModProductionStatusSerializer(source='status_id', read_only=True)
    completion_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = WorkOrder
        fields = ['work_order_id','product','quantity','completed_qty','completion_percentage','status','start_date','end_date']
    
class WorkOrderStatusReportSerializer(serializers.ModelSerializer):
    product = ModproductsSerializer(source='product_id', read_only=True)
    status = ModProductionStatusSerializer(source='status_id', read_only=True)
    completion_percentage = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrder
        fields = ['work_order_id','product','quantity','completed_qty','completion_percentage','status','start_date','end_date']

    def get_completion_percentage(self, obj):
        if obj.quantity and obj.quantity > 0:
            return round((obj.completed_qty / obj.quantity) * 100, 2)
        return 0.0
    
class RawMaterialConsumptionReportSerializer(serializers.Serializer):
    product_name = serializers.CharField(source="product_id__name")
    total_consumed_quantity = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_cost = serializers.DecimalField(max_digits=18, decimal_places=2)
    avg_unit_cost = serializers.SerializerMethodField()
    last_consumption_date = serializers.DateTimeField(required=False)
    
    def get_avg_unit_cost(self, obj):
        if obj['total_consumed_quantity'] and obj['total_consumed_quantity'] > 0:
            return round(obj['total_cost'] / obj['total_consumed_quantity'], 2)
        return 0.0

class FinishedGoodsReportSerializer(serializers.ModelSerializer):
    product = ModproductsSerializer(source='product_id', read_only=True)
    completion_percentage = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrder
        fields = ['work_order_id','product','quantity','completed_qty','completion_percentage','start_date','end_date']

    def get_completion_percentage(self, obj):
        if obj.quantity and obj.quantity > 0:
            return round((obj.completed_qty / obj.quantity) * 100, 2)
        return 0.0      

class ProductionCostReportSerializer(serializers.ModelSerializer):
    # Map product_id.name to 'product'
    product = serializers.CharField()
    # Aggregated fields from the query:
    total_quantity = serializers.IntegerField()
    total_cost = serializers.DecimalField(max_digits=18, decimal_places=2)
    avg_unit_cost = serializers.DecimalField(max_digits=18, decimal_places=2)
    
    class Meta:
        model = BillOfMaterials
        fields = ['product', 'total_quantity', 'total_cost', 'avg_unit_cost']
        
class MachineUtilizationReportSerializer(serializers.Serializer):
    machine_name = serializers.CharField()
    total_usage_hours = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_work_orders = serializers.IntegerField()
    avg_usage_per_work_order = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_work_time = serializers.IntegerField()
    downtime_hours = serializers.IntegerField()
   
class WIPReportSerializer(serializers.Serializer):
    """Serializer for Work in Progress (WIP) Report"""
    work_order_id = serializers.UUIDField()
    product_name = serializers.CharField(source="product_id__name")
    status_name = serializers.CharField(source="status_id__status_name")
    quantity = serializers.IntegerField()
    completed_qty = serializers.IntegerField()
    pending_qty = serializers.IntegerField()

class BOMReportSerializer(serializers.ModelSerializer):
    product = ModproductsSerializer(source='product_id', read_only=True)
    items = BillOfMaterialsSerializer(source='billofmaterials_set', many=True, read_only=True)
    
    class Meta:
        model = BOM
        fields = ['bom_id','bom_name','product','notes','created_at','items']


class MaterialIssueSerializer(serializers.ModelSerializer):
    production_floor = ModProductionFloorSerializer(source='production_floor_id', read_only=True)
    flow_status = ModFlowstatusSerializer(source='flow_status_id', read_only=True)
    order_status = ModOrderStatusesSerializer(source='order_status_id', read_only=True)

    # production_floor_id = serializers.UUIDField(required=True)
    class Meta:
        model = MaterialIssue
        fields = '__all__'

    def validate_issue_no(self, value):
            # Get the pk from instance or from initial data
            material_issue_id = None
            if self.instance and hasattr(self.instance, 'material_issue_id'):
                material_issue_id = self.instance.material_issue_id
            elif 'material_issue_id' in self.initial_data:
                material_issue_id = self.initial_data['material_issue_id']
            qs = MaterialIssue.objects.filter(issue_no=value)
            if material_issue_id:
                qs = qs.exclude(material_issue_id=material_issue_id)
            if qs.exists():
                raise serializers.ValidationError("material issue with this issue no already exists.")
            return value


class MaterialIssueItemSerializer(serializers.ModelSerializer):
    product = ModproductsSerializer(source='product_id', read_only=True)
    unit_options = ModUnitOptionsSerializer(source='unit_options_id', read_only=True)
    class Meta:
        model = MaterialIssueItem
        fields = '__all__'


class MaterialIssueAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialIssueAttachment
        fields = '__all__'



class MaterialReceivedSerializer(serializers.ModelSerializer):
    production_floor = ModProductionFloorSerializer(source='production_floor_id', read_only=True)
   
    class Meta:
        model = MaterialReceived
        fields = '__all__'

class MaterialReceivedItemSerializer(serializers.ModelSerializer):
    product = ModproductsSerializer(source='product_id', read_only=True)
    unit_options = ModUnitOptionsSerializer(source='unit_options_id', read_only=True)
    no_of_boxes = serializers.IntegerField(required=False, allow_null=True)


    class Meta:
        model = MaterialReceivedItem
        fields = '__all__'

class MaterialReceivedAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaterialReceivedAttachment
        fields = '__all__'        



class StockJournalsSerializer(serializers.ModelSerializer):
    product = ModStockJournalProductSerializer(source='product_id', read_only=True)
    quantity = serializers.SerializerMethodField()


    def get_quantity(self, obj):
        return int(obj.quantity) if obj.quantity is not None else 0

    class Meta:
        model = StockJournal
        fields = [
            'journal_id',
            'product',
            'transaction_type',
            'quantity',
            'reference_id',
            'remarks',
            'is_deleted',
            'created_at',
            'updated_at',
        ]
             

# Add after the existing StockRegisterSerializer class

class StockSummarySerializer(serializers.ModelSerializer):
    product = ModStockJournalProductSerializer(source='product_id', read_only=True)
    unit_options = ModUnitOptionsSerializer(source='unit_options_id', read_only=True)
    group_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    hsn_code = serializers.SerializerMethodField()
    
    class Meta:
        model = StockSummary
        fields = '__all__'
    
    def get_group_name(self, obj):
        if obj.product_id and obj.product_id.product_group_id:
            return obj.product_id.product_group_id.group_name
        return None
    
    def get_category_name(self, obj):
        if obj.product_id and obj.product_id.category_id:
            return obj.product_id.category_id.category_name
        return None
        
    def get_hsn_code(self, obj):
        if obj.product_id:
            return obj.product_id.hsn_code
        return None