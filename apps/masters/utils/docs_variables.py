import os
import random
import string
from django.conf import settings
from apps.company.models import Companies
from apps.company.serializers import CompaniesSerializer
from apps.customer.models import Customer
from apps.customer.serializers import CustomerSerializer
from apps.purchase.models import PurchaseOrders, PurchaseorderItems
from apps.purchase.serializers import PurchaseReturnOrdersSerializer
from apps.purchase.models import PurchaseReturnOrders, PurchaseReturnItems
from apps.sales.models import PaymentTransactions, SaleOrder, SaleOrderItems, SaleInvoiceOrders, SaleReturnItems, SaleReturnOrders, SaleInvoiceItems, OrderShipments
from  apps.purchase.serializers import PurchaseOrdersSerializer, PurchaseReturnItemsSerializer, PurchaseorderItemsSerializer
from apps.sales.serializers import PaymentTransactionSerializer, SaleOrderSerializer, SaleOrderItemsSerializer,SaleInvoiceOrdersSerializer, SaleInvoiceItemsSerializer, OrderShipmentsSerializer, SaleReturnItemsSerializer, SaleReturnOrdersSerializer

# needed for DocumentGeneratorView(present in sales.view) view for sending sales order rcpt, sales invoice rcpt etc 
doc_data = {
            'sale_order': {
                'Model': SaleOrder,
                'Serializer': SaleOrderSerializer,
                'Item_Model': SaleOrderItems,
                'Items_Serializer': SaleOrderItemsSerializer,
                'Item_Model_PK': 'sale_order_id',
                'Related_Model': OrderShipments,
                'Related_Serializer': OrderShipmentsSerializer,
                'Related_filter_field': 'order_id',

                'number_lbl': 'SO No.',
                'date_lbl': 'SO Date',
                'Doc_Header': 'SALES ORDER',
                'net_lbl': 'Net  Total',

                'number_value': 'order_no',
                'date_value': 'order_date',
            },

            'sale_invoice': {
                'Model': SaleInvoiceOrders,
                'Serializer': SaleInvoiceOrdersSerializer,
                'Item_Model': SaleInvoiceItems,
                'Items_Serializer': SaleInvoiceItemsSerializer,
                'Item_Model_PK': 'sale_invoice_id',
                'Related_Model': OrderShipments,
                'Related_Serializer': OrderShipmentsSerializer,
                'Related_filter_field': 'order_id',                

                'number_lbl': 'Invoice No.',
                'date_lbl': 'Invoice Date',
                'Doc_Header': 'TAX INVOICE',
                'net_lbl': 'Net Amount',

                'number_value': 'invoice_no',
                'date_value': 'invoice_date',
            },
            # ... your existing document types ...
            "sale_return": {
                "Model": SaleReturnOrders,  # Replace with your actual model
                "Serializer": SaleReturnOrdersSerializer,  # Replace with your actual serializer
                "Item_Model": SaleReturnItems,  # Replace with your actual item model
                "Items_Serializer": SaleReturnItemsSerializer,  # Replace with your actual item serializer
                "Item_Model_PK": "sale_return_id",  # Replace with your actual foreign key field
                "Related_Model": OrderShipments,  # Or add if you have related models
                "Related_Serializer": OrderShipmentsSerializer,
                "Related_filter_field": "order_id",
                
                "number_lbl": "Invoice No",
                "date_lbl": "Invoice Date",
                "Doc_Header": "BILL OF SUPPLY",
                "net_lbl": "Bill Total",
                "number_value": "sale_invoice_id",  # Field name in your model
                "date_value": "sale_invoice_id"  # Field name in your model
            },
            'purchase_order': {
                'Model': PurchaseOrders,
                'Serializer': PurchaseOrdersSerializer,
                'Item_Model': PurchaseorderItems,
                'Items_Serializer': PurchaseorderItemsSerializer,
                'Item_Model_PK': 'purchase_order_id',
                'Related_Model': OrderShipments,
                'Related_Serializer': OrderShipmentsSerializer,
                'Related_filter_field': 'order_id',

                'number_lbl': 'Voucher No.',
                'date_lbl': 'Date',
                'Doc_Header': 'Purchase Bill',
                'net_lbl': 'Order Total',

                'number_value': 'order_no',
                'date_value': 'order_date',
            },
            'purchase_return' : {
                'Model': PurchaseReturnOrders,
                'Serializer': PurchaseReturnOrdersSerializer,

                'Item_Model': PurchaseReturnItems,
                'Items_Serializer': PurchaseReturnItemsSerializer,
                'Item_Model_PK': 'purchase_return_id',

                'Related_Model': OrderShipments,
                'Related_Serializer': OrderShipmentsSerializer,
                'Related_filter_field': 'order_id',

                'number_lbl': 'Voucher No.',
                'date_lbl': 'Date',
                'Doc_Header': 'Purchase Return',
                'net_lbl': 'Bill Total',

                'number_value': 'return_no',
                'date_value': 'return_date',
            },
            "payment_receipt": {
                "Model": PaymentTransactions,
                "Serializer": PaymentTransactionSerializer,
                "Item_Model": Customer,  # No items for payment receipts
                "Items_Serializer": CustomerSerializer,
                "Item_Model_PK": "customer_id",
                "Related_Model": None,
                "Related_Serializer": None,
                "Related_filter_field": None,
                
                "number_lbl": "Receipt No.",
                "date_lbl": "Receipt Date",
                "Doc_Header": "RECEIPT VOUCHER",
                "net_lbl": "Net Amount",
                
                "number_value": "payment_receipt_no",
                "date_value": "payment_date",
            }
        }






