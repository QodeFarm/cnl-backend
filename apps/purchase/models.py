from decimal import Decimal
from django.db import models
from apps.finance.models import ChartOfAccounts
from config.utils_variables import *
from apps.masters.models import PurchaseTypes,State,ProductBrands, GstTypes, OrderStatuses, UnitOptions
from apps.customer.models import LedgerAccounts,CustomerCategories
from apps.vendor.models import Vendor,VendorAgent,VendorAddress,VendorPaymentTerms
from apps.products.models import Products, Size, Color
import uuid
from config.utils_methods import OrderNumberMixin, generate_order_number

# Create your models here.
class PurchaseOrders(OrderNumberMixin):
    purchase_order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_type_id = models.ForeignKey(PurchaseTypes, on_delete=models.PROTECT, null=True, default=None, db_column = 'purchase_type_id')
    order_date = models.DateField()
    order_no = models.CharField(max_length=255, null=True, default='')
    order_no_prefix = 'PO'
    order_no_field = 'order_no'
    gst_type_id = models.ForeignKey(GstTypes, on_delete=models.PROTECT, null=True, default=None, db_column = 'GST_Type_id')
    vendor_id = models.ForeignKey(Vendor, on_delete=models.PROTECT, db_column = 'vendor_id')
    email = models.EmailField(max_length=255, null=True, default=None)
    delivery_date = models.DateField(blank=True, null=True)
    ref_no = models.CharField(max_length=255, null=True, default=None)
    ref_date = models.DateField(blank=True, null=True)
    vendor_agent_id = models.ForeignKey(VendorAgent, on_delete=models.PROTECT, null=True, default=None, db_column = 'vendor_agent_id')
    TAX_CHOICES = [('Exclusive', 'Exclusive'),
                   ('Inclusive', 'Inclusive')
                ]
    tax = models.CharField(max_length=20, choices=TAX_CHOICES , blank=True, null=True, default=None)
    vendor_address_id = models.ForeignKey(VendorAddress, on_delete=models.PROTECT, null=True, default=None, db_column = 'vendor_address_id')
    remarks = models.CharField(max_length=1024, null=True, default=None)
    payment_term_id = models.ForeignKey(VendorPaymentTerms, on_delete=models.PROTECT, null=True, default=None, db_column = 'payment_term_id')
    advance_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    ledger_account_id = models.ForeignKey(LedgerAccounts, on_delete=models.PROTECT, null=True, default=None, db_column = 'ledger_account_id')
    item_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    discount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    dis_amt = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    taxable = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    cess_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    round_off = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    order_status_id = models.ForeignKey(OrderStatuses, on_delete=models.PROTECT, null=True, default=None, db_column = 'order_status_id')
    shipping_address = models.CharField(max_length=1024, null=True, default=None)
    billing_address = models.CharField(max_length=1024, null=True, default=None)   
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
	
    class Meta:
        db_table = purchaseorderstable

    def __str__(self):
        return f"{self.purchase_order_id}"
    
    def save(self, *args, **kwargs):
        from apps.masters.views import increment_order_number
        """
        Override save to ensure the order number is only generated on creation, not on updates.
        """
        # Determine if this is a new record based on the `adding` state
        is_new_record = self._state.adding

        # Ensure the order status is set if not already set
        if not self.order_status_id:
            self.order_status_id = OrderStatuses.objects.get_or_create(status_name='Pending')[0]

        # Only generate and set the order number if this is a new record
        if is_new_record:
            # Generate the order number if it's not already set
            if not getattr(self, self.order_no_field):  # Ensure the order number is not already set
                order_number = generate_order_number(self.order_no_prefix)
                setattr(self, self.order_no_field, order_number)

        # Save the record
        super().save(*args, **kwargs)

        # After the record is saved, increment the order number sequence only for new records
        if is_new_record:
            print("from create", self.pk)
            increment_order_number(self.order_no_prefix)
        else:
            print("from edit", self.pk)


