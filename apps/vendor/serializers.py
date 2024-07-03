from rest_framework import serializers
from .models import *
from apps.customer.serializers import ModLedgerAccountsSerializers
from apps.masters.serializers import ModFirmStatusesSerializers, ModTerritorySerializers, ModGstCategoriesSerializers, ModTransportersSerializers, ModPriceCategoriesSerializers, ModCitySerializer,ModStateSerializer, ModCountrySerializer

#Create Serializers

class ModVendorSerializer(serializers.ModelSerializer):  #HyperlinkedModelSerializer
    class Meta:
        model = Vendor
        fields = ['vendor_id','name','code']

class VendorCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorCategory
        fields = '__all__'

class ModVendorCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorCategory
        fields = ['vendor_category_id','name','code']

class VendorPaymentTermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorPaymentTerms
        fields = '__all__'

class ModVendorPaymentTermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorPaymentTerms
        fields = ['payment_term_id','name','code']


class VendorAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorAgent
        fields = '__all__'

class ModVendorAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorAgent
        fields = ['vendor_agent_id','name','code']

class VendorAttachmentSerializer(serializers.ModelSerializer):
    vendor = ModVendorSerializer(source='vendor_id', read_only = True)
    class Meta:
        model = VendorAttachment
        fields = '__all__'

class VendorAddressSerializer(serializers.ModelSerializer):
    vendor = ModVendorSerializer(source='vendor_id', read_only = True)
    city = ModCitySerializer(source='city_id', read_only = True)
    state = ModStateSerializer(source='state_id', read_only = True)
    country = ModCountrySerializer(source='country_id', read_only = True)
    class Meta:
        model = VendorAddress
        fields = '__all__'


class VendorSerializer(serializers.ModelSerializer):  #HyperlinkedModelSerializer

    ledger_account = ModLedgerAccountsSerializers(source='ledger_account_id', read_only = True)
    firm_status = ModFirmStatusesSerializers(source='firm_status_id', read_only = True)
    territory = ModTerritorySerializers(source='territory_id', read_only = True)
    vendor_category = ModVendorCategorySerializer(source='vendor_category_id', read_only = True)
    gst_category = ModGstCategoriesSerializers(source='gst_category_id', read_only = True)
    payment_term = ModVendorPaymentTermsSerializer(source='payment_term_id', read_only = True)
    price_category = ModPriceCategoriesSerializers(source='price_category_id', read_only = True)
    vendor_agent = ModVendorAgentSerializer(source='vendor_agent_id', read_only = True)
    transporter = ModTransportersSerializers(source='transporter_id', read_only = True)

    class Meta:
        model = Vendor
        fields = '__all__'
    