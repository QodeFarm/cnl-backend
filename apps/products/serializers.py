from rest_framework import serializers
from .models import *
from apps.masters.serializers import ProductUniqueQuantityCodesSerializer,ProductTypesSerializer,UnitOptionsSerializer,ProductItemTypeSerializer,ProductDrugTypesSerializer,ModProductBrandsSerializer


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
    class Meta:
        model = Products
        fields = ['product_id','name']

class productsSerializer(serializers.ModelSerializer):
    product_group = ModProductGroupsSerializer(source='product_group_id',read_only=True)
    category = ModProductCategoriesSerializer(source='category_id',read_only=True)
    type = ProductTypesSerializer(source='type_id',read_only=True)
    unit_options = UnitOptionsSerializer(source='unit_options_id',read_only=True)
    stock_unit = ModProductStockUnitsSerializer(source='stock_unit_id',read_only=True)
    gst_classification = ModProductGstClassificationsSerializer(source='gst_classification_id',read_only=True)
    sales_gl = ModProductSalesGlSerializer(source='sales_gl_id',read_only=True)
    purchase_gl = ModProductPurchaseGlSerializer(source='purchase_gl_id',read_only=True)
    item_type = ProductItemTypeSerializer(source='item_type_id',read_only=True)
    drug_type = ProductDrugTypesSerializer(source='drug_type_id',read_only=True)
    brand = ModProductBrandsSerializer(source='brand_id',read_only=True)
    class Meta:
        model = Products
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



class ProductOptionsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Products
        fields = ['product_id', 'name', 'sales_description', 'barcode', 'mrp', 'sales_rate','discount', 'dis_amount']
 
    def get_product_summary(products):
        serializer = ProductOptionsSerializer(products, many=True)
        return {
            "count": len(serializer.data),
            "msg": "SUCCESS",
            "data": serializer.data
        }