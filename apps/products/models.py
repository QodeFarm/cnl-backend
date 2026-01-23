import os,uuid
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from apps.inventory.models import WarehouseLocations, Warehouses
from config.utils_methods import *
from config.utils_variables import *
from config.utils_methods import OrderNumberMixin
from apps.masters.models import GPackageUnit, ItemMaster, PackageUnit, ProductUniqueQuantityCodes,ProductTypes,UnitOptions,ProductItemType,ProductDrugTypes,ProductBrands

def product_groups_picture(instance, filename):
    # Get the file extension
    file_extension = os.path.splitext(filename)[-1]
 
    # Generate a unique identifier
    unique_id = uuid.uuid4().hex[:6]
 
    # Construct the filename
    #branch_name = instance.name.replace(' ', '_')
    original_filename = os.path.splitext(filename)[0]  # Get the filename without extension
    return f"products/product_groups/{original_filename}_{unique_id}{file_extension}"

# Create your models here.
class ProductGroups(models.Model):
    product_group_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group_name = models.CharField(max_length=255)
    description = models.TextField(null=True, default=None)
    picture = models.ImageField(max_length=255, null=True, default=None, upload_to=product_groups_picture)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = productgroupstable

    def __str__(self):
        return f"{self.product_group_id} {self.group_name}"

    @receiver(pre_delete, sender='products.ProductGroups')
    def delete_branches_picture(sender, instance, **kwargs):
        if instance.picture and instance.picture.name:
            file_path = instance.picture.path
            if os.path.exists(file_path):
                os.remove(file_path)
                picture_dir = os.path.dirname(file_path)
                if not os.listdir(picture_dir):
                    os.rmdir(picture_dir)


def product_categories_picture(instance, filename):
    # Get the file extension
    file_extension = os.path.splitext(filename)[-1]
 
    # Generate a unique identifier
    unique_id = uuid.uuid4().hex[:6]
 
    # Construct the filename
    #branch_name = instance.name.replace(' ', '_')
    original_filename = os.path.splitext(filename)[0]  # Get the filename without extension
    return f"products/product_categories/{original_filename}_{unique_id}{file_extension}"

class ProductCategories(models.Model):
    category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category_name = models.CharField(max_length=255)
    picture = models.ImageField(max_length=255,  null=True, default=None, upload_to=product_categories_picture)
    code = models.CharField(max_length=50, null=True, default=None)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = productcategoriestable

    def __str__(self):
        return f"{self.category_id} {self.category_name}"

    @receiver(pre_delete, sender='products.ProductCategories')
    def delete_branches_picture(sender, instance, **kwargs):
        if instance.picture and instance.picture.name:
            file_path = instance.picture.path
            if os.path.exists(file_path):
                os.remove(file_path)
                picture_dir = os.path.dirname(file_path)
                if not os.listdir(picture_dir):
                    os.rmdir(picture_dir)


class ProductStockUnits(models.Model):
    stock_unit_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stock_unit_name = models.CharField(max_length=255)
    description = models.TextField(null=True, default=None)
    quantity_code_id = models.ForeignKey(ProductUniqueQuantityCodes, on_delete=models.PROTECT, null=True, default=None, db_column = 'quantity_code_id')
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = productstockunitstable

    def __str__(self):
        return f"{self.stock_unit_id} {self.stock_unit_name}"


class ProductGstClassifications(models.Model):
    gst_classification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    TYPE_CHOICES = [ 
        ('HSN', 'HSN'),
        ('SAC', 'SAC'),
        ('Both','Both'),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, null=True, default=None)
    code = models.CharField(max_length=50, null=True, default=None)
    hsn_or_sac_code = models.CharField(max_length=50, null=True, default=None)
    hsn_description = models.TextField(null=True, default=None)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = productgstclassificationstable

    def __str__(self):
        return f"{self.gst_classification_id} {self.code}"


