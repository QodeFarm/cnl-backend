from rest_framework import serializers
from .models import *
from apps.masters.serializers import GPackageUnitSerializer, PackageUnitSerializer, ProductUniqueQuantityCodesSerializer,ProductTypesSerializer,UnitOptionsSerializer,ProductItemTypeSerializer,ProductDrugTypesSerializer,ModProductBrandsSerializer, ModUnitOptionsSerializer
from apps.inventory.serializers import ModWarehouseLocationsSerializer


class ModProductItemBalanceSerializer(serializers.ModelSerializer):
    warehouse_location = ModWarehouseLocationsSerializer(source='warehouse_location_id',read_only=True)
    class Meta:
        model = ProductItemBalance
        fields = '__all__'

    def get_locations(self, obj):
        product_variations = ProductVariation.objects.filter(product_id=obj.product_id).values_list('product_variation_id', flat=True)
        query_set = ProductItemBalance.objects.filter(product_variation_id__in=product_variations)
        return ProductItemBalanceSerializer(query_set, many=True).data

class ModProductVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariation
        fields = ['product_variation_id']

class ModProductGroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGroups
        fields = ['product_group_id','group_name']

class ProductGroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGroups
        fields = '__all__'

    def create(self, validated_data):
            picture = validated_data.pop('picture', None)
            instance = super().create(validated_data)
            if picture:
                instance.picture = picture
                instance.save()
            return instance
   
    def update(self, instance, validated_data):
        picture = validated_data.pop('picture', None)
        if picture:
            # Delete the previous picture file and its directory if they exist
            if instance.picture:
                picture_path = instance.picture.path
                if os.path.exists(picture_path):
                    os.remove(picture_path)
                    picture_dir = os.path.dirname(picture_path)
                    if not os.listdir(picture_dir):
                        os.rmdir(picture_dir)
            instance.picture = picture
            instance.save()
        return super().update(instance, validated_data)

class ModProductCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategories
        fields = ['category_id','category_name','code']

class ProductCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategories
        fields = '__all__'

    def create(self, validated_data):
            picture = validated_data.pop('picture', None)
            instance = super().create(validated_data)
            if picture:
                instance.picture = picture
                instance.save()
            return instance
   
    def update(self, instance, validated_data):
        picture = validated_data.pop('picture', None)
        if picture:
            # Delete the previous picture file and its directory if they exist
            if instance.picture:
                picture_path = instance.picture.path
                if os.path.exists(picture_path):
                    os.remove(picture_path)
                    picture_dir = os.path.dirname(picture_path)
                    if not os.listdir(picture_dir):
                        os.rmdir(picture_dir)
            instance.picture = picture
            instance.save()
        return super().update(instance, validated_data)

class ModProductStockUnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductStockUnits
        fields = ['stock_unit_id','stock_unit_name']

class ProductStockUnitsSerializer(serializers.ModelSerializer):
    quantity_code = ProductUniqueQuantityCodesSerializer(source='quantity_code_id',read_only=True)
    class Meta:
        model = ProductStockUnits
        fields = '__all__'

class ModProductGstClassificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGstClassifications
        fields = ['gst_classification_id','type','code','hsn_or_sac_code']
        
class ProductGstClassificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductGstClassifications
        fields = '__all__'

class ModProductSalesGlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSalesGl
        fields = ['sales_gl_id','name','sales_accounts','code','type']

class ProductSalesGlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSalesGl
        fields = '__all__'

class ModProductPurchaseGlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPurchaseGl
        fields = ['purchase_gl_id','name','purchase_accounts','code','type']
		    	
class ProductPurchaseGlSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPurchaseGl
        fields = '__all__'

class ModproductsSerializer(serializers.ModelSerializer):
    unit_options = ModUnitOptionsSerializer(source = 'unit_options_id', read_only = True)
    class Meta:
        model = Products
        fields = ['product_id','name', 'code', 'print_name', 'unit_options', 'sales_rate', 'mrp', 'discount', 'gst_input', 'wholesale_rate', 'dealer_rate']

class ModStockJournalProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['product_id','name']

class ModSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['size_id','size_name']

class ModColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['color_id','color_name']
#--------------------------------------------------------------
class PictureSerializer(serializers.Serializer):
    uid = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    attachment_name = serializers.CharField(max_length=255)
    file_size = serializers.IntegerField()
    attachment_path = serializers.CharField(max_length=255)
#-------------------------------------------------------------------

class productsSerializer(serializers.ModelSerializer):
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
    
    class Meta:
        model = Products
        fields = '__all__'

class ProductItemBalanceSerializer(serializers.ModelSerializer):
    product = ModproductsSerializer(source='product_id',read_only=True)
    warehouse_location = ModWarehouseLocationsSerializer(source='warehouse_location_id',read_only=True)
    class Meta:
        model = ProductItemBalance
        fields = '__all__'

class ProductOptionsSerializer(serializers.ModelSerializer):
    unit_options = ModUnitOptionsSerializer(source = 'unit_options_id', read_only = True)

    class Meta:
        model = Products
        fields = ['product_id', 'code', 'name', 'barcode', 'print_name', 'unit_options', 'sales_rate', 'wholesale_rate', 'dealer_rate', 'mrp', 'dis_amount', 'discount', 'balance', 'hsn_code', 'gst_input', 'created_at']

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = '__all__'

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'

class ProductVariationSerializer(serializers.ModelSerializer):
    product = ModproductsSerializer(source='product_id',read_only=True)
    size = ModSizeSerializer(source='size_id',read_only=True)
    color = ColorSerializer(source='color_id',read_only=True)

    class Meta:
        model = ProductVariation
        fields = '__all__'	