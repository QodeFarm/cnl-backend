from rest_framework import serializers
from .models import *
from .serializers import *
from apps.vendor.serializers import ModVendorSerializer,ModVendorAgentSerializer,VendorAddressSerializer,ModVendorPaymentTermsSerializer
from apps.masters.serializers import ModOrderStatusesSerializer, ModProductBrandsSerializer, ModUnitOptionsSerializer, PurchaseTypesSerializer, ModGstTypesSerializer, ModPurchaseTypesSerializer
from apps.customer.serializers import ModLedgerAccountsSerializers,ModCustomersSerializer
from apps.products.serializers import ModproductsSerializer


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
    vendor_id = ModVendorSerializer()
    purchase_type_id = ModPurchaseTypesSerializer()

    class Meta:
        model = PurchaseOrders
        fields = ['purchase_order_id', 'order_no', 'tax', 'advance_amount', 'remarks', 'order_date', 'tax_amount','total_amount', 'vendor_id', 'purchase_type_id']
 
    def get_purchase_orders_summary(purchase_orders):
        serializer = PurchaseOrdersOptionsSerializer(purchase_orders, many=True)
        return serializer.data

class PurchaseReturnOrdersOptionsSerializer(serializers.ModelSerializer):
    vendor_id = ModVendorSerializer()
    purchase_type_id = ModPurchaseTypesSerializer()

    class Meta:
        model = PurchaseReturnOrders
        fields = ['purchase_return_id', 'return_no', 'tax', 'return_reason', 'remarks', 'total_amount', 'due_date', 'tax_amount', 'vendor_id', 'purchase_type_id']
    
    def get_purchase_return_orders_summary(purchase_return_orders):
        serializer = PurchaseReturnOrdersOptionsSerializer(purchase_return_orders, many=True)
        return serializer.data

class PurchaseInvoiceOrdersOptionsSerializer(serializers.ModelSerializer):
    vendor_id = ModVendorSerializer()
    order_status_id = ModOrderStatusesSerializer()

    class Meta:
        model = PurchaseInvoiceOrders
        fields = ['purchase_invoice_id', 'invoice_no', 'supplier_invoice_no', 'tax', 'advance_amount', 'remarks', 'total_amount', 'tax_amount', 'vendor_id', 'order_status_id']
    
    def get_purchase_invoice_orders_summary(purchase_invoice_orders):
        serializer = PurchaseInvoiceOrdersOptionsSerializer(purchase_invoice_orders, many=True)
        return serializer.data