import uuid
from django.db import models
from apps import products
from apps.customer.models import CustomerAddresses, LedgerAccounts, Customer
from apps.masters.models import CustomerPaymentTerms, GstTypes, ProductBrands, CustomerCategories, SaleTypes, UnitOptions, OrderStatuses, ReturnOptions, FlowStatus
from apps.products.models import Products, Size, Color
from apps.users.models import ModuleSections
from config.utils_variables import quickpackitems, quickpacks, saleorders, paymenttransactions, saleinvoiceitemstable, salespricelist, saleorderitemstable, saleinvoiceorderstable, salereturnorderstable, salereturnitemstable, orderattachmentstable, ordershipmentstable, workflow, workflowstages, salereceipts, default_workflow_name, default_workflow_stages, salecreditnote, salecreditnoteitems, saledebitnote, saledebitnoteitems
from config.utils_methods import OrderNumberMixin, get_active_workflow, get_section_id, generate_order_number
import logging
from django.core.exceptions import ObjectDoesNotExist

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
        ('Exclusive', 'Exclusive'),
        ('Inclusive', 'Inclusive')
        ]
    tax = models.CharField(max_length=10, choices=TAX_CHOICES, null=True, default=None)
    SALE_ESTIMATE_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No')
    ]
    sale_estimate = models.CharField(max_length=3, choices=SALE_ESTIMATE_CHOICES, default='No')
    flow_status_id = models.ForeignKey(FlowStatus, on_delete=models.CASCADE, db_column='flow_status_id', null=True, default=None)
    # workflow_id = models.ForeignKey('Workflow', on_delete=models.CASCADE, db_column='workflow_id')
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
    sale_return_id = models.ForeignKey('sales.SaleReturnOrders', on_delete=models.CASCADE, null=True, default=None, db_column='sale_return_id')
    shipping_address = models.CharField(max_length=1024, null=True, default=None)
    billing_address = models.CharField(max_length=1024, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.sale_order_id}'
    
    class Meta:
        db_table = saleorders
        ordering = ['-created_at', '-updated_at']
        
    def save(self, *args, **kwargs):
        from apps.masters.views import increment_order_number

        # Determine if this is a new record based on the `_state.adding` property
        is_new_record = self._state.adding

        # Set the order status to "Pending" if not already set
        if not self.order_status_id:
            self.order_status_id = OrderStatuses.objects.get_or_create(status_name='Pending')[0]

        # Only assign the flow_status_id when creating a new sale order
        if is_new_record or self.flow_status_id is None:  # Check if it's a new order or if flow_status_id is None
            try:
                print("Assigning flow_status_id to the first stage...")

                # Fetch the section ID for Sale Order
                section_id = get_section_id('Sale Order')
                print(f"Section ID for 'Sale Order': {section_id}")

                # Fetch the active workflow for this section
                workflow = get_active_workflow(section_id)
                print(f"Active Workflow: {workflow}")

                if workflow:
                    # Fetch the first stage of the workflow (ensure stage_order=1)
                    first_stage = WorkflowStage.objects.filter(workflow_id=workflow.workflow_id, stage_order=1).first()
                    print(f"First Stage: {first_stage}")

                    if first_stage:
                        # Explicitly reset flow_status_id to ensure it starts at the first stage
                        self.flow_status_id = first_stage.flow_status_id
                        print(f"Assigned flow_status_id: {self.flow_status_id}")
                    else:
                        print(f"No Stage 1 found for workflow {workflow.workflow_id}")
                else:
                    print(f"No active workflow found for section_id: {section_id}")

            except Exception as e:
                print(f"Error during SaleOrder save: {str(e)}")

        # Check if flow_status_id is set to "Completed"
        try:
            # Assuming the "Completed" status has a specific name or identifier in FlowStatus
            completed_status = FlowStatus.objects.get(flow_status_name="Completed")
            
            if self.flow_status_id == completed_status:
                # Set the order status to "Completed" if flow_status_id is "Completed"
                self.order_status_id = OrderStatuses.objects.get_or_create(status_name='Completed')[0]
                print("Order status set to Completed")
        
        except ObjectDoesNotExist:
            print("Completed flow status or order status does not exist")

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
    size_id = models.ForeignKey(Size, on_delete=models.CASCADE, null=True, db_column='size_id')
    color_id = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, db_column='color_id')    
    print_name = models.CharField(max_length=255, null=True, default=None)
    quantity = models.IntegerField(null=True, default=None) #changed to Integerfield
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
    TAX_CHOICES = [('Exclusive', 'Exclusive'),('Inclusive', 'Inclusive')]
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
        ordering = ['-created_at', '-updated_at']

    def __str__(self):
        return str(self.sale_invoice_id)
    
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

        # Save the record
        super().save(*args, **kwargs)

        # After the record is saved, increment the order number sequence only for new records
        if is_new_record:
            print("from create", self.pk)
            increment_order_number(self.order_no_prefix)
        else:
            print("from edit", self.pk)

    
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
    size_id = models.ForeignKey(Size, on_delete=models.CASCADE, null=True, db_column='size_id')
    color_id = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, db_column='color_id')
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
    return_option_id = models.ForeignKey(ReturnOptions, on_delete=models.CASCADE, null=True, db_column='return_option_id')
    gst_type_id = models.ForeignKey('masters.GstTypes', on_delete=models.CASCADE, db_column='gst_type_id', null=True, default=None)
    email = models.EmailField(max_length=255, null=True, default=None)
    ref_no = models.CharField(max_length=255, null=True, default=None)
    ref_date = models.DateField()
    order_salesman_id = models.ForeignKey('masters.OrdersSalesman', on_delete=models.CASCADE, db_column='order_salesman_id', null=True, default=None)
    against_bill = models.CharField(max_length=255, null=True, default=None)
    against_bill_date = models.DateField(null=True, default=None)
    TAX_CHOICES = [('Exclusive', 'Exclusive'),('Inclusive', 'Inclusive')]
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
        ordering = ['-created_at', '-updated_at']

    def __str__(self):
        return str(self.sale_return_id)
    
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
    
