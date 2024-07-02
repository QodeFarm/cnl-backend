from django.db import models
from apps.customer.models import CustomerAddresses, LedgerAccounts, Customer
from apps.inventory.models import Warehouses
from apps.masters.models import CustomerPaymentTerms, GstTypes, ProductBrands, ProductItemType, CustomerCategories, SaleTypes, ShippingCompanies, ShippingModes
from config.utils_variables import saleorderreturns, saleorders, paymenttransactions, invoices, saleinvoiceitemstable, shipments, salespricelist, saleorderitemstable, saleinvoiceorderstable, salereturnorderstable, salereturnitemstable, orderattachmentstable, ordershipmentstable
from apps.products.models import ProductGroups, Products
import uuid
from config.utils_methods import OrderNumberMixin
# Create your models here.


class SaleOrder(OrderNumberMixin): #required fields are updated
    sale_order_id  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gst_type_id = models.ForeignKey(GstTypes, on_delete=models.CASCADE, null=True, default=None, db_column='gst_type_id')
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='customer_id')
    email = models.CharField(max_length=255, null=True, default=None)
    delivery_date = models.DateField()
    order_date = models.DateField()
    order_no = models.CharField(max_length=20, unique=True, default='')
    order_no_prefix = 'SO'
    order_no_field = 'order_no'
    ref_no = models.CharField(max_length=255, null=True, default=None)
    ref_date = models.DateField()
    TAX_CHOICES = [
        ('Inclusive', 'Inclusive'),
        ('Exclusive', 'Exclusive')
        ]
    tax = models.CharField(max_length=10, choices=TAX_CHOICES, null=True, default=None)
    customer_address_id = models.ForeignKey(CustomerAddresses, on_delete=models.CASCADE, null=True, default=None, db_column='customer_address_id')
    remarks = models.TextField(null=True, default=None)
    payment_term_id = models.ForeignKey(CustomerPaymentTerms, on_delete=models.CASCADE, null=True, default=None, db_column='payment_term_id')
    sale_type_id = models.ForeignKey(SaleTypes, on_delete=models.CASCADE, null=True, default=None, db_column='sale_type_id')
    advance_amount = models.DecimalField(max_digits=18, decimal_places=2,null=True, default=None)
    ledger_account_id = models.ForeignKey(LedgerAccounts, on_delete=models.CASCADE, null=True, default=None, db_column='ledger_account_id')
    item_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    discount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    dis_amt = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    taxable = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None, help_text= 'ENTER NUMBER')
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    cess_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    round_off = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    doc_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    vehicle_name = models.CharField(max_length=255, null=True, default=None)
    total_boxes = models.IntegerField(null=True, default=None)
    order_status_id  = models.ForeignKey('masters.OrderStatuses', on_delete=models.CASCADE, null=True, default=None, db_column='order_status_id')
    shipping_address = models.CharField(max_length=1024, null=True, default=None)
    billing_address = models.CharField(max_length=1024, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.sale_order_id}'
    
    class Meta:
        db_table = saleorders

class SalesPriceList(models.Model): #required fields are updated
    sales_price_list_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=255)
    customer_category_id = models.ForeignKey(CustomerCategories, on_delete=models.CASCADE, db_column='customer_category_id')
    brand_id = models.ForeignKey(ProductBrands, on_delete=models.CASCADE, null=True, default=None, db_column='brand_id')
    effective_From = models.DateField()
    # effective_date = models.DateField(null=True, default=None)
    # product_group_id = models.ForeignKey(ProductGroups, on_delete=models.CASCADE, null=True, default=None, db_column='product_group_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.sales_price_list_id}'
    
    class Meta:
        db_table = salespricelist

class SaleOrderItems(models.Model):
    sale_order_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale_order_id = models.ForeignKey(SaleOrder, on_delete=models.CASCADE, db_column='sale_order_id')
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, db_column='product_id')
    quantity = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
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
        db_table = saleorderitemstable

    def __str__(self):
        return str(self.sale_order_item_id)
    
