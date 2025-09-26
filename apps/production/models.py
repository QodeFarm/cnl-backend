import re
from django.db import models
from apps.masters.models import FlowStatus, OrderStatuses, ProductionFloor, UnitOptions
from config.utils_variables import bom, billofmaterials, productionstatuses, workorders, machines, rawmaterials, workorderstages, productionworkers, defaultmachinery, workordermachines, completedquantity
from apps.products.models import Color, Products, Size
from apps.hrms.models import Employees
from apps.sales.models import SaleOrder
# Create your models here.
from django.db import models
import uuid
from django.db import transaction

class RawMaterial(models.Model):
    raw_material_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = rawmaterials

    def __str__(self):
        return self.name

class BOM(models.Model):
    bom_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bom_name = models.CharField(max_length=100)
    product_id = models.ForeignKey(Products, on_delete=models.PROTECT, db_column='product_id', related_name='bom')
    notes = models.TextField(default=None, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = bom

    def __str__(self):
        return f"{self.bom_name}"

class BillOfMaterials(models.Model):
    material_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_id = models.CharField(max_length=36, null=False)
    product_id = models.ForeignKey(Products, on_delete=models.PROTECT, db_column='product_id')
    size_id = models.ForeignKey(Size, on_delete=models.PROTECT, null=True, default=None, db_column='size_id')
    color_id = models.ForeignKey(Color, on_delete=models.PROTECT, null=True, default=None, db_column='color_id')
    quantity = models.IntegerField(default=0)
    original_quantity = models.IntegerField(default=0)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(default=None, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = billofmaterials
        
    def save(self, *args, **kwargs):
        # If original_quantity is not set and this is a new BOM entry, set it
        if not self.original_quantity and self.quantity > 0:
            self.original_quantity = self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.material_id}"

class ProductionStatus(models.Model):
    status_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = productionstatuses

    def __str__(self):
        return f'{self.status_name}'

class WorkOrder(models.Model):
    work_order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_id = models.ForeignKey(Products, on_delete=models.PROTECT, db_column='product_id')
    size_id = models.ForeignKey(Size, on_delete=models.PROTECT, null=True, default=None, db_column='size_id')
    color_id = models.ForeignKey(Color, on_delete=models.PROTECT, null=True, default=None, db_column='color_id')    
    quantity =  models.IntegerField(default=0)
    completed_qty = models.IntegerField(null=True, default=0)
    temp_quantity = models.IntegerField(null=True, default=0)
    status_id = models.ForeignKey(ProductionStatus, on_delete=models.PROTECT, null=True, default=None, db_column='status_id')
    start_date = models.DateField(null=True, default=None)
    end_date = models.DateField(null=True, default=None)
    sale_order_id = models.ForeignKey(SaleOrder, on_delete=models.PROTECT, db_column='sale_order_id', null=True, default=None)
    sync_qty = models.BooleanField(null=False, default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if self.pk:  # Check if the object already exists
            try:
                previous_instance = type(self).objects.get(pk=self.pk)
                previous_sync_qty = previous_instance.sync_qty
                previous_completed_qty = previous_instance.completed_qty or 0
                previous_temp_qty = previous_instance.temp_quantity or 0
            except type(self).DoesNotExist:
                previous_sync_qty = True
                previous_completed_qty = 0
                previous_temp_qty = 0
            
            # Get the new completed_qty value from the form
            new_completed_qty = self.completed_qty or 0
            
            if self.sync_qty:
                if not previous_sync_qty:
                    # Changing from False to True: Add temp_quantity + new completed_qty
                    self.completed_qty = previous_completed_qty + previous_temp_qty + new_completed_qty
                    self.temp_quantity = 0
                else:
                    # Already True: Use the new completed_qty value directly
                    self.completed_qty = new_completed_qty
                    self.temp_quantity = 0
            else:
                # sync_qty is False: Store new value in temp_quantity, keep completed_qty unchanged
                self.temp_quantity = previous_temp_qty + new_completed_qty
                self.completed_qty = previous_completed_qty

        super().save(*args, **kwargs)

        # if self.pk:  # Check if the object already exists
        #     status_name = self.status_id.status_name.lower() if self.status_id else ""
        #     is_closed = "closed" in status_name

        #     try:
        #         previous_instance = type(self).objects.get(pk=self.pk)
        #         previous_completed_qty = previous_instance.completed_qty or 0
        #         previous_sync_qty = previous_instance.sync_qty
        #     except type(self).DoesNotExist:
        #         pass  # New object, no previous data exists

        #     if not is_closed:  # Status other than 'closed'
        #         if self.sync_qty:
        #             # If changing from sync_qty=False to sync_qty=True, include unsynced quantities
        #             if not previous_sync_qty and self.sync_qty:
        #                 # Get all unsynced quantities from CompletedQuantity
        #                 try:
        #                     completed_quantity = CompletedQuantity.objects.get(work_order_id=self.work_order_id)
        #                     unsynced_qty = completed_quantity.quantity
        #                     # Add unsynced quantity to current completed_qty
        #                     self.completed_qty = (self.completed_qty or 0) + unsynced_qty
        #                     # Clear the unsynced quantity record
        #                     completed_quantity.delete()
        #                 except CompletedQuantity.DoesNotExist:
        #                     # No unsynced quantities, proceed normally
        #                     self.completed_qty = previous_completed_qty + (self.completed_qty or 0)
        #             else:
        #                 # Normal sync operation
        #                 self.completed_qty = previous_completed_qty + (self.completed_qty or 0)
        #         else:
        #             # sync_qty is False, store in CompletedQuantity
        #             with transaction.atomic():
        #                 completed_quantity, created = CompletedQuantity.objects.get_or_create(
        #                     work_order_id=self.work_order_id,
        #                     defaults={'quantity': self.completed_qty or 0}
        #                 )
        #                 if not created:
        #                     completed_quantity.quantity += self.completed_qty or 0
        #                     completed_quantity.save()
        #                 # Keep completed_qty as previous value since we're not syncing
        #                 self.completed_qty = previous_completed_qty
        #     else:  # If status is 'closed'
        #         # When closing, include any unsynced quantities
        #         try:
        #             completed_quantity = CompletedQuantity.objects.get(work_order_id=self.work_order_id)
        #             unsynced_qty = completed_quantity.quantity
        #             self.completed_qty = previous_completed_qty + (self.completed_qty or 0) + unsynced_qty
        #             completed_quantity.delete()  # Remove the unsynced record
        #         except CompletedQuantity.DoesNotExist:
        #             self.completed_qty = previous_completed_qty + (self.completed_qty or 0)
        
        # # Reset sync_qty to True only if it's currently True
        # # Don't reset if user explicitly set it to False
        # if self.sync_qty:
        #     self.sync_qty = True

        # super().save(*args, **kwargs)

    class Meta:
        db_table = workorders

    def __str__(self):
        return f'{self.product_id.name}_{self.status_id.status_name}'

class CompletedQuantity(models.Model):
    quantity_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quantity = models.IntegerField(null=True)
    sync_time = models.DateTimeField(auto_now_add=True)
    work_order = models.ForeignKey('WorkOrder', on_delete=models.PROTECT, related_name='completed_quantities')

    class Meta:
        db_table = completedquantity
    
    def __str__(self):
        return f"quantity={self.quantity})"    

class Machine(models.Model):
    machine_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    machine_name = models.CharField(max_length=100)
    description = models.TextField(null=True, default=None)
    status = models.CharField(max_length=20, choices=[
        ('Operational', 'Operational'),
        ('Out of Service', 'Out of Service'),
        ('Under Maintenance', 'Under Maintenance'),
    ], default='Operational')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = machines

    def __str__(self):
        return f'{self.machine_name}'

class DefaultMachinery(models.Model):
    default_machinery_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_id = models.ForeignKey(Products, on_delete=models.PROTECT, db_column='product_id')
    machine_id = models.ForeignKey(Machine, on_delete=models.PROTECT, null=True, db_column='machine_id')

    class Meta:
        db_table = defaultmachinery

    def __str__(self):
        return f"Default machinery for {self.product.name}: {self.machine.name}"

class WorkOrderMachine(models.Model):
    work_order_machines_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_order_id = models.ForeignKey(WorkOrder, on_delete=models.PROTECT, db_column='work_order_id')
    machine_id = models.ForeignKey(Machine, on_delete=models.PROTECT, null=True,db_column='machine_id')

    class Meta:
        db_table = workordermachines

    def __str__(self):
        return f"Machine {self.machine.name} for Work Order {self.work_order.id}"
    

class ProductionWorker(models.Model):
    worker_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.ForeignKey(Employees, on_delete=models.PROTECT,null=True, db_column='employee_id')
    work_order_id = models.ForeignKey(WorkOrder, on_delete=models.PROTECT, db_column='work_order_id')
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = productionworkers

    def __str__(self):
        return f'{self.employee_id}'

class WorkOrderStage(models.Model):
    work_stage_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_order_id = models.ForeignKey(WorkOrder, on_delete=models.PROTECT, db_column='work_order_id')
    stage_name = models.CharField(max_length=255, null=True)
    stage_description = models.TextField(default=None, null=True)
    stage_start_date = models.DateField(default=None, null=True, blank=True)
    stage_end_date = models.DateField(default=None, null=True, blank=True) 
    notes = models.TextField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = workorderstages

    def __str__(self):
        return f"{self.stage_name}"

class MaterialIssue(models.Model):
    material_issue_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    production_floor_id = models.ForeignKey(ProductionFloor, on_delete=models.PROTECT, db_column='production_floor_id')
    issue_no = models.CharField(max_length=20, unique=True, default='')
    issue_date = models.DateField()
    reference_no = models.CharField(max_length=50, null=True, default=None)
    reference_date = models.DateField(null=True, default=None)
    remarks = models.TextField(null=True, default=None)
    flow_status_id = models.ForeignKey(FlowStatus, on_delete=models.PROTECT, db_column='flow_status_id', null=True, default=None)
    order_status_id = models.ForeignKey(OrderStatuses, on_delete=models.PROTECT, db_column='order_status_id', null=True, default=None)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'material_issues'

    def __str__(self):
        return str(self.material_issue_id)

class MaterialIssueItem(models.Model):
    material_issue_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    material_issue_id = models.ForeignKey(MaterialIssue, on_delete=models.PROTECT, db_column='material_issue_id')
    product_id = models.ForeignKey(Products, on_delete=models.PROTECT, db_column='product_id', null=True, default=None)
    description = models.CharField(max_length=255, null=True, default=None)
    attribute = models.CharField(max_length=255, null=True, default=None)  # For Attribute column
    widget = models.CharField(max_length=255, null=True, default=None)     # For Widget column
    item_barcode = models.CharField(max_length=50, null=True, default=None)
    unit_options_id = models.ForeignKey(UnitOptions, on_delete=models.PROTECT, db_column='unit_options_id', null=True, default=None)
    no_of_boxes = models.IntegerField(null=True, default=None)
    quantity = models.DecimalField(max_digits=18, decimal_places=3, null=True, default=None)
    rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    remark = models.CharField(max_length=255, null=True, default=None)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    mrp = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    net_rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    print_description = models.CharField(max_length=255, null=True, default=None)
    item_balance = models.IntegerField(null=True, default=0)
    hsn_code = models.CharField(max_length=15, null=True, default=None)
    brand = models.CharField(max_length=100, null=True, default=None)
    gp_vno = models.CharField(max_length=50, null=True, default=None)
    gp_ref_no = models.CharField(max_length=50, null=True, default=None)
    gp_ref_date = models.DateField(null=True, default=None)
    gp_vdate = models.DateField(null=True, default=None)
    pfr_vno = models.CharField(max_length=50, null=True, default=None)
    pfr_ref_no = models.CharField(max_length=50, null=True, default=None)
    pfr_ref_date = models.DateField(null=True, default=None)
    pfr_vdate = models.DateField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'material_issue_items'

    def __str__(self):
        return str(self.material_issue_item_id)

class MaterialIssueAttachment(models.Model):
    attachment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    material_issue_id = models.ForeignKey(MaterialIssue, on_delete=models.PROTECT, db_column='material_issue_id')
    attachment_name = models.CharField(max_length=255)
    attachment_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'material_issue_attachments'

    def __str__(self):
        return self.attachment_name


class MaterialReceived(models.Model):
    material_received_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    production_floor_id = models.ForeignKey(ProductionFloor, on_delete=models.PROTECT, db_column='production_floor_id')
    receipt_no = models.CharField(max_length=20, unique=True)
    receipt_date = models.DateField()
    reference_no = models.CharField(max_length=50, null=True, default=None)
    reference_date = models.DateField(null=True, default=None)
    flow_status_id = models.ForeignKey(FlowStatus, on_delete=models.PROTECT, db_column='flow_status_id', null=True, default=None)
    order_status_id = models.ForeignKey(OrderStatuses, on_delete=models.PROTECT, db_column='order_status_id', null=True, default=None)
    remarks = models.TextField(null=True, default=None)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'material_received'

    def __str__(self):
        return self.receipt_no

class MaterialReceivedItem(models.Model):
    material_received_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    material_received_id = models.ForeignKey(MaterialReceived, on_delete=models.PROTECT, db_column='material_received_id')
    product_id = models.ForeignKey(Products, on_delete=models.PROTECT, db_column='product_id', null=True, default=None)
    description = models.CharField(max_length=255, null=True, default=None)
    attribute = models.CharField(max_length=255, null=True, default=None)
    widget = models.CharField(max_length=255, null=True, default=None)
    item_barcode = models.CharField(max_length=50, null=True, default=None)
    unit_options_id = models.ForeignKey(UnitOptions, on_delete=models.PROTECT, db_column='unit_options_id', null=True, default=None)
    no_of_boxes = models.IntegerField(max_length=255,null=True, default=None)
    quantity = models.DecimalField(max_digits=18, decimal_places=3, null=True, default=None)
    rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    remark = models.CharField(max_length=255, null=True, default=None)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    mrp = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    net_rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    print_description = models.CharField(max_length=255, null=True, default=None)
    mipf_vno = models.CharField(max_length=50, null=True, default=None)
    mipf_ref_no = models.CharField(max_length=50, null=True, default=None)
    mipf_ref_date = models.DateField(null=True, default=None)
    mipf_vdate = models.DateField(null=True, default=None)
    item_balance = models.IntegerField(null=True, default=0)
    hsn_code = models.CharField(max_length=15, null=True, default=None)
    brand = models.CharField(max_length=100, null=True, default=None)
    gp_vno = models.CharField(max_length=50, null=True, default=None)
    gp_ref_no = models.CharField(max_length=50, null=True, default=None)
    gp_ref_date = models.DateField(null=True, default=None)
    gp_vdate = models.DateField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'material_received_items'

    def __str__(self):
        return str(self.material_received_item_id)

class MaterialReceivedAttachment(models.Model):
    material_received_attachment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    material_received_id = models.ForeignKey(MaterialReceived, on_delete=models.PROTECT, db_column='material_received_id')
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'material_received_attachments'

    def __str__(self):
        return self.file_name   

class StockJournal(models.Model):
    journal_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_id = models.ForeignKey(Products, on_delete=models.PROTECT, db_column='product_id', null=True, default=None)
    transaction_type = models.CharField(max_length=20)
    quantity = models.DecimalField(max_digits=18, decimal_places=3)
    reference_id = models.CharField(max_length=36, null=True, blank=True)
    remarks = models.CharField(max_length=255, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stock_journal'       

class StockSummary(models.Model):
    summary_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_id = models.ForeignKey(Products, on_delete=models.PROTECT, db_column='product_id')
    opening_quantity = models.IntegerField(default=0)
    closing_quantity = models.IntegerField(default=0)
    received_quantity = models.IntegerField(default=0)
    issued_quantity = models.IntegerField(default=0)
    unit_options_id = models.ForeignKey(UnitOptions, on_delete=models.PROTECT, db_column='unit_options_id', null=True)
    mrp = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=0)
    sales_rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=0)
    purchase_rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=0)
    period_start = models.DateField()
    period_end = models.DateField()
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stock_summary'
        

   