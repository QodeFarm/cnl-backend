from django.db import models
from config.utils_variables import bom, billofmaterials, productionstatuses, workorders, machines, rawmaterials, workorderstages, productionworkers, defaultmachinery, workordermachines
from apps.products.models import Color, Products, Size
from apps.hrms.models import Employees
from apps.sales.models import SaleOrder
# Create your models here.
from django.db import models
import uuid

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
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, db_column='product_id')
    notes = models.TextField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = bom

    def __str__(self):
        return f"{self.bom_name}"

class BillOfMaterials(models.Model):
    material_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference_id = models.CharField(max_length=36, null=False)
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, db_column='product_id')
    size_id = models.ForeignKey(Size, on_delete=models.CASCADE, null=True, default=None, db_column='size_id')
    color_id = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, default=None, db_column='color_id')
    quantity = models.IntegerField(default=0)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = billofmaterials

    def __str__(self):
        return f"{self.material_id}"

class ProductionStatus(models.Model):
    status_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = productionstatuses

    # def __str__(self):
    #     return f'{self.status_name}'

class WorkOrder(models.Model):
    work_order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, db_column='product_id')
    size_id = models.ForeignKey(Size, on_delete=models.CASCADE, null=True, default=None, db_column='size_id')
    color_id = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, default=None, db_column='color_id')    
    quantity =  models.IntegerField(default=0)
    completed_qty = models.IntegerField(null=True, default=0)
    status_id = models.ForeignKey(ProductionStatus, on_delete=models.CASCADE, null=True, default=None, db_column='status_id')
    start_date = models.DateField(null=True, default=None)
    end_date = models.DateField(null=True, default=None)
    sale_order_id = models.ForeignKey(SaleOrder, on_delete=models.CASCADE, db_column='sale_order_id', null=True, default=None)
    sync_qty = models.BooleanField(null=False, default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        previous_completed_qty = 0

        if self.pk:  # Check if the object already exists
            try:
                # Fetch the previous instance from the database
                previous_instance = type(self).objects.get(pk=self.pk)
                previous_completed_qty = previous_instance.completed_qty
            except type(self).DoesNotExist:
                pass  # If the object is new, no previous completed quantity exists

        if self.sync_qty:
            # Update completed quantity only if sync is True.
            if self.completed_qty:
                self.completed_qty = previous_completed_qty + self.completed_qty
        else:
            if self.completed_qty and not CompletedQuantity.objects.filter(work_order_id=self.work_order_id).exists(): # Track unsync data and store it into 'completed_quantity'.
                CompletedQuantity.objects.create(quantity=self.completed_qty, work_order_id=self.pk)
            # Maintain the same completed quantity if sync is False
            # self.completed_qty = previous_completed_qty
            else:
                try:
                    instance = CompletedQuantity.objects.get(work_order_id=self.work_order_id)
                    previous_qty = instance.quantity
                    instance.quantity = previous_qty + self.completed_qty
                    instance.save()
                except CompletedQuantity.DoesNotExist: pass

            self.completed_qty = previous_completed_qty + self.completed_qty

        # Call the parent save method
        super().save(*args, **kwargs)

    class Meta:
        db_table = workorders

    def __str__(self):
        return f'{self.product_id.name}_{self.status_id.status_name}'

class CompletedQuantity(models.Model):
    quantity_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quantity = models.IntegerField(null=True)
    sync_time = models.DateTimeField(auto_now_add=True)
    work_order = models.ForeignKey('WorkOrder', on_delete=models.CASCADE, related_name='completed_quantities')

    class Meta:
        db_table = 'completed_quantity'
    
    def __str__(self):
        return f"quantity={self.quantity})"    

class Machine(models.Model):
    machine_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    machine_name = models.CharField(max_length=100)
    description = models.TextField(null=True, default=None)
    status = models.CharField(max_length=20, choices=[
        ('Operational', 'Operational'),
        ('Under Maintenance', 'Under Maintenance'),
        ('Out of Service', 'Out of Service'),
    ], default='Operational')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = machines

    def __str__(self):
        return f'{self.machine_name}'

class DefaultMachinery(models.Model):
    default_machinery_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, db_column='product_id')
    machine_id = models.ForeignKey(Machine, on_delete=models.CASCADE, db_column='machine_id')

    class Meta:
        db_table = defaultmachinery

    def __str__(self):
        return f"Default machinery for {self.product.name}: {self.machine.name}"

class WorkOrderMachine(models.Model):
    work_order_machines_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_order_id = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, db_column='work_order_id')
    machine_id = models.ForeignKey(Machine, on_delete=models.CASCADE, db_column='machine_id')

    class Meta:
        db_table = workordermachines

    def __str__(self):
        return f"Machine {self.machine.name} for Work Order {self.work_order.id}"
    

class ProductionWorker(models.Model):
    worker_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.ForeignKey(Employees, on_delete=models.CASCADE, db_column='employee_id')
    work_order_id = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, db_column='work_order_id')
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = productionworkers

    def __str__(self):
        return f'{self.employee_id}'

class WorkOrderStage(models.Model):
    work_stage_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    work_order_id = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, db_column='work_order_id')
    stage_name = models.CharField(max_length=255)
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