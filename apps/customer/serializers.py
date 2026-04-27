from rest_framework import serializers

from apps.finance.models import JournalEntryLines, PaymentTransaction
from apps.sales.models import SaleInvoiceOrders
from .models import *
from apps.products.serializers import PictureSerializer
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
        

# class CustomerSerializer(serializers.ModelSerializer):
#     ledger_account = ModLedgerAccountsSerializers(source='ledger_account_id', read_only=True)
#     firm_status = ModFirmStatusesSerializers(source='firm_status_id', read_only=True)
#     territory = ModTerritorySerializers(source='territory_id', read_only=True)
#     # picture = PictureSerializer(many=True)
#     picture = PictureSerializer(required=False, allow_null=True, many=True)

#     customer_category = ModCustomerCategoriesSerializers(source='customer_category_id', read_only=True)
#     gst_category = GstCategoriesSerializers(source='gst_category_id', read_only=True)
#     payment_term = ModCustomerPaymentTermsSerializers(source='payment_term_id', read_only=True)
#     price_category = PriceCategoriesSerializers(source='price_category_id', read_only=True)
#     transporter = ModTransportersSerializers(source='transporter_id', read_only=True)
#     class Meta:
#         model = Customer
#         fields = '__all__'  

class CustomerSerializer(serializers.ModelSerializer):
    ledger_account = ModLedgerAccountsSerializers(source='ledger_account_id', read_only=True)
    firm_status = ModFirmStatusesSerializers(source='firm_status_id', read_only=True)
    territory = ModTerritorySerializers(source='territory_id', read_only=True)
    picture = PictureSerializer(required=False, allow_null=True, many=True)
    customer_category = ModCustomerCategoriesSerializers(source='customer_category_id', read_only=True)
    gst_category = GstCategoriesSerializers(source='gst_category_id', read_only=True)
    payment_term = ModCustomerPaymentTermsSerializers(source='payment_term_id', read_only=True)
    price_category = PriceCategoriesSerializers(source='price_category_id', read_only=True)
    transporter = ModTransportersSerializers(source='transporter_id', read_only=True)
    
    # Add new portal fields
    username = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    password = serializers.CharField(required=False, write_only=True, allow_blank=True, allow_null=True)
    is_portal_user = serializers.BooleanField(required=False, default=False)
    last_login = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Customer
        fields = '__all__'  # This will automatically include the new fields
        extra_kwargs = {
            'password': {'write_only': True},  # Ensure password never appears in responses
            'username': {'read_only': False},  # Username can be written but will be read in responses
        }

    def create(self, validated_data):
        # Hash password if provided and it's a portal user
        if validated_data.get('is_portal_user'):
            password = validated_data.get('password')
            if password:
                from django.contrib.auth.hashers import make_password
                validated_data['password'] = make_password(password)
            
            # Auto-generate username if not provided
            if not validated_data.get('username'):
                name = validated_data.get('name', '')
                validated_data['username'] = self.generate_username_from_name(name)
        else:
            # If not portal user, ensure these fields are null/empty
            validated_data['username'] = None
            validated_data['password'] = None
            validated_data['is_portal_user'] = False
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Handle password update
        if 'password' in validated_data:
            password = validated_data.get('password')
            if password:
                from django.contrib.auth.hashers import make_password
                validated_data['password'] = make_password(password)
            else:
                # If empty password provided, remove it from update (keep existing)
                validated_data.pop('password')
        
        # Handle username auto-generation if needed
        if validated_data.get('is_portal_user') and not validated_data.get('username'):
            name = validated_data.get('name', instance.name)
            validated_data['username'] = self.generate_username_from_name(name)
        
        # If turning off portal access, clear credentials
        if 'is_portal_user' in validated_data and not validated_data['is_portal_user']:
            validated_data['username'] = None
            validated_data['password'] = None
        
        return super().update(instance, validated_data)

    def generate_username_from_name(self, name):
        """Generate username from customer name"""
        if not name:
            return None
        import re
        # Convert to lowercase, replace spaces with dots, remove special chars
        username = name.lower().replace(' ', '.')
        username = re.sub(r'[^a-z0-9.]', '', username)
        
        # Check for uniqueness and append number if needed
        original_username = username
        counter = 1
        while Customer.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1
        
        return username

    def to_representation(self, instance):
        """Customize the response representation"""
        data = super().to_representation(instance)
        
        # Remove sensitive data
        if 'password' in data:
            del data['password']
        
        # Add portal info summary
        if instance.is_portal_user:
            data['portal_info'] = {
                'has_access': True,
                'username': instance.username,
                'last_login': instance.last_login
            }
        else:
            data['portal_info'] = {
                'has_access': False
            }
        
        return data
           
        
