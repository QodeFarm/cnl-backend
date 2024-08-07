from rest_framework import serializers
from apps.customer.serializers import ModCustomerAddressesSerializer, ModCustomersSerializer, ModCustomerPaymentTermsSerializers, ModLedgerAccountsSerializers
from apps.masters.serializers import ModCustomerCategoriesSerializers, ModGstTypesSerializer, ModProductBrandsSerializer, ModSaleTypesSerializer, ModShippingCompaniesSerializer, ModUnitOptionsSerializer, ShippingModesSerializer, ModOrdersSalesmanSerializer, ModPaymentLinkTypesSerializer, ModOrderStatusesSerializer, ModOrderTypesSerializer
from apps.products.serializers import ModProductGroupsSerializer, ModproductsSerializer
from .models import *
from django.conf import settings

#----------Modified Serializers--------------------------

class ModSaleOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleOrder
        fields = ['sale_order_id','customer_id','order_date','delivery_date']

class ModSaleReturnOrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleReturnOrders
        fields = ['sale_return_id','return_date','return_no']

class ModSaleInvoiceOrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleInvoiceOrders
        fields = ['sale_invoice_id','invoice_date','invoice_no',]

class ModSaleOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleOrderItems
        fields = ['sale_order_item_id','amount']
# -------------------------------------------------------

class SaleOrderSerializer(serializers.ModelSerializer):
    gst_type = ModGstTypesSerializer(source='gst_type_id', read_only=True)
    customer = ModCustomersSerializer(source='customer_id', read_only=True)
    customer_address = ModCustomerAddressesSerializer(source='customer_address_id', read_only=True)
    payment_term = ModCustomerPaymentTermsSerializers(source='payment_term_id', read_only=True)
    sale_type = ModSaleTypesSerializer(source='sale_type_id', read_only=True)
    ledger_account = ModLedgerAccountsSerializers(source='ledger_account_id', read_only=True)
    order_status = ModOrderStatusesSerializer(source='order_status_id',read_only=True)
    
    class Meta:
        model = SaleOrder
        fields = '__all__'
        
class PaymentTransactionsSerializer(serializers.ModelSerializer):
    invoice = ModSaleInvoiceOrdersSerializer(source='sale_invoice_id', read_only=True)
    
    class Meta:
        model = PaymentTransactions
        fields = '__all__'

class SaleInvoiceItemsSerializer(serializers.ModelSerializer):
    sale_order = ModSaleOrderSerializer(source='sale_order_id', read_only=True)
    product = ModproductsSerializer(source='product_id', read_only=True)
    unit_options = ModUnitOptionsSerializer(source='unit_options_id', read_only=True)

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

    class Meta:
        model = SaleReturnOrders
        fields = '__all__'
    
class SaleReturnItemsSerializer(serializers.ModelSerializer):
    sale_return = ModSaleReturnOrdersSerializer(source='sale_return_id', read_only=True)
    product = ModproductsSerializer(source='product_id', read_only=True)
    unit_options = ModUnitOptionsSerializer(source='unit_options_id', read_only=True)
    
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
    customer_id = ModCustomersSerializer()
    sale_type_id = ModSaleTypesSerializer()
    amount = serializers.SerializerMethodField()
    order_status_id = ModOrderStatusesSerializer()

    class Meta:
        model = SaleOrder
        fields = ['sale_order_id', 'order_no', 'order_date', 'tax', 'tax_amount', 'amount', 'advance_amount', 'customer_id', 'sale_type_id', 'order_status_id', 'remarks']

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
    
    @staticmethod
    def get_sale_order_summary(sale_order):
        serializer = SaleOrderOptionsSerializer(sale_order, many=True)
        return {
            "count": len(serializer.data),
            "msg": "SUCCESS",
            "data": serializer.data
        }

class SaleInvoiceOrderOptionsSerializer(serializers.ModelSerializer):
    customer_id = ModCustomersSerializer()
    order_status_id = ModOrderStatusesSerializer()

    class Meta:
        model = SaleInvoiceOrders
        fields = ['sale_invoice_id', 'invoice_no',  'invoice_date', 'tax', 'advance_amount', 'total_amount', 'tax_amount', 'customer_id', 'order_status_id', 'remarks']

    def get_sale_invoice_order_summary(sale_invoice_order):
        serializer = SaleInvoiceOrderOptionsSerializer(sale_invoice_order, many=True)
        return serializer.data

class SaleReturnOrdersOptionsSerializer(serializers.ModelSerializer):
    customer_id = ModCustomersSerializer()
    order_status_id = ModOrderStatusesSerializer()

    class Meta:
        model = SaleReturnOrders
        fields = ['sale_return_id', 'return_no', 'return_date', 'tax', 'return_reason', 'total_amount', 'due_date', 'tax_amount', 'customer_id', 'order_status_id', 'remarks']

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

    class Meta:
        model = QuickPackItems
        fields = '__all__'