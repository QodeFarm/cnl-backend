import uuid
from django.db import models
from config.utils_methods import *
from config.utils_variables import *
from phonenumber_field.modelfields import PhoneNumberField

class Designations(models.Model):
    designation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    designation_name = models.CharField(max_length=50, null=True, default=None)

    class Meta:
        db_table = designations

    def __str__(self):
        return f"{self.designation_name}"

class Departments(models.Model):
    department_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    department_name = models.CharField(max_length=50, null=True, default=None)

    class Meta:
        db_table = departments

    def __str__(self):
        return f"{self.department_name}"

class Employees(models.Model):
    employee_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name =  models.CharField(max_length=255)
    email = models.EmailField(max_length=255, null=True, default=None)
    phone = models.PhoneNumberField(null=True, default=None)
    designation_id = models.ForeignKey(Designations, on_delete=models.CASCADE, db_column='lead_status_id')
    department_id = models.ForeignKey(Departments, on_delete=models.CASCADE, db_column='lead_status_id')

    class Meta:
        db_table = employees

    def __str__(self):
        return f"{self.name}"