class ModCustomersSerializer(serializers.ModelSerializer):
    customer_category = ModCustomerCategoriesSerializers(source='customer_category_id', read_only=True)
    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'customer_category']
        
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
    city = serializers.SerializerMethodField() 
    ledger_account = serializers.SerializerMethodField()
    pin_code = serializers.SerializerMethodField()
    customer_category = ModCustomerCategoriesSerializers(source='customer_category_id', read_only=True)

    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'code', 'phone', 'email', 'city', 'gst', 'ledger_account', 'created_at', 'customer_addresses', 'credit_limit', 'max_credit_days','pin_code', 'customer_category', 'is_deleted']

    def get_customer_details(self, obj):
        addresses = CustomerAddresses.objects.filter(customer_id=obj.customer_id)
        
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
                
        def format_address(addr):
            if not addr:
                return None

            parts = [
                addr.address or '',
                addr.city_id.city_name if addr.city_id else '',
                addr.state_id.state_name if addr.state_id else '',
                addr.country_id.country_name if addr.country_id else '',
                addr.pin_code or '',
                f"Phone: {addr.phone}" if addr.phone else '',
                f"email: {addr.email}" if addr.email else ''
            ]
            return ', '.join([p for p in parts if p])  # remove empty parts        

        customer_addresses = {
            "billing_address": None,
            "shipping_address": None,
            "custom_shipping_address": None
        }
        
        if billing_address:
            customer_addresses["billing_address"] = format_address(billing_address)
        if shipping_address:
            customer_addresses["shipping_address"] = format_address(shipping_address)
            customer_addresses["custom_shipping_address"] = shipping_address.address or None

        
        # if billing_address:
        #     customer_addresses["billing_address"] = f"{billing_address.address}, {billing_address.city_id.city_name}, {billing_address.state_id.state_name}, {billing_address.country_id.country_name}, {billing_address.pin_code}, Phone: {billing_address.phone},email: {billing_address.email}"
        # if shipping_address:
        #     customer_addresses["shipping_address"] = f"{shipping_address.address}, {shipping_address.city_id.city_name}, {shipping_address.state_id.state_name}, {shipping_address.country_id.country_name}, {shipping_address.pin_code}, Phone: {shipping_address.phone},email: {shipping_address.email}"
        
        return email, phone, city, customer_addresses

    def get_email(self, obj):
        return self.get_customer_details(obj)[0]

    def get_phone(self, obj):
        return self.get_customer_details(obj)[1]
    
    def get_city(self, obj):
        city = self.get_customer_details(obj)[2]
        if city:
            return ModCitySerializer(city).data
        return None

    def get_customer_addresses(self, obj):
        return self.get_customer_details(obj)[3]
    
    def get_pin_code(self, obj):
        addresses = CustomerAddresses.objects.filter(customer_id=obj.customer_id)
        # Try to get pin code from shipping address first
        shipping_address = addresses.filter(address_type='Shipping').first()
        if shipping_address and shipping_address.pin_code:
            return shipping_address.pin_code
            
        # # If no shipping address pin code, try billing address
        # billing_address = addresses.filter(address_type='Billing').first()
        # if billing_address and billing_address.pin_code:
        #     return billing_address.pin_code
        
        # If no specific address with pin code, try any address
        for address in addresses:
            if address.pin_code:
                return address.pin_code
        
        return None
    
    # def get_ledger_account(self, obj):
    #     if obj.ledger_account_id:
    #         return ModLedgerAccountsSerializers(obj.ledger_account_id).data
    #     return None
    
    def get_ledger_account(self, obj):
        if obj.ledger_account_id_id:  # Check the raw foreign key ID, not just the relation
            try:
                ledger_account = LedgerAccounts.objects.get(ledger_account_id=obj.ledger_account_id_id)
                return ModLedgerAccountsSerializers(ledger_account).data
            except LedgerAccounts.DoesNotExist:
                return None  # Avoid raising an error
        return None
    
        
    def get_customer_summary(customers):
        serializer = CustomerOptionSerializer(customers, many=True)
        return {
            "count": len(serializer.data),
            "msg": "SUCCESS",
            "data": serializer.data
        }

