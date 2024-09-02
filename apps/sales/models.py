import uuid
from django.db import models
from apps import products
from apps.customer.models import CustomerAddresses, LedgerAccounts, Customer
from apps.masters.models import CustomerPaymentTerms, GstTypes, ProductBrands, CustomerCategories, SaleTypes, UnitOptions, OrderStatuses
from apps.products.models import Products
from config.utils_variables import quickpackitems, quickpacks, saleorders, paymenttransactions, saleinvoiceitemstable, salespricelist, saleorderitemstable, saleinvoiceorderstable, salereturnorderstable, salereturnitemstable, orderattachmentstable, ordershipmentstable, workflow, workflowstages, salereceipts, default_workflow_name, default_workflow_stages
from config.utils_methods import OrderNumberMixin
import logging

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
    flow_status = models.CharField(max_length=255, null=True, default=None)
    workflow_id = models.ForeignKey('Workflow', on_delete=models.CASCADE, db_column='workflow_id')
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
        
    def save(self, *args, **kwargs):
        # Set default order status if not provided
        if not self.order_status_id:
            self.order_status_id = OrderStatuses.objects.get_or_create(status_name='Pending')[0]

        # Automatically assign the default workflow if none is selected
        if not self.workflow_id:
            self.workflow_id = Workflow.objects.get_or_create(name=default_workflow_name)[0]

        # Check if the workflow is the default one
        if not self.flow_status:
            if self.workflow_id.name == default_workflow_name:
                # Hardcode the flow status based on the predefined stages
                self.flow_status = default_workflow_stages[1]  # 'sale_order'
            else:
                # Dynamically set flow status based on the second stage of the selected workflow
                stages = WorkflowStage.objects.filter(
                    workflow_id=self.workflow_id
                ).order_by('stage_order')

                if stages.count() > 1:
                    # Set to the second stage (index 1)
                    self.flow_status = stages[1].stage_name
                elif stages.exists():
                    # Fallback to the first stage if only one stage exists
                    self.flow_status = stages.first().stage_name

        # Call the original save() method to handle the rest
        super().save(*args, **kwargs)




    def progress_workflow(self):
        logger = logging.getLogger(__name__)

        # Handle progress for default workflow
        if self.workflow_id and self.workflow_id.name == default_workflow_name:
            current_stage_index = default_workflow_stages.index(self.flow_status)
            if current_stage_index + 1 < len(default_workflow_stages):
                self.flow_status = default_workflow_stages[current_stage_index + 1]
                self.save()
                logger.info(f"SaleOrder {self.sale_order_id} moved to stage: {self.flow_status}")
                return True
            else:
                logger.info(f"SaleOrder {self.sale_order_id} has completed the default workflow.")
                return False
        else:
            # Dynamic handling for non-default workflows
            current_stage = WorkflowStage.objects.filter(
                workflow=self.workflow_id,
                stage_name=self.flow_status
            ).first()

            if current_stage:
                next_stage = WorkflowStage.objects.filter(
                    workflow=self.workflow_id,
                    stage_order__gt=current_stage.stage_order
                ).order_by('stage_order').first()

                if next_stage:
                    self.flow_status = next_stage.stage_name
                    self.save()
                    logger.info(f"SaleOrder {self.sale_order_id} moved to stage: {next_stage.stage_name}")
                    return True
                else:
                    logger.info(f"SaleOrder {self.sale_order_id} has completed the workflow.")
                    return False
            else:
                logger.warning(f"SaleOrder {self.sale_order_id} could not find current stage in workflow.")
                return False



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
    unit_options_id = models.ForeignKey(UnitOptions, on_delete=models.CASCADE, db_column='unit_options_id')
    print_name = models.CharField(max_length=255, null=True, default=None)
    quantity = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    total_boxes = models.IntegerField(null=True, default=None)
    rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    discount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    tax = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    remarks = models.CharField(max_length=1024, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = saleorderitemstable

    def __str__(self):
        return str(self.sale_order_item_id)
    
class SaleInvoiceOrders(OrderNumberMixin):
    sale_invoice_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale_order_id = models.ForeignKey(SaleOrder, on_delete=models.CASCADE, db_column='sale_order_id', null=True, default=None)
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
        return str(self.sale_invoice_id)
    
    def save(self, *args, **kwargs):
        if not self.order_status_id:
            self.order_status_id = OrderStatuses.objects.get_or_create(status_name='In Progress')[0]
        super().save(*args, **kwargs)
    
    
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
    unit_options_id = models.ForeignKey(UnitOptions, on_delete=models.CASCADE, db_column='unit_options_id')
    print_name = models.CharField(max_length=255, null=True, default=None)
    quantity = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    total_boxes = models.IntegerField(null=True, default=None)
    rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    discount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    tax = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    remarks = models.CharField(max_length=1024, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.sale_invoice_item_id}'
    
    class Meta:
        db_table = saleinvoiceitemstable

class SaleReturnOrders(OrderNumberMixin):
    sale_return_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale_invoice_id = models.ForeignKey(SaleInvoiceOrders, on_delete=models.CASCADE, db_column='sale_invoice_id', null=True, default=None )
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
        return str(self.sale_return_id)
    
    def save(self, *args, **kwargs):
        if not self.order_status_id:
            self.order_status_id = OrderStatuses.objects.get_or_create(status_name='Pending')[0]
        super().save(*args, **kwargs)
    
class SaleReturnItems(models.Model):
    sale_return_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale_return_id = models.ForeignKey(SaleReturnOrders, on_delete=models.CASCADE, db_column='sale_return_id')
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, db_column='product_id')
    unit_options_id = models.ForeignKey(UnitOptions, on_delete=models.CASCADE, db_column='unit_options_id')
    print_name = models.CharField(max_length=255, null=True, default=None)
    quantity = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    total_boxes = models.IntegerField(null=True, default=None)
    rate = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    amount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    discount = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    tax = models.DecimalField(max_digits=18, decimal_places=2, null=True, default=None)
    remarks = models.CharField(max_length=1024, null=True, default=None)
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
    shipping_tracking_no = models.CharField(max_length=20, default='')
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

