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
        

class CustomerSerializer(serializers.ModelSerializer):
    ledger_account = ModLedgerAccountsSerializers(source='ledger_account_id', read_only=True)
    firm_status = ModFirmStatusesSerializers(source='firm_status_id', read_only=True)
    territory = ModTerritorySerializers(source='territory_id', read_only=True)
    # picture = PictureSerializer(many=True)
    picture = PictureSerializer(required=False, allow_null=True, many=True)

    customer_category = ModCustomerCategoriesSerializers(source='customer_category_id', read_only=True)
    gst_category = GstCategoriesSerializers(source='gst_category_id', read_only=True)
    payment_term = ModCustomerPaymentTermsSerializers(source='payment_term_id', read_only=True)
    price_category = PriceCategoriesSerializers(source='price_category_id', read_only=True)
    transporter = ModTransportersSerializers(source='transporter_id', read_only=True)
    class Meta:
        model = Customer
        fields = '__all__'  
           
        
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
        fields = ['customer_id', 'name', 'phone', 'email', 'city', 'gst', 'ledger_account', 'created_at', 'customer_addresses', 'credit_limit', 'max_credit_days','pin_code', 'customer_category', 'is_deleted']

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