class CustomerBalanceSerializer(serializers.ModelSerializer):
    customer = ModCustomersSerializer(source='customer_id', read_only=True)
    class Meta:
        model = CustomerBalance
        fields = ['customer_balance_id','customer','balance_amount','created_at' ]

class CustomerSummaryReportSerializer(serializers.ModelSerializer):
    total_sales = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    outstanding_payments = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    total_advance = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)

    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'total_sales', 'total_advance', 'outstanding_payments']   

class CustomerOrderHistoryReportSerializer(serializers.ModelSerializer):
    customer = ModCustomersSerializer(source='customer_id', read_only=True)
    order_status = ModOrderStatusesSerializer(source='order_status_id',read_only=True)

    class Meta:
        model = SaleInvoiceOrders
        fields = ['invoice_no','invoice_date','total_amount','order_status','customer']

class CustomerCreditLimitReportSerializer(serializers.ModelSerializer):
    credit_usage = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    remaining_credit = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    
    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'credit_limit', 'credit_usage', 'remaining_credit']

class CustomerLedgerReportSerializer(serializers.ModelSerializer):
    """
    Serializer for Customer Ledger Report that tracks all financial transactions with a customer.
    This includes sales, payments, and any other debit/credit transactions.
    """
    transaction_date = serializers.DateField(source='journal_entry_id.entry_date')
    reference_number = serializers.CharField(source='journal_entry_id.reference')
    description = serializers.SerializerMethodField()
    debit = serializers.DecimalField(max_digits=18, decimal_places=2)
    credit = serializers.DecimalField(max_digits=18, decimal_places=2)
    running_balance = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    transaction_type = serializers.SerializerMethodField()
    
    class Meta:
        model = JournalEntryLines
        fields = ['journal_entry_line_id','transaction_date','reference_number','description','debit','credit','running_balance','transaction_type']
    
    def get_description(self, obj):
        """
        Returns either the line description or falls back to the journal entry description
        """
        return obj.description or obj.journal_entry_id.description
    
    def get_transaction_type(self, obj):
        """
        Determines transaction type based on the journal entry reference or other attributes
        """
        reference = obj.journal_entry_id.reference or ''
        if 'SO-' in reference:
            return 'Sale Order'
        elif 'SO-INV' in reference or 'INV' in reference:
            return 'Sale Invoice'
        elif 'SR-' in reference:
            return 'Sale Return'
        elif 'CN-' in reference:
            return 'Credit Note'  
        elif 'DN-' in reference:
            return 'Debit Note'
        elif 'RCPT-' in reference:
            return 'Receipt'
        elif 'PMT-' in reference:
            return 'Payment'
        else:
            return 'Other'

class CustomerOutstandingReportSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for Customer Outstanding Report showing pending payments per customer.
    """
    total_sales = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    total_paid = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    total_pending = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    last_payment_date = serializers.DateField(read_only=True)
    phone = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = ['customer_id', 'name', 'total_sales', 'total_paid', 'total_pending', 
                 'last_payment_date', 'phone', 'email']
    
    def get_phone(self, obj):
        """Get the customer's phone number from addresses"""
        address = obj.customeraddresses_set.filter(phone__isnull=False).first()
        return address.phone if address else None
    
    def get_email(self, obj):
        """Get the customer's email from addresses"""
        address = obj.customeraddresses_set.filter(email__isnull=False).first()
        return address.email if address else None