class SaleReturnItems(models.Model):
    sale_return_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale_return_id = models.ForeignKey(SaleReturnOrders, on_delete=models.CASCADE, db_column='sale_return_id')
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, db_column='product_id')
    unit_options_id = models.ForeignKey(UnitOptions, on_delete=models.CASCADE, db_column='unit_options_id')
    size_id = models.ForeignKey(Size, on_delete=models.CASCADE, null=True, db_column='size_id')
    color_id = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, db_column='color_id')    
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
    shipping_date = models.DateField(null=True, default=None)
    shipping_charges = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None)
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

        # Save the record
        super().save(*args, **kwargs)

        # After the record is saved, increment the order number sequence only for new records
        if is_new_record:
            print("from create", self.pk)
            increment_order_number(self.order_no_prefix)
        else:
            print("from edit", self.pk)

class QuickPacks(models.Model):
    quick_pack_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=512, null=True, default=None)
    active = models.CharField(max_length=1, choices=[('N', 'No'),('Y', 'Yes')], null=True, default='Y')
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
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = workflow

    def __str__(self):
        return self.name

class WorkflowStage(models.Model):
    workflow_stage_id  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow_id = models.ForeignKey(Workflow, on_delete=models.CASCADE, db_column='workflow_id')
    # stage_name = models.CharField(max_length=255)
    stage_order = models.IntegerField()
    description = models.CharField(max_length=255, null=True, default=None)
    section_id = models.ForeignKey(ModuleSections, on_delete=models.CASCADE,  db_column = 'section_id')
    flow_status_id = models.ForeignKey(FlowStatus, on_delete=models.CASCADE, db_column='flow_status_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = workflowstages

    def __str__(self):
        return f"{self.section_id.section_name} (Order: {self.stage_order})"
    

class SaleReceipt(models.Model):
    sale_receipt_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale_invoice_id = models.ForeignKey('SaleInvoiceOrders', on_delete=models.CASCADE, db_column='sale_invoice_id')
    receipt_name = models.CharField(max_length=255)
    description = models.CharField(max_length=1024, null=True, default=None)
    receipt_path = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = salereceipts

    def __str__(self):
        return self.receipt_name
    
class SaleCreditNotes(OrderNumberMixin):
    credit_note_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale_invoice_id = models.ForeignKey(SaleInvoiceOrders, on_delete=models.CASCADE, db_column='sale_invoice_id')
    sale_return_id = models.ForeignKey(SaleReturnOrders, on_delete=models.CASCADE, null=True, default=None, db_column='sale_return_id')
    credit_note_number = models.CharField(max_length=100, unique=True, default='')
    order_no_prefix = 'CN'
    order_no_field = 'credit_note_number'
    credit_date = models.DateField(auto_now=True)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='customer_id')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=None)
    reason = models.CharField(max_length=1024, null=True, default=None)
    order_status_id = models.ForeignKey(OrderStatuses, on_delete=models.CASCADE, null=True, default=None, db_column='order_status_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.credit_note_number}'
    
    class Meta:
        db_table = salecreditnote
        
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
    
class SaleCreditNoteItems(models.Model):
    credit_note_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    credit_note_id = models.ForeignKey(SaleCreditNotes, on_delete=models.CASCADE, db_column='credit_note_id')
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, db_column='product_id')
    quantity = models.IntegerField(default=None)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=None)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
        
    def __str__(self):
        return f'{self.credit_note_item_id}'
    
    
    class Meta:
        db_table = salecreditnoteitems
        
class SaleDebitNotes(OrderNumberMixin):
    debit_note_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sale_invoice_id = models.ForeignKey(SaleInvoiceOrders, on_delete=models.CASCADE, db_column='sale_invoice_id')
    sale_return_id = models.ForeignKey(SaleReturnOrders, on_delete=models.CASCADE, null=True, default=None, db_column='sale_return_id')
    debit_note_number = models.CharField(max_length=100, unique=True, default='')
    order_no_prefix = 'DN'
    order_no_field = 'debit_note_number'
    debit_date = models.DateField(auto_now=True)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='customer_id')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=None)
    reason = models.CharField(max_length=1024, null=True, default=None)
    order_status_id = models.ForeignKey(OrderStatuses, on_delete=models.CASCADE, null=True, default=None, db_column='order_status_id')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'{self.debit_note_number}'
    
    class Meta:
        db_table = saledebitnote
        
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

    
class SaleDebitNoteItems(models.Model):
    debit_note_item_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    debit_note_id = models.ForeignKey(SaleDebitNotes, on_delete=models.CASCADE, db_column='debit_note_id')
    product_id = models.ForeignKey(Products, on_delete=models.CASCADE, db_column='product_id')
    quantity = models.IntegerField(default=None)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=None)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
        
    def __str__(self):
        return f'{self.debit_note_item_id}'
    
    
    class Meta:
        db_table = saledebitnoteitems