from rest_framework import serializers

from apps.vendor.serializers import ModVendorSerializer
from .models import  CustomField, CustomFieldOption, CustomFieldValue
from apps.masters.serializers import ModFieldTypeSerializer, ModEntitiesSerializer, ModOrderTypesSerializer


class ModCustomFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomField
        fields = ['custom_field_id', 'field_name']

class CustomFieldSerializer(serializers.ModelSerializer):
    field_type = ModFieldTypeSerializer(source='field_type_id', read_only = True)
    entity = ModEntitiesSerializer(source='entity_id', read_only = True)
    class Meta:
        model = CustomField
        fields = '__all__'


class CustomFieldOptionSerializer(serializers.ModelSerializer):
    custom_field = ModCustomFieldSerializer(source='custom_field_id', read_only = True)
    class Meta:
        model = CustomFieldOption
        fields = '__all__'

class CustomFieldValueSerializer(serializers.ModelSerializer):
    custom_field = ModCustomFieldSerializer(source='custom_field_id', read_only = True)
    entity = ModEntitiesSerializer(source='entity_id', read_only = True)
    class Meta:
        model = CustomFieldValue
        fields = '__all__'