class SaleInvoiceOrders(OrderNumberMixin):
    sale_invoice_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    BILL_TYPE_CHOICES = [('CASH', 'Cash'),('CREDIT', 'Credit'),('OTHERS', 'Others'),]
    bill_type = models.CharField(max_length=6, choices=BILL_TYPE_CHOICES)
    invoice_date = models.DateField()
    invoice_no = models.CharField(max_length=20, unique=True,default='')
    order_no_prefix = 'SO-INV'
    order_no_field = 'invoice_no'
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='customer_id')
    gst_type_id = models.ForeignKey('masters.GstTypes', on_delete=models.CASCADE, db_column='gst_type_id', null=True, default=None)
    email = models.EmailField(max_length=255, null=True, default=None)
    ref_no = models.CharField(max_length=255, null=True, default=None)
    ref_date = models.DateField()
    order_salesman_id = models.ForeignKey('masters.OrdersSalesman', on_delete=models.CASCADE, db_column='order_salesman_id', null=True, default=None)
    TAX_CHOICES = [('Inclusive', 'Inclusive'),('Exclusive', 'Exclusive'),]
    tax = models.CharField(max_length=10, choices=TAX_CHOICES, null=True, default=None)
    customer_address_id = models.ForeignKey(CustomerAddresses, on_delete=models.CASCADE, db_column='customer_address_id', null=True, default=None)
    payment_term_id = models.ForeignKey(CustomerPaymentTerms, on_delete=models.CASCADE, db_column='payment_term_id', null=True, default=None)
    due_date = models.DateField(null=True, default=None)
    payment_link_type_id = models.ForeignKey('masters.PaymentLinkTypes', on_delete=models.CASCADE, db_column='payment_link_type_id', null=True, default=None)
    remarks = models.CharField(max_length=1024, null=True, default=None)
    advance_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    ledger_account_id = models.ForeignKey(LedgerAccounts, on_delete=models.CASCADE, null=True, default=None, db_column='ledger_account_id')
    item_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    discount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    dis_amt = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    taxable = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    cess_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    transport_charges = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    round_off = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    vehicle_name = models.CharField(max_length=255, null=True, default=None)
    total_boxes = models.IntegerField(null=True, default=None)
    order_status_id = models.ForeignKey('masters.OrderStatuses', on_delete=models.CASCADE, db_column='order_status_id', null=True, default=None)
    shipping_address = models.CharField(max_length=1024, null=True, default=None)
    billing_address = models.CharField(max_length=1024, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = saleinvoiceorderstable

    def __str__(self):
        return self.sale_invoice_id
    
class PaymentTransactions(models.Model): #required fields are updated
    transaction_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale_invoice_id = models.ForeignKey(SaleInvoiceOrders, on_delete=models.CASCADE, db_column='sale_invoice_id')
    payment_date = models.DateField(null=True, default=None)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None)
    payment_method = models.CharField(max_length=100,null=True,default=None)
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ]
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    reference_number = models.CharField(max_length=100,null=True,default=None)
    notes = models.TextField(null=True, default=None)
    currency = models.CharField(max_length=10,null=True,default=None)
    TRANSACTION_TYPE_CHOICES = [('Credit', 'Credit'),('Debit', 'Debit'),]
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.transaction_id}'
    
    class Meta:
        db_table = paymenttransactions

class SaleInvoiceItems(models.Model): #required fields are updated
    sale_invoice_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale_invoice_id = models.ForeignKey(SaleInvoiceOrders, on_delete=models.CASCADE, db_column='sale_invoice_id')
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, db_column='product_id')
    quantity = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    discount_percentage = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    discount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    dis_amt = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    tax_code = models.CharField(max_length=255,null=True,default=None)
    tax_rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.sale_invoice_item_id}'
    
    class Meta:
        db_table = saleinvoiceitemstable

