from apps.masters.serializers import ModCustomerCategoriesSerializers, ModGstTypesSerializer, ModProductBrandsSerializer, ModSaleTypesSerializer, ModShippingCompaniesSerializer, ModUnitOptionsSerializer, ShippingModesSerializer, ModOrdersSalesmanSerializer, ModPaymentLinkTypesSerializer, ModOrderStatusesSerializer, ModOrderTypesSerializer, ReturnOptionsSerializers, ModFlowstatusSerializer
from apps.customer.serializers import ModCustomerAddressesSerializer, ModCustomersSerializer, ModCustomerPaymentTermsSerializers, ModLedgerAccountsSerializers
from apps.products.serializers import ColorSerializer, ModProductGroupsSerializer, ModproductsSerializer, SizeSerializer
from apps.users.serializers import ModModuleSectionsSerializer
from rest_framework import serializers
from .models import *

#----------Modified Serializers--------------------------

class ModSaleOrderSerializer(serializers.ModelSerializer):
    customer = ModCustomersSerializer(source='customer_id', read_only=True)
    class Meta:
        model = SaleOrder
        fields = ['sale_order_id','customer','order_date','delivery_date', 'sale_estimate']

class UdfSaleOrderSerializer(serializers.ModelSerializer):
    status_name = serializers.SerializerMethodField()
    class Meta:
        model = SaleOrder
        fields = ['sale_order_id','order_no','flow_status_id','status_name']

    def get_status_name(self, obj):
        return obj.flow_status_id.flow_status_name if obj.flow_status_id else None

class ModSaleReturnOrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleReturnOrders
        fields = ['sale_return_id','return_date','return_no']

class ModSaleInvoiceOrdersSerializer(serializers.ModelSerializer):
    customer = ModCustomersSerializer(source='customer_id', read_only=True)
    class Meta:
        model = SaleInvoiceOrders
        fields = ['sale_invoice_id','invoice_date','invoice_no','customer']

class ModSaleOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleOrderItems
        fields = ['sale_order_item_id','amount']

class ModWorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = ['workflow_id','name']
# -------------------------------------------------------

class SaleOrderSerializer(serializers.ModelSerializer):
    gst_type = ModGstTypesSerializer(source='gst_type_id', read_only=True)
    customer = ModCustomersSerializer(source='customer_id', read_only=True)
    customer_address = ModCustomerAddressesSerializer(source='customer_address_id', read_only=True)
    payment_term = ModCustomerPaymentTermsSerializers(source='payment_term_id', read_only=True)
    sale_type = ModSaleTypesSerializer(source='sale_type_id', read_only=True)
    ledger_account = ModLedgerAccountsSerializers(source='ledger_account_id', read_only=True)
    order_status = ModOrderStatusesSerializer(source='order_status_id',read_only=True)
    # workflow = ModWorkflowSerializer(source='workflow_id',read_only=True)
    sale_return = ModSaleReturnOrdersSerializer(source='sale_return_id', read_only=True)
    flow_status = ModFlowstatusSerializer(source='flow_status_id', read_only=True)
    
    class Meta:
        model = SaleOrder
        fields = '__all__'
        
class SaleInvoiceItemsSerializer(serializers.ModelSerializer):
    sale_order = ModSaleOrderSerializer(source='sale_order_id', read_only=True)
    product = ModproductsSerializer(source='product_id', read_only=True)
    unit_options = ModUnitOptionsSerializer(source='unit_options_id', read_only=True)
    size = SizeSerializer(source='size_id',read_only=True)
    color = ColorSerializer(source='color_id',read_only=True)       

    class Meta:
        model = SaleInvoiceItems
        fields = '__all__'

class SalesPriceListSerializer(serializers.ModelSerializer):
    customer_category = ModCustomerCategoriesSerializers(source='customer_category_id', read_only=True)
    brand = ModProductBrandsSerializer(source='brand_id', read_only=True)
    group = ModProductGroupsSerializer(source='product_group_id', read_only=True)
    class Meta:
        model = SalesPriceList
        fields = '__all__'