class CustomerPaymentReportSerializer(serializers.ModelSerializer):
    """
    Serializer for Customer Payment Report showing payments received from customers.
    """
    payment_id = serializers.UUIDField()
    payment_date = serializers.DateField()
    payment_amount = serializers.DecimalField(source='amount', max_digits=15, decimal_places=2)
    payment_method = serializers.CharField()
    payment_status = serializers.CharField()
    reference_number = serializers.CharField()
    invoice_id = serializers.CharField()
    customer_name = serializers.SerializerMethodField()
    customer_gst = serializers.SerializerMethodField()
    notes = serializers.CharField()
    
    class Meta:
        model = PaymentTransaction
        fields = ['payment_id', 'payment_date', 'payment_amount', 'payment_method',
                  'payment_status', 'reference_number', 'invoice_id',
                  'customer_name', 'customer_gst', 'notes']
    
    def get_customer_name(self, obj):
        """Get customer name based on invoice_id"""
        from apps.sales.models import SaleInvoiceOrders
        if obj.order_type == 'Sale':
            try:
                sale_invoice = SaleInvoiceOrders.objects.filter(
                    sale_invoice_id=obj.invoice_id
                ).select_related('customer_id').first()
                if sale_invoice and sale_invoice.customer_id:
                    return sale_invoice.customer_id.name
            except Exception:
                pass
        return "N/A"
    
    def get_customer_gst(self, obj):
        """Get customer GST based on invoice_id"""
        from apps.sales.models import SaleInvoiceOrders
        if obj.order_type == 'Sale':
            try:
                sale_invoice = SaleInvoiceOrders.objects.filter(
                    sale_invoice_id=obj.invoice_id
                ).select_related('customer_id').first()
                if sale_invoice and sale_invoice.customer_id:
                    return sale_invoice.customer_id.gst
            except Exception:
                pass
        return "N/A"
    
#Customer Authentication Serializer
# serializers.py
from rest_framework import serializers
from .models import Customer
from django.contrib.auth.hashers import check_password

class CustomerPortalLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        try:
            customer = Customer.objects.get(username=username, is_portal_user=True, is_deleted=False)
            
            # Check password
            if not check_password(password, customer.password):
                raise serializers.ValidationError("Invalid credentials")
            
            data['customer'] = customer
            return data
            
        except Customer.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials or account not activated")

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'customer_id', 'name', 'print_name', 'code', 'gst', 'pan',
            'contact_person', 'website', 'credit_limit', 'max_credit_days',
            'registration_date', 'username', 'last_login'
        ]
        read_only_fields = fields  # Make all fields read-only
        
#-------------------customer password changes and resets serializers-----------------------
# serializers.py (in your customers app)

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
import uuid

# serializers.py - UPDATED VERSION

# serializers.py

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
import uuid

# serializers.py - Fixed version

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
import uuid
from django.conf import settings
# from apps.customers.models import Customer, CustomerAddresses, CustomerPasswordReset

# serializers.py - Validate by username

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
import uuid
from django.conf import settings
# from apps.customers.models import Customer, CustomerAddresses, CustomerPasswordReset

# serializers.py

# serializers.py - Fixed version

# serializers.py - Clean version without URL shortening

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
import uuid
import requests
import re
from django.conf import settings
# from apps.customers.models import Customer, CustomerAddresses, CustomerPasswordReset