class SaleReturnOrders(OrderNumberMixin):
    sale_return_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    BILL_TYPE_CHOICES = [('CASH', 'Cash'),('CREDIT', 'Credit'),('OTHERS', 'Others'),]
    bill_type = models.CharField(max_length=6, choices=BILL_TYPE_CHOICES)  
    return_date = models.DateField()
    return_no = models.CharField(max_length=20, unique=True, default='')
    order_no_prefix = 'SR'
    order_no_field = 'return_no'
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='customer_id')
    gst_type_id = models.ForeignKey('masters.GstTypes', on_delete=models.CASCADE, db_column='gst_type_id', null=True, default=None)
    email = models.EmailField(max_length=255, null=True, default=None)
    ref_no = models.CharField(max_length=255, null=True, default=None)
    ref_date = models.DateField()
    order_salesman_id = models.ForeignKey('masters.OrdersSalesman', on_delete=models.CASCADE, db_column='order_salesman_id', null=True, default=None)
    against_bill = models.CharField(max_length=255, null=True, default=None)
    against_bill_date = models.DateField(null=True, default=None)
    TAX_CHOICES = [('Inclusive', 'Inclusive'),('Exclusive', 'Exclusive'),]
    tax = models.CharField(max_length=10, choices=TAX_CHOICES, null=True, default=None)
    customer_address_id = models.ForeignKey(CustomerAddresses, on_delete=models.CASCADE, db_column='customer_address_id', null=True, default=None)
    payment_term_id = models.ForeignKey(CustomerPaymentTerms, on_delete=models.CASCADE, db_column='payment_term_id', null=True, default=None)
    due_date = models.DateField(null=True, default=None)
    payment_link_type_id = models.ForeignKey('masters.PaymentLinkTypes', on_delete=models.CASCADE, db_column='payment_link_type_id', null=True, default=None)
    return_reason = models.CharField(max_length=1024, null=True, default=None)
    remarks = models.CharField(max_length=1024, null=True, default=None)
    item_value = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    discount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    dis_amt = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    taxable = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    cess_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    transport_charges = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    round_off = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    vehicle_name = models.CharField(max_length=255, null=True, default=None)
    total_boxes = models.IntegerField(null=True, default=None)
    order_status_id = models.ForeignKey('masters.OrderStatuses', on_delete=models.CASCADE, db_column='order_status_id', null=True, default=None)
    shipping_address = models.CharField(max_length=1024, null=True, default=None)
    billing_address = models.CharField(max_length=1024, null=True, default=None)   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = salereturnorderstable

    def __str__(self):
        return self.sale_return_id
    
class SaleReturnItems(models.Model):
    sale_return_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale_return_id = models.ForeignKey(SaleReturnOrders, on_delete=models.CASCADE, db_column='sale_return_id')
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, db_column='product_id')
    quantity = models.DecimalField(max_digits=18, decimal_places=2)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2)
    rate = models.DecimalField(max_digits=18, decimal_places=2)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=18, decimal_places=2)
    discount = models.DecimalField(max_digits=18, decimal_places=2)
    dis_amt = models.DecimalField(max_digits=18, decimal_places=2)
    tax_code = models.CharField(max_length=255, null=True, default=None)
    tax_rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = salereturnitemstable

    def __str__(self):
        return str(self.sale_return_item_id)
    
class OrderAttachments(models.Model):
    attachment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id = models.CharField(max_length=255)
    attachment_name = models.CharField(max_length=255)
    attachment_path = models.CharField(max_length=255)
    order_type_id = models.ForeignKey('masters.OrderTypes', on_delete=models.CASCADE, db_column='order_type_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = orderattachmentstable

    def __str__(self):
        return self.attachment_name
    

class OrderShipments(OrderNumberMixin):
    shipment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id = models.CharField(max_length=255)
    destination = models.CharField(max_length=255, null=True, default=None)
    shipping_mode_id = models.ForeignKey('masters.ShippingModes', on_delete=models.CASCADE, db_column='shipping_mode_id', null=True, default=None)
    shipping_company_id = models.ForeignKey('masters.ShippingCompanies', on_delete=models.CASCADE, db_column='shipping_company_id', null=True, default=None)
    shipping_tracking_no = models.CharField(max_length=20, unique=True, default='')
    order_no_prefix = 'SHIP'
    order_no_field = 'shipping_tracking_no'
    shipping_date = models.DateField()
    shipping_charges = models.DecimalField(max_digits=10, decimal_places=2)
    vehicle_vessel = models.CharField(max_length=255, null=True, default=None)
    charge_type = models.CharField(max_length=255, null=True, default=None)
    document_through = models.CharField(max_length=255, null=True, default=None)
    port_of_landing = models.CharField(max_length=255, null=True, default=None)
    port_of_discharge = models.CharField(max_length=255, null=True, default=None)
    no_of_packets = models.IntegerField(null=True, default=None)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None)
    order_type_id = models.ForeignKey('masters.OrderTypes', on_delete=models.CASCADE, db_column='order_type_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    class Meta:
        db_table = ordershipmentstable

    def __str__(self):
        return self.shipment_id
