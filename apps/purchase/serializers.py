from rest_framework import serializers
from .models import *
from .serializers import *
from apps.vendor.serializers import ModVendorSerializer,ModVendorAgentSerializer,VendorAddressSerializer,ModVendorPaymentTermsSerializer
from apps.masters.serializers import ModOrderStatusesSerializer, ModProductBrandsSerializer, ModUnitOptionsSerializer, PurchaseTypesSerializer, ModGstTypesSerializer, ModPurchaseTypesSerializer
from apps.customer.serializers import ModLedgerAccountsSerializers,ModCustomersSerializer
from apps.products.serializers import ColorSerializer, ModproductsSerializer, SizeSerializer


class ModPurchaseOrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrders
        fields = ['purchase_order_id','email','delivery_date','order_date','order_no','ref_no','ref_date']

class PurchaseOrdersSerializer(serializers.ModelSerializer):
    gst_type = ModGstTypesSerializer(source='gst_type_id',read_only=True)
    vendor = ModVendorSerializer(source='vendor_id',read_only=True)
    vendor_agent = ModVendorAgentSerializer(source='vendor_agent_id',read_only=True)
    vendor_address = VendorAddressSerializer(source='vendor_address_id',read_only=True)
    payment_term = ModVendorPaymentTermsSerializer(source='payment_term_id',read_only=True)
    purchase_type = PurchaseTypesSerializer(source='purchase_type_id',read_only=True)
    ledger_account = ModLedgerAccountsSerializers(source='ledger_account_id',read_only=True)
    order_status = ModOrderStatusesSerializer(source='order_status_id',read_only=True)

    class Meta:
        model = PurchaseOrders
        fields = '__all__'

class ModPurchaseorderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseorderItems
        fields = ['purchaseorder_item_id','print_name','quantity', 'amount']

class PurchaseorderItemsSerializer(serializers.ModelSerializer):
    purchaseorder = ModPurchaseOrdersSerializer(source='purchase_order_id',read_only=True)
    product = ModproductsSerializer(source='product_id',read_only=True)
    unit_options = ModUnitOptionsSerializer(source='unit_options_id', read_only=True)
    size = SizeSerializer(source='size_id',read_only=True)
    color = ColorSerializer(source='color_id',read_only=True)    
    class Meta:
        model = PurchaseorderItems
        fields = '__all__'
        
class ModPurchaseInvoiceOrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseInvoiceOrders
        fields = ['purchase_invoice_id', 'invoice_no']

class PurchaseInvoiceOrdersSerializer(serializers.ModelSerializer):
    gst_type = ModGstTypesSerializer(source='gst_type_id',read_only=True)
    vendor = ModVendorSerializer(source='vendor_id',read_only=True)
    vendor_agent = ModVendorAgentSerializer(source='vendor_agent_id',read_only=True)
    vendor_address = VendorAddressSerializer(source='vendor_address_id',read_only=True)
    payment_term = ModVendorPaymentTermsSerializer(source='payment_term_id',read_only=True)
    purchase_type = PurchaseTypesSerializer(source='purchase_type_id',read_only=True)
    ledger_account = ModLedgerAccountsSerializers(source='ledger_account_id',read_only=True)
    order_status = ModOrderStatusesSerializer(source='order_status_id',read_only=True)
    
        
    class Meta:
        model = PurchaseInvoiceOrders
        fields = '__all__'

class ModPurchaseInvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseInvoiceItem
        fields = ['purchase_invoice_item_id','print_name','quantity', 'amount']

class PurchaseInvoiceItemSerializer(serializers.ModelSerializer):
    purchase_invoice = ModPurchaseInvoiceOrdersSerializer(source='purchase_invoice_id',read_only=True)
    product = ModproductsSerializer(source='product_id',read_only=True)
    unit_options = ModUnitOptionsSerializer(source='unit_options_id', read_only=True)
    size = SizeSerializer(source='size_id',read_only=True)
    color = ColorSerializer(source='color_id',read_only=True)      
    class Meta:
        model = PurchaseInvoiceItem
        fields = '__all__'

class ModPurchaseReturnOrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseReturnOrders
        fields = ['purchase_return_id', 'return_date', 'return_no']