class ProductSalesGl(models.Model):
    sales_gl_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    sales_accounts = models.CharField(max_length=255, null=True, default=None)
    code = models.CharField(max_length=50, null=True, default=None)
    is_subledger = models.BooleanField(null=True, default=None)
    inactive = models.BooleanField(null=True, default=None)
    type = models.CharField(max_length=255, null=True, default=None)
    account_no = EncryptedTextField(max_length=255, null=True, default=None)
    rtgs_ifsc_code = models.CharField(max_length=255, null=True, default=None)
    classification = models.CharField(max_length=255, null=True, default=None)
    is_loan_account = models.BooleanField(null=True, default=None)
    tds_applicable = models.BooleanField(null=True, default=None)
    address = models.CharField(max_length=255, null=True, default=None)
    pan = models.CharField(max_length=50, null=True, default=None)
    employee = models.BooleanField(null=True, default=None)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = productsalesgltable

    def __str__(self):
        return f"{self.sales_gl_id} {self.name}"

class ProductPurchaseGl(models.Model):
    purchase_gl_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    purchase_accounts = models.CharField(max_length=255, null=True, default=None)
    code = models.CharField(max_length=50, null=True, default=None)
    is_subledger = models.BooleanField(null=True, default=None)
    inactive = models.BooleanField(null=True, default=None)
    type = models.CharField(max_length=255, null=True, default=None)
    account_no = EncryptedTextField(max_length=255, null=True, default=None)
    rtgs_ifsc_code = models.CharField(max_length=255, null=True, default=None)
    classification = models.CharField(max_length=255, null=True, default=None)
    is_loan_account = models.BooleanField(null=True, default=None)
    tds_applicable = models.BooleanField(null=True, default=None)
    address = models.CharField(max_length=255, null=True, default=None)
    pan = models.CharField(max_length=50, null=True, default=None)
    employee = models.BooleanField(null=True, default=None)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_purchase_gl'

    def __str__(self):
        return f"{self.purchase_gl_id} {self.name}"


def products_picture(instance, filename):
    # Get the file extension
    file_extension = os.path.splitext(filename)[-1]
 
    # Generate a unique identifier
    unique_id = uuid.uuid4().hex[:6]
 
    # Construct the filename
    #branch_name = instance.name.replace(' ', '_')
    original_filename = os.path.splitext(filename)[0]  # Get the filename without extension
    return f"products/products/{original_filename}_{unique_id}{file_extension}"

