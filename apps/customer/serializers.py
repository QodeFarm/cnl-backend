from rest_framework import serializers
from .models import *
from apps.masters.serializers import *
from django.conf import settings
from django.core.files.storage import default_storage

#Create Serializers
        
class LedgerAccountsSerializers(serializers.ModelSerializer):
    ledger_group = ModLedgerGroupsSerializer(source='ledger_group_id', read_only=True)
    class Meta:
        model = LedgerAccounts
        fields = '__all__'

class ModLedgerAccountsSerializers(serializers.ModelSerializer):
    class Meta:
        model = LedgerAccounts
        fields = ['ledger_account_id', 'name', 'code']
        

class CustomerSerializer(serializers.ModelSerializer):
    ledger_account = ModLedgerAccountsSerializers(source='ledger_account_id', read_only=True)
    firm_status = ModFirmStatusesSerializers(source='firm_status_id', read_only=True)
    territory = ModTerritorySerializers(source='territory_id', read_only=True)
    customer_category = ModCustomerCategoriesSerializers(source='customer_category_id', read_only=True)
    gst_category = GstCategoriesSerializers(source='gst_category_id', read_only=True)
    payment_term = ModCustomerPaymentTermsSerializers(source='payment_term_id', read_only=True)
    price_category = PriceCategoriesSerializers(source='price_category_id', read_only=True)
    transporter = ModTransportersSerializers(source='transporter_id', read_only=True)
    class Meta:
        model = Customer
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
        
class ModCustomersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id', 'name']
        
class CustomerAttachmentsSerializers(serializers.ModelSerializer):
    customer = ModCustomersSerializer(source='customer_id', read_only=True)
    class Meta:
        model = CustomerAttachments
        fields = '__all__'

class CustomerAddressesSerializers(serializers.ModelSerializer):
    customer = ModCustomersSerializer(source='customer_id', read_only=True)
    city = ModCitySerializer(source='city_id', read_only=True)
    state = ModStateSerializer(source='state_id', read_only=True)
    country = ModCountrySerializer(source='country_id', read_only=True)
    class Meta:
        model = CustomerAddresses
        fields = '__all__'

class ModCustomerAddressesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddresses
        fields = ['customer_address_id','customer_id']

class CustomerAddressesSummarySerializer(serializers.ModelSerializer):
    billing_address = serializers.SerializerMethodField()
    shipping_address = serializers.SerializerMethodField()

    class Meta:
        model = CustomerAddresses
        fields = ['billing_address', 'shipping_address']

    def get_billing_address(self, obj):
        if obj.address_type == 'Billing':
            return f"{obj.address}, {obj.city_id.city_name}, {obj.state_id.state_name}, {obj.country_id.country_name}, {obj.pin_code}, Phone: {obj.phone}"
        return None

    def get_shipping_address(self, obj):
        if obj.address_type == 'Shipping':
            return f"{obj.address}, {obj.city_id.city_name}, {obj.state_id.state_name}, {obj.country_id.country_name}, {obj.pin_code}, Phone: {obj.phone}"
        return None

class CustomerOptionSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    customer_addresses = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'email', 'phone', 'customer_addresses']

    def get_customer_details(self, obj):
        addresses = CustomerAddresses.objects.filter(customer_id=obj.customer_id)
        
        email = None
        phone = None
        billing_address = None
        shipping_address = None
        
        for address in addresses:
            if email is None:
                email = address.email
            if phone is None:
                phone = address.phone
            if address.address_type == 'Billing':
                billing_address = address
            elif address.address_type == 'Shipping':
                shipping_address = address

        customer_addresses = {
            "billing_address": None,
            "shipping_address": None
        }
        
        if billing_address:
            customer_addresses["billing_address"] = f"{billing_address.address}, {billing_address.city_id.city_name}, {billing_address.state_id.state_name}, {billing_address.country_id.country_name}, {billing_address.pin_code}, Phone: {billing_address.phone}"
        if shipping_address:
            customer_addresses["shipping_address"] = f"{shipping_address.address}, {shipping_address.city_id.city_name}, {shipping_address.state_id.state_name}, {shipping_address.country_id.country_name}, {shipping_address.pin_code}, Phone: {shipping_address.phone}"

        return email, phone, customer_addresses

    def get_email(self, obj):
        return self.get_customer_details(obj)[0]

    def get_phone(self, obj):
        return self.get_customer_details(obj)[1]

    def get_customer_addresses(self, obj):
        return self.get_customer_details(obj)[2]
    
    def get_customer_summary(customers):
        serializer = CustomerOptionSerializer(customers, many=True)
        return {
            "count": len(serializer.data),
            "msg": "SUCCESS",
            "data": serializer.data
        }