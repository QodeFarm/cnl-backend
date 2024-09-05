from django.db import models
from config.utils_variables import billofmaterials, productionstatuses, workorders, inventory, machines, rawmaterials, workorderstages, productionworkers, defaultmachinery, workordermachines
from apps.products.models import Products
from apps.hrms.models import Employees

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

class BillOfMaterials(models.Model): # verified
    bom_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_id = models.ForeignKey(Products, on_delete=models.SET_NULL, null=True, db_column='product_id')
    component_name = models.CharField(max_length=100, null=True, default=None)
    quantity_required = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None)
    order_id = models.CharField(max_length=36, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = billofmaterials

    def __str__(self):
        return f'{self.component_name}'

class ProductionStatus(models.Model):
    status_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status_name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = productionstatuses

    def __str__(self):
        return f'{self.status_name}'

class WorkOrder(models.Model):
    work_order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, db_column='product_id')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    status_id = models.ForeignKey(ProductionStatus, on_delete=models.CASCADE, db_column='status_id')
    start_date = models.DateField(null=True, default=None)
    end_date = models.DateField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = workorders

    def __str__(self):
        return f'{self.product_id.name}_{self.status_id.status_name}'

class Inventory(models.Model):
    inventory_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, db_column='product_id')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None)
    location = models.CharField(max_length=100, null=True, default=None)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = inventory

    def __str__(self):
        return f'{self.inventory_id}'

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