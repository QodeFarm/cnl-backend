from decimal import Decimal
from rest_framework import serializers

from apps.products.models import ProductItemBalance, Products, ProductGroups, ProductCategories, ProductStockUnits, ProductGstClassifications, ProductSalesGl, ProductPurchaseGl
from .models import *
from apps.masters.serializers import ModItemMasterSerializer, ModProductBrandsSerializer, ProductDrugTypesSerializer, ProductItemTypeSerializer,ModCitySerializer,ModStateSerializer,ModCountrySerializer, ProductTypesSerializer, UnitOptionsSerializer


# ============= Mod Serializers for Products (defined here to avoid circular imports) =============
class ModProductGroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGroups
        fields = ['product_group_id','group_name']

class ModProductCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategories
        fields = ['category_id','category_name','code']

class ModProductStockUnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStockUnits
        fields = ['stock_unit_id','stock_unit_name']

class ModProductGstClassificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGstClassifications
        fields = ['gst_classification_id','type','code','hsn_or_sac_code']

class ModProductSalesGlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSalesGl
        fields = ['sales_gl_id','name','sales_accounts','code','type']

class ModProductPurchaseGlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPurchaseGl
        fields = ['purchase_gl_id','name','purchase_accounts','code','type']

class PictureSerializer(serializers.Serializer):
    uid = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    attachment_name = serializers.CharField(max_length=255)
    file_size = serializers.IntegerField()
    attachment_path = serializers.CharField(max_length=255)
# ================================================================================================


class ModWarehousesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouses
        fields = ['warehouse_id','name','code']

class ModWarehouseLocationsSerializer(serializers.ModelSerializer):
    warehouse = ModWarehousesSerializer(source='warehouse_id',read_only=True)
    class Meta:
        model = WarehouseLocations
        fields = ['location_id','location_name', 'warehouse']

class WarehousesSerializer(serializers.ModelSerializer):
    item_type = ProductItemTypeSerializer(source='item_type_id',read_only=True)
    city = ModCitySerializer(source='city_id', read_only = True)
    state = ModStateSerializer(source='state_id', read_only = True)
    country = ModCountrySerializer(source='country_id', read_only = True)
    class Meta:
        model = Warehouses
        fields = '__all__'

class WarehouseLocationsSerializer(serializers.ModelSerializer):
    warehouse = ModWarehousesSerializer(source='warehouse_id',read_only=True)

    class Meta:
        model = WarehouseLocations
        fields = '__all__'


class InventoryBlockConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryBlockConfig
        fields = '__all__'

class BlockedInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedInventory
        fields = '__all__'


class ProductStockForecastSerializer(serializers.ModelSerializer):
    """
    Stock Forecast Report Serializer - Same format as productsSerializer
    """
    product_group = ModProductGroupsSerializer(source='product_group_id',read_only=True)
    category = ModProductCategoriesSerializer(source='category_id',read_only=True)
    type = ProductTypesSerializer(source='type_id',read_only=True)
    unit_options = UnitOptionsSerializer(source='unit_options_id',read_only=True)
    picture = PictureSerializer(required=False, allow_null=True, many=True)
    stock_unit = ModProductStockUnitsSerializer(source='stock_unit_id',read_only=True)
    gst_classification = ModProductGstClassificationsSerializer(source='gst_classification_id',read_only=True)
    sales_gl = ModProductSalesGlSerializer(source='sales_gl_id',read_only=True)
    purchase_gl = ModProductPurchaseGlSerializer(source='purchase_gl_id',read_only=True)
    item_type = ProductItemTypeSerializer(source='item_type_id',read_only=True)
    drug_type = ProductDrugTypesSerializer(source='drug_type_id',read_only=True)
    brand = ModProductBrandsSerializer(source='brand_id',read_only=True)
    pack_unit = ModProductStockUnitsSerializer(source='pack_unit_id',read_only=True)
    g_pack_unit = ModProductStockUnitsSerializer(source='g_pack_unit_id',read_only=True)
    product_mode = ModItemMasterSerializer(source='product_mode_id', read_only=True)
    
    current_stock = serializers.SerializerMethodField()
    average_sales = serializers.SerializerMethodField()
    stock_difference = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    status_message = serializers.SerializerMethodField()
    recommended_action = serializers.SerializerMethodField()
    action_label = serializers.SerializerMethodField()

    class Meta:
        model = Products
        fields = '__all__'

    def get_current_stock(self, obj):
        """
        Get current stock from Products.balance field
        (Same source as Inventory Products API)
        """
        try:
            # Use Products.balance field directly (same as inventory list)
            if obj.balance is not None:
                return float(obj.balance)
            return 0.0
        except Exception:
            return 0.0

    def get_average_sales(self, obj):
        """Calculate average monthly sales based on period"""
        try:
            sales_dict = self.context.get('sales_dict', {})
            period_days = self.context.get('period_days', 180)
            
            pid_str = str(obj.product_id).replace('-', '')
            total_sales = sales_dict.get(pid_str, Decimal('0'))
            
            # Calculate number of months from period_days
            months = max(period_days / 30, 1)  # At least 1 month to avoid division by zero
            
            # Average monthly sales
            avg_sales = float(total_sales) / months
            return round(avg_sales, 2)
        except Exception:
            return 0.0

    def get_stock_difference(self, obj):
        """Current stock minus average monthly sales"""
        current = self.get_current_stock(obj)
        avg = self.get_average_sales(obj)
        return round(current - avg, 2)

    def get_status(self, obj):
        """Determine stock status: RED, YELLOW, GREEN"""
        current = self.get_current_stock(obj)
        avg = self.get_average_sales(obj)
        diff = current - avg
        
        if current <= 0:
            return "RED"
        elif avg > 0 and diff < 0:
            return "RED"
        elif avg > 0 and diff < avg:
            return "YELLOW"
        else:
            return "GREEN"

    def get_status_message(self, obj):
        """Human readable status message"""
        status = self.get_status(obj)
        current = self.get_current_stock(obj)
        avg = self.get_average_sales(obj)
        
        if status == "RED":
            if current <= 0:
                return "Critical - No Stock"
            return "Critical - Stock Below Average Sales"
        elif status == "YELLOW":
            return "Warning - Low Stock"
        else:
            if avg == 0:
                return "In Stock - No Recent Sales"
            return "Healthy Stock"

    def get_recommended_action(self, obj):
        """Suggest action based on status"""
        status = self.get_status(obj)
        if status in ["RED", "YELLOW"]:
            return "CREATE_WORK_ORDER"
        return "CREATE_WORK_ORDER"

    def get_action_label(self, obj):
        """Button label for frontend"""
        return "Request"