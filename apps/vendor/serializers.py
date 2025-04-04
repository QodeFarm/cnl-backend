from apps.masters.serializers import ModFirmStatusesSerializers, ModTerritorySerializers, ModGstCategoriesSerializers, ModTransportersSerializers, ModPriceCategoriesSerializers, ModCitySerializer,ModStateSerializer, ModCountrySerializer
from apps.customer.serializers import ModLedgerAccountsSerializers
from rest_framework import serializers
from .models import *
from apps.products.serializers import PictureSerializer

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
    picture = PictureSerializer(many=True)

    class Meta:
        model = Vendor
        fields = '__all__'

class VendorsOptionsSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    vendor_addresses = serializers.SerializerMethodField()
    vendor_category = serializers.SerializerMethodField() 
    # ledger_account = serializers.SerializerMethodField() 
    city = serializers.SerializerMethodField() 

    class Meta:
        model = Vendor
        fields = ['vendor_id', 'name', 'phone', 'email', 'city', 'gst_no', 'vendor_category', 'created_at','vendor_addresses', 'updated_at'] 

    def get_vendor_address_details(self, obj):
        addresses = VendorAddress.objects.filter(vendor_id=obj.vendor_id)
      
        email = None
        phone = None  
        city = None   
        billing_address = None
        shipping_address = None
        
        for address in addresses:
            if email is None:
                email = address.email
            if phone is None:
                phone = address.phone
            if city is None:
                city = address.city_id
            if address.address_type == 'Billing':
                billing_address = address
            elif address.address_type == 'Shipping':
                shipping_address = address

        vendor_addresses = {
            "billing_address": None,
            "shipping_address": None
        }

        if billing_address:
            vendor_addresses["billing_address"] = f"{billing_address.address}, {billing_address.city_id.city_name}, {billing_address.state_id.state_name}, {billing_address.country_id.country_name}, {billing_address.pin_code}, Phone: {billing_address.phone},email: {billing_address.email}"
        if shipping_address:
            vendor_addresses["shipping_address"] = f"{shipping_address.address}, {shipping_address.city_id.city_name}, {shipping_address.state_id.state_name}, {shipping_address.country_id.country_name}, {shipping_address.pin_code}, Phone: {shipping_address.phone},email: {shipping_address.email}"

        return email, phone, city, vendor_addresses

    def get_email(self, obj):
         return self.get_vendor_address_details(obj)[0]

    def get_phone(self, obj):
        return self.get_vendor_address_details(obj)[1]
    
    def get_city(self, obj):
        city = self.get_vendor_address_details(obj)[2]
        if city:
            return ModCitySerializer(city).data
        return None
    
    def get_vendor_addresses(self, obj):
        return self.get_vendor_address_details(obj)[3]
    
    def get_ledger_account(self, obj):
        if obj.ledger_account_id:
            return ModLedgerAccountsSerializers(obj.ledger_account_id).data
        return None
    
    def get_vendor_category(self, obj):
        if obj.vendor_category_id:
            return ModVendorCategorySerializer(obj.vendor_category_id).data
        return None
    
    def get_vendors_summary(vendors):
        serializer = VendorsOptionsSerializer(vendors, many=True)
        return serializer.data