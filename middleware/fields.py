#Specify required fields in all models


custom_filters = [
    'sales_by_customer',
    'sales_by_product',
    'sales_return_report',
    'sales_order_status',
    'customers_not_purchasing',
    'products_not_moving',
    ]


all_model_fields = {
    'actions':['action_id','action_name','description','created_at','updated_at'],
    'branch_bank_details':['bank_detail_id','branch_id','bank_name','account_number','branch_name','ifsc_code','swift_code','address','created_at','updated_at'],
    'branches':['branch_id','company_id','name','code','party','gst_no','status_id','allowed_warehouse','e_way_username','e_way_password','gstn_username','gstn_password','other_license_1','other_license_2','picture','address','city_id','state_id','country_id','pin_code','phone','email','longitude','latitude','created_at','updated_at'],
    'brand_salesman':['brand_salesman_id','code','name','commission_rate','rate_on','created_at','updated_at'],
    'city':['city_id','state_id','city_name','city_code','created_at','updated_at'],
    'companies':['company_id','name','print_name','short_name','code','num_branches','num_employees','logo','address','city_id','state_id','country_id','pin_code','phone','email','longitude','latitude','print_address','website','facebook_url','skype_id','twitter_handle','linkedin_url','pan','tan','cin','gst_tin','establishment_code','esi_no','pf_no','authorized_person','iec_code','eway_username','eway_password','gstn_username','gstn_password','vat_gst_status','gst_type','einvoice_approved_only','marketplace_url','drug_license_no','other_license_1','other_license_2','turnover_less_than_5cr','created_at','updated_at','is_deleted'],
    'country':['country_id','country_name','country_code','created_at','updated_at'],
    'customer_addresses':['customer_address_id','customer_id','address_type','address','city_id','state_id','country_id','pin_code','phone','email','longitude','latitude','route_map','created_at','updated_at'],
    'customer_attachments':['attachment_id','customer_id','attachment_name','attachment_path','created_at','updated_at'],
    'customer_categories':['customer_category_id','code','name','created_at','updated_at'],
    'customer_payment_terms':['payment_term_id','name','code','fixed_days','no_of_fixed_days','payment_cycle','run_on','created_at','updated_at'],
    'customers':['customer_id','name','print_name','identification','code','ledger_account_id','customer_common_for_sales_purchase','is_sub_customer','firm_status_id','territory_id','customer_category_id','contact_person','picture','gst','registration_date','cin','pan','gst_category_id','gst_suspend','tax_type','distance','tds_on_gst_applicable','tds_applicable','website','facebook','skype','twitter','linked_in','payment_term_id','price_category_id','batch_rate_category','transporter_id','credit_limit','max_credit_days','interest_rate_yearly','created_at','updated_at'],
    'firm_statuses':['firm_status_id','name','created_at','updated_at'],
    'gst_categories':['gst_category_id','name','created_at','updated_at'],
    'gst_types':['gst_type_id','name','created_at','updated_at'],
    'ledger_accounts':['ledger_account_id','name','code','is_subledger','ledger_group_id','inactive','type','account_no','rtgs_ifsc_code','classification','is_loan_account','tds_applicable','address','pan','created_at','updated_at'],
    'ledger_groups':['ledger_group_id','name','code','inactive','under_group','nature','created_at','updated_at'],
    'module_sections':['section_id','module_id','section_name','created_at','updated_at'],
    'modules':['module_id','module_name','description','created_at','updated_at'],
    'order_attachments':['attachment_id','order_id','attachment_name','attachment_path','order_type_id','created_at','updated_at'],
    'order_shipments':['shipment_id','order_id','destination','shipping_mode_id','shipping_company_id','shipping_tracking_no','shipping_date','shipping_charges','vehicle_vessel','charge_type','document_through','port_of_landing','port_of_discharge','no_of_packets','weight','order_type_id','created_at','updated_at'],
    'order_statuses':['order_status_id','status_name','description','created_at','updated_at'],
    'order_types':['order_type_id','name','created_at','updated_at'],
    'orders_salesman':['order_salesman_id','code','name','commission_rate','rate_on','amount_type','email','phone','created_at','updated_at'],
    'payment_link_types':['payment_link_type_id','name','description','created_at','updated_at'],
    'payment_transactions':['transaction_id','sale_invoice_id','payment_date','amount','payment_method','payment_status','reference_number','notes','currency','transaction_type','created_at','updated_at'],
    'permissions':['permission_id','permission_name','description','created_at','updated_at'],
    'price_categories':['price_category_id','code','name','created_at','updated_at'],
    'product_brands':['brand_id','brand_name','code','picture','brand_salesman_id','created_at','updated_at'],
    'product_categories':['category_id','category_name','picture','code','created_at','updated_at'],
    'product_drug_types':['drug_type_id','drug_type_name','created_at','updated_at'],
    'product_groups':['group_id','group_name','description','picture','created_at','updated_at'],
    'product_gst_classifications':['gst_classification_id','type','code','hsn_or_sac_code','hsn_description','created_at','updated_at'],
    'product_item_type':['item_type_id','item_name','created_at','updated_at'],
    'product_purchase_gl':['purchase_gl_id','name','purchase_accounts','code','is_subledger','inactive','type','account_no','rtgs_ifsc_code','classification','is_loan_account','tds_applicable','address','pan','employee','created_at','updated_at'],
    'product_sales_gl':['sales_gl_id','name','sales_accounts','code','is_subledger','inactive','type','account_no','rtgs_ifsc_code','classification','is_loan_account','tds_applicable','address','pan','employee','created_at','updated_at'],
    'product_stock_units':['stock_unit_id','stock_unit_name','description','quantity_code_id','created_at','updated_at'],
    'product_types':['type_id','type_name','created_at','updated_at'],
    'product_unique_quantity_codes':['quantity_code_id','quantity_code_name','created_at','updated_at'],
    'products':['product_id','name','product_group_id','category_id','type_id','code','barcode','unit_options_id','gst_input','stock_unit_id','print_barcode','gst_classification_id','picture','sales_description','sales_gl_id','mrp','minimum_price','sales_rate','wholesale_rate','dealer_rate','rate_factor','discount','dis_amount','purchase_description','purchase_gl_id','purchase_rate','purchase_rate_factor','purchase_discount','item_type_id','minimum_level','maximum_level','salt_composition','drug_type_id','weighscale_mapping_code','brand_id','purchase_warranty_months','sales_warranty_months','status','created_at','updated_at'],
    'purchase_invoice_items':['purchase_invoice_item_id','purchase_invoice_id','product_id','quantity','unit_price','rate','amount','discount_percentage','discount','dis_amt','tax_code','tax_rate','created_at','updated_at'],
    'purchase_invoice_orders':['purchase_invoice_id','purchase_type_id','invoice_date','invoice_no','gst_type_id','vendor_id','email','delivery_date','supplier_invoice_no','supplier_invoice_date','vendor_agent_id','tax','vendor_address_id','remarks','payment_term_id','due_date','advance_amount','ledger_account_id','item_value','discount','dis_amt','taxable','tax_amount','cess_amount','transport_charges','round_off','total_amount','order_status_id','created_at','updated_at'],
    'purchase_invoice_order':['purchase_type','invoice_no','invoice_date','supplier_invoice_no','tax','tax_amount','total_amount','advance_amount','vendor','status','remarks'],
    'purchase_order_items':['purchase_order_item_id','purchase_order_id','product_id','quantity','unit_price','rate','amount','discount_percentage','discount','dis_amt','tax_code','tax_rate','created_at','updated_at'],
    # 'purchase_order':['purchase_order_id','purchase_type_id','order_date','order_no','gst_type_id','vendor_id','email','delivery_date','ref_no','ref_date','vendor_agent_id','tax','vendor_address_id','remarks','payment_term_id','advance_amount','ledger_account_id','item_value','discount','dis_amt','taxable','tax_amount','cess_amount','round_off','total_amount','order_status_id','created_at','updated_at'],
    'purchase_order':['purchase_type','order_date','order_no','tax','tax_amount','total_amount','vendor','status','remarks'],
    'purchase_price_list':['purchase_price_list_id','description','customer_category_id','brand_id','effective_from','created_at','updated_at'],
    'purchase_return_items':['purchase_return_item_id','purchase_return_id','product_id','quantity','unit_price','rate','amount','discount_percentage','discount','dis_amt','tax_code','tax_rate','created_at','updated_at'],
    'purchase_return_orders':['purchase_return_id','purchase_type_id','return_date','return_no','gst_type_id','vendor_id','email','ref_no','ref_date','vendor_agent_id','tax','vendor_address_id','remarks','payment_term_id','due_date','return_reason','item_value','discount','dis_amt','taxable','tax_amount','cess_amount','transport_charges','round_off','total_amount','order_status_id','created_at','updated_at'],
    'purchase_return_order':['purchase_type','return_no','return_reason','due_date','tax','tax_amount','total_amount','vendor','status','remarks'],
    'purchase_types':['purchase_type_id','name','created_at','updated_at'],
    'role_permissions':['role_permission_id','role_id','permission_id','access_level','created_at','updated_at'],
    'roles':['role_id','role_name','description','created_at','updated_at'],
    'sale_invoice_items':['sale_invoice_item_id','sale_invoice_id','product_id','quantity','unit_price','rate','amount','discount_percentage','discount','dis_amt','tax_code','tax_rate','created_at','updated_at'],
    'sale_invoice_orders':['sale_invoice_id','bill_type','invoice_date','invoice_no','customer_id','gst_type_id','email','ref_no','ref_date','order_salesman_id','tax','customer_address_id','payment_term_id','due_date','payment_link_type_id','remarks','advance_amount','ledger_account_id','item_value','discount','dis_amt','taxable','tax_amount','cess_amount','transport_charges','round_off','total_amount','vehicle_name','total_boxes','order_status_id','created_at','updated_at'],
    'sale_order_items':['sale_order_item_id','sale_order_id','product_id','quantity','unit_price','rate','amount','discount_percentage','discount','dis_amt','tax_code','tax_rate','created_at','updated_at'],
    'sale_order':['sale_order_id','sale_type_id','order_no','order_date','customer_id','gst_type_id','email','delivery_date','ref_no','ref_date','tax','customer_address_id','payment_term_id','remarks','advance_amount','ledger_account_id','item_value','discount','dis_amt','taxable','tax_amount','cess_amount','round_off','doc_amount','vehicle_name','total_boxes','order_status_id','created_at','updated_at'],
    'sale_return_items':['sale_return_item_id','sale_return_id','product_id','quantity','unit_price','rate','amount','discount_percentage','discount','dis_amt','tax_code','tax_rate','created_at','updated_at'],
    'sale_return_orders':['sale_return_id','bill_type','return_date','return_no','customer_id','gst_type_id','email','ref_no','ref_date','order_salesman_id','against_bill','against_bill_date','tax','customer_address_id','payment_term_id','due_date','payment_link_type_id','return_reason','remarks','item_value','discount','dis_amt','taxable','tax_amount','cess_amount','transport_charges','round_off','total_amount','vehicle_name','total_boxes','order_status_id','created_at','updated_at'],
    'sale_types':['sale_type_id','name','created_at','updated_at'],
    'sales_price_list':['sales_price_list_id','description','customer_category_id','brand_id','effective_from','created_at','updated_at'],
    'shipping_companies':['shipping_company_id','code','name','gst_no','website_url','created_at','updated_at'],
    'shipping_modes':['shipping_mode_id','name','created_at','updated_at'],
    'state':['state_id','country_id','state_name','state_code','created_at','updated_at'],
    'statuses':['status_id','status_name','created_at','updated_at','status_id','status_name'],
    'territory':['territory_id','code','name','created_at','updated_at'],
    'transporters':['transporter_id','code','name','gst_no','website_url','created_at','updated_at'],
    'unit_options':['unit_options_id','unit_name','created_at','updated_at'],
    'user_allowed_weekdays':['id','user_id','weekday','created_at','updated_at'],
    'user_permissions':['user_permission_id','section_id','action_id','description','created_at','updated_at'],
    'user_time_restrictions':['id','user_id','start_time','end_time','created_at','updated_at'],
    'users':['user_id','branch_id','company_id','username','password','first_name','last_name','email','mobile','otp_required','role_id','status_id','profile_picture_url','bio','timezone','language','is_active','created_at','updated_at','last_login','date_of_birth','gender','user_id','username','password','status','employee_id','created_time','updated_time','USER','CURRENT_CONNECTIONS','TOTAL_CONNECTIONS','MAX_SESSION_CONTROLLED_MEMORY','MAX_SESSION_TOTAL_MEMORY'],
    'vendor':['vendor_id','gst_no','name','print_name','identification','code','ledger_account_id','vendor_common_for_sales_purchase','is_sub_vendor','firm_status_id','territory_id','vendor_category_id','contact_person','picture','gst','registration_date','cin','pan','gst_category_id','gst_suspend','tax_type','distance','tds_on_gst_applicable','tds_applicable','website','facebook','skype','twitter','linked_in','payment_term_id','price_category_id','vendor_agent_id','transporter_id','credit_limit','max_credit_days','interest_rate_yearly','rtgs_ifsc_code','accounts_number','bank_name','branch','created_at','updated_at'],
    'vendor_addresses':['vendor_address_id','vendor_id','address_type','address','city_id','state_id','country_id','pin_code','phone','email','longitude','latitude','route_map','created_at','updated_at'],
    'vendor_agent':['vendor_agent_id','code','name','commission_rate','rate_on','amount_type','created_at','updated_at'],
    'vendor_attachments':['attachment_id','vendor_id','attachment_name','attachment_path','created_at','updated_at'],
    'vendor_category':['vendor_category_id','code','name','created_at','updated_at'],
    'vendor_payment_terms':['payment_term_id','name','code','fixed_days','no_of_fixed_days','payment_cycle','run_on','created_at','updated_at'],
    'warehouses':['warehouse_id','name','code','item_type_id','customer_id','address','city_id','state_id','country_id','pin_code','phone','email','longitude','latitude','created_at','updated_at'],
}