class QuickPacks(models.Model):
    quick_pack_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=512, null=True, default=None)
    active = models.CharField(max_length=1, choices=[('Y', 'Yes'), ('N', 'No')], null=True, default='Y')
    lot_qty = models.IntegerField(default=1, null=True)
    customer_id = models.ForeignKey(Customer,on_delete=models.CASCADE, db_column='customer_id', null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    class Meta:
        db_table = quickpacks

    def __str__(self):
        return self.name

class QuickPackItems(models.Model):
    quick_pack_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quantity = models.IntegerField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    quick_pack_id = models.ForeignKey(QuickPacks,on_delete=models.CASCADE, db_column='quick_pack_id')
    product_id = models.ForeignKey(Products,on_delete=models.CASCADE, db_column='product_id')
     
    class Meta:
        db_table = quickpackitems

    def __str__(self):
        return str(self.quick_pack_item_id)
    
class Workflow(models.Model):
    workflow_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = workflow

    def __str__(self):
        return self.name

class WorkflowStage(models.Model):
    stage_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='stages')
    stage_name = models.CharField(max_length=255)
    stage_order = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = workflowstages

    def __str__(self):
        return f"{self.stage_name} (Order: {self.stage_order})"
    

class SaleReceipt(models.Model):
    sale_receipt_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale_invoice_id = models.ForeignKey('SaleInvoiceOrders', on_delete=models.CASCADE, db_column='sale_invoice_id')
    receipt_name = models.CharField(max_length=255)
    description = models.CharField(max_length=1024, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = salereceipts

    def __str__(self):
        return self.receipt_name