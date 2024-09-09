#Table Names
#===========:-

baseurl = 'http://195.35.20.172:8000/'

#Company db_tables
companytable ='companies'
branchestable ='branches'
branchbankdetails = 'branch_bank_details'

#Customer db_tables
ledgeraccountstable = 'ledger_accounts'
customerstable = 'customers'
customeraddressestable = 'customer_addresses'
customerattachmentstable = 'customer_attachments'

#Products db_tables
productgroupstable = 'product_groups'
productcategoriestable = 'product_categories'
productstockunitstable = 'product_stock_units'
productgstclassificationstable = 'product_gst_classifications'
productsalesgltable = 'product_sales_gl'
productpurchasegltable ='product_purchase_gl'
productstable = 'products'
productitembalancetable = 'product_item_balance'
colors = 'colors'
sizes = 'sizes'
productvariations = 'product_variations'

#vendor db_tables
vendorcategory='vendor_category'
vendorpaymentterms = 'vendor_payment_terms'
vendoragent = 'vendor_agent'
vendor = 'vendor'
vendorattachments = 'vendor_attachments'
vendoraddresses = 'vendor_addresses'

#sales db_tables
saleorders = 'sale_orders'
paymenttransactions = 'payment_transactions'
invoices = 'invoices'
warehouses = 'warehouses'
warehouselocations = 'warehouse_locations'
saleinvoiceitemstable = 'sale_invoice_items'
shipments = 'shipments'
salespricelist  = 'sales_price_list'
saleorderreturns = 'sale_order_returns'
orderssalesmantable = 'orders_salesman'
saleorderitemstable = 'sale_order_items'
saleinvoiceorderstable = 'sale_invoice_orders'
salereturnorderstable = 'sale_return_orders'
salereturnitemstable = 'sale_return_items'
orderattachmentstable = 'order_attachments' 
ordershipmentstable = 'order_shipments'
quickpackitems = 'quick_pack_items'
quickpacks = 'quick_packs'
salereceipts = 'sale_receipts'
#inventory db_tables
warehousestable ='warehouses'

#purchase db_tables
purchaseorderstable = 'purchase_orders'
purchaseorderitemstable = 'purchase_order_items'
purchaseinvoiceorders = 'purchase_invoice_orders'
purchaseinvoiceitems = 'purchase_invoice_items'
purchasereturnorders = 'purchase_return_orders'
purchasereturnitems = 'purchase_return_items'
purchasepricelisttable = 'purchase_price_list'

#tasks db_tables
taskstable = 'tasks'
taskcommentstable ='task_comments'
taskattachmentstable ='task_attachments'
taskhistorytable='task_history'

#assets db_tables
assetstatusestable = 'asset_statuses'
assetcategoriestable = 'asset_categories'
locationstable ='locations'
assetstable = 'assets'
assetmaintenancetable ='asset_maintenance'

#Master db_tables
countrytable = 'country'
statetable = 'state'
citytable = 'city'
statusestable = 'statuses'
ledgergroupstable = 'ledger_groups'
firmstatusestable = 'firm_statuses'
territoriestable = 'territory'
customercategoriestable = 'customer_categories'
gstcategoriestable = 'gst_categories'
customerpaymenttermstable = 'customer_payment_terms'
pricecategoriestable = 'price_categories'
transportertable = 'transporters'
producttypestable = 'product_types'
productuniquequantitycodestable = 'product_unique_quantity_codes'
unitoptionstable = 'unit_options'
productdrugtypestable = 'product_drug_types'
productitemtypetable = 'product_item_type'
brandsalesmantable = 'brand_salesman'
productbrandstable = 'product_brands'
purchasetypestable = 'purchase_types'
shippingcompanies = 'shipping_companies'
gsttypes = 'gst_types'
shippingmodes = 'shipping_modes'
saletypes = 'sale_types'
paymentlinktable = 'payment_link_types'
orderstatusestable = 'order_statuses'
ordertypestable = 'order_types'
taskprioritiestable ='task_priorities'
returnoptions = 'return_options'

#Authentication db_tables
userstable = 'users'
rolestable = 'roles'
actionstable = 'actions'
modulestable = 'modules'
permissionstable = 'permissions'
modulesections = 'module_sections'
rolepermissionstable = 'role_permissions'
usertimerestrictions = 'user_time_restrictions'
userallowedweekdays = 'user_allowed_weekdays'
userpermissions = 'user_permissions'
userroles = 'user_roles'

# LEAD Management
leadstatuses = 'lead_statuses'
interactiontypes = 'interaction_types'
leads = 'leads'
leadassignments = 'lead_assignments'
leadinteractions = 'lead_interactions'
leadassignmenthistory = 'lead_assignment_history'

# HRMS
designations = 'designations'
departments = 'departments'
employees = 'employees'

# Production
billofmaterials = 'bill_of_materials'
productionstatuses = 'production_statuses'
workorders = 'work_orders'
inventory = 'inventory'
machines = 'machines'
productionworkers = 'production_workers'
rawmaterials = 'raw_materials'
workorderstages = 'work_order_stages'
defaultmachinery = 'default_machinery'
workordermachines = 'work_order_machines'
labor = 'labor'

#workflow tables
workflow = 'workflows'
workflowstages = 'workflow_stages'

#Define default work flow name
default_workflow_name = 'sales'

# Define the stages for the default workflow
default_workflow_stages = {
    1: 'sale_order',
    2: 'dispatch',
    3: 'invoice'
}
