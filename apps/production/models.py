from django.db import models
from config.utils_variables import billofmaterials, productionstatuses, workorders, inventory, machines, labor
from apps.products.models import Products
from apps.hrms.models import Employees

# Create your models here.
from django.db import models
import uuid

class BillOfMaterials(models.Model):
    bom_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, default=None, db_column='product_id')
    component_name = models.CharField(max_length=100, null=True, default=None,)
    quantity_required = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None,)
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
    status_id = models.ForeignKey('ProductionStatus', on_delete=models.CASCADE, db_column='status_id')
    start_date = models.DateField()
    end_date = models.DateField()
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

class Labor(models.Model):
    labor_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_id = models.ForeignKey(Employees, on_delete=models.CASCADE, db_column='employee_id')
    work_order_id = models.ForeignKey(WorkOrder, on_delete=models.CASCADE, db_column='work_order_id')
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = labor

    def __str__(self):
        return f'{self.employee_id}'