class SaleOrderItemsSerializer(serializers.ModelSerializer):
    sale_order = ModSaleOrderSerializer(source='sale_order_id', read_only=True)
    product = ModproductsSerializer(source='product_id', read_only=True)
    unit_options = ModUnitOptionsSerializer(source='unit_options_id', read_only=True)
    size = SizeSerializer(source='size_id',read_only=True)
    color = ColorSerializer(source='color_id',read_only=True)    

    class Meta:
        model = SaleOrderItems
        fields = '__all__'

class SaleInvoiceOrdersSerializer(serializers.ModelSerializer):
    gst_type = ModGstTypesSerializer(source='gst_type_id', read_only=True)
    customer = ModCustomersSerializer(source='customer_id', read_only=True)
    customer_address = ModCustomerAddressesSerializer(source='customer_address_id', read_only=True)
    payment_term = ModCustomerPaymentTermsSerializers(source='payment_term_id', read_only=True)
    orders_salesman = ModOrdersSalesmanSerializer(source='order_salesman_id', read_only=True)
    payment_link_type = ModPaymentLinkTypesSerializer(source='payment_link_type_id', read_only=True)
    ledger_account = ModLedgerAccountsSerializers(source='ledger_account_id', read_only=True)
    order_status = ModOrderStatusesSerializer(source='order_status_id', read_only=True)
    sale_order = ModSaleOrderSerializer(source='sale_order_id', read_only=True)
    
    class Meta:
        model = SaleInvoiceOrders
        fields = '__all__'

class SaleReturnOrdersSerializer(serializers.ModelSerializer):
    gst_type = ModGstTypesSerializer(source='gst_type_id', read_only=True)
    customer = ModCustomersSerializer(source='customer_id', read_only=True)
    customer_address = ModCustomerAddressesSerializer(source='customer_address_id', read_only=True)
    payment_term = ModCustomerPaymentTermsSerializers(source='payment_term_id', read_only=True)
    orders_salesman = ModOrdersSalesmanSerializer(source='order_salesman_id', read_only=True)
    payment_link_type = ModPaymentLinkTypesSerializer(source='payment_link_type_id', read_only=True)
    order_status = ModOrderStatusesSerializer(source='order_status_id', read_only=True)
    sale_invoice = ModSaleInvoiceOrdersSerializer(source='sale_invoice_id', read_only=True)
    return_option = ReturnOptionsSerializers(source='return_option_id', read_only=True)

    class Meta:
        model = SaleReturnOrders
        fields = '__all__'
    
class SaleReturnItemsSerializer(serializers.ModelSerializer):
    sale_return = ModSaleReturnOrdersSerializer(source='sale_return_id', read_only=True)
    product = ModproductsSerializer(source='product_id', read_only=True)
    unit_options = ModUnitOptionsSerializer(source='unit_options_id', read_only=True)
    size = SizeSerializer(source='size_id',read_only=True)
    color = ColorSerializer(source='color_id',read_only=True)
    
    class Meta:
        model = SaleReturnItems
        fields = '__all__'

class OrderAttachmentsSerializer(serializers.ModelSerializer):
    order_type = ModOrderTypesSerializer(source='order_type_id', read_only=True)

    class Meta:
        model = OrderAttachments
        fields = '__all__'

class OrderShipmentsSerializer(serializers.ModelSerializer):
    shipping_mode = ShippingModesSerializer(source='shipping_mode_id', read_only=True)
    shipping_company = ModShippingCompaniesSerializer(source='shipping_company_id', read_only=True)
    order_type = ModOrderTypesSerializer(source='order_type_id', read_only=True)

    class Meta:
        model = OrderShipments
        fields = '__all__'

