import uuid
from django.db import models
from config.utils_methods import *
from config.utils_variables import *
from phonenumber_field.modelfields import PhoneNumberField
from masters.models import Departments, Designations


class Employees(models.Model):
    employee_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name =  models.CharField(max_length=255, null=False)
    email = models.EmailField(max_length=255, null=False)
    phone = PhoneNumberField(blank=True, null=True, default=None, help_text="Enter the phone number with country code, e.g., +91 XXXXXXXXXX")
    designation_id = models.ForeignKey(Designations, on_delete=models.CASCADE, db_column='designation_id', null=False)
    department_id = models.ForeignKey(Departments, on_delete=models.CASCADE, db_column='department_id', null=False)

    class Meta:
        db_table = employees

    def __str__(self):
        return f"{self.name}"