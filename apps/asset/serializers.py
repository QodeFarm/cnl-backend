from rest_framework import serializers
from apps.masters.serializers import ModAssetCategoriesSerializers, ModAssetStatusesSerializers, ModLocationsSerializers
from apps.asset.models import Assets,AssetMaintenance


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