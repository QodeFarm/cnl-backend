from rest_framework import serializers
from .models import FieldType, CustomField, CustomFieldOption, CustomFieldValue, Entities

class ModFieldTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldType
        fields = ['field_type_id', 'field_type_name']

class ModCustomFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomField
        fields = ['custom_field_id', 'field_name']

class ModEntitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entities
        fields = ['entity_id', 'entity_name']

class FieldTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldType
        fields = '__all__'

class CustomFieldSerializer(serializers.ModelSerializer):
    field_type = ModFieldTypeSerializer(source='field_type_id', read_only = True)
    class Meta:
        model = CustomField
        fields = '__all__'


class CustomFieldOptionSerializer(serializers.ModelSerializer):
    # custom_field = ModCustomFieldSerializer(source='custom_field_id', read_only = True)
    class Meta:
        model = CustomFieldOption
        fields = '__all__'

class EntitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entities
        fields = ['entity_id', 'entity_name', 'created_at', 'updated_at']

class CustomFieldValueSerializer(serializers.ModelSerializer):
    custom_field = ModCustomFieldSerializer(source='custom_field_id', read_only = True)
    entity = ModEntitiesSerializer(source='entity_id', read_only = True)
    class Meta:
        model = CustomFieldValue
        fields = '__all__'

# class CustomFieldEntityMappingSerializer(serializers.ModelSerializer):
#     custom_field = ModCustomFieldSerializer(source='custom_field_id', read_only = True)
#     class Meta:
#         model = CustomFieldEntityMapping
#         fields = '__all__'