class SaleOrderOptionsSerializer(serializers.ModelSerializer):
    customer = ModCustomersSerializer(source='customer_id', read_only=True)
    sale_type = ModSaleTypesSerializer(source='sale_type_id', read_only=True)
    amount = serializers.SerializerMethodField()
    order_status = ModOrderStatusesSerializer(source='order_status_id', read_only=True)
    flow_status = ModFlowstatusSerializer(source='flow_status_id', read_only=True)
    products = serializers.SerializerMethodField()  # New field for products
    invoice_no = serializers.SerializerMethodField()

    class Meta:
        model = SaleOrder
        fields = ['sale_order_id', 'order_no', 'order_date', 'sale_estimate', 'tax', 'tax_amount', 'total_amount', 'amount', 'advance_amount', 'customer', 'products', 'sale_type', 'order_status', 'flow_status', 'remarks', 'invoice_no', 'created_at', 'updated_at']

    def get_sale_order_details(self, obj):
        sale_order_items = SaleOrderItems.objects.filter(sale_order_id=obj.sale_order_id)
        
        amount = 0
        
        for saleorderamount in sale_order_items:
            item_amount = saleorderamount.amount
            if item_amount is not None:
                amount += item_amount
        
        return amount

    def get_amount(self, obj):
        return self.get_sale_order_details(obj)
    
    def get_products(self, obj):
        # Detect DB used by the sale order instance
        db_alias = obj._state.db

        # Fetch sale order items and their associated products
        sale_order_items = SaleOrderItems.objects.using(db_alias).filter(sale_order_id=obj.sale_order_id)
        products = []
        
        for item in sale_order_items:
            product = item.product_id 
            if product:
                product_data = {
                    "product_id": product.product_id,
                    "product_name": product.name,
                    "quantity": item.quantity,
                    "work_order_created": item.work_order_created  # Include the field here
                }
                products.append(product_data)
        
        return products
    
    def get_invoice_no(self, obj):
        # Detect DB used by the sale order instance
        db_alias = obj._state.db
        
    # Retrieve all associated SaleInvoiceOrders instances
        sale_invoices = SaleInvoiceOrders.objects.using(db_alias).filter(sale_order_id=obj.sale_order_id)
        
        if sale_invoices.exists():
            # Collect all invoice numbers and return as a list
            return [invoice.invoice_no for invoice in sale_invoices]
        else:
            # Return None if no invoices are associated
            return None

        
    @staticmethod
    def get_sale_order_summary(sale_order):
        serializer = SaleOrderOptionsSerializer(sale_order, many=True)
        return {
            "count": len(serializer.data),
            "msg": "SUCCESS",
            "data": serializer.data
        }

class SaleInvoiceOrderOptionsSerializer(serializers.ModelSerializer):
    customer = ModCustomersSerializer(source='customer_id', read_only=True)
    order_status = ModOrderStatusesSerializer(source='order_status_id', read_only=True)

    class Meta:
        model = SaleInvoiceOrders
        fields = ['sale_invoice_id', 'invoice_no',  'invoice_date', 'tax', 'advance_amount', 'total_amount', 'tax_amount', 'customer', 'order_status', 'remarks', 'created_at', 'updated_at']

    def get_sale_invoice_order_summary(sale_invoice_order):
        serializer = SaleInvoiceOrderOptionsSerializer(sale_invoice_order, many=True)
        return serializer.data

class SaleReturnOrdersOptionsSerializer(serializers.ModelSerializer):
    customer = ModCustomersSerializer(source='customer_id', read_only=True)
    order_status = ModOrderStatusesSerializer(source='order_status_id', read_only=True)

    class Meta:
        model = SaleReturnOrders
        fields = ['sale_return_id', 'return_no', 'return_date', 'tax', 'return_reason', 'total_amount', 'due_date', 'tax_amount', 'customer', 'order_status', 'remarks', 'created_at', 'updated_at']

    def get_sale_return_orders_summary(sale_return_order):
        serializer = SaleReturnOrdersOptionsSerializer(sale_return_order, many=True)
        return serializer.data
           
class ModQuickPackSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuickPacks
        fields = ['quick_pack_id','name'] 

class QuickPackSerializer(serializers.ModelSerializer):
    customer = ModCustomersSerializer(source='customer_id', read_only=True)
    
    class Meta:
        model = QuickPacks
        fields = '__all__'

class ModQuickPackItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuickPackItems
        fields = ['quick_pack_item_id'] 

class QuickPackItemSerializer(serializers.ModelSerializer):
    product = ModproductsSerializer(source='product_id', read_only=True)
    quickpack = ModQuickPackSerializer(source='quick_pack_id', read_only=True)
    size = SizeSerializer(source='size_id',read_only=True)
    color = ColorSerializer(source='color_id',read_only=True) 

    class Meta:
        model = QuickPackItems
        fields = '__all__'