class PurchaseReturnOrdersSerializer(serializers.ModelSerializer):
    purchase_type = PurchaseTypesSerializer(source='purchase_type_id',read_only=True)
    gst_type = ModGstTypesSerializer(source='gst_type_id',read_only=True)
    vendor = ModVendorSerializer(source='vendor_id',read_only=True)
    vendor_agent = ModVendorAgentSerializer(source='vendor_agent_id',read_only=True)
    vendor_address = VendorAddressSerializer(source='vendor_address_id',read_only=True)
    payment_term = ModVendorPaymentTermsSerializer(source='payment_term_id',read_only=True)
    order_status = ModOrderStatusesSerializer(source='order_status_id',read_only=True)   

    class Meta:
        model = PurchaseReturnOrders
        fields = '__all__'
        
class ModPurchaseReturnItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseReturnItems
        fields = ['purchase_return_item_id', 'print_name','quantity', 'amount']

class PurchaseReturnItemsSerializer(serializers.ModelSerializer):
    purchase_return = ModPurchaseReturnOrdersSerializer(source='purchase_return_id',read_only=True)
    product = ModproductsSerializer(source='product_id',read_only=True)
    unit_options = ModUnitOptionsSerializer(source='unit_options_id', read_only=True)
    size = SizeSerializer(source='size_id',read_only=True)
    color = ColorSerializer(source='color_id',read_only=True)      
    class Meta:
        model = PurchaseReturnItems
        fields = '__all__'

class ModPurchasePriceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasePriceList
        fields = ['purchase_price_list_id','description']

class PurchasePriceListSerializer(serializers.ModelSerializer):
    customer_category = ModCustomersSerializer(source='customer_category_id',read_only=True)
    brand = ModProductBrandsSerializer(source='brand_id',read_only=True)

    class Meta:
        model = PurchasePriceList
        fields = '__all__'

class PurchaseOrdersOptionsSerializer(serializers.ModelSerializer):
    vendor = ModVendorSerializer(source='vendor_id', read_only=True)
    purchase_type = ModPurchaseTypesSerializer(source='purchase_type_id', read_only=True)
    amount = serializers.SerializerMethodField()
    order_status = ModOrderStatusesSerializer(source='order_status_id', read_only=True)
    products = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseOrders
        fields = ['purchase_order_id', 'order_no', 'order_date', 'amount', 'products', 'tax', 'tax_amount','total_amount', 'vendor', 'purchase_type', 'order_status', 'remarks', 'created_at', 'updated_at', 'is_deleted']
 
    def get_purchase_orders_summary(purchase_orders):
        serializer = PurchaseOrdersOptionsSerializer(purchase_orders, many=True)
        return serializer.data
    
    def get_purchase_order_details(self, obj):
        purchase_order_items = PurchaseorderItems.objects.filter(purchase_order_id=obj.purchase_order_id)
        
        amount = 0
        
        for purchaseorderamount in purchase_order_items:
            item_amount = purchaseorderamount.amount
            if item_amount is not None:
                amount += item_amount
        
        return amount
    
    def get_amount(self, obj):
        return self.get_purchase_order_details(obj)
    
    def get_products(self, obj):
        # Fetch sale order items and their associated products
        purchase_order_items = PurchaseorderItems.objects.filter(purchase_order_id=obj.purchase_order_id)
        products = []
        
        for item in purchase_order_items:
            product = item.product_id 
            if product:
                product_data = {
                    "product_id": product.product_id,
                    "product_name": product.name,
                    "quantity": item.quantity,
                }
                products.append(product_data)
        
        return products

class PurchaseReturnOrdersOptionsSerializer(serializers.ModelSerializer):
    vendor = ModVendorSerializer(source='vendor_id', read_only=True)
    purchase_type = ModPurchaseTypesSerializer(source='purchase_type_id', read_only=True)
    order_status = ModOrderStatusesSerializer(source='order_status_id', read_only=True)

    class Meta:
        model = PurchaseReturnOrders
        fields = ['purchase_return_id', 'return_no', 'due_date', 'tax', 'total_amount', 'tax_amount', 'return_reason', 'vendor', 'purchase_type', 'order_status', 'remarks', 'created_at', 'updated_at', 'is_deleted']
    
    def get_purchase_return_orders_summary(purchase_return_orders):
        serializer = PurchaseReturnOrdersOptionsSerializer(purchase_return_orders, many=True)
        return serializer.data

