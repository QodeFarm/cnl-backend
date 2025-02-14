import uuid
from django.db import models
from apps.customer.models import Customer
from apps.vendor.models import Vendor
from config.utils_variables import  customfields, customfieldoptions, customfieldvalues
from apps.masters.models import FieldType, Entities


class CustomField(models.Model):
    """
    Stores the definition of custom fields, including entity associations.
    """
    custom_field_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    field_name = models.CharField(max_length=255)
    field_type_id = models.ForeignKey(FieldType, on_delete=models.CASCADE, db_column='field_type_id')
    entity_id = models.ForeignKey(Entities, on_delete=models.CASCADE, db_column='entity_id')
    is_required = models.BooleanField(default=False)
    validation_rules = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # unique_together = ('field_name', 'entity_id')  # Prevents duplicate field names for the same entity
        db_table = customfields

    def __str__(self):
        return f"{self.field_name}"
    
        # return f"{self.field_name} ({self.entity_id.entity_name})"


class CustomFieldOption(models.Model):
    """
    Stores the options for fields of type Select or MultiSelect.
    """
    option_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    custom_field_id = models.ForeignKey(CustomField, on_delete=models.CASCADE, db_column='custom_field_id')
    option_value = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"Option for {self.custom_field.field_name}: {self.option_value}"
    
    class Meta:
        db_table = customfieldoptions

class CustomFieldValue(models.Model):
    """
    Stores the values assigned to custom fields for various entities.
    """
    custom_field_value_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    custom_field_id = models.ForeignKey(CustomField, on_delete=models.CASCADE, db_column='custom_field_id')
    entity_id = models.ForeignKey(Entities, on_delete=models.CASCADE, db_column='entity_id')  # UUID of the entity (e.g., customer, vendor, etc.)
    entity_data_id = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, related_name="custom_field_values", db_column='entity_data_id')  # Correct naming
    vendor_id = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True, db_column='vendor_id')  # Correct naming
    field_value = models.CharField(max_length=255)
    field_value_type = models.CharField(max_length=50, null=True)  # e.g., 'string', 'number', 'date'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.custom_field.field_name} for Entity {self.entity_id}"
    
    class Meta:
        db_table = customfieldvalues