class Products(OrderNumberMixin):
    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    product_mode_id = models.ForeignKey(ItemMaster, on_delete=models.PROTECT, null=True, default=None, db_column='product_mode_id')
    product_group_id = models.ForeignKey(ProductGroups, null=True,on_delete=models.PROTECT, db_column = 'product_group_id')
    category_id = models.ForeignKey(ProductCategories, on_delete=models.PROTECT, null=True, default=None, db_column = 'category_id')
    type_id = models.ForeignKey(ProductTypes, on_delete=models.PROTECT, null=True, default=None, db_column = 'type_id')
    code = models.CharField(max_length=50,null=True,)
    order_no_prefix = 'PRD'
    order_no_field = 'code'
    barcode = models.CharField(max_length=50, null=True, default=None)
    unit_options_id = models.ForeignKey(UnitOptions, on_delete=models.PROTECT, null=True, default=None, db_column = 'unit_options_id')
    gst_input = models.IntegerField(null=True, default=None)
    stock_unit_id = models.ForeignKey(ProductStockUnits, on_delete=models.PROTECT, null=True, db_column = 'stock_unit_id')
    print_barcode = models.BooleanField(null=True, default=None)
    gst_classification_id = models.ForeignKey(ProductGstClassifications, on_delete=models.PROTECT, null=True, default=None, db_column = 'gst_classification_id')
    picture = models.JSONField(null=True, default=None)
    sales_description = models.TextField(null=True, default=None)
    sales_gl_id = models.ForeignKey(ProductSalesGl,null=True, on_delete=models.PROTECT, db_column = 'sales_gl_id')
    mrp = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    minimum_price = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    sales_rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    wholesale_rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    dealer_rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    rate_factor = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    discount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    dis_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    purchase_description = models.TextField(null=True, default=None)
    purchase_gl_id = models.ForeignKey(ProductPurchaseGl, on_delete=models.PROTECT,null=True, db_column = 'purchase_gl_id')
    purchase_rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    purchase_rate_factor = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    purchase_discount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    item_type_id = models.ForeignKey(ProductItemType, on_delete=models.PROTECT, null=True, default=None, db_column = 'item_type_id')
    minimum_level = models.IntegerField(null=True, default=None)
    maximum_level = models.IntegerField(null=True, default=None)
    salt_composition = models.TextField(null=True, default=None)
    drug_type_id = models.ForeignKey(ProductDrugTypes, on_delete=models.PROTECT, null=True, default=None, db_column = 'drug_type_id')
    weighscale_mapping_code = models.CharField(max_length=50, null=True, default=None)
    brand_id = models.ForeignKey(ProductBrands, on_delete=models.PROTECT, null=True, default=None, db_column = 'brand_id')
    purchase_warranty_months = models.IntegerField(null=True, default=None)
    sales_warranty_months = models.IntegerField(null=True, default=None)
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, null=True, default=None)
    print_name = models.CharField(max_length=255)
    hsn_code= models.CharField(max_length=15, null=True, default=None)
    balance = models.IntegerField(default=0)
    physical_balance = models.IntegerField(default=0)
    balance_diff = models.IntegerField(default=0)
    pack_unit_id = models.ForeignKey(ProductStockUnits, on_delete=models.PROTECT, null=True, default=None, db_column = 'pack_unit_id', related_name='pack_unit')
    g_pack_unit_id = models.ForeignKey(ProductStockUnits, on_delete=models.PROTECT, null=True, default=None, db_column = 'g_pack_unit_id', related_name='g_pack_unit')
    pack_vs_stock = models.IntegerField(default=0)
    g_pack_vs_pack = models.IntegerField(default=0)
    packet_barcode = models.CharField(max_length=50, null=True, default=None)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = productstable

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        from apps.masters.views import increment_order_number
        """
        Override save to ensure the order number is only generated on creation, not on updates.
        """
        # Determine if this is a new record based on the `adding` state
        is_new_record = self._state.adding

        # Only generate and set the order number if this is a new record
        if is_new_record:
            # Generate the order number if it's not already set
            if not getattr(self, self.order_no_field):  # Ensure the order number is not already set
                order_number = generate_order_number(self.order_no_prefix)
                setattr(self, self.order_no_field, order_number)
                
        # AUTO CALCULATE BALANCE DIFF
        self.balance_diff = (self.physical_balance or 0) - (self.balance or 0)

        # Save the record
        super().save(*args, **kwargs)

        # After the record is saved, increment the order number sequence only for new records
        if is_new_record:
            print("from create", self.pk)
            increment_order_number(self.order_no_prefix)
        else:
            print("from edit", self.pk)   

class Size(models.Model):
    size_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    size_name = models.CharField(max_length=50, blank=True, null=True)
    size_category = models.CharField(max_length=100)
    size_system = models.CharField(max_length=50, blank=True, null=True)
    length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    size_unit = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = sizes

    def __str__(self):
        return f"{self.size_name} ({self.size_category}, {self.size_system})"


class Color(models.Model):
    color_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    color_name = models.CharField(max_length=50, unique=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    

    class Meta:
        db_table = colors

    def __str__(self):
        return self.color_name

class ProductVariation(models.Model):
    product_variation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_id = models.ForeignKey(Products, on_delete=models.PROTECT, db_column = 'product_id', related_name='locations')
    size_id = models.ForeignKey(Size, on_delete=models.PROTECT, null=True, default=None, db_column='size_id')
    color_id = models.ForeignKey(Color, on_delete=models.PROTECT, null=True, default=None, db_column='color_id')
    sku = models.CharField(max_length=100, unique=True,null=True,)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True,)
    quantity = models.IntegerField(default=0,null=True,)
    # is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = productvariations

    def __str__(self):
        return f"{self.product_id.name} - {self.size_id.size_name} - {self.color_id.color_name}"

class ProductItemBalance(models.Model):
    product_item_balance_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_id = models.ForeignKey(Products, on_delete=models.PROTECT, db_column='product_id')
    warehouse_location_id = models.ForeignKey(WarehouseLocations, null=True,on_delete=models.PROTECT, db_column='warehouse_location_id')
    quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = productitembalancetable

    def __str__(self):
        return f'{self.warehouse_location_id}'
