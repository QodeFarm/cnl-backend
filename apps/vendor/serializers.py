from apps.finance.models import JournalEntryLines, PaymentTransaction
from apps.masters.serializers import ModFirmStatusesSerializers, ModTerritorySerializers, ModGstCategoriesSerializers, ModTransportersSerializers, ModPriceCategoriesSerializers, ModCitySerializer,ModStateSerializer, ModCountrySerializer
from apps.customer.serializers import ModLedgerAccountsSerializers
from rest_framework import serializers

from apps.sales.models import PaymentTransactions
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
    picture = PictureSerializer(required=False, allow_null=True, many=True)

    class Meta:
        model = Vendor
        fields = '__all__'

class VendorsOptionsSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    vendor_addresses = serializers.SerializerMethodField()
    vendor_category = serializers.SerializerMethodField() 
    ledger_account = serializers.SerializerMethodField() 
    city = serializers.SerializerMethodField() 

    class Meta:
        model = Vendor
        fields = ['vendor_id', 'name', 'phone', 'email', 'city', 'gst_no', 'vendor_category', 'ledger_account', 'created_at','vendor_addresses', 'updated_at'] 

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
    
    # def get_ledger_account(self, obj):
    #     print("-"*20)
    #     print("obj : ", obj)
    #     print("-"*20)
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

    
    def get_vendor_category(self, obj):
        if obj.vendor_category_id:
            return ModVendorCategorySerializer(obj.vendor_category_id).data
        return None
    
    def get_vendors_summary(vendors):
        serializer = VendorsOptionsSerializer(vendors, many=True)
        return serializer.data

class VendorSummaryReportSerializer(serializers.ModelSerializer):
    """
    Serializer for Vendor Summary Report showing total purchases and pending payments.
    """
    total_purchases = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    total_paid = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    total_pending = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    last_purchase_date = serializers.DateField(read_only=True)
    phone = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    
    class Meta:
        model = Vendor
        fields = ['vendor_id', 'name', 'total_purchases', 'total_paid', 'total_pending', 
                 'last_purchase_date', 'phone', 'email', 'gst']
    
    def get_phone(self, obj):
        """Get the vendor's phone number from addresses"""
        address = obj.vendoraddress_set.filter(phone__isnull=False).first()
        return address.phone if address else None
    
    def get_email(self, obj):
        """Get the vendor's email from addresses"""
        address = obj.vendoraddress_set.filter(email__isnull=False).first()
        return address.email if address else None

class VendorOutstandingReportSerializer(serializers.ModelSerializer):
    """
    Serializer for Vendor Outstanding Report showing pending dues to vendors.
    """
    total_purchases = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    total_paid = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    total_pending = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    last_purchase_date = serializers.DateField(read_only=True)
    phone = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    
    class Meta:
        model = Vendor
        fields = ['vendor_id', 'name', 'total_purchases', 'total_paid', 'total_pending', 
                 'last_purchase_date', 'phone', 'email', 'gst']
    
    def get_phone(self, obj):
        """Get the vendor's phone number from addresses"""
        address = obj.vendoraddress_set.filter(phone__isnull=False).first()
        return address.phone if address else None
    
    def get_email(self, obj):
        """Get the vendor's email from addresses"""
        address = obj.vendoraddress_set.filter(email__isnull=False).first()
        return address.email if address else None

class VendorLedgerReportSerializer(serializers.ModelSerializer):
    """
    Serializer for Vendor Ledger Report that tracks all financial transactions with a vendor.
    This includes purchases, payments, and any other debit/credit transactions.
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
        fields = [
            'journal_entry_line_id',
            'transaction_date',
            'reference_number',
            'description',
            'debit',
            'credit',
            'running_balance',
            'transaction_type'
        ]
    
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
        if 'PO-' in reference:
            return 'Purchase Order'
        elif 'PI-' in reference or 'PINV-' in reference:
            return 'Purchase Invoice'
        elif 'PR-' in reference:
            return 'Purchase Return'
        elif 'CN-' in reference:
            return 'Credit Note'  
        elif 'DN-' in reference:
            return 'Debit Note'
        elif 'PMT-' in reference:
            return 'Payment'
        else:
            return 'Other'

class VendorPerformanceReportSerializer(serializers.ModelSerializer):
    """
    Serializer for Vendor Performance Report analyzing delivery and service quality.
    """
    total_orders = serializers.IntegerField(read_only=True)
    on_time_deliveries = serializers.IntegerField(read_only=True)
    delayed_deliveries = serializers.IntegerField(read_only=True)
    on_time_percentage = serializers.FloatField(read_only=True)
    average_delay_days = serializers.FloatField(read_only=True)
    rejected_items_count = serializers.IntegerField(read_only=True)
    quality_rating = serializers.FloatField(read_only=True)
    last_order_date = serializers.DateField(read_only=True)
    phone = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    
    class Meta:
        model = Vendor
        fields = ['vendor_id', 'name', 'total_orders', 'on_time_deliveries', 'delayed_deliveries', 
                 'on_time_percentage', 'average_delay_days', 'rejected_items_count', 
                 'quality_rating', 'last_order_date', 'phone', 'email']
    
    def get_phone(self, obj):
        """Get the vendor's phone number from addresses"""
        address = obj.vendoraddress_set.filter(phone__isnull=False).first()
        return address.phone if address else None
    
    def get_email(self, obj):
        """Get the vendor's email from addresses"""
        address = obj.vendoraddress_set.filter(email__isnull=False).first()
        return address.email if address else None

class VendorPaymentReportSerializer(serializers.ModelSerializer):
    """
    Serializer for Vendor Payment Report showing payments made to vendors.
    """
    payment_id = serializers.UUIDField()
    payment_date = serializers.DateField()
    payment_amount = serializers.DecimalField(source='amount', max_digits=15, decimal_places=2)
    payment_method = serializers.CharField()
    payment_status = serializers.CharField()
    reference_number = serializers.CharField()
    invoice_id = serializers.CharField()
    vendor_name = serializers.SerializerMethodField()
    vendor_gst = serializers.SerializerMethodField()
    notes = serializers.CharField()
    
    class Meta:
        model = PaymentTransaction
        fields = ['payment_id', 'payment_date', 'payment_amount', 'payment_method', 'payment_status', 'reference_number', 'invoice_id', 'vendor_name', 'vendor_gst', 'notes']
    
    def get_vendor_name(self, obj):
        """Get vendor name based on invoice_id"""
        from apps.purchase.models import PurchaseInvoiceOrders
        if obj.order_type == 'Purchase':
            try:
                purchase_invoice = PurchaseInvoiceOrders.objects.filter(
                    purchase_invoice_id=obj.invoice_id
                ).select_related('vendor_id').first()
                if purchase_invoice and purchase_invoice.vendor_id:
                    return purchase_invoice.vendor_id.name
            except Exception:
                pass
        return "Unknown Vendor"
    
    def get_vendor_gst(self, obj):
        """Get vendor GST based on invoice_id"""
        from apps.purchase.models import PurchaseInvoiceOrders
        if obj.order_type == 'Purchase':
            try:
                purchase_invoice = PurchaseInvoiceOrders.objects.filter(
                    purchase_invoice_id=obj.invoice_id
                ).select_related('vendor_id').first()
                if purchase_invoice and purchase_invoice.vendor_id:
                    return purchase_invoice.vendor_id.gst
            except Exception:
                pass
        return "N/A"