class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = '__all__'

class WorkflowStageSerializer(serializers.ModelSerializer):
    workflow = ModWorkflowSerializer(source='workflow_id', read_only=True)
    section = ModModuleSectionsSerializer(source='section_id', read_only=True)
    flow_status = ModFlowstatusSerializer(source='flow_status_id', read_only=True)

    class Meta:
        model = WorkflowStage
        fields = '__all__'

# class SaleReceiptSerializer(serializers.ModelSerializer):
#     sale_invoice = ModSaleInvoiceOrdersSerializer(source='sale_invoice_id', read_only=True)

#     class Meta:
#         model = SaleReceipt
#         fields = '__all__'

class SaleReceiptSerializer(serializers.ModelSerializer):
    sale_invoice = ModSaleInvoiceOrdersSerializer(source='sale_invoice_id', read_only=True)

    class Meta:
        model = SaleReceipt
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        db_alias = self.context.get('db_alias', 'default')
        # Dynamically set queryset for FK based on db_alias
        self.fields['sale_invoice_id'].queryset = SaleInvoiceOrders.objects.using(db_alias).all()

    def create(self, validated_data):
        db_alias = self.context.get('db_alias', None)
        if db_alias:
            return SaleReceipt.objects.using(db_alias).create(**validated_data)
        return super().create(validated_data)

        
class SaleCreditNoteSerializers(serializers.ModelSerializer):
    sale_invoice = ModSaleInvoiceOrdersSerializer(source='sale_invoice_id', read_only=True)
    customer = ModCustomersSerializer(source='customer_id', read_only=True)
    order_status = ModOrderStatusesSerializer(source='order_status_id',read_only=True)
    sale_return = ModSaleReturnOrdersSerializer(source='sale_return_id', read_only=True)
    
    class Meta:
        model = SaleCreditNotes
        fields = '__all__'

class ModSaleCreditNoteSerializers(serializers.ModelSerializer):
    class Meta:
        model = SaleCreditNotes
        fields = ['credit_note_id', 'credit_note_number', 'reason']
        
class SaleCreditNoteItemsSerializers(serializers.ModelSerializer):
    credit_note = ModSaleCreditNoteSerializers(source='credit_note_id', read_only=True)
    product = ModproductsSerializer(source='product_id', read_only=True)
    
    class Meta:
        model = SaleCreditNoteItems
        fields = '__all__'
        
class SaleDebitNoteSerializers(serializers.ModelSerializer):
    sale_invoice = ModSaleInvoiceOrdersSerializer(source='sale_invoice_id', read_only=True)
    customer = ModCustomersSerializer(source='customer_id', read_only=True)
    order_status = ModOrderStatusesSerializer(source='order_status_id',read_only=True)
    sale_return = ModSaleReturnOrdersSerializer(source='sale_return_id', read_only=True)
    
    class Meta:
        model = SaleDebitNotes
        fields = '__all__'

class ModSaleDebitNoteSerializers(serializers.ModelSerializer):
    class Meta:
        model = SaleDebitNotes
        fields = ['debit_note_id', 'debit_note_number', 'reason']
        
class SaleDebitNoteItemsSerializers(serializers.ModelSerializer):
    debit_note = ModSaleDebitNoteSerializers(source='debit_note_id', read_only=True)
    product = ModproductsSerializer(source='product_id', read_only=True)
    
    class Meta:
        model = SaleDebitNoteItems
        fields = '__all__'

