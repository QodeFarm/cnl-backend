import os
import uuid
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from config.utils_methods import *
from config.utils_variables import *
from django.core.validators import RegexValidator

# Create your models here.
class Country(models.Model):
    country_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=100, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.country_name
    
    class Meta:
        db_table = countrytable

class State(models.Model):
    state_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country_id = models.ForeignKey(Country, on_delete=models.CASCADE, db_column = 'country_id')
    state_name = models.CharField(max_length=100)
    state_code = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.state_name
    
    class Meta:
        db_table = statetable

class City(models.Model):
    city_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state_id = models.ForeignKey(State, on_delete=models.CASCADE, db_column = 'state_id')
    city_name = models.CharField(max_length=100)
    city_code = models.CharField(max_length=100, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.city_name
    
    class Meta:
        db_table = citytable


class Statuses(models.Model):
    status_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status_name = models.CharField(max_length=50, unique=True, default='Pending')

    def __str__(self):
        return f"{self.status_name}"
    
    class Meta:
        db_table = statusestable


class LedgerGroups(models.Model):
    ledger_group_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, null=True, default=None)
    inactive = models.BooleanField(default=False, null=True)
    under_group = models.CharField(max_length=255, null=True, default=None)
    nature = models.CharField(max_length=255, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):   
        return f"{self.ledger_group_id} {self.name}"
    
    class Meta:
        db_table = ledgergroupstable
        
class FirmStatuses(models.Model):
    firm_status_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):   
        return f"{self.firm_status_id} {self.name}"
    
    class Meta:
        db_table = firmstatusestable

class Territory(models.Model):
    territory_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.territory_id} {self.name}"
    
    class Meta:
        db_table = territoriestable

class CustomerCategories(models.Model):
    customer_category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.customer_category_id} {self.name}"
    
    class Meta:
        db_table = customercategoriestable

class GstCategories(models.Model):
    gst_category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.gst_category_id} {self.name}"
    
    class Meta:
        db_table = gstcategoriestable

class CustomerPaymentTerms(models.Model):
    payment_term_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, null=True, default=None)
    fixed_days = models.PositiveIntegerField(null=True, default=None)
    no_of_fixed_days = models.PositiveIntegerField(null=True, default=None)
    payment_cycle = models.CharField(max_length=255, null=True, default=None)
    run_on = models.CharField(max_length=255, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.payment_term_id} {self.name}"
    
    class Meta:
        db_table = customerpaymenttermstable

class PriceCategories(models.Model):
    price_category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.price_category_id} {self.name}"
    
    class Meta:
        db_table = pricecategoriestable

class Transporters(models.Model):
    transporter_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, null=True,default=None)
    gst_no = models.CharField(max_length=50, null=True,default=None)
    website_url = models.CharField(max_length=255, null=True,default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.transporter_id} {self.name}"
    
    class Meta:
        db_table = transportertable

class ProductTypes(models.Model):
    type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = producttypestable

    def __str__(self):
        return f"{self.type_id} {self.type_name}"

class ProductUniqueQuantityCodes(models.Model):
    quantity_code_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quantity_code_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = productuniquequantitycodestable

    def __str__(self):
        return f"{self.quantity_code_id} {self.quantity_code_name}"

class UnitOptions(models.Model):
    unit_options_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    unit_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = unitoptionstable

    def __str__(self):
        return f"{self.unit_options_id} {self.unit_name}"

class ProductDrugTypes(models.Model):
    drug_type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    drug_type_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = productdrugtypestable

    def __str__(self):
        return f"{self.drug_type_id} {self.drug_type_name}"

class ProductItemType(models.Model):
    item_type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = productitemtypetable

    def __str__(self):
        return f"{self.item_type_id} {self.item_name}"

class BrandSalesman(models.Model):
    brand_salesman_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, null=True, default=None)
    name = models.CharField(max_length=255)
    commission_rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    RATE_ON_CHOICES = [ 
        ('Qty', 'Qty'),
        ('Amount', 'Amount'),
        ('Both','Both'),
    ]
    rate_on = models.CharField(max_length=10, choices=RATE_ON_CHOICES, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = brandsalesmantable

    def __str__(self):
        return f"{self.brand_salesman_id} {self.name}"


def product_brands_picture(instance, filename):
    # Get the file extension
    file_extension = os.path.splitext(filename)[-1]
 
    # Generate a unique identifier
    unique_id = uuid.uuid4().hex[:6]
 
    # Construct the filename
    #branch_name = instance.name.replace(' ', '_')
    original_filename = os.path.splitext(filename)[0]  # Get the filename without extension
    return f"products/product_brands/{original_filename}_{unique_id}{file_extension}"

class ProductBrands(models.Model):
    brand_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand_name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, null=True, default=None)
    picture = models.ImageField(max_length=255, null=True, default=None, upload_to=product_brands_picture)
    brand_salesman_id = models.ForeignKey(BrandSalesman, on_delete=models.CASCADE, null=True, default=None, db_column='brand_salesman_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = productbrandstable

    def __str__(self):
        return f"{self.brand_id} {self.brand_name}"

    @receiver(pre_delete, sender='masters.ProductBrands')
    def delete_branches_picture(sender, instance, **kwargs):
        if instance.picture and instance.picture.name:
            file_path = instance.picture.path
            if os.path.exists(file_path):
                os.remove(file_path)
                picture_dir = os.path.dirname(file_path)
                if not os.listdir(picture_dir):
                    os.rmdir(picture_dir)


class PurchaseTypes(models.Model):
    purchase_type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.purchase_type_id} {self.name}"
    
    class Meta:
        db_table = purchasetypestable

class ShippingCompanies(models.Model):
    shipping_company_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=255,null=True,default=None)
    name = models.CharField(max_length=255,null=True,default=None)
    gst_no = models.CharField(max_length=255,null=True,default=None)
    website_url = models.CharField(max_length=255,null=True,default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'
    
    class Meta:
        db_table = shippingcompanies

class GstTypes(models.Model):
    gst_type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255,null=True,default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = gsttypes

class SaleTypes(models.Model):
    sale_type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255,null=True,default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = saletypes

class ShippingModes(models.Model):
    shipping_mode_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255,null=True,default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'
    
    class Meta:
        db_table = shippingmodes

class OrdersSalesman(models.Model):
    order_salesman_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, null=True, default=None)
    name = models.CharField(max_length=255)
    commission_rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    ORDER_RATE_CHOICES = [('Qty', 'Quantity'),('Amount', 'Amount'),]
    rate_on = models.CharField(max_length=6, choices=ORDER_RATE_CHOICES, null=True, default=None)
    AMOUNT_TYPE_CHOICES = [('Taxable', 'Taxable'),('BillAmount', 'Bill Amount'),]
    amount_type = models.CharField(max_length=10, choices=AMOUNT_TYPE_CHOICES, null=True, default=None)
    email = models.EmailField(max_length=255, null=True, default=None)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=20, default=None, null=True)  # validators should be a list
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = orderssalesmantable

class PaymentLinkTypes(models.Model):
    payment_link_type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, null=True,default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = paymentlinktable

    def __str__(self):
        return self.name

class OrderStatuses(models.Model):
    order_status_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status_name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, null=True,default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = orderstatusestable

    def __str__(self):
        return self.status_name
    
class OrderTypes(models.Model):
    order_type_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = ordertypestable

    def __str__(self):
        return self.name
    
class TaskPriorities(models.Model):
    priority_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    priority_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.priority_id} {self.priority_name}"
    
    class Meta:
        db_table = taskprioritiestable
