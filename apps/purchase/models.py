from django.db import models
from config.utils_variables import *
from apps.masters.models import PurchaseTypes,State,ProductBrands, GstTypes, OrderStatuses
from apps.customer.models import LedgerAccounts,CustomerCategories
from apps.vendor.models import Vendor,VendorAgent,VendorAddress,VendorPaymentTerms
from apps.products.models import Products
import uuid
from config.utils_methods import OrderNumberMixin

# Create your models here.
class PurchaseOrders(OrderNumberMixin):
    purchase_order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_type_id = models.ForeignKey(PurchaseTypes, on_delete=models.CASCADE, null=True, default=None, db_column = 'purchase_type_id')
    order_date = models.DateField()
    order_no = models.CharField(max_length=255, unique=True, default='')
    order_no_prefix = 'PO'
    order_no_field = 'order_no'
    gst_type_id = models.ForeignKey(GstTypes, on_delete=models.CASCADE, null=True, default=None, db_column = 'GST_Type_id')
    vendor_id = models.ForeignKey(Vendor, on_delete=models.CASCADE, db_column = 'vendor_id')
    email = models.EmailField(max_length=255, null=True, default=None)
    delivery_date = models.DateField(blank=True, null=True)
    ref_no = models.CharField(max_length=255, null=True, default=None)
    ref_date = models.DateField(blank=True, null=True)
    vendor_agent_id = models.ForeignKey(VendorAgent, on_delete=models.CASCADE, null=True, default=None, db_column = 'vendor_agent_id')
    TAX_CHOICES = [('inclusive', 'Inclusive'),
                   ('exclusive', 'Exclusive')
                ]
    tax = models.CharField(max_length=20, choices=TAX_CHOICES , blank=True, null=True, default=None)
    vendor_address_id = models.ForeignKey(VendorAddress, on_delete=models.CASCADE, null=True, default=None, db_column = 'vendor_address_id')
    remarks = models.CharField(max_length=1024, null=True, default=None)
    payment_term_id = models.ForeignKey(VendorPaymentTerms, on_delete=models.CASCADE, null=True, default=None, db_column = 'payment_term_id')
    advance_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    ledger_account_id = models.ForeignKey(LedgerAccounts, on_delete=models.CASCADE, null=True, default=None, db_column = 'ledger_account_id')
    item_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    discount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    dis_amt = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    taxable = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    cess_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    round_off = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    order_status_id = models.ForeignKey(OrderStatuses, on_delete=models.CASCADE, null=True, default=None, db_column = 'order_status_id')
    shipping_address = models.CharField(max_length=1024, null=True, default=None)
    billing_address = models.CharField(max_length=1024, null=True, default=None)   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
	
    class Meta:
        db_table = purchaseorderstable

    def __str__(self):
        return f"{self.purchase_order_id}"

class PurchaseorderItems(models.Model):
    purchase_order_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_order_id = models.ForeignKey(PurchaseOrders, on_delete=models.CASCADE, db_column = 'purchase_order_id')
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, db_column = 'product_id')
    quantity = models.DecimalField(max_digits=18, decimal_places=2, default=None)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    discount_percentage = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    discount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    dis_amt = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    tax_code = models.CharField(max_length=255, null=True, default=None)
    tax_rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
	
    class Meta:
        db_table = purchaseorderitemstable
		
    def __str__(self):
        return f"{self.purchase_order_item_id}"

class PurchaseInvoiceOrders(OrderNumberMixin):
    purchase_invoice_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_type_id = models.ForeignKey(PurchaseTypes, on_delete=models.CASCADE, null=True, default=None, db_column = 'purchase_type_id')
    invoice_date = models.DateField()
    invoice_no = models.CharField(max_length=20, unique=True, default='')
    order_no_prefix = 'PO-INV'
    order_no_field = 'invoice_no'
    gst_type_id = models.ForeignKey(GstTypes, on_delete=models.CASCADE, null=True, default=None, db_column = 'GST_Type_id')
    vendor_id = models.ForeignKey(Vendor, on_delete=models.CASCADE, db_column = 'vendor_id')
    email = models.EmailField(max_length=255, blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)
    supplier_invoice_no = models.CharField(max_length=255)
    supplier_invoice_date = models.DateField(blank=True, null=True)
    vendor_agent_id = models.ForeignKey(VendorAgent, on_delete=models.CASCADE, null=True, default=None, db_column = 'vendor_agent_id')
    
    TAX_CHOICES = [
        ('Inclusive', 'Inclusive'),
        ('Exclusive', 'Exclusive')
    ]
    tax = models.CharField(max_length=20, choices=TAX_CHOICES, blank=True, null=True)    
    vendor_address_id = models.ForeignKey(VendorAddress, on_delete=models.CASCADE, null=True, default=None, db_column = 'vendor_address_id')
    remarks = models.CharField(max_length=1024, blank=True, null=True)
    payment_term_id = models.ForeignKey(VendorPaymentTerms, on_delete=models.CASCADE, null=True, default=None, db_column = 'payment_term_id')
    due_date = models.DateField(blank=True, null=True)
    advance_amount = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    ledger_account_id = models.ForeignKey(LedgerAccounts, on_delete=models.CASCADE, null=True, default=None, db_column = 'ledger_account_id')
    item_value = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    discount = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    dis_amt = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    taxable = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    cess_amount = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    transport_charges = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    round_off = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    order_status_id = models.ForeignKey(OrderStatuses, on_delete=models.CASCADE, null=True, default=None, db_column = 'order_status_id')
    shipping_address = models.CharField(max_length=1024, null=True, default=None)
    billing_address = models.CharField(max_length=1024, null=True, default=None)   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = purchaseinvoiceorders

    def __str__(self):
        return f"{self.purchase_invoice_id}"
    

class PurchaseInvoiceItem(models.Model):
    purchase_invoice_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_invoice_id = models.ForeignKey(PurchaseInvoiceOrders, on_delete=models.CASCADE, db_column = 'purchase_invoice_id')
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, db_column = 'product_id')
    quantity = models.DecimalField(max_digits=18, decimal_places=2)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    discount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    dis_amt = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    tax_code = models.CharField(max_length=255, null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = purchaseinvoiceitems

    def __str__(self):
        return f"{self.purchase_invoice_item_id}"

class PurchaseReturnOrders(OrderNumberMixin):
    TAX_CHOICES = [
        ('Inclusive', 'Inclusive'),
        ('Exclusive', 'Exclusive'),
    ]
    
    purchase_return_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_type_id = models.ForeignKey(PurchaseTypes, on_delete=models.CASCADE, null=True, default=None, db_column = 'purchase_type_id')
    return_date = models.DateField()
    return_no = models.CharField(max_length=20, unique=True, default='')
    order_no_prefix = 'PR'
    order_no_field = 'return_no'
    gst_type_id = models.ForeignKey(GstTypes, on_delete=models.CASCADE, null=True, default=None, db_column = 'GST_Type_id')
    vendor_id = models.ForeignKey(Vendor, on_delete=models.CASCADE, db_column = 'vendor_id')
    email = models.EmailField(max_length=255, null=True, blank=True)
    ref_no = models.CharField(max_length=255, null=True, blank=True)
    ref_date = models.DateField(null=True, blank=True)
    vendor_agent_id = models.ForeignKey(VendorAgent, on_delete=models.CASCADE, null=True, default=None, db_column = 'vendor_agent_id')
    tax = models.CharField(max_length=10, choices=TAX_CHOICES, blank=True, null=True)
    vendor_address_id = models.ForeignKey(VendorAddress, on_delete=models.CASCADE, null=True, default=None, db_column = 'vendor_address_id')
    remarks = models.TextField(max_length=1024, null=True, blank=True)
    payment_term_id = models.ForeignKey(VendorPaymentTerms, on_delete=models.CASCADE, null=True, default=None, db_column = 'payment_term_id')
    due_date = models.DateField(null=True, blank=True)
    return_reason = models.TextField(max_length=1024, null=True, blank=True)
    item_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    discount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    dis_amt = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    taxable = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    cess_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    transport_charges = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    round_off = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    order_status_id = models.ForeignKey(OrderStatuses, on_delete=models.CASCADE, null=True, default=None, db_column = 'order_status_id')
    shipping_address = models.CharField(max_length=1024, null=True, default=None)
    billing_address = models.CharField(max_length=1024, null=True, default=None)    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = purchasereturnorders

    def __str__(self):
        return f"{self.purchase_return_id}"

class PurchaseReturnItems(models.Model):
    purchase_return_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_return_id = models.ForeignKey(PurchaseReturnOrders, on_delete=models.CASCADE, db_column='purchase_return_id')
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, db_column='product_id')
    quantity = models.DecimalField(max_digits=18, decimal_places=2)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    discount = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    dis_amt = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    tax_code = models.CharField(max_length=255, null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = purchasereturnitems

    def __str__(self):
        return f"{self.purchase_return_item_id}"


class PurchasePriceList(models.Model):
    purchase_price_list_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=255)
    customer_category_id = models.ForeignKey(CustomerCategories, on_delete=models.CASCADE, db_column = 'customer_category_id')
    brand_id = models.ForeignKey(ProductBrands, on_delete=models.CASCADE, null=True, default=None, db_column = 'brand_id')
    effective_from = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = purchasepricelisttable

    def __str__(self):
        return f"{self.purchase_price_list_id}"