class PaymentTransactionSerializer(serializers.ModelSerializer):
    # Fields from SaleInvoiceOrders via the sale_invoice foreign key
    invoice_no = serializers.CharField(source='sale_invoice.invoice_no')
    invoice_date = serializers.DateField(source='sale_invoice.invoice_date')
    due_date = serializers.DateField(source='sale_invoice.due_date')
    ref_date = serializers.DateField(source='sale_invoice.ref_date')
    total_amount = serializers.DecimalField(source='sale_invoice.total_amount', max_digits=18, decimal_places=2)
    taxable = serializers.DecimalField(source='sale_invoice.taxable', max_digits=18, decimal_places=2)
    tax_amount = serializers.DecimalField(source='sale_invoice.tax_amount', max_digits=18, decimal_places=2)
    # customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_name = serializers.CharField(source='sale_invoice.customer_id.name', read_only=True)

    class Meta:
        model = PaymentTransactions
        fields = ['transaction_id', 'invoice_no','customer','customer_name','invoice_date', 'amount', 'due_date', 'payment_receipt_no', 'payment_date', 'payment_method', 'total_amount', 'outstanding_amount', 'adjusted_now', 'payment_status', 'ref_date', 'taxable', 'tax_amount']

class SalesByProductReportSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source="product_id__name")  
    total_quantity_sold = serializers.IntegerField()
    total_sales = serializers.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        model = SaleOrderItems
        fields = [ "product", "total_quantity_sold","total_sales"]
    
    
class SalesByCustomerSerializer(serializers.Serializer):
    customer = serializers.CharField()
    total_sales = serializers.DecimalField(max_digits=18, decimal_places=2)
    
    
class SalesOrderReportSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(source='customer_id.name')
    sale_type = serializers.CharField(source='sale_type_id')
    order_status = ModOrderStatusesSerializer(source='order_status_id',read_only=True)
    amount = serializers.DecimalField(source='item_value', max_digits=18, decimal_places=2)

    class Meta:
        model = SaleOrder
        fields = ['order_no', 'customer', 'order_date', 'sale_type','order_status','amount']
        

class SalesInvoiceReportSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(source='customer_id.name')
    order_status = ModOrderStatusesSerializer(source='order_status_id',read_only=True)

    class Meta:
        model = SaleInvoiceOrders
        fields = ['invoice_no','invoice_date','customer','bill_type','item_value','dis_amt','tax_amount','total_amount','due_date','order_status']

    def get_payment_status(self, obj):
        # Check if order_status_id exists and return its status_name; otherwise, return None.
        if obj.order_status_id:
            return obj.order_status_id.status_name
        return None


class OutstandingSalesSerializer(serializers.Serializer):
    customer = serializers.CharField()
    total_invoice = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_pending = serializers.DecimalField(max_digits=18, decimal_places=2)
    
class SalesTaxByProductReportSerializer(serializers.Serializer):
    product = serializers.CharField()
    gst_type = serializers.CharField()
    total_sales = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_tax = serializers.DecimalField(max_digits=18, decimal_places=2)

class SalespersonPerformanceReportSerializer(serializers.Serializer):
    salesperson = serializers.CharField()
    total_sales = serializers.DecimalField(max_digits=18, decimal_places=2)
    
class ProfitMarginReportSerializer(serializers.Serializer):
    product = serializers.CharField()
    total_sales = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_cost = serializers.DecimalField(max_digits=18, decimal_places=2)
    profit = serializers.DecimalField(max_digits=18, decimal_places=2)
    profit_margin = serializers.DecimalField(max_digits=5, decimal_places=2)    
       
class AgingReportSerializer(serializers.ModelSerializer):
    aging_category = serializers.CharField(read_only=True)
    pending_amount = serializers.DecimalField(max_digits=18, decimal_places=2, read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)

    class Meta:
        model = SaleInvoiceOrders
        fields = ['invoice_no', 'due_date', 'pending_amount', 'days_overdue', 'aging_category']       
        
class MstcnlSaleOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MstcnlSaleOrder
        fields = '__all__'
        
class MstcnlSaleInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MstcnlSaleInvoiceOrder
        fields = '__all__'
        
class MstcnlSaleOrderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MstcnlSaleOrderItem
        fields = '__all__'
        
class MstcnlSaleInvoiceItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MstcnlSaleInvoiceItem
        fields = '__all__'

class MstcnlOrderAttachmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MstcnlOrderAttachment
        fields = '__all__'

class MstcnlOrderShipmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MstcnlOrderShipment
        fields = '__all__'
        
class MstcnlCustomFieldValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = MstcnlCustomFieldValue
        fields = '__all__'