import uuid
from django.db import models
from config.utils_variables import fieldtypes, customfields, customfieldoptions, customfieldvalues, entities

class FieldType(models.Model):
    """
    Stores possible field types for custom fields.
    """
    field_type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    field_type_name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.field_type_name
    
    class Meta:
        db_table = fieldtypes


class CustomField(models.Model):
    """
    Stores the definition of custom fields, including entity associations.
    """
    custom_field_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    field_name = models.CharField(max_length=255)
    field_type_id = models.ForeignKey(FieldType, on_delete=models.CASCADE, db_column='field_type_id')
    entity_name = models.CharField(max_length=100)  # e.g., 'customers', 'vendors'
    is_required = models.BooleanField(default=False)
    validation_rules = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('field_name', 'entity_name')  # Prevents duplicate field names for the same entity
        db_table = customfields

    def __str__(self):
        return f"{self.field_name} ({self.entity_name})"


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

class Entities(models.Model):
    """
    Model representing the different types of entities (e.g., 'customer', 'order').
    """
    entity_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.entity_name
    
    class Meta:
        db_table = entities

class CustomFieldValue(models.Model):
    """
    Stores the values assigned to custom fields for various entities.
    """
    custom_field_value_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    custom_field_id = models.ForeignKey(CustomField, on_delete=models.CASCADE, db_column='custom_field_id')
    entity_id = models.ForeignKey(Entities, on_delete=models.CASCADE, db_column='entity_id')  # UUID of the entity (e.g., customer, vendor, etc.)
    field_value = models.CharField(max_length=255)
    field_value_type = models.CharField(max_length=50)  # e.g., 'string', 'number', 'date'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.custom_field.field_name} for Entity {self.entity_id}"
    
    class Meta:
        db_table = customfieldvalues


# class CustomFieldEntityMapping(models.Model):
#     """
#     Defines which custom fields are available for which entities.
#     """
#     mapping_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     custom_field_id = models.ForeignKey(CustomField, on_delete=models.CASCADE, db_column='custom_field_id')
#     entity_name = models.CharField(max_length=100)  # e.g., 'customers', 'vendors'

#     def __str__(self):
#         return f"{self.custom_field.field_name} mapped to {self.entity_name}"
    
#     class Meta:
#         db_table = customfieldentitymappings
