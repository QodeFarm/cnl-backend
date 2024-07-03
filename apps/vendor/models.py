from django.db import models
from apps.customer.models import LedgerAccounts
from apps.masters.models import FirmStatuses, GstCategories, PriceCategories, Territory, Transporters
from config.utils_variables import vendorcategory, vendorpaymentterms, vendoragent, vendor, vendorattachments, vendoraddresses
from config.utils_methods import custom_upload_to, EncryptedTextField
import uuid

# Create your models here.
    
class VendorCategory(models.Model): #required fields are updated
    vendor_category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, null=True, default=None)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.vendor_category_id}_{self.name} ({self.code})'

    class Meta:
        db_table = vendorcategory


class VendorPaymentTerms(models.Model):
    payment_term_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, null=True, default=None)
    fixed_days = models.IntegerField(null=True, default=None)
    no_of_fixed_days = models.IntegerField(null=True, default=None)
    payment_cycle = models.CharField(max_length=255, null=True, default=None)
    run_on = models.CharField(max_length=255, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.payment_term_id}_{self.name} ({self.code})'
    
    class Meta:
        db_table = vendorpaymentterms


class VendorAgent(models.Model):
    vendor_agent_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, null=True, default=None)
    name = models.CharField(max_length=255)
    commission_rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    
    RATE_ON_CHOICES = [
        ('Qty', 'Quantity'),
        ('Amount', 'Amount'),
    ]
    rate_on = models.CharField(max_length=20, choices=RATE_ON_CHOICES, null=True, default=None)
    
    AMOUNT_TYPE_CHOICES = [
        ('Taxable', 'Taxable'),
        ('BillAmount', 'Bill Amount'),
    ]
    amount_type = models.CharField(max_length=20, choices=AMOUNT_TYPE_CHOICES, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.vendor_agent_id}_{self.name} ({self.code})'
    
    class Meta:
        db_table = vendoragent


class Vendor(models.Model):
    vendor_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gst_no = models.CharField(max_length=255, null=True, default=None)
    name = models.CharField(max_length=255)
    print_name = models.CharField(max_length=255)
    identification = models.CharField(max_length=255, null=True, default=None)
    code = models.CharField(max_length=255)
    ledger_account_id = models.ForeignKey(LedgerAccounts, on_delete=models.CASCADE, db_column='ledger_account_id')
    vendor_common_for_sales_purchase = models.BooleanField(null=True, default=None)
    is_sub_vendor = models.BooleanField(null=True, default=None)
    firm_status_id = models.ForeignKey(FirmStatuses, on_delete=models.CASCADE, null=True, default=None, db_column='firm_status_id')
    territory_id = models.ForeignKey(Territory,  on_delete=models.CASCADE,null=True, default=None, db_column='territory_id')
    vendor_category_id = models.ForeignKey(VendorCategory, on_delete=models.CASCADE, null=True, default=None, db_column='vendor_category_id')
    contact_person = models.CharField(max_length=255, null=True, default=None)
    picture = models.CharField(max_length=255, null=True, default=None)
    gst = models.CharField(max_length=255, null=True, default=None)
    registration_date = models.DateField(null=True, default=None)
    cin = models.CharField(max_length=255, null=True, default=None)
    pan = models.CharField(max_length=255, null=True, default=None)
    gst_category_id = models.ForeignKey(GstCategories, on_delete=models.CASCADE, null=True, default=None, db_column='gst_category_id')
    gst_suspend = models.BooleanField(null=True, default=None)
    TAX_TYPE_CHOICES = [('Inclusive', 'Inclusive'),
                        ('Exclusive', 'Exclusive')
                        ]
    tax_type = models.CharField(max_length=20, choices=TAX_TYPE_CHOICES , default= 'Inclusive')
    distance = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    tds_on_gst_applicable = models.BooleanField(null=True, default=None)
    tds_applicable = models.BooleanField(null=True, default=None)
    website = models.URLField(max_length=255, null=True, default=None)
    facebook = models.URLField(max_length=255, null=True, default=None)
    skype = models.URLField(max_length=255, null=True, default=None)
    twitter = models.URLField(max_length=255, null=True, default=None)
    linked_in = models.URLField(max_length=255, null=True, default=None)
    payment_term_id = models.ForeignKey(VendorPaymentTerms,on_delete=models.CASCADE, null=True, default=None, db_column='payment_term_id')
    price_category_id = models.ForeignKey(PriceCategories, on_delete=models.CASCADE, null=True, default=None, db_column='price_category_id')
    vendor_agent_id = models.ForeignKey(VendorAgent, on_delete=models.CASCADE, null=True, default=None, db_column='vendor_agent_id')
    transporter_id = models.ForeignKey(Transporters, on_delete=models.CASCADE, null=True, default=None, db_column='transporter_id')
    credit_limit = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    max_credit_days = models.IntegerField(null=True, default=None)
    interest_rate_yearly = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    rtgs_ifsc_code = models.CharField(max_length=255, null=True, default=None)
    accounts_number = EncryptedTextField(max_length=255, null=True, default=None)
    bank_name = models.CharField(max_length=255, null=True, default=None)
    branch = models.CharField(max_length=255, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.vendor_id}_{self.name} ({self.code})'

    class Meta:
        db_table = vendor


class VendorAttachment(models.Model):
    attachment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor_id = models.ForeignKey(Vendor, on_delete=models.CASCADE, db_column='vendor_id')
    attachment_name = models.CharField(max_length=255)
    attachment_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = vendorattachments

    def __str__(self):
        return f'{self.attachment_id}_{self.attachment_name}'
    
class VendorAddress(models.Model):
    vendor_address_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor_id = models.ForeignKey(Vendor, on_delete=models.CASCADE, db_column='vendor_id')
    ADDRESS_TYPE_CHOICES = [
        ('Billing', 'Billing'),
        ('Shipping', 'Shipping')
        ]
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, null=True, default=None)
    address = models.CharField(max_length=255, null=True, default=None)
    city_id = models.ForeignKey('masters.City', on_delete=models.CASCADE, db_column = 'city_id')
    state_id = models.ForeignKey('masters.State', on_delete=models.CASCADE, db_column = 'state_id')
    country_id = models.ForeignKey('masters.Country', on_delete=models.CASCADE,null=True, default=None, db_column = 'country_id')
    pin_code = models.CharField(max_length=50, null=True, default=None)
    phone = models.CharField(max_length=50, null=True, default=None)
    email = models.EmailField(max_length=255, null=True, default=None)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, default=None)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, default=None)
    route_map = models.CharField(max_length=255, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = vendoraddresses

    def __str__(self):
        return f'{self.vendor_address_id}_{self.address}'