from rest_framework import serializers
from .models import *

#Create serializers
class ModCountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['country_id','country_name']

class ModStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['state_id','state_name']

class ModCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['city_id','city_name']
        
class ModStatusesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statuses
        fields = ['status_id','status_name']

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class StateSerializer(serializers.ModelSerializer):
    country = ModCountrySerializer(source='country_id', read_only = True)
    class Meta:
        model = State
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    state = ModStateSerializer(source='state_id', read_only = True)
    class Meta:
        model = City
        fields = '__all__'
        
class StatusesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statuses 
        fields = '__all__'

class LedgerGroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerGroups
        fields = '__all__'

class ModLedgerGroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerGroups
        fields = ['ledger_group_id', 'name', 'code']

class FirmStatusesSerializers(serializers.ModelSerializer):
    class Meta:
        model = FirmStatuses
        fields = '__all__'
        
class ModFirmStatusesSerializers(serializers.ModelSerializer):
    class Meta:
        model = FirmStatuses
        fields = ['firm_status_id', 'name']

class TerritorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Territory
        fields = '__all__'

class ModTerritorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Territory
        fields = ['territory_id', 'name', 'code']
        
class CustomerCategoriesSerializers(serializers.ModelSerializer):
    class Meta:
        model = CustomerCategories
        fields = '__all__'

class ModCustomerCategoriesSerializers(serializers.ModelSerializer):
    class Meta:
        model = CustomerCategories
        fields = ['customer_category_id', 'name', 'code']


class GstCategoriesSerializers(serializers.ModelSerializer):
    class Meta:
        model = GstCategories
        fields = '__all__'

class ModGstCategoriesSerializers(serializers.ModelSerializer):
    class Meta:
        model = GstCategories
        fields = ['gst_category_id','name']

class CustomerPaymentTermsSerializers(serializers.ModelSerializer):
    class Meta:
        model = CustomerPaymentTerms
        fields = '__all__'

class ModCustomerPaymentTermsSerializers(serializers.ModelSerializer):
    class Meta:
        model = CustomerPaymentTerms
        fields = ['payment_term_id', 'name', 'code']
        
class PriceCategoriesSerializers(serializers.ModelSerializer):
    class Meta:
        model = PriceCategories
        fields = '__all__'

class ModPriceCategoriesSerializers(serializers.ModelSerializer):
    class Meta:
        model = PriceCategories
        fields = ['price_category_id' ,'name', 'code']
        
class TransportersSerializers(serializers.ModelSerializer):
    class Meta:
        model = Transporters
        fields = '__all__'

class ModTransportersSerializers(serializers.ModelSerializer):
    class Meta:
        model = Transporters
        fields = ['transporter_id', 'name', 'code', 'gst_no', 'website_url']

class ProductTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTypes
        fields = '__all__'

class ProductUniqueQuantityCodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductUniqueQuantityCodes
        fields = '__all__'

class UnitOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOptions
        fields = '__all__'

class ModUnitOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOptions
        fields = ['unit_options_id', 'unit_name']

class ProductDrugTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDrugTypes
        fields = '__all__'

class ProductItemTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductItemType
        fields = '__all__'

class ModBrandSalesmanSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandSalesman
        fields = ['brand_salesman_id','code','name']

class BrandSalesmanSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandSalesman
        fields = '__all__'

class ModProductBrandsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductBrands
        fields = ['brand_id','brand_name']
       
class ProductBrandsSerializer(serializers.ModelSerializer):
    brand_salesman = ModBrandSalesmanSerializer(source='brand_salesman_id',read_only=True)
    class Meta:
        model = ProductBrands
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


class PurchaseTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseTypes
        fields = '__all__'

class ModGstTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GstTypes
        fields = ['gst_type_id','name']

class ModSaleTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleTypes
        fields = ['sale_type_id','name']

class SaleTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleTypes
        fields = '__all__'

class ShippingModesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingModes
        fields = '__all__'

class GstTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GstTypes
        fields = '__all__'

class ModShippingCompaniesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingCompanies
        fields = ['shipping_company_id','code','name']

class ShippingCompaniesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingCompanies
        fields = '__all__'

class ModOrdersSalesmanSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdersSalesman
        fields = ['order_salesman_id','name']

class OrdersSalesmanSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrdersSalesman
        fields = '__all__'

class ModPaymentLinkTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentLinkTypes
        fields = ['payment_link_type_id','name']


class PaymentLinkTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentLinkTypes
        fields = '__all__'

class ModOrderStatusesSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatuses
        fields = ['order_status_id','status_name']

class OrderStatusesSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatuses
        fields = '__all__'

class ModOrderTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTypes
        fields = ['order_type_id','name']

class OrderTypesSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTypes
        fields = '__all__'

class ModTaskPrioritiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskPriorities
        fields = ['priority_id','priority_name']

class ModUnitOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOptions
        fields = ['unit_options_id','unit_name']

class TaskPrioritiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskPriorities
        fields = '__all__'
