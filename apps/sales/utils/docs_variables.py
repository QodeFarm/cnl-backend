from apps.sales.models import SaleOrder, SaleOrderItems, SaleInvoiceOrders,SaleInvoiceItems, OrderShipments
from apps.sales.serializers import SaleOrderSerializer, SaleOrderItemsSerializer,SaleInvoiceOrdersSerializer, SaleInvoiceItemsSerializer, OrderShipmentsSerializer

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

                'number_lbl': 'Quotation No.',
                'date_lbl': 'Quote Date',
                'Doc_Header': 'SALES QUOTATION',
                'net_lbl': 'Net Amount',

                'number_value': 'invoice_no',
                'date_value': 'invoice_date',
            }
        }