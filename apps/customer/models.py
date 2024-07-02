import os
import uuid
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from apps.masters.models import *
from config.utils_methods import EncryptedTextField
from config.utils_variables import *

# Create your models here.

class LedgerAccounts(models.Model):
    TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('Bank', 'Bank'),
        ('Cash', 'Cash'),
    )
    ledger_account_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, null=True, default=None)
    is_subledger = models.BooleanField(default=False, null=True)
    ledger_group_id = models.ForeignKey(LedgerGroups, on_delete=models.CASCADE, db_column='ledger_group_id')
    inactive = models.BooleanField(default=False, null=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=None, null=True)
    account_no = EncryptedTextField(max_length=255, default=None, null=True)
    rtgs_ifsc_code = models.CharField(max_length=50, default=None, null=True)
    classification = models.CharField(max_length=50, default=None, null=True)
    is_loan_account = models.BooleanField(default=False, null=True)
    tds_applicable = models.BooleanField(default=False, null=True)
    address = models.CharField(max_length=255, null=True)
    pan = models.CharField(max_length=50, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):   
        return f"{self.ledger_account_id} {self.name}"
    
    class Meta:
        db_table = ledgeraccountstable 
        
def customer_picture(instance, filename):
    # Get the file extension
    file_extension = os.path.splitext(filename)[-1]
 
    # Generate a unique identifier
    unique_id = uuid.uuid4().hex[:6]
 
    # Construct the filename
    original_filename = os.path.splitext(filename)[0]  # Get the filename without extension
    return f"customers/{original_filename}_{unique_id}{file_extension}"

class Customer(models.Model):
    TAX_CHOICES = [
        ('Inclusive', 'Inclusive'),
        ('Exclusive', 'Exclusive'),
        ('Both', 'Both'),
    ]
    customer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    print_name = models.CharField(max_length=255)
    identification = models.CharField(max_length=255, null=True, default=None)
    code = models.CharField(max_length=50)
    ledger_account_id = models.ForeignKey(LedgerAccounts, on_delete=models.CASCADE, db_column='ledger_account_id')
    customer_common_for_sales_purchase = models.BooleanField(default=False, null=True)
    is_sub_customer = models.BooleanField(default=False, null=True)
    firm_status_id = models.ForeignKey(FirmStatuses, on_delete=models.CASCADE, null=True, default=None, db_column='firm_status_id')
    territory_id = models.ForeignKey(Territory, on_delete=models.CASCADE, null=True, default=None, db_column='territory_id')
    customer_category_id = models.ForeignKey(CustomerCategories, on_delete=models.CASCADE, null=True, default=None, db_column='customer_category_id')
    contact_person = models.CharField(max_length=255, null=True, default=None,)
    picture = models.ImageField(max_length=255, default=None, null=True, upload_to=customer_picture)
    gst = models.CharField(max_length=50, null=True, default=None)
    registration_date = models.DateField(auto_now_add=True, null=True)
    cin = models.CharField(max_length=50, null=True, default=None)
    pan = models.CharField(max_length=50, null=True, default=None)
    gst_category_id = models.ForeignKey(GstCategories, on_delete=models.CASCADE, null=True, default=None, db_column='gst_category_id')
    gst_suspend = models.BooleanField(default=False, null=True)
    tax_type = models.CharField(max_length=10, choices=TAX_CHOICES, default='Inclusive', null=True)
    distance = models.FloatField(null=True, default=None)
    tds_on_gst_applicable = models.BooleanField(default=False, null=True)
    tds_applicable = models.BooleanField(default=False, null=True)
    website = models.CharField(max_length=255, null=True, default=None)
    facebook = models.CharField(max_length=255, null=True, default=None)
    skype = models.CharField(max_length=255, null=True, default=None)
    twitter = models.CharField(max_length=255, null=True, default=None)
    linked_in = models.CharField(max_length=255, null=True, default=None)
    payment_term_id = models.ForeignKey(CustomerPaymentTerms, on_delete=models.CASCADE, null=True, default=None, db_column='payment_term_id')
    price_category_id = models.ForeignKey(PriceCategories, on_delete=models.CASCADE, null=True, default=None, db_column='price_category_id')
    batch_rate_category = models.CharField(max_length=50, null=True, default=None)
    transporter_id = models.ForeignKey(Transporters, on_delete=models.CASCADE, null=True, default=None, db_column='transporter_id')
    credit_limit = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    max_credit_days = models.PositiveIntegerField(null=True, default=None)
    interest_rate_yearly = models.DecimalField(max_digits=5, decimal_places=2, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):   
        return f"{self.name}_{self.customer_id}"
    
    class Meta:
        db_table = customerstable

    @receiver(pre_delete, sender='customer.Customer')
    def delete_branches_picture(sender, instance, **kwargs):
        if instance.picture and instance.picture.name:
            file_path = instance.picture.path
            if os.path.exists(file_path):
                os.remove(file_path)
                picture_dir = os.path.dirname(file_path)
                if not os.listdir(picture_dir):
                    os.rmdir(picture_dir)
                    
class CustomerAttachments(models.Model):
    attachment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='customer_id')
    attachment_name = models.CharField(max_length=255)
    attachment_path = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    
    def __str__(self):
        return f"{self.attachment_id} {self.attachment_name}"
    
    class Meta:
        db_table = customerattachmentstable
    
        
class CustomerAddresses(models.Model):
    ADDRESS_CHOICE = [
        ('Billing', 'Billing'),
        ('Shipping', 'Shipping')
    ]
    customer_address_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='customer_id')
    address_type = models.CharField(max_length=10, choices=ADDRESS_CHOICE, null=True, default=None)
    address = models.CharField(max_length=255, null=True, default=None)
    city_id = models.ForeignKey(City, on_delete=models.CASCADE, db_column='city_id')
    state_id = models.ForeignKey(State, on_delete=models.CASCADE, db_column='state_id')
    country_id = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, default=None, db_column='country_id')
    pin_code = models.CharField(max_length=50, null=True, default=None)
    phone = models.CharField(max_length=50, null=True, default=None)
    email= models.CharField(max_length=255, null=True, default=None)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, default=None)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, default=None)
    route_map = models.CharField(max_length=255, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
    
    def __str__(self):
        return f"{self.customer_address_id}"
    
    class Meta:
        db_table = customeraddressestable

    
