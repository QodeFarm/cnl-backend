from rest_framework import serializers
from .models import *
from apps.masters.serializers import ProductItemTypeSerializer,ModCitySerializer,ModStateSerializer,ModCountrySerializer
from apps.customer.serializers import ModCustomersSerializer

class ModWarehousesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouses
        fields = ['warehouse_id','name','code']

class WarehousesSerializer(serializers.ModelSerializer):
    item_type = ProductItemTypeSerializer(source='item_type_id',read_only=True)
    customer = ModCustomersSerializer(source='customer_id',read_only=True)
    city = ModCitySerializer(source='city_id', read_only = True)
    state = ModStateSerializer(source='state_id', read_only = True)
    country = ModCountrySerializer(source='country_id', read_only = True)
    class Meta:
        model = Warehouses
        fields = '__all__'