class PurchaseInvoiceOrdersOptionsSerializer(serializers.ModelSerializer):
    vendor = ModVendorSerializer(source='vendor_id', read_only=True)
    purchase_type = ModPurchaseTypesSerializer(source='purchase_type_id', read_only=True)
    order_status = ModOrderStatusesSerializer(source='order_status_id', read_only=True)

    class Meta:
        model = PurchaseInvoiceOrders
        fields = ['purchase_invoice_id', 'invoice_no', 'invoice_date', 'supplier_invoice_no', 'tax', 'total_amount', 'tax_amount', 'advance_amount', 'vendor','purchase_type', 'order_status', 'remarks', 'created_at', 'updated_at', 'is_deleted']
    
    def get_purchase_invoice_orders_summary(purchase_invoice_orders):
        serializer = PurchaseInvoiceOrdersOptionsSerializer(purchase_invoice_orders, many=True)
        return serializer.data
    
class LandedCostReportSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField()
    landed_cost = serializers.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        model = PurchaseInvoiceOrders
        fields = ["invoice_no","invoice_date","due_date","total_amount","advance_amount","tax_amount","cess_amount","transport_charges","dis_amt","round_off","vendor_name","landed_cost"]    
         

class PurchasesByVendorReportSerializer(serializers.Serializer):
    vendor = serializers.CharField()
    total_purchase = serializers.DecimalField(max_digits=18, decimal_places=2)
    order_count = serializers.IntegerField()

class PurchasePriceVarianceReportSerializer(serializers.ModelSerializer):
    product = serializers.CharField()
    vendor_name = serializers.CharField()
    order_date = serializers.DateField() 
    min_price = serializers.DecimalField(max_digits=18, decimal_places=2)
    max_price = serializers.DecimalField(max_digits=18, decimal_places=2)
    avg_price = serializers.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        model = PurchaseorderItems
        fields = ["product","vendor_name","order_date","min_price","max_price","avg_price"]  
    
class OutstandingPurchaseReportSerializer(serializers.Serializer):
    vendor_name = serializers.CharField()
    invoice_num = serializers.CharField()
    invoice_dates = serializers.DateField()
    due_dates = serializers.DateField()
    total_amounts = serializers.DecimalField(max_digits=18, decimal_places=2)
    advance_payments = serializers.DecimalField(max_digits=18, decimal_places=2)
    outstanding_amount = serializers.DecimalField(max_digits=18, decimal_places=2)
    payment_status = serializers.SerializerMethodField()

    def get_payment_status(self, obj):
        return "Pending" if obj["outstanding_amount"] > 0 else "Paid"
    
class StockReplenishmentReportSerializer(serializers.ModelSerializer):
    # Map each field explicitly for clarity
    name = serializers.CharField(help_text="Product name")
    current_stock = serializers.IntegerField(help_text="Current available stock")
    minimum_stock = serializers.IntegerField(source='minimum_level', help_text="Minimum required stock level")
    reorder_quantity = serializers.IntegerField(read_only=True, help_text="Quantity to reorder (minimum_stock - current_stock)")

    class Meta:
        model = Products
        fields = ['name', 'current_stock', 'minimum_stock', 'reorder_quantity']
        
#---------------- Bill Payments ---------------------------------
class BillPaymentTransactionSerializer(serializers.ModelSerializer):
    # Fields from PurchaseInvoiceOrders via the purchase_invoice foreign key
    bill_no = serializers.CharField(source='purchase_invoice.invoice_no')
    bill_date = serializers.DateField(source='purchase_invoice.invoice_date')
    due_date = serializers.DateField(source='purchase_invoice.due_date')
    ref_date = serializers.DateField(source='purchase_invoice.ref_date', allow_null=True)
    total_amount = serializers.DecimalField(source='purchase_invoice.total_amount', max_digits=18, decimal_places=2)
    pending_amount = serializers.DecimalField(source='purchase_invoice.pending_amount', max_digits=18, decimal_places=2)
    taxable = serializers.DecimalField(source='purchase_invoice.taxable', max_digits=18, decimal_places=2)
    tax_amount = serializers.DecimalField(source='purchase_invoice.tax_amount', max_digits=18, decimal_places=2)
    
    # Vendor details from related vendor_id
    vendor_name = serializers.CharField(source='purchase_invoice.vendor_id.name', read_only=True)
    vendor_id = serializers.CharField(source='purchase_invoice.vendor_id.vendor_id', read_only=True)

    class Meta:
        model = BillPaymentTransactions
        fields = [
            'transaction_id', 'account_id',
            'bill_no', 'vendor_id', 'vendor_name',
            'bill_date', 'due_date', 'ref_date',
            'amount', 'payment_receipt_no', 'payment_date',
            'payment_method', 'payment_status', 'total_amount', 'pending_amount',
            'outstanding_amount', 'adjusted_now', 'taxable', 'tax_amount'
        ]