class SendCustomerPasswordResetSerializer(serializers.Serializer):
    """Serializer for sending password reset via Email or WhatsApp"""
    
    username = serializers.CharField(required=True)
    
    # WATI Configuration
    WATI_INSTANCE_ID = "10114393"
    WATI_TOKEN = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6ImFkbWluQGNubGVycC5jb20iLCJuYW1laWQiOiJhZG1pbkBjbmxlcnAuY29tIiwiZW1haWwiOiJhZG1pbkBjbmxlcnAuY29tIiwiYXV0aF90aW1lIjoiMDQvMDgvMjAyNiAwNTozNjozMyIsInRlbmFudF9pZCI6IjEwMTE0MzkzIiwiZGJfbmFtZSI6Im10LXByb2QtVGVuYW50cyIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6IkFETUlOSVNUUkFUT1IiLCJleHAiOjI1MzQwMjMwMDgwMCwiaXNzIjoiQ2xhcmVfQUkiLCJhdWQiOiJDbGFyZV9BSSJ9.fgw-FrZ17KIRnuwXeftK55HeRi61PCTRBa-TI7NSgbY"
    
    def _get_frontend_url(self, request):
        """Get frontend URL based on backend subdomain"""
        host = request.get_host().lower()
        
        print(f"🌐 Backend host: {host}")
        
        # Extract subdomain from backend host
        parts = host.split('.')
        subdomain = parts[0] if parts else 'rudhra'
        
        print(f"📌 Subdomain: {subdomain}")
        
        # Map backend subdomain to frontend URL
        if subdomain == 'prod':
            frontend_url = 'https://prod.cnlerp.com'
        elif subdomain == 'rudhra':
            frontend_url = 'https://rudhra.cnlerp.com'
        elif subdomain == 'qa':
            frontend_url = 'https://qa.cnlerp.com'
        elif 'localhost' in host or '127.0.0.1' in host:
            frontend_url = 'http://localhost:4200'
        else:
            frontend_url = f"https://{subdomain}.cnlerp.com"
        
        print(f"🏠 Frontend URL: {frontend_url}")
        return frontend_url
    
    def validate(self, attrs):
        username = attrs.get('username')
        
        try:
            # Find customer by username
            customer = Customer.objects.filter(
                username__iexact=username,
                is_deleted=False,
                is_portal_user=True
            ).first()
            
            if not customer:
                raise serializers.ValidationError("No customer found with this username")
            
            # Get customer contact details
            customer_address = CustomerAddresses.objects.filter(
                customer_id=customer.customer_id,
                is_deleted=False
            ).first()
            
            if not customer_address:
                raise serializers.ValidationError("No contact details found for this customer")
            
            # Store details
            self.context['customer'] = customer
            self.context['customer_id'] = customer.customer_id
            self.context['customer_name'] = customer.name
            self.context['customer_username'] = customer.username
            self.context['customer_email'] = customer_address.email
            self.context['customer_phone'] = customer_address.phone
            
            print(f"🔍 Customer found: {customer.name}")
            print(f"   Email: {customer_address.email or 'Not found'}")
            print(f"   Phone: {customer_address.phone or 'Not found'}")
            
        except Exception as e:
            raise serializers.ValidationError(f"Error: {str(e)}")
        
        return attrs
    
    def save(self, **kwargs):
        """Create reset token and send via available channel"""
        customer_id = self.context.get('customer_id')
        customer_name = self.context.get('customer_name')
        customer_username = self.context.get('customer_username')
        customer_email = self.context.get('customer_email')
        customer_phone = self.context.get('customer_phone')
        request = self.context.get('request')
        
        # Delete existing unused tokens
        CustomerPasswordReset.objects.filter(
            customer_id=customer_id,
            is_used=False,
            expires_at__gt=timezone.now()
        ).delete()
        
        # Create new reset token
        token = uuid.uuid4()
        expires_at = timezone.now() + timedelta(hours=24)
        
        reset_token = CustomerPasswordReset.objects.create(
            customer_id=customer_id,
            token=token,
            expires_at=expires_at,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT')
        )
        
        # ✅ Get frontend URL using same pattern as reference method
        frontend_url = self._get_frontend_url(request)
        reset_link = f"{frontend_url}/#/customer-portal/reset-password/{token}/"
        
        print(f"🔗 Reset link: {reset_link}")
        
        # Logic: Email first, WhatsApp as fallback
        if customer_email and customer_email.strip():
            print(f"📧 Email found, sending reset link to {customer_email}")
            self._send_reset_email(
                customer_name=customer_name,
                customer_username=customer_username,
                email=customer_email,
                reset_link=reset_link
            )
            self.context['sent_via'] = 'email'
            
        elif customer_phone and customer_phone.strip():
            print(f"📱 No email found, sending WhatsApp to {customer_phone}")
            success = self._send_reset_whatsapp_via_wati(
                customer_name=customer_name,
                phone=customer_phone,
                reset_link=reset_link,
                token=token
            )
            
            if success:
                self.context['sent_via'] = 'whatsapp'
            else:
                raise serializers.ValidationError(
                    "Unable to send reset link. WhatsApp delivery failed. Please contact support."
                )
        else:
            raise serializers.ValidationError(
                "No email or phone number found. Please contact support."
            )
        
        return reset_token
    
    def _send_reset_email(self, customer_name, customer_username, email, reset_link):
        """Send password reset email"""
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = "Reset Your Customer Portal Password"
        message = f"""
        Hello {customer_name},
        
        You requested to reset your password for the Customer Portal.
        
        Username: {customer_username}
        
        Click the link below to set a new password:
        
        {reset_link}
        
        This link is valid for 24 hours.
        
        If you didn't request this, please ignore this email.
        
        Thanks,
        ERP Support Team
        """
        
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
        print(f"✅ Password reset email sent to {customer_name} ({email})")
    
    def _send_reset_whatsapp_via_wati(self, customer_name, phone, reset_link, token):
        """
        Send password reset link via WATI using utility template
        """
        try:
            # Clean phone number
            clean_phone = re.sub(r'\D', '', phone)
            if len(clean_phone) == 10:
                clean_phone = '91' + clean_phone
            
            print(f"📱 Clean phone: {phone} -> {clean_phone}")
            print(f"🔗 Reset link: {reset_link}")
            
            # Headers
            auth_headers = {
                'Authorization': self.WATI_TOKEN,
                'Content-Type': 'application/json'
            }
            
            # Step 1: Add contact
            try:
                add_response = requests.post(
                    f"https://live-mt-server.wati.io/{self.WATI_INSTANCE_ID}/api/v1/addContact/{clean_phone}",
                    headers=auth_headers,
                    json={"name": customer_name or "Customer"},
                    timeout=30
                )
                print(f"📞 Add contact response: {add_response.status_code}")
            except Exception as e:
                print(f"⚠️ Add contact error: {e}")
            
            # Step 2: Send template message
            template_payload = {
                "template_name": "password_reset",
                "broadcast_name": f"password_reset_{clean_phone}_{int(timezone.now().timestamp())}",
                "parameters": [
                    {"name": "1", "value": customer_name},
                    {"name": "2", "value": reset_link},
                    {"name": "3", "value": "24"}
                ]
            }
            
            print(f"📨 Sending WhatsApp template")
            print(f"   Template: password_reset")
            print(f"   Phone: {clean_phone}")
            print(f"   Parameters: {template_payload['parameters']}")
            
            response = requests.post(
                f"https://live-mt-server.wati.io/{self.WATI_INSTANCE_ID}/api/v1/sendTemplateMessage?whatsappNumber={clean_phone}",
                headers=auth_headers,
                json=template_payload,
                timeout=30
            )
            
            print(f"📨 Response status: {response.status_code}")
            print(f"📨 Response body: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('result'):
                    print(f"✅ WhatsApp template sent successfully!")
                    print(f"   Message ID: {result.get('messageId', 'N/A')}")
                    return True
                else:
                    print(f"❌ Template failed: {result.get('info', 'Unknown error')}")
                    return False
            else:
                print(f"❌ WhatsApp failed: {response.status_code}")
                return False
            
        except Exception as e:
            print(f"❌ WATI error: {str(e)}")
            return False

class CustomerPasswordResetSerializer(serializers.Serializer):
    """Serializer for resetting customer password using token"""
    new_password = serializers.CharField(max_length=100, min_length=6, required=True)
    confirm_password = serializers.CharField(max_length=100, required=True)
    
    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        
        if new_password != confirm_password:
            raise serializers.ValidationError("Passwords do not match")
        
        if len(new_password) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters")
        
        return attrs
    
    def save(self, **kwargs):
        """Reset customer password"""
        token = self.context.get('token')
        
        try:
            # ✅ Find the reset token by token UUID
            reset_token = CustomerPasswordReset.objects.get(
                token=token,
                is_used=False
            )
            
            # Check if token is expired
            if not reset_token.is_valid():
                raise serializers.ValidationError("Reset link has expired")
            
            # ✅ Get customer by customer_id (UUID field)
            customer = Customer.objects.get(
                customer_id=reset_token.customer_id,
                is_deleted=False
            )
            
            # Update password
            new_password = self.validated_data.get('new_password')
            customer.password = make_password(new_password)
            customer.save()
            
            # Mark token as used
            reset_token.is_used = True
            reset_token.save()
            
            # Send confirmation email
            self._send_confirmation_email(customer)
            
            return customer
            
        except CustomerPasswordReset.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired reset link")
        except Customer.DoesNotExist:
            raise serializers.ValidationError("Customer not found")
    
    def _send_confirmation_email(self, customer):
        """Send confirmation that password was changed"""
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = "Your Customer Portal Password Has Been Changed"
        message = f"""
        Hello {customer.name},
        
        Your customer portal password has been successfully changed.
        
        If you did not make this change, please contact our support team immediately.
        
        Thanks,
        ERP Support Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [customer.email],
            fail_silently=True,
        )