from rest_framework import serializers
from apps.assets.models import AssetStatuses, AssetCategories, Locations, Assets, AssetMaintenance


#Create your serializers here.
class ModAssetStatusesSerializers(serializers.ModelSerializer):
    class Meta:
        model = AssetStatuses
        fields = ['asset_status_id','status_name']

class AssetStatusesSerializers(serializers.ModelSerializer):
    class Meta:
        model = AssetStatuses
        fields = '__all__'

class ModAssetCategoriesSerializers(serializers.ModelSerializer):
    class Meta:
        model = AssetCategories
        fields = ['asset_category_id','category_name']

class AssetCategoriesSerializers(serializers.ModelSerializer):
    class Meta:
        model = AssetCategories
        fields = '__all__'
		
class ModLocationsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Locations
        fields = ['location_id','location_name','address']

class LocationsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Locations
        fields = '__all__'

class ModAssetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assets
        fields = ['asset_id','name','price']

class AssetsSerializer(serializers.ModelSerializer):
    asset_category = ModAssetCategoriesSerializers(source='asset_category_id', read_only=True)
    asset_status = ModAssetStatusesSerializers(source='asset_status_id', read_only=True)
    location = ModLocationsSerializers(source='location_id', read_only=True)
    class Meta:
        model = Assets
        fields = '__all__'
		
class ModAssetMaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetMaintenance
        fields = ['asset_maintenance_id','asset_id','maintenance_date']

class AssetMaintenanceSerializer(serializers.ModelSerializer):
    asset = ModAssetsSerializer(source='asset_id', read_only=True)
    class Meta:
        model = AssetMaintenance
        fields = '__all__'