class PurchaseorderItems(models.Model):
    purchase_order_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_order_id = models.ForeignKey(PurchaseOrders, on_delete=models.PROTECT, db_column = 'purchase_order_id')
    product_id = models.ForeignKey(Products, on_delete=models.PROTECT, db_column='product_id')
    unit_options_id = models.ForeignKey(UnitOptions, on_delete=models.PROTECT, db_column='unit_options_id')
    size_id = models.ForeignKey(Size, on_delete=models.PROTECT, null=True, db_column='size_id')
    color_id = models.ForeignKey(Color, on_delete=models.PROTECT, null=True, db_column='color_id')    
    print_name = models.CharField(max_length=255, null=True, default=None)
    quantity = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    total_boxes = models.IntegerField(null=True, default=None)
    rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    tax = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    cgst = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=0.00)
    sgst = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=0.00)
    igst = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=0.00) 
    remarks = models.CharField(max_length=1024, null=True, default=None)
    discount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
	
    class Meta:
        db_table = purchaseorderitemstable
		
    def __str__(self):
        return f"{self.purchase_order_item_id}"

class PurchaseInvoiceOrders(OrderNumberMixin):
    purchase_invoice_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_type_id = models.ForeignKey(PurchaseTypes, on_delete=models.PROTECT, null=True, default=None, db_column = 'purchase_type_id')
    invoice_date = models.DateField()
    invoice_no = models.CharField(max_length=20, null=True, default='')
    order_no_prefix = 'PO-INV'
    order_no_field = 'invoice_no'
    gst_type_id = models.ForeignKey(GstTypes, on_delete=models.PROTECT, null=True, default=None, db_column = 'GST_Type_id')
    vendor_id = models.ForeignKey(Vendor, on_delete=models.PROTECT, db_column = 'vendor_id')
    email = models.EmailField(max_length=255, blank=True, null=True)
    delivery_date = models.DateField(blank=True, null=True)
    supplier_invoice_no = models.CharField(max_length=255)
    supplier_invoice_date = models.DateField(blank=True, null=True)
    vendor_agent_id = models.ForeignKey(VendorAgent, on_delete=models.PROTECT, null=True, default=None, db_column = 'vendor_agent_id')
    TAX_CHOICES = [
        ('Exclusive', 'Exclusive'),
        ('Inclusive', 'Inclusive')
    ]
    tax = models.CharField(max_length=20, choices=TAX_CHOICES, blank=True, null=True)    
    vendor_address_id = models.ForeignKey(VendorAddress, on_delete=models.PROTECT, null=True, default=None, db_column = 'vendor_address_id')
    remarks = models.CharField(max_length=1024, blank=True, null=True)
    payment_term_id = models.ForeignKey(VendorPaymentTerms, on_delete=models.PROTECT, null=True, default=None, db_column = 'payment_term_id')
    due_date = models.DateField(blank=True, null=True)
    advance_amount = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    ledger_account_id = models.ForeignKey(LedgerAccounts, on_delete=models.PROTECT, null=True, default=None, db_column = 'ledger_account_id')
    item_value = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    discount = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    dis_amt = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    taxable = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    cess_amount = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    transport_charges = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    round_off = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    order_status_id = models.ForeignKey(OrderStatuses, on_delete=models.PROTECT, null=True, default=None, db_column = 'order_status_id')
    shipping_address = models.CharField(max_length=1024, null=True, default=None)
    billing_address = models.CharField(max_length=1024, null=True, default=None) 
    paid_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=0.0)
    pending_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = purchaseinvoiceorders

    def __str__(self):
        return f"{self.purchase_invoice_id}"
    
    def save(self, *args, **kwargs):
        from apps.masters.views import increment_order_number
        """
        Override save to ensure the order number is only generated on creation, not on updates.
        """
        # Determine if this is a new record based on the `adding` state
        is_new_record = self._state.adding

        # Ensure the order status is set if not already set
        if not self.order_status_id:
            self.order_status_id = OrderStatuses.objects.get_or_create(status_name='Pending')[0]

        # Only generate and set the order number if this is a new record
        if is_new_record and not getattr(self, self.order_no_field):
            # Generate the order number if it's not already set
            # if not getattr(self, self.order_no_field):  # Ensure the order number is not already set
            #     order_number = generate_order_number(self.order_no_prefix)
            #     setattr(self, self.order_no_field, order_number)
            order_number = generate_order_number(
                self.order_no_prefix,
                model_class=PurchaseInvoiceOrders,
                field_name='invoice_no'
            )
            setattr(self, self.order_no_field, order_number)
            
        # ✅ Set pending amount by default = total_amount if new record
        if is_new_record:
            if self.total_amount and (self.pending_amount is None or self.pending_amount == 0):
                self.pending_amount = self.total_amount

        # ✅ Ensure pending_amount doesn’t go below 0
        if self.pending_amount and self.pending_amount < 0:
            self.pending_amount = 0

        # Save the record
        super().save(*args, **kwargs)

        # After the record is saved, increment the order number sequence only for new records
        if is_new_record:
            print("from create", self.pk)
            increment_order_number(self.order_no_prefix)
        else:
            print("from edit", self.pk)
            
    def update_paid_amount_and_pending_amount_after_bill_payment(self, payment_amount, outstanding_amount, adjusted_now_amount=0):
        """
        Update the paid_amount and pending_amount in PurchaseInvoiceOrders
        whenever a Bill Payment Transaction is created.
        """
        if self.paid_amount is None:
            self.paid_amount = Decimal('0.00')

        # Update paid and pending amounts based on AdjustNow or normal payment
        if adjusted_now_amount > Decimal("0.00"):
            self.paid_amount += Decimal(adjusted_now_amount)
            self.pending_amount = Decimal(outstanding_amount)
        else:
            self.paid_amount += Decimal(payment_amount)
            self.pending_amount = Decimal(outstanding_amount)

        self.save()
        print(
            f"Updated PurchaseInvoiceOrders for Invoice {self.invoice_no} with Total Amount {self.total_amount}, "
            f"Paid Amount {self.paid_amount}, Pending Amount {self.pending_amount}."
        )

    

class PurchaseInvoiceItem(models.Model):
    purchase_invoice_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_invoice_id = models.ForeignKey(PurchaseInvoiceOrders, on_delete=models.PROTECT, db_column = 'purchase_invoice_id')
    product_id = models.ForeignKey(Products, on_delete=models.PROTECT, db_column='product_id')
    unit_options_id = models.ForeignKey(UnitOptions, on_delete=models.PROTECT, db_column='unit_options_id')
    size_id = models.ForeignKey(Size, on_delete=models.PROTECT, null=True, db_column='size_id')
    color_id = models.ForeignKey(Color, on_delete=models.PROTECT, null=True, db_column='color_id')     
    print_name = models.CharField(max_length=255, null=True, default=None)
    quantity = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    total_boxes = models.IntegerField(null=True, default=None)
    rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    tax = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    cgst = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=0.00)
    sgst = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=0.00)
    igst = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=0.00) 
    remarks = models.CharField(max_length=1024, null=True, default=None)
    discount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = purchaseinvoiceitems

    def __str__(self):
        return f"{self.purchase_invoice_item_id}"

class PurchaseReturnOrders(OrderNumberMixin):
    TAX_CHOICES = [
        ('Exclusive', 'Exclusive'),
        ('Inclusive', 'Inclusive')
    ]
    
    purchase_return_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_type_id = models.ForeignKey(PurchaseTypes, on_delete=models.PROTECT, null=True, default=None, db_column = 'purchase_type_id')
    return_date = models.DateField()
    return_no = models.CharField(max_length=20, null=True, default='')
    order_no_prefix = 'PR'
    order_no_field = 'return_no'
    gst_type_id = models.ForeignKey(GstTypes, on_delete=models.PROTECT, null=True, default=None, db_column = 'GST_Type_id')
    vendor_id = models.ForeignKey(Vendor, on_delete=models.PROTECT, db_column = 'vendor_id')
    email = models.EmailField(max_length=255, null=True, blank=True)
    ref_no = models.CharField(max_length=255, null=True, blank=True)
    ref_date = models.DateField(null=True, blank=True)
    vendor_agent_id = models.ForeignKey(VendorAgent, on_delete=models.PROTECT, null=True, default=None, db_column = 'vendor_agent_id')
    tax = models.CharField(max_length=10, choices=TAX_CHOICES, blank=True, null=True)
    vendor_address_id = models.ForeignKey(VendorAddress, on_delete=models.PROTECT, null=True, default=None, db_column = 'vendor_address_id')
    remarks = models.TextField(max_length=1024, null=True, blank=True)
    payment_term_id = models.ForeignKey(VendorPaymentTerms, on_delete=models.PROTECT, null=True, default=None, db_column = 'payment_term_id')
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
    order_status_id = models.ForeignKey(OrderStatuses, on_delete=models.PROTECT, null=True, default=None, db_column = 'order_status_id')
    shipping_address = models.CharField(max_length=1024, null=True, default=None)
    billing_address = models.CharField(max_length=1024, null=True, default=None) 
    is_deleted = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = purchasereturnorders

    def __str__(self):
        return f"{self.purchase_return_id}"
    
    def save(self, *args, **kwargs):
        from apps.masters.views import increment_order_number
        """
        Override save to ensure the order number is only generated on creation, not on updates.
        """
        # Determine if this is a new record based on the `adding` state
        is_new_record = self._state.adding

        # Ensure the order status is set if not already set
        if not self.order_status_id:
            self.order_status_id = OrderStatuses.objects.get_or_create(status_name='Pending')[0]

        # Only generate and set the order number if this is a new record
        if is_new_record and not getattr(self, self.order_no_field):
            # Generate the order number if it's not already set
            # if not getattr(self, self.order_no_field):  # Ensure the order number is not already set
            #     order_number = generate_order_number(self.order_no_prefix)
            #     setattr(self, self.order_no_field, order_number)
            order_number = generate_order_number(
                self.order_no_prefix,
                model_class=PurchaseReturnOrders,
                field_name='return_no'
            )
            setattr(self, self.order_no_field, order_number)

        # Save the record
        super().save(*args, **kwargs)

        # After the record is saved, increment the order number sequence only for new records
        if is_new_record:
            print("from create", self.pk)
            increment_order_number(self.order_no_prefix)
        else:
            print("from edit", self.pk)

class PurchaseReturnItems(models.Model):
    purchase_return_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_return_id = models.ForeignKey(PurchaseReturnOrders, on_delete=models.CASCADE, db_column='purchase_return_id')
    product_id = models.ForeignKey(Products, on_delete=models.PROTECT, db_column='product_id')
    unit_options_id = models.ForeignKey(UnitOptions, on_delete=models.PROTECT, db_column='unit_options_id')
    size_id = models.ForeignKey(Size, on_delete=models.PROTECT, null=True, db_column='size_id')
    color_id = models.ForeignKey(Color, on_delete=models.PROTECT, null=True, db_column='color_id')     
    print_name = models.CharField(max_length=255, null=True, default=None)
    quantity = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    total_boxes = models.IntegerField(null=True, default=None)
    rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    tax = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    cgst = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=0.00)
    sgst = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=0.00)
    igst = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=0.00) 
    remarks = models.CharField(max_length=1024, null=True, default=None)
    discount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = purchasereturnitems

    def __str__(self):
        return f"{self.purchase_return_item_id}"


class PurchasePriceList(models.Model):
    purchase_price_list_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=255)
    customer_category_id = models.ForeignKey(CustomerCategories, on_delete=models.PROTECT, db_column = 'customer_category_id')
    brand_id = models.ForeignKey(ProductBrands, on_delete=models.PROTECT, null=True, default=None, db_column = 'brand_id')
    effective_from = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = purchasepricelisttable

    def __str__(self):
        return f"{self.purchase_price_list_id}"
    
#------------------- Bill Payments ----------------------------------

class BillPaymentTransactions(OrderNumberMixin):
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment_receipt_no = models.CharField(max_length=50, unique=True, default='')
    order_no_prefix = 'BPR'  # Payment Receipt prefix
    order_no_field = 'payment_receipt_no'  # Field to store the order number
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=100, null=True, blank=True)
    cheque_no = models.CharField(max_length=50, null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    outstanding_amount = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    adjusted_now = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    payment_status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed')
    ], default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    purchase_invoice = models.ForeignKey("PurchaseInvoiceOrders", on_delete=models.CASCADE, db_column='purchase_invoice_id')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, db_column='vendor_id')
    bill_no = models.CharField(max_length=20, null=True, default=None)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    ledger_account_id = models.ForeignKey(LedgerAccounts, on_delete=models.PROTECT, null=False, db_column='ledger_account_id')

    class Meta:
        db_table = "bill_payment_transactions"

    def __str__(self):
        return f"{self.payment_receipt_no}"
    
    def save(self, *args, **kwargs):
        from apps.masters.views import increment_order_number
        """
        Override save to ensure the order number is only generated on creation, not on updates.
        """
        # Determine if this is a new record based on the `adding` state
        is_new_record = self._state.adding
        
        # Only generate and set the order number if this is a new record
        if is_new_record and not getattr(self, self.order_no_field):
            order_number = generate_order_number(
                self.order_no_prefix,
                model_class=BillPaymentTransactions,
                field_name='payment_receipt_no'
            )
            setattr(self, self.order_no_field, order_number)

        # Save the record
        super().save(*args, **kwargs)

        # After the record is saved, increment the order number sequence only for new records
        if is_new_record:
            print(f"Creating new Bill payment receipt: {self.payment_receipt_no}")
            increment_order_number(self.order_no_prefix)
        else:
            print(f"Updating existing Bill payment receipt: {self.payment_receipt_no}")
            