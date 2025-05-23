/*
Nthras Product ERP System Database Schema
This schema is optimized for MySQL, focusing on performance, scalability, and data integrity for an Enterprise Resource Planning system. It includes comprehensive structures for managing companies, branches, users, roles, permissions, and other essential entities.

--- Recommendations for Developers ---

1. Indexing:
   - Always ensure to index foreign keys and columns frequently used in WHERE clauses, JOIN conditions, or as part of a foreign key relationship to enhance query performance.
   - Consider creating composite indexes for queries that span multiple columns frequently.

2. Data Types:
   - Choose the most appropriate data types for each column to optimize storage and performance. For instance, use INT UNSIGNED for identifiers, ENUM for columns with a limited set of predefined values, and appropriate VARCHAR lengths.
   - Use DECIMAL for precise arithmetic operations, especially for financial data.

3. Security:
   - Sensitive data such as passwords should be stored securely. Use hashing algorithms like bcrypt for passwords. Avoid storing plain-text passwords.
   - Consider field-level encryption for highly sensitive data like personal identification numbers or financial information.

4. Large Objects:
   - For large binary objects (BLOBs), such as images or documents, prefer storing them in an external storage solution (e.g., AWS S3) and save the reference URL in the database. This approach keeps the database size manageable and improves performance.

5. Data Integrity:
   - Use foreign key constraints to enforce relational integrity across tables.
   - Utilize transaction controls to ensure data consistency, particularly for operations that span multiple tables.

6. Normalization:
   - Adhere to normalization principles to reduce data redundancy and ensure data integrity. However, be mindful of over-normalization, which can lead to complex queries and affect performance.

7. Performance Optimization:
   - Use EXPLAIN to analyze and optimize query performance.
   - Consider partitioning large tables to improve query performance and management.

8. Auditing:
   - Include `created_at` and `updated_at` timestamps in all tables to track data creation and modifications.
   - Implement soft deletion (`is_deleted`) to maintain historical data without permanently removing records from the database.

9. Application-Level Considerations:
   - Where possible, offload data processing and business logic to the application level to leverage application caching and reduce database load.
   - Regularly review and optimize SQL queries used by the application, especially those that are executed frequently or involve large datasets.

10. Database Maintenance:
    - Regularly perform database maintenance tasks such as analyzing tables, optimizing indexes, and cleaning up unused data or tables to ensure optimal performance.
    - Plan for regular backups and establish a robust disaster recovery plan to safeguard your data.

By following these best practices, developers can ensure that the database layer of the Nthras Product ERP system remains robust, performant, and scalable to support the evolving needs of the business.

*/

/* Country Table */
-- Stores all countries info
CREATE TABLE IF NOT EXISTS country (
    country_id CHAR(36) PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL,
    country_code VARCHAR(100),
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

/* State Table */
-- Stores all states info
CREATE TABLE IF NOT EXISTS state (
    state_id CHAR(36) PRIMARY KEY,
    country_id CHAR(36) NOT NULL,
    state_name VARCHAR(100) NOT NULL,
    state_code VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (country_id) REFERENCES country(country_id)
) ENGINE=InnoDB;

/* City Table */
-- Stores all city info
CREATE TABLE IF NOT EXISTS city (
    city_id CHAR(36) PRIMARY KEY,
    state_id CHAR(36) NOT NULL,
    city_name VARCHAR(100) NOT NULL,
    city_code VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (state_id) REFERENCES state(state_id)
) ENGINE=InnoDB;


/* Companies Table */
-- Stores comprehensive information about each company, including contact info, identification numbers, and social media links.
CREATE TABLE IF NOT EXISTS companies (
    company_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    print_name VARCHAR(255) NOT NULL,
    short_name VARCHAR(100),
    code VARCHAR(50),
    num_branches INT DEFAULT 0,
    num_employees INT,
    logo JSON DEFAULT NULL, -- URL to logo image stored externally
    address VARCHAR(255),
    city_id CHAR(36) NOT NULL,
	state_id CHAR(36) NOT NULL,
	country_id CHAR(36),
    pin_code VARCHAR(20),
    phone VARCHAR(20),
    email VARCHAR(255),
    longitude DECIMAL(9, 6),
    latitude DECIMAL(9, 6),
    print_address VARCHAR(255),
    website VARCHAR(255),
    facebook_url VARCHAR(255),
    skype_id VARCHAR(50),
    twitter_handle VARCHAR(50),
    linkedin_url VARCHAR(255),
    pan VARCHAR(50),
    tan VARCHAR(50),
    cin VARCHAR(50),
    gst_tin VARCHAR(50),
    establishment_code VARCHAR(50),
    esi_no VARCHAR(50),
    pf_no VARCHAR(50),
    authorized_person VARCHAR(255),
    iec_code VARCHAR(50),
    eway_username VARCHAR(100),
    eway_password VARCHAR(100),
    gstn_username VARCHAR(100),
    gstn_password VARCHAR(100),
    vat_gst_status ENUM('Active', 'Inactive', 'Pending'),
    gst_type ENUM('Goods', 'Service', 'Both'),
    einvoice_approved_only BOOLEAN DEFAULT 0,
    marketplace_url VARCHAR(255),
    drug_license_no VARCHAR(50),
    other_license_1 VARCHAR(50),
    other_license_2 VARCHAR(50),
    turnover_less_than_5cr BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT 0,
	FOREIGN KEY (state_id) REFERENCES state(state_id),
	FOREIGN KEY (country_id) REFERENCES country(country_id),
    FOREIGN KEY (city_id) REFERENCES city(city_id)
) ENGINE=InnoDB;

/* Statuses Table */
-- Defines various statuses that can be applied to records within the system, such as Active, Inactive, Pending Approval.
CREATE TABLE IF NOT EXISTS statuses (
    status_id CHAR(36) PRIMARY KEY,
    status_name VARCHAR(50) NOT NULL UNIQUE DEFAULT 'Pending',
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

/* Branches Table */
-- Represents individual branches or offices of a company, including basic contact information.
CREATE TABLE IF NOT EXISTS branches (
    branch_id CHAR(36) PRIMARY KEY,
    company_id CHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50),
    party VARCHAR(255),  -- This will be changed later
    gst_no VARCHAR(50),
    status_id CHAR(36) NOT NULL,
    allowed_warehouse VARCHAR(255),
    e_way_username VARCHAR(255),
    e_way_password VARCHAR(255),
    gstn_username VARCHAR(255),
    gstn_password VARCHAR(255),
    other_license_1 VARCHAR(255),
    other_license_2 VARCHAR(255),
    picture JSON DEFAULT NULL,
    address VARCHAR(255),
    city_id CHAR(36) NOT NULL,
	state_id CHAR(36) NOT NULL,
	country_id CHAR(36),
    pin_code VARCHAR(20),
    phone VARCHAR(20),
    email VARCHAR(255),
    longitude DECIMAL(10, 7),
    latitude DECIMAL(10, 7),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_company_id (company_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    FOREIGN KEY (status_id) REFERENCES statuses(status_id),
	FOREIGN KEY (city_id) REFERENCES city(city_id),
	FOREIGN KEY (state_id) REFERENCES state(state_id),
	FOREIGN KEY (country_id) REFERENCES country(country_id)
) ENGINE=InnoDB;

/* Branch Bank Details Table */
-- Stores sensitive bank information related to each branch, including bank name, account numbers, and branch details. 
CREATE TABLE IF NOT EXISTS branch_bank_details (
    bank_detail_id CHAR(36) PRIMARY KEY,
    branch_id CHAR(36) NOT NULL,
    bank_name VARCHAR(255),
    account_number VARCHAR(255),
    branch_name VARCHAR(255),
    ifsc_code VARCHAR(100),
    swift_code VARCHAR(100),
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
) ENGINE=InnoDB;

/* Roles Table */
-- Lists the roles that can be assigned to users, determining permissions and access levels within the ERP system.
CREATE TABLE IF NOT EXISTS roles (
    role_id CHAR(36) PRIMARY KEY,
    role_name VARCHAR(255) NOT NULL UNIQUE,
    description VARCHAR(512),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

/* Users Table */
-- Contains user profiles, including authentication details, contact information, and role within the ERP system.
CREATE TABLE IF NOT EXISTS users (
    user_id CHAR(36) PRIMARY KEY,
    branch_id CHAR(36),
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255),
    email VARCHAR(255) NOT NULL,
    mobile VARCHAR(20) NOT NULL,
    otp_required BOOLEAN DEFAULT 0,
    status_id CHAR(36) NOT NULL,
    profile_picture_url VARCHAR(1024),
    bio VARCHAR(1024),
    timezone VARCHAR(100),
    language VARCHAR(10),
	is_active TINYINT,
    role_id CHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    date_of_birth DATE,
    gender ENUM('Male', 'Female', 'Other', 'Prefer Not to Say'),
    title ENUM('Mr.','Ms.'),
    INDEX idx_branch_id (branch_id),
    INDEX idx_status_id (status_id),
    INDEX idx_role_id (role_id),
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id),
    FOREIGN KEY (status_id) REFERENCES statuses(status_id),
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
) ENGINE=InnoDB;


/* User_roles Table */
-- Maintain user roles many to many relations
CREATE TABLE IF NOT EXISTS user_roles (
    user_role_id CHAR(36) PRIMARY KEY, 
    user_id CHAR(36) NOT NULL,
    role_id CHAR(36) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)ENGINE=InnoDB;

/* Modules Table */
-- Stores information about different modules within the ERP system, such as HR, Finance, etc.
CREATE TABLE IF NOT EXISTS modules (
    module_id CHAR(36) PRIMARY KEY,
    module_name VARCHAR(255) UNIQUE NOT NULL,
    description VARCHAR(512),
    mod_icon VARCHAR(255),
    mod_link VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

/* Module_Sections Table */
-- Organizes modules into smaller sections for more granular access control and management.
CREATE TABLE IF NOT EXISTS module_sections (
    section_id CHAR(36) PRIMARY KEY,
    module_id CHAR(36) NOT NULL,
    section_name VARCHAR(255) NOT NULL,
    sec_icon VARCHAR(255),
    sec_link VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (module_id) REFERENCES modules(module_id)
) ENGINE=InnoDB;

/* Actions Table */
-- Lists the actions that can be performed within each module section, such as Create, Read, Update, Delete.
CREATE TABLE IF NOT EXISTS actions (
    action_id CHAR(36) PRIMARY KEY,
    action_name VARCHAR(255) NOT NULL,
    description VARCHAR(512),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

/* Role_permissions Table */
-- Connects roles with specific permissions, denoting what actions a user can perform in different module sections.
CREATE TABLE IF NOT EXISTS role_permissions (
    role_permission_id CHAR(36) PRIMARY KEY,
    role_id CHAR(36) NOT NULL,
    module_id CHAR(36) NOT NULL,
    section_id CHAR(36) NOT NULL,
    action_id CHAR(36) NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE,
    FOREIGN KEY (module_id) REFERENCES modules(module_id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES module_sections(section_id) ON DELETE CASCADE,
    FOREIGN KEY (action_id) REFERENCES actions(action_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)ENGINE=InnoDB;


/* user_time_restrictions Table */
-- Defines specific times during which users are allowed to access the ERP system, enhancing security and compliance.
CREATE TABLE IF NOT EXISTS user_time_restrictions (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB;

/* user_allowed_weekdays Table */
-- Specifies the days of the week on which users are permitted to access the ERP system, further customizing access control.
CREATE TABLE IF NOT EXISTS user_allowed_weekdays (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    weekday ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB;

/* django_admin_log Table */
-- This table is used for Action Tracking.
CREATE TABLE IF NOT EXISTS django_admin_log (
  id int NOT NULL DEFAULT '0',
  action_time datetime(6) NOT NULL,
  object_id longtext,
  object_repr varchar(200) NOT NULL,
  action_flag smallint unsigned NOT NULL,
  change_message longtext NOT NULL,
  content_type_id int DEFAULT NULL,
  user_id int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/* Ledger Groups Table */
-- Stores information about ledger groups used in accounting.
CREATE TABLE IF NOT EXISTS ledger_groups (
    ledger_group_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50),
    inactive BOOLEAN,
    under_group VARCHAR(255),
    nature ENUM('Asset', 'Liability', 'Income', 'Expense') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Ledger Accounts Table */
-- Stores information about ledger accounts used in accounting.
CREATE TABLE IF NOT EXISTS ledger_accounts (
    ledger_account_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50),
    is_subledger BOOLEAN,
    ledger_group_id CHAR(36) NOT NULL,
    inactive BOOLEAN,
    type ENUM("Bank", "Cash", "Customer",) NOT NULL,
    account_no VARCHAR(50),
    rtgs_ifsc_code VARCHAR(50),
    classification VARCHAR(50),
    is_loan_account BOOLEAN,
    tds_applicable BOOLEAN,
    address VARCHAR(255),
    pan VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (ledger_group_id) REFERENCES ledger_groups(ledger_group_id)
);

/* journal table */
-- Record financial transactions (headers for double-entry) 
CREATE TABLE IF NOT EXISTS journal (
    journal_id CHAR(36) PRIMARY KEY,
    date DATE NOT NULL,
    description VARCHAR(255),
    total_debit DECIMAL(18, 2),
    total_credit DECIMAL(18, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

/* journal_details */
--Store debit/credit entries linked to the journal table.
CREATE TABLE IF NOT EXISTS journal_details (
    journal_detail_id CHAR(36) PRIMARY KEY,
    journal_id CHAR(36) NOT NULL,
    ledger_account_id CHAR(36) NOT NULL,
    debit DECIMAL(18, 2) DEFAULT 0.00,
    credit DECIMAL(18, 2) DEFAULT 0.00,
    FOREIGN KEY (journal_id) REFERENCES journal(journal_id),
    FOREIGN KEY (ledger_account_id) REFERENCES ledger_accounts(ledger_account_id)
);


/* Firm Statuses Table */
-- Stores information about different statuses of firms.
CREATE TABLE IF NOT EXISTS firm_statuses (
    firm_status_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Territory Table */
-- Stores information about territories.
CREATE TABLE IF NOT EXISTS territory (
    territory_id CHAR(36) PRIMARY KEY,
    code VARCHAR(50),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Customer Categories Table */
-- Stores information about customer categories.
CREATE TABLE IF NOT EXISTS customer_categories (
    customer_category_id CHAR(36) PRIMARY KEY,
    code VARCHAR(50),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* GST Categories Table */
-- Stores information about GST categories.
CREATE TABLE IF NOT EXISTS gst_categories (
    gst_category_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Customer Payment Terms Table */
-- Stores information about payment terms for customers.
CREATE TABLE IF NOT EXISTS customer_payment_terms (
    payment_term_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL ,
    code VARCHAR(50),
    fixed_days INT,
    no_of_fixed_days INT,
    payment_cycle VARCHAR(255),
    run_on VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Price Categories Table */
-- Stores information about price categories.
CREATE TABLE IF NOT EXISTS price_categories (
    price_category_id CHAR(36) PRIMARY KEY,
    code VARCHAR(50),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Transporters Table */
-- Stores information about transporters.
CREATE TABLE IF NOT EXISTS transporters (
    transporter_id CHAR(36) PRIMARY KEY,
    code VARCHAR(50),
    name VARCHAR(255) NOT NULL,
    gst_no VARCHAR(50),
    website_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Customers Table */
-- Stores information about customers.
CREATE TABLE IF NOT EXISTS customers (
    customer_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    print_name VARCHAR(255) NOT NULL,
    identification VARCHAR(255),
    code VARCHAR(50) NOT NULL,
    ledger_account_id CHAR(36) NOT NULL,
    customer_common_for_sales_purchase BOOLEAN,
    is_sub_customer BOOLEAN,
    firm_status_id CHAR(36),
    territory_id CHAR(36),
    customer_category_id CHAR(36),
    contact_person VARCHAR(255),
    picture JSON DEFAULT NULL,
    gst VARCHAR(50),
    registration_date DATE,
    cin VARCHAR(50),
    pan VARCHAR(50),
    gst_category_id CHAR(36),
    gst_suspend BOOLEAN,
    tax_type ENUM('Inclusive', 'Exclusive'),
    distance FLOAT,
    tds_on_gst_applicable BOOLEAN,
    tds_applicable BOOLEAN,
    website VARCHAR(255),
    facebook VARCHAR(255),
    skype VARCHAR(255),
    twitter VARCHAR(255),
    linked_in VARCHAR(255),
    payment_term_id CHAR(36),
    price_category_id CHAR(36),
    batch_rate_category VARCHAR(50),
    transporter_id CHAR(36),
    credit_limit DECIMAL(18,2),
    max_credit_days INT,
    interest_rate_yearly DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (ledger_account_id) REFERENCES ledger_accounts(ledger_account_id),
    FOREIGN KEY (firm_status_id) REFERENCES firm_statuses(firm_status_id),
    FOREIGN KEY (territory_id) REFERENCES territory(territory_id),
    FOREIGN KEY (customer_category_id) REFERENCES customer_categories(customer_category_id),
    FOREIGN KEY (gst_category_id) REFERENCES gst_categories(gst_category_id),
    FOREIGN KEY (payment_term_id) REFERENCES customer_payment_terms(payment_term_id),
    FOREIGN KEY (price_category_id) REFERENCES price_categories(price_category_id),
    FOREIGN KEY (transporter_id) REFERENCES transporters(transporter_id)
);

/* Customer Attachments Table */
-- Stores attachments associated with Customer.
CREATE TABLE IF NOT EXISTS customer_attachments (
    attachment_id CHAR(36) PRIMARY KEY,
    customer_id CHAR(36) NOT NULL,
    attachment_name VARCHAR(255) NOT NULL,
    attachment_path VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

/* Customer Addresses Table */
-- Stores information about customer addresses.
CREATE TABLE IF NOT EXISTS customer_addresses (
    customer_address_id CHAR(36) PRIMARY KEY,
    customer_id CHAR(36) NOT NULL,
    address_type ENUM('Billing', 'Shipping'),
    address VARCHAR(255),
    city_id CHAR(36) NOT NULL,
	state_id CHAR(36) NOT NULL,
	country_id CHAR(36),
    pin_code VARCHAR(50),
    phone VARCHAR(50),
    email VARCHAR(255),
    longitude DECIMAL(10,6),
    latitude DECIMAL(10,6),
    route_map VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
	FOREIGN KEY (city_id) REFERENCES city(city_id),
	FOREIGN KEY (state_id) REFERENCES state(state_id),
	FOREIGN KEY (country_id) REFERENCES country(country_id)
);

/* Customer Balance Table */
-- Stores information about customer balance.
CREATE TABLE IF NOT EXISTS customer_balance (
  customer_balance_id CHAR(36) PRIMARY KEY,
  customer_id char(36) NOT NULL,
  balance_amount decimal(10,2) NOT NULL DEFAULT '0.00',
  last_updated datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  created_at timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
)

/* Product Groups Table */
-- Stores information about different groups of products.
CREATE TABLE IF NOT EXISTS product_groups (
    product_group_id CHAR(36) PRIMARY KEY,
    group_name VARCHAR(255) NOT NULL ,
    description VARCHAR(512),
    picture VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Product Categories Table */
-- Stores information about different categories of products.
CREATE TABLE IF NOT EXISTS product_categories (
    category_id CHAR(36) PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL,
    picture VARCHAR(255),
    code VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Product Types Table */
-- Stores information about different types of products.
CREATE TABLE IF NOT EXISTS product_types (
    type_id CHAR(36) PRIMARY KEY,
    type_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Product Unique Quantity Codes Table */
-- Stores information about unique quantity codes for products.
CREATE TABLE IF NOT EXISTS product_unique_quantity_codes (
    quantity_code_id CHAR(36) PRIMARY KEY,
    quantity_code_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Unit Options Table */
-- Stores information about unit options.
CREATE TABLE IF NOT EXISTS unit_options (
    unit_options_id CHAR(36) PRIMARY KEY,
    unit_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


/* Product Stock Units Table */
-- Stores information about stock units for products.
CREATE TABLE IF NOT EXISTS product_stock_units (
    stock_unit_id CHAR(36) PRIMARY KEY,
    stock_unit_name VARCHAR(255) NOT NULL,
    description VARCHAR(512),
    quantity_code_id CHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (quantity_code_id) REFERENCES product_unique_quantity_codes(quantity_code_id)
);

/* Product GST Classifications Table */
-- Stores information about GST classifications for products.
CREATE TABLE IF NOT EXISTS product_gst_classifications (
    gst_classification_id CHAR(36) PRIMARY KEY,
    type ENUM('HSN', 'SAC'),
    code VARCHAR(50),
    hsn_or_sac_code VARCHAR(50),
    hsn_description VARCHAR(1024),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Product Sales GL Table */
-- Stores information about sales GL accounts for products.
CREATE TABLE IF NOT EXISTS product_sales_gl (
    sales_gl_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sales_accounts VARCHAR(255),
    code VARCHAR(50),
    is_subledger BOOLEAN,
    inactive BOOLEAN,
    type VARCHAR(255),
    account_no VARCHAR(255),
    rtgs_ifsc_code VARCHAR(255),
    classification VARCHAR(255),
    is_loan_account BOOLEAN,
    tds_applicable BOOLEAN,
    address VARCHAR(255),
    pan VARCHAR(50),
    employee BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Product Drug Types Table */
-- Stores information about drug types for products.
CREATE TABLE IF NOT EXISTS product_drug_types (
    drug_type_id CHAR(36) PRIMARY KEY,
    drug_type_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Product Purchase GL Table */
-- Stores information about purchase GL accounts for products.
CREATE TABLE IF NOT EXISTS product_purchase_gl (
    purchase_gl_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    purchase_accounts VARCHAR(255),
    code VARCHAR(50),
    is_subledger BOOLEAN,
    inactive BOOLEAN,
    type VARCHAR(255),
    account_no VARCHAR(255),
    rtgs_ifsc_code VARCHAR(255),
    classification VARCHAR(255),
    is_loan_account BOOLEAN,
    tds_applicable BOOLEAN,
    address VARCHAR(255),
    pan VARCHAR(50),
    employee BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Product Item Types Table */
-- Stores information about item types for products.
CREATE TABLE IF NOT EXISTS product_item_type (
    item_type_id CHAR(36) PRIMARY KEY,
    item_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Brand Salesman Table */
-- Stores information about salesmen for brands.
CREATE TABLE IF NOT EXISTS brand_salesman (
    brand_salesman_id CHAR(36) PRIMARY KEY,
    code VARCHAR(50),
    name VARCHAR(255) NOT NULL,
    commission_rate DECIMAL(18,2),
    rate_on ENUM("Qty", "Amount"),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Product Brands Table */
-- Stores information about brands for products.
CREATE TABLE IF NOT EXISTS product_brands (
    brand_id CHAR(36) PRIMARY KEY,
    brand_name VARCHAR(255) NOT NULL,
    code VARCHAR(50),
    picture VARCHAR(255),
    brand_salesman_id CHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (brand_salesman_id) REFERENCES brand_salesman(brand_salesman_id)
);

CREATE TABLE IF NOT EXISTS package_units (
    pack_unit_id CHAR(36) PRIMARY KEY,
    unit_name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS g_package_units (
    g_pack_unit_id CHAR(36) PRIMARY KEY,
    unit_name VARCHAR(50) NOT NULL
);

/* Products Table */
-- Stores information about products.
CREATE TABLE IF NOT EXISTS products (
    product_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    product_group_id CHAR(36) NOT NULL,
    category_id CHAR(36),
    type_id CHAR(36),
    code VARCHAR(50) NOT NULL,
    barcode VARCHAR(50),
    unit_options_id CHAR(36),
    gst_input INT,
    stock_unit_id CHAR(36) NOT NULL,
	print_barcode BOOLEAN,
    gst_classification_id CHAR(36),
    picture JSON DEFAULT NULL,
    sales_description VARCHAR(1024),
    sales_gl_id CHAR(36) NOT NULL,
    mrp DECIMAL(18,2),
    minimum_price DECIMAL(18,2),
    sales_rate DECIMAL(18,2),
    wholesale_rate DECIMAL(18,2),
    dealer_rate DECIMAL(18,2),
    rate_factor DECIMAL(18,2),
    discount DECIMAL(18,2),
    dis_amount DECIMAL(18,2),
    purchase_description VARCHAR(1024),
    purchase_gl_id CHAR(36) NOT NULL,
    purchase_rate DECIMAL(18,2),
    purchase_rate_factor DECIMAL(18,2),
    purchase_discount DECIMAL(18,2),
    item_type_id CHAR(36),
    minimum_level INT,
    maximum_level INT,
    salt_composition VARCHAR(1024),
    drug_type_id CHAR(36),
    weighscale_mapping_code VARCHAR(50),
    brand_id CHAR(36),
    purchase_warranty_months INT,
    sales_warranty_months INT,
    status ENUM('Active', 'Inactive'),
    print_name VARCHAR(255),
    hsn_code VARCHAR(15),
    balance INT DEFAULT 0,
	pack_unit_id CHAR(36) NULL,
	pack_vs_stock INT DEFAULT 0,
	g_pack_unit_id CHAR(36) NULL,
	g_pack_vs_pack INT DEFAULT 0,
	packet_barcode VARCHAR(50) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_group_id) REFERENCES product_groups(product_group_id),
    FOREIGN KEY (category_id) REFERENCES product_categories(category_id),
    FOREIGN KEY (type_id) REFERENCES product_types(type_id),
    FOREIGN KEY (unit_options_id) REFERENCES unit_options(unit_options_id),
    FOREIGN KEY (gst_classification_id) REFERENCES product_gst_classifications(gst_classification_id),
    FOREIGN KEY (sales_gl_id) REFERENCES product_sales_gl(sales_gl_id),
    FOREIGN KEY (purchase_gl_id) REFERENCES product_purchase_gl(purchase_gl_id),
    FOREIGN KEY (item_type_id) REFERENCES product_item_type(item_type_id),
    FOREIGN KEY (drug_type_id) REFERENCES product_drug_types(drug_type_id),
    FOREIGN KEY (brand_id) REFERENCES product_brands(brand_id),
    FOREIGN KEY (stock_unit_id) REFERENCES product_stock_units(stock_unit_id),
	FOREIGN KEY (pack_unit_id) REFERENCES product_stock_units(stock_unit_id),
	FOREIGN KEY (g_pack_unit_id) REFERENCES product_stock_units(stock_unit_id)
);

/* Sizes Table */
-- Stores information about different sizes.
CREATE TABLE IF NOT EXISTS sizes (
    size_id CHAR(36) PRIMARY KEY,
    size_name VARCHAR(50),
    size_category VARCHAR(100) NOT NULL,
    size_system VARCHAR(50),
    length DECIMAL(10, 2),                    
    height DECIMAL(10, 2),                    
    width DECIMAL(10, 2),                     
    size_unit VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Colors Table */
-- Stores information about different colors.
CREATE TABLE IF NOT EXISTS colors (
    color_id CHAR(36) PRIMARY KEY,
    color_name VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP    
);

/* Product_variations Table */
-- Stores information about product_variations.
CREATE TABLE IF NOT EXISTS product_variations (
    product_variation_id CHAR(36) PRIMARY KEY,
    product_id CHAR(36) NOT NULL,
    size_id CHAR(36) NULL,
    color_id CHAR(36) NULL,
    sku VARCHAR(100) UNIQUE,  -- A stock keeping unit (SKU) is a unique alphanumeric code that retailers use to identify and track products in their inventory
    price DECIMAL(10, 2) NOT NULL,
    quantity INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (size_id) REFERENCES sizes(size_id),
    FOREIGN KEY (color_id) REFERENCES colors(color_id)
);

/* Warehouse Table */
-- Stores information about warehouses.
CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(255),
    item_type_id CHAR(36),
    address VARCHAR(255),
    city_id CHAR(36) NOT NULL,
	state_id CHAR(36) NOT NULL,
	country_id CHAR(36),
    pin_code VARCHAR(50),
    phone VARCHAR(50),
    email VARCHAR(255),
    longitude DECIMAL(10, 6),
    latitude DECIMAL(10, 6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (item_type_id) REFERENCES product_item_type(item_type_id),
    FOREIGN KEY (city_id) REFERENCES city(city_id),
	FOREIGN KEY (state_id) REFERENCES state(state_id),
	FOREIGN KEY (country_id) REFERENCES country(country_id)
);


/* Warehouse_Locations Table */
-- Stores information about warehouse locations.
CREATE TABLE IF NOT EXISTS warehouse_locations (
    location_id CHAR(36) PRIMARY KEY,
    warehouse_id CHAR(36) NOT NULL,
    location_name VARCHAR(255) NOT NULL,
    description VARCHAR(512),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id)
);

/* Product_item_balance Table */
-- Stores information about product_item_balance.
CREATE TABLE IF NOT EXISTS product_item_balance (
    product_item_balance_id CHAR(36) PRIMARY KEY,
    product_id CHAR(36) NOT NULL,
    warehouse_location_id CHAR(36) NOT NULL,
    quantity INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (warehouse_location_id) REFERENCES warehouse_locations(location_id)
);

/* Vendor Category Table */
-- Stores vendor categories, providing classification for vendors.
CREATE TABLE IF NOT EXISTS vendor_category (
    vendor_category_id CHAR(36) PRIMARY KEY,
    code VARCHAR(50),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Vendor Payment Terms Table */
-- Stores payment terms applicable to vendors.
CREATE TABLE IF NOT EXISTS vendor_payment_terms (
    payment_term_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50),
    fixed_days INT,
    no_of_fixed_days INT,
    payment_cycle VARCHAR(255),
    run_on VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Vendor Agent Table */
-- Stores information about vendor agents, including commission rates and types.
CREATE TABLE IF NOT EXISTS vendor_agent (
    vendor_agent_id CHAR(36) PRIMARY KEY,
    code VARCHAR(50),
    name VARCHAR(255) NOT NULL,
    commission_rate DECIMAL(18, 2),
    rate_on ENUM("Amount", "Qty"),
    amount_type ENUM("BillAmount", "Taxable"),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Vendor Table */
-- Stores information about vendors including their details, contacts, and financial information.
CREATE TABLE IF NOT EXISTS vendor (
    vendor_id CHAR(36) PRIMARY KEY,
    gst_no VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    print_name VARCHAR(255) NOT NULL,
    identification VARCHAR(255),
    code VARCHAR(255) NOT NULL,
    ledger_account_id CHAR(36) NOT NULL,
    vendor_common_for_sales_purchase BOOLEAN,
    is_sub_vendor BOOLEAN,
    firm_status_id CHAR(36),
    territory_id CHAR(36),
    vendor_category_id CHAR(36),
    contact_person VARCHAR(255),
    picture JSON DEFAULT NULL,
    gst VARCHAR(255),
    registration_date DATE,
    cin VARCHAR(255),
    pan VARCHAR(255),
    gst_category_id CHAR(36),
    gst_suspend BOOLEAN,
    tax_type ENUM('Inclusive', 'Exclusive'),
    distance DECIMAL(18, 2),
    tds_on_gst_applicable BOOLEAN,
    tds_applicable BOOLEAN,
    website VARCHAR(255),
    facebook VARCHAR(255),
    skype VARCHAR(255),
    twitter VARCHAR(255),
    linked_in VARCHAR(255),
    payment_term_id CHAR(36),
    price_category_id CHAR(36),
    vendor_agent_id CHAR(36),
    transporter_id CHAR(36),
    credit_limit DECIMAL(18, 2),
    max_credit_days INT,
    interest_rate_yearly DECIMAL(18, 2),
    rtgs_ifsc_code VARCHAR(255),
    accounts_number VARCHAR(255),
    bank_name VARCHAR(255),
    branch VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (ledger_account_id) REFERENCES ledger_accounts(ledger_account_id),
    FOREIGN KEY (firm_status_id) REFERENCES firm_statuses(firm_status_id),
    FOREIGN KEY (territory_id) REFERENCES territory(territory_id),
    FOREIGN KEY (vendor_category_id) REFERENCES vendor_category(vendor_category_id),
    FOREIGN KEY (gst_category_id) REFERENCES gst_categories(gst_category_id),
    FOREIGN KEY (payment_term_id) REFERENCES vendor_payment_terms(payment_term_id),
    FOREIGN KEY (price_category_id) REFERENCES price_categories(price_category_id),
    FOREIGN KEY (vendor_agent_id) REFERENCES vendor_agent(vendor_agent_id),
    FOREIGN KEY (transporter_id) REFERENCES transporters(transporter_id)
);

/* Vendor Attachments Table */
-- Stores attachments associated with vendors.
CREATE TABLE IF NOT EXISTS vendor_attachments (
    attachment_id CHAR(36) PRIMARY KEY,
    vendor_id CHAR(36) NOT NULL,
    attachment_name VARCHAR(255) NOT NULL,
    attachment_path VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendor(vendor_id)
);

/* Vendor Addresses Table */
-- Stores addresses associated with vendors.
CREATE TABLE IF NOT EXISTS vendor_addresses (
    vendor_address_id CHAR(36) PRIMARY KEY,
    vendor_id CHAR(36) NOT NULL,
    address_type ENUM('Billing', 'Shipping'),
    address VARCHAR(255),
    city_id CHAR(36) NOT NULL,
	state_id CHAR(36) NOT NULL,
	country_id CHAR(36),
    pin_code VARCHAR(50),
    phone VARCHAR(50),
    email VARCHAR(255),
    longitude DECIMAL(10,6),
    latitude DECIMAL(10,6),
    route_map VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendor(vendor_id),
	FOREIGN KEY (city_id) REFERENCES city(city_id),
	FOREIGN KEY (state_id) REFERENCES state(state_id),
	FOREIGN KEY (country_id) REFERENCES country(country_id)
);

/* Shipping Modes Table */
-- Stores information about different shipping modes.
CREATE TABLE IF NOT EXISTS shipping_modes (
    shipping_mode_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Shipping Companies Table */
-- Stores information about different shipping companies.
CREATE TABLE IF NOT EXISTS shipping_companies (
    shipping_company_id CHAR(36) PRIMARY KEY,
    code VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    gst_no VARCHAR(255),
    website_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Sale Types Table */
-- Stores information about different types of sales.
CREATE TABLE IF NOT EXISTS sale_types (
    sale_type_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


/* GST Types Table */
-- Stores information about different types of GST.
CREATE TABLE IF NOT EXISTS gst_types (
    gst_type_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Salesman Table */
-- Stores information about salesmen.
CREATE TABLE IF NOT EXISTS orders_salesman (
    order_salesman_id CHAR(36) PRIMARY KEY,
    code VARCHAR(50),
    name VARCHAR(255) NOT NULL,
    commission_rate DECIMAL(18,2),
    rate_on ENUM("Qty", "Amount"),
    amount_type ENUM("Taxable", "BillAmount"),
    email VARCHAR(255),
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Payment Link Types Table */
-- Stores information about payment links.
CREATE TABLE IF NOT EXISTS payment_link_types (
    payment_link_type_id CHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* order_statuses Table */
-- Stores information about the different statuses that an order can have.
CREATE TABLE IF NOT EXISTS order_statuses (
    order_status_id CHAR(36) PRIMARY KEY,
    status_name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS return_options (
    return_option_id CHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Workflows Table */
-- Stores details about different workflows used in the ERP system.
CREATE TABLE IF NOT EXISTS workflows (
    workflow_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Sales Order Table */
-- Stores information about sales orders.
CREATE TABLE IF NOT EXISTS sale_orders(
    sale_order_id CHAR(36) PRIMARY KEY,
    sale_type_id CHAR(36),
    order_no VARCHAR(20) UNIQUE NOT NULL,
    order_date DATE NOT NULL,
    customer_id CHAR(36) NOT NULL,
    gst_type_id CHAR(36),
    email VARCHAR(255),
    delivery_date DATE NOT NULL,
    ref_no VARCHAR(255),
    ref_date DATE NOT NULL,
    tax ENUM('Exclusive','Inclusive'),
    sale_estimate ENUM('Yes', 'No') DEFAULT 'No',
    customer_address_id CHAR(36),
    payment_term_id CHAR(36),
    remarks VARCHAR(1024),
    advance_amount DECIMAL(18, 2),
    ledger_account_id CHAR(36),
    item_value DECIMAL(18, 2),
    discount DECIMAL(18, 2),
    dis_amt DECIMAL(18, 2),
    taxable DECIMAL(18, 2),
    tax_amount DECIMAL(18, 2),
    cess_amount DECIMAL(18, 2),
    round_off DECIMAL(18, 2),
    doc_amount DECIMAL(18, 2),
    vehicle_name VARCHAR(255),
    total_boxes INT,
    flow_status_id CHAR(36),
	order_status_id CHAR(36),
    sale_return_id CHAR(36),
	shipping_address VARCHAR(1024),
	billing_address VARCHAR(1024),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (gst_type_id) REFERENCES gst_types(gst_type_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (customer_address_id) REFERENCES customer_addresses(customer_address_id),
    FOREIGN KEY (payment_term_id) REFERENCES customer_payment_terms(payment_term_id),
    FOREIGN KEY (sale_type_id) REFERENCES sale_types(sale_type_id),
    FOREIGN KEY (ledger_account_id) REFERENCES ledger_accounts(ledger_account_id),
	FOREIGN KEY (order_status_id) REFERENCES order_statuses(order_status_id),
    FOREIGN KEY (flow_status_id) REFERENCES flow_status(flow_status_id),/*,
    FOREIGN KEY (sale_return_id) REFERENCES sale_return_orders(sale_return_id)*/
);

/* Order Items Table */
-- Stores information about items in orders.
CREATE TABLE IF NOT EXISTS sale_order_items (
    sale_order_item_id CHAR(36) PRIMARY KEY,
    sale_order_id CHAR(36) NOT NULL,
    product_id CHAR(36) NOT NULL,
	unit_options_id CHAR(36) NOT NULL,
    size_id CHAR(36) NULL,
    color_id CHAR(36) NULL,	
    print_name CHAR(255),
    quantity DECIMAL(18, 2),
	total_boxes INT,
    rate DECIMAL(18, 2),
    amount DECIMAL(18, 2),
	tax DECIMAL(18, 2),
    cgst DECIMAL(18,2) DEFAULT 0.00 NULL,
    sgst DECIMAL(18,2) DEFAULT 0.00 NULL,
    igst DECIMAL(18,2) DEFAULT 0.00 NULL
	remarks VARCHAR(255),
    invoiced VARCHAR(3) DEFAULT 'NO',
    work_order_created VARCHAR(3) DEFAULT 'NO',
    discount DECIMAL(18, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sale_order_id) REFERENCES sale_orders(sale_order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
	FOREIGN KEY (unit_options_id) REFERENCES unit_options(unit_options_id),
    FOREIGN KEY (size_id) REFERENCES sizes(size_id),
    FOREIGN KEY (color_id) REFERENCES colors(color_id)	
);

/* Invoices Table */
-- Stores information about invoices generated from sales orders.
CREATE TABLE IF NOT EXISTS sale_invoice_orders(
    sale_invoice_id CHAR(36) PRIMARY KEY,
    bill_type ENUM('CASH', 'CREDIT', 'OTHERS'),
    invoice_date DATE NOT NULL,
    invoice_no VARCHAR(20) UNIQUE NOT NULL, 
    customer_id CHAR(36) NOT NULL,
    gst_type_id CHAR(36),
    email VARCHAR(255),
    ref_no VARCHAR(255),
    ref_date DATE NOT NULL,
    order_salesman_id CHAR(36),
    tax ENUM('Exclusive','Inclusive'),
    customer_address_id CHAR(36),
    payment_term_id CHAR(36),
    due_date DATE,
    payment_link_type_id CHAR(36),
    remarks VARCHAR(1024),
    advance_amount DECIMAL(18, 2),
    ledger_account_id CHAR(36),
    item_value DECIMAL(18, 2),
    discount DECIMAL(18, 2),
    dis_amt DECIMAL(18, 2),
    taxable DECIMAL(18, 2),
    tax_amount DECIMAL(18, 2),
    cess_amount DECIMAL(18, 2),
    transport_charges DECIMAL(18, 2),
    round_off DECIMAL(18, 2),
    total_amount DECIMAL(18, 2),
    vehicle_name VARCHAR(255),
    total_boxes INT,
	order_status_id CHAR(36),
	shipping_address VARCHAR(1024),
	billing_address VARCHAR(1024),
    sale_order_id CHAR(36),
    paid_amount DECIMAL(18, 2) DEFAULT 0.00, -- This is like the amount paid compared to the total amount.
    pending_amount DECIMAL(18, 2),   --It is the same as the outstanding amount (initially pending_amount = total_amount)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (gst_type_id) REFERENCES gst_types(gst_type_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (customer_address_id) REFERENCES customer_addresses(customer_address_id),
    FOREIGN KEY (payment_term_id) REFERENCES customer_payment_terms(payment_term_id),
    FOREIGN KEY (order_salesman_id) REFERENCES orders_salesman(order_salesman_id),
    FOREIGN KEY (payment_link_type_id) REFERENCES payment_link_types(payment_link_type_id),
    FOREIGN KEY (ledger_account_id) REFERENCES ledger_accounts(ledger_account_id),
	FOREIGN KEY (order_status_id) REFERENCES order_statuses(order_status_id),
    FOREIGN KEY (sale_order_id) REFERENCES sale_orders(sale_order_id)
);

/* Order Items Table */
-- Stores information about items in orders.
CREATE TABLE IF NOT EXISTS sale_invoice_items (
    sale_invoice_item_id CHAR(36) PRIMARY KEY,
    sale_invoice_id CHAR(36) NOT NULL,
    product_id CHAR(36) NOT NULL,
	unit_options_id CHAR(36) NOT NULL,
    size_id CHAR(36) NULL,
    color_id CHAR(36) NULL,    
    print_name CHAR(255),
    quantity DECIMAL(18, 2),
	total_boxes INT,
    rate DECIMAL(18, 2),
    amount DECIMAL(18, 2),
	tax DECIMAL(18, 2),
    cgst DECIMAL(18,2) DEFAULT 0.00 NULL,
    sgst DECIMAL(18,2) DEFAULT 0.00 NULL,
    igst DECIMAL(18,2) DEFAULT 0.00 NULL
	remarks VARCHAR(255),
    discount DECIMAL(18, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sale_invoice_id) REFERENCES sale_invoice_orders(sale_invoice_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
	FOREIGN KEY (unit_options_id) REFERENCES unit_options(unit_options_id),
    FOREIGN KEY (size_id) REFERENCES sizes(size_id),
    FOREIGN KEY (color_id) REFERENCES colors(color_id)    
);

/* Sale Retuns Table */
-- Stores information about sale returns.
CREATE TABLE IF NOT EXISTS sale_return_orders(
    sale_return_id CHAR(36) PRIMARY KEY,
    bill_type ENUM('CASH', 'CREDIT', 'OTHERS'),
    return_date DATE NOT NULL,
    return_no VARCHAR(20) UNIQUE NOT NULL,  -- ex pattern: SR-2406-00001
    customer_id CHAR(36) NOT NULL,
    return_option_id CHAR(36),
    gst_type_id CHAR(36),
    email VARCHAR(255),
    ref_no VARCHAR(255),
    ref_date DATE NOT NULL,
    order_salesman_id CHAR(36),
    against_bill VARCHAR(255),
    against_bill_date DATE,
    tax ENUM('Exclusive', 'Inclusive'),
    customer_address_id CHAR(36),
    payment_term_id CHAR(36),
    due_date DATE,
    payment_link_type_id CHAR(36),
    return_reason VARCHAR(1024),
    remarks VARCHAR(1024),
    item_value DECIMAL(18, 2),
    discount DECIMAL(18, 2),
    dis_amt DECIMAL(18, 2),
    taxable DECIMAL(18, 2),
    tax_amount DECIMAL(18, 2),
    cess_amount DECIMAL(18, 2),
    transport_charges DECIMAL(18, 2),
    round_off DECIMAL(18, 2),
    total_amount DECIMAL(18, 2),
    vehicle_name VARCHAR(255),
    total_boxes INT,
	order_status_id CHAR(36),
	shipping_address VARCHAR(1024),
	billing_address VARCHAR(1024),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    sale_invoice_id CHAR(36),
    FOREIGN KEY (gst_type_id) REFERENCES gst_types(gst_type_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (return_option_id) REFERENCES return_options(return_option_id),
    FOREIGN KEY (customer_address_id) REFERENCES customer_addresses(customer_address_id),
    FOREIGN KEY (payment_term_id) REFERENCES customer_payment_terms(payment_term_id),
    FOREIGN KEY (order_salesman_id) REFERENCES orders_salesman(order_salesman_id),
    FOREIGN KEY (payment_link_type_id) REFERENCES payment_link_types(payment_link_type_id),
	FOREIGN KEY (order_status_id) REFERENCES order_statuses(order_status_id),
    FOREIGN KEY (sale_invoice_id) REFERENCES sale_invoice_orders(sale_invoice_id)
);

/* Order Items Table */
-- Stores information about items in return orders.
CREATE TABLE IF NOT EXISTS sale_return_items (
    sale_return_item_id CHAR(36) PRIMARY KEY,
    sale_return_id CHAR(36) NOT NULL,
    product_id CHAR(36) NOT NULL,
	unit_options_id CHAR(36) NOT NULL,
    size_id CHAR(36) NULL,
    color_id CHAR(36) NULL,     
    print_name CHAR(255),
    quantity DECIMAL(18, 2),
	total_boxes INT,
    rate DECIMAL(18, 2),
    amount DECIMAL(18, 2),
	tax DECIMAL(18, 2),
    cgst DECIMAL(18,2) DEFAULT 0.00 NULL,
    sgst DECIMAL(18,2) DEFAULT 0.00 NULL,
    igst DECIMAL(18,2) DEFAULT 0.00 NULL
	remarks VARCHAR(255),
    discount DECIMAL(18, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sale_return_id) REFERENCES sale_return_orders(sale_return_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
	FOREIGN KEY (unit_options_id) REFERENCES unit_options(unit_options_id),
    FOREIGN KEY (size_id) REFERENCES sizes(size_id),
    FOREIGN KEY (color_id) REFERENCES colors(color_id)
);

/* Payment Transactions Table */
-- Stores information about payment transactions made against invoices.
CREATE TABLE IF NOT EXISTS  payment_transactions (
  transaction_id char(36) NOT NULL PRIMARY KEY,
  Payment_receipt_No varchar(50) NOT NULL,
  payment_date timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  payment_method varchar(100) DEFAULT NULL,
  cheque_no varchar(50) DEFAULT NULL,
  amount decimal(18,2) NOT NULL DEFAULT 0.00,
  outstanding_amount decimal(18,2) DEFAULT 0.00,
  adjusted_now decimal(18,2) DEFAULT 0.00,
  payment_status enum(Pending,Completed,Failed) DEFAULT Pending,
  sale_invoice_id char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  customer_id char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  invoice_no VARCHAR(20),
  total_amount DECIMAL(18, 2),
  account_id CHAR(36) NOT NULL,
  created_at timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY fk_payment_transactions_sale_invoice (sale_invoice_id),
  KEY fk_payment_transactions_customer (customer_id),
  FOREIGN KEY (account_id) REFERENCES(account_id),
  CONSTRAINT fk_payment_transactions_customer FOREIGN KEY (customer_id) REFERENCES customers (customer_id) ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT fk_payment_transactions_sale_invoice FOREIGN KEY (sale_invoice_id) REFERENCES sale_invoice_orders (sale_invoice_id) ON DELETE RESTRICT ON UPDATE CASCADE
) 



/* Order types Table */
-- Stores information about type of orders.
CREATE TABLE IF NOT EXISTS order_types (
    order_type_id CHAR(36) PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Order Attachments Table */
-- Stores attachments associated with orders.
CREATE TABLE IF NOT EXISTS order_attachments (
    attachment_id CHAR(36) PRIMARY KEY,
    order_id CHAR(36) NOT NULL,
    attachment_name VARCHAR(255) NOT NULL,
    attachment_path VARCHAR(255) NOT NULL,
    order_type_id CHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (order_type_id) REFERENCES order_types(order_type_id)
);

/* Order Shipments Table */
-- Stores information about order shipments.
CREATE TABLE IF NOT EXISTS order_shipments (
    shipment_id CHAR(36) PRIMARY KEY,
    order_id CHAR(36) NOT NULL,
    destination VARCHAR(255),
    shipping_mode_id CHAR(36),
    shipping_company_id CHAR(36),
    shipping_tracking_no VARCHAR(20) NOT NULL UNIQUE,  -- ex pattern: SHIP-2406-00001
    shipping_date DATE NOT NULL,
    shipping_charges DECIMAL(10, 2),
    vehicle_vessel VARCHAR(255),
    charge_type VARCHAR(255),
    document_through VARCHAR(255),
    port_of_landing VARCHAR(255),
    port_of_discharge VARCHAR(255),
    no_of_packets INT,
    weight DECIMAL(10, 2),
    order_type_id CHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (shipping_mode_id) REFERENCES shipping_modes(shipping_mode_id),
    FOREIGN KEY (shipping_company_id) REFERENCES shipping_companies(shipping_company_id),
    FOREIGN KEY (order_type_id) REFERENCES order_types(order_type_id)
);

/* Purchase Types Table */
-- Stores information about different types of purchases.
CREATE TABLE IF NOT EXISTS purchase_types (
    purchase_type_id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Purchase Orders Table */
-- Stores information about orders related to purchases.
CREATE TABLE IF NOT EXISTS purchase_orders (
    purchase_order_id CHAR(36) PRIMARY KEY,
	purchase_type_id CHAR(36),
	order_date DATE NOT NULL,
	order_no VARCHAR(20),  -- ex pattern: PO-2406-00001
    gst_type_id CHAR(36),
    vendor_id CHAR(36) NOT NULL,
    email VARCHAR(255),
    delivery_date DATE,
    ref_no VARCHAR(255),
    ref_date DATE,
    vendor_agent_id CHAR(36),
    tax ENUM('Exclusive','Inclusive'),
    vendor_address_id CHAR(36),
    remarks VARCHAR(1024),
    payment_term_id CHAR(36),
    advance_amount DECIMAL(18, 2),
    ledger_account_id CHAR(36),
    item_value DECIMAL(18, 2),
    discount DECIMAL(18, 2),
    dis_amt DECIMAL(18, 2),
    taxable DECIMAL(18, 2),
    tax_amount DECIMAL(18, 2),
    cess_amount DECIMAL(18, 2),
    round_off DECIMAL(18, 2),
    total_amount DECIMAL(18, 2),
	order_status_id CHAR(36),
	shipping_address VARCHAR(1024),
	billing_address VARCHAR(1024),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (gst_type_id) REFERENCES gst_types(gst_type_id),
    FOREIGN KEY (vendor_id) REFERENCES vendor(vendor_id),
    FOREIGN KEY (vendor_agent_id) REFERENCES vendor_agent(vendor_agent_id),
    FOREIGN KEY (vendor_address_id) REFERENCES vendor_addresses(vendor_address_id),
    FOREIGN KEY (payment_term_id) REFERENCES vendor_payment_terms(payment_term_id),
    FOREIGN KEY (purchase_type_id) REFERENCES purchase_types(purchase_type_id),
    FOREIGN KEY (ledger_account_id) REFERENCES ledger_accounts(ledger_account_id),
    FOREIGN KEY (order_status_id) REFERENCES order_statuses(order_status_id)
);


/* Purchase Order Items Table */
-- Stores information about items in purchase orders.
CREATE TABLE IF NOT EXISTS purchase_order_items (
    purchase_order_item_id CHAR(36) PRIMARY KEY,
    purchase_order_id CHAR(36) NOT NULL,
    product_id CHAR(36) NOT NULL,
    unit_options_id CHAR(36) NOT NULL,
    size_id CHAR(36) NULL,
    color_id CHAR(36) NULL,     
    print_name CHAR(255),
    quantity DECIMAL(18, 2),
    total_boxes INT,
    rate DECIMAL(18, 2),
    amount DECIMAL(18, 2),
    tax DECIMAL(18, 2),
    cgst DECIMAL(18,2) DEFAULT 0.00 NULL,
    sgst DECIMAL(18,2) DEFAULT 0.00 NULL,
    igst DECIMAL(18,2) DEFAULT 0.00 NULL
    remarks VARCHAR(1024),
    discount DECIMAL(18, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (purchase_order_id) REFERENCES purchase_orders(purchase_order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (unit_options_id) REFERENCES unit_options(unit_options_id),
    FOREIGN KEY (size_id) REFERENCES sizes(size_id),
    FOREIGN KEY (color_id) REFERENCES colors(color_id)    
);

/* Purchase Invoices Table */
-- Stores information about invoices related to purchases.
CREATE TABLE IF NOT EXISTS purchase_invoice_orders (
    purchase_invoice_id CHAR(36) PRIMARY KEY,
	purchase_type_id CHAR(36),
	invoice_date DATE NOT NULL,
    invoice_no VARCHAR(20),  -- ex pattern: PO-INV-2406-00001
    gst_type_id CHAR(36),
    vendor_id CHAR(36) NOT NULL,
    email VARCHAR(255),
    delivery_date DATE,
    supplier_invoice_no VARCHAR(255) NOT NULL,
    supplier_invoice_date DATE,
    vendor_agent_id CHAR(36),
    tax ENUM('Exclusive','Inclusive'),
    vendor_address_id CHAR(36),
    remarks VARCHAR(1024),
    payment_term_id CHAR(36),
	due_date DATE,
    advance_amount DECIMAL(18, 2),
    ledger_account_id CHAR(36),
    item_value DECIMAL(18, 2),
    discount DECIMAL(18, 2),
    dis_amt DECIMAL(18, 2),
    taxable DECIMAL(18, 2),
    tax_amount DECIMAL(18, 2),
    cess_amount DECIMAL(18, 2),
	transport_charges DECIMAL(18, 2),
    round_off DECIMAL(18, 2),
    total_amount DECIMAL(18, 2),
	order_status_id CHAR(36),
	shipping_address VARCHAR(1024),
	billing_address VARCHAR(1024),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (gst_type_id) REFERENCES gst_types(gst_type_id),
    FOREIGN KEY (vendor_id) REFERENCES vendor(vendor_id),
    FOREIGN KEY (vendor_agent_id) REFERENCES vendor_agent(vendor_agent_id),
    FOREIGN KEY (vendor_address_id) REFERENCES vendor_addresses(vendor_address_id),
    FOREIGN KEY (payment_term_id) REFERENCES vendor_payment_terms(payment_term_id),
    FOREIGN KEY (purchase_type_id) REFERENCES purchase_types(purchase_type_id),
    FOREIGN KEY (ledger_account_id) REFERENCES ledger_accounts(ledger_account_id),
    FOREIGN KEY (order_status_id) REFERENCES order_statuses(order_status_id)
);


/* Purchase Order Items Table */
-- Stores information about items in purchase orders.
CREATE TABLE IF NOT EXISTS purchase_invoice_items (
    purchase_invoice_item_id CHAR(36) PRIMARY KEY,
    purchase_invoice_id CHAR(36) NOT NULL,
    product_id CHAR(36) NOT NULL,
    unit_options_id CHAR(36) NOT NULL,
    size_id CHAR(36) NULL,
    color_id CHAR(36) NULL,     
    print_name CHAR(255),
    quantity DECIMAL(18, 2),
    total_boxes INT,
    rate DECIMAL(18, 2),
    amount DECIMAL(18, 2),
    tax DECIMAL(18, 2),
    cgst DECIMAL(18,2) DEFAULT 0.00 NULL,
    sgst DECIMAL(18,2) DEFAULT 0.00 NULL,
    igst DECIMAL(18,2) DEFAULT 0.00 NULL
    remarks VARCHAR(1024),
    discount DECIMAL(18, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (purchase_invoice_id) REFERENCES purchase_invoice_orders(purchase_invoice_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (unit_options_id) REFERENCES unit_options(unit_options_id),
    FOREIGN KEY (size_id) REFERENCES sizes(size_id),
    FOREIGN KEY (color_id) REFERENCES colors(color_id)    
);

/* Purchase Returns Table */
-- Stores information about returns related to purchases.
CREATE TABLE IF NOT EXISTS purchase_return_orders (
    purchase_return_id CHAR(36) PRIMARY KEY,
	purchase_type_id CHAR(36),
	return_date DATE NOT NULL,
    return_no VARCHAR(20),  -- ex pattern: PR-2406-00001
    gst_type_id CHAR(36),
    vendor_id CHAR(36) NOT NULL,
    email VARCHAR(255),
    ref_no VARCHAR(255),
    ref_date DATE,
    vendor_agent_id CHAR(36),
    tax ENUM('Exclusive','Inclusive'),
    vendor_address_id CHAR(36),
    remarks VARCHAR(1024),
    payment_term_id CHAR(36),
	due_date DATE,
	return_reason VARCHAR(1024),
    item_value DECIMAL(18, 2),
    discount DECIMAL(18, 2),
    dis_amt DECIMAL(18, 2),
    taxable DECIMAL(18, 2),
    tax_amount DECIMAL(18, 2),
    cess_amount DECIMAL(18, 2),
	transport_charges DECIMAL(18, 2),
    round_off DECIMAL(18, 2),
    total_amount DECIMAL(18, 2),
	order_status_id CHAR(36),
	shipping_address VARCHAR(1024),
	billing_address VARCHAR(1024),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (gst_type_id) REFERENCES gst_types(gst_type_id),
    FOREIGN KEY (vendor_id) REFERENCES vendor(vendor_id),
    FOREIGN KEY (vendor_agent_id) REFERENCES vendor_agent(vendor_agent_id),
    FOREIGN KEY (vendor_address_id) REFERENCES vendor_addresses(vendor_address_id),
    FOREIGN KEY (payment_term_id) REFERENCES vendor_payment_terms(payment_term_id),
    FOREIGN KEY (purchase_type_id) REFERENCES purchase_types(purchase_type_id),
    FOREIGN KEY (order_status_id) REFERENCES order_statuses(order_status_id)
);


/* Purchase Returns Items Table */
-- Stores information about items in purchase returns.
CREATE TABLE IF NOT EXISTS purchase_return_items (
    purchase_return_item_id CHAR(36) PRIMARY KEY,
    purchase_return_id CHAR(36) NOT NULL,
    product_id CHAR(36) NOT NULL,
    unit_options_id CHAR(36) NOT NULL,
    size_id CHAR(36) NULL,
    color_id CHAR(36) NULL,     
    print_name CHAR(255),
    quantity DECIMAL(18, 2),
    total_boxes INT,
    rate DECIMAL(18, 2),
    amount DECIMAL(18, 2),
    tax DECIMAL(18, 2),
    cgst DECIMAL(18,2) DEFAULT 0.00 NULL,
    sgst DECIMAL(18,2) DEFAULT 0.00 NULL,
    igst DECIMAL(18,2) DEFAULT 0.00 NULL
    remarks VARCHAR(1024),
    discount DECIMAL(18, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (purchase_return_id) REFERENCES purchase_return_orders(purchase_return_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (unit_options_id) REFERENCES unit_options(unit_options_id),
    FOREIGN KEY (size_id) REFERENCES sizes(size_id),
    FOREIGN KEY (color_id) REFERENCES colors(color_id)    
);

/* Sales Price List Table */
-- Stores information about sales price lists.
CREATE TABLE IF NOT EXISTS sales_price_list (
    sales_price_list_id CHAR(36) PRIMARY KEY,
    description VARCHAR(255) NOT NULL,
    customer_category_id CHAR(36) NOT NULL,
    brand_id CHAR(36),
    effective_from DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_category_id) REFERENCES customer_categories(customer_category_id),
    FOREIGN KEY (brand_id) REFERENCES product_brands(brand_id)
);

/* Purchase Price List Table */
-- Stores information about purchase price lists.
CREATE TABLE IF NOT EXISTS purchase_price_list (
    purchase_price_list_id CHAR(36) PRIMARY KEY,
    description VARCHAR(255) NOT NULL,
    customer_category_id CHAR(36) NOT NULL,
    brand_id CHAR(36),
    effective_from DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_category_id) REFERENCES customer_categories(customer_category_id),
    FOREIGN KEY (brand_id) REFERENCES product_brands(brand_id)
);

/* ======== HRMS Management ======== */

CREATE TABLE IF NOT EXISTS job_types (
    job_type_id CHAR(36) PRIMARY KEY,
    job_type_name varchar(55) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS designations (
    designation_id CHAR(36) PRIMARY KEY,
    designation_name varchar(55) NOT NULL,
    responsibilities varchar(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS job_codes (
    job_code_id CHAR(36) PRIMARY KEY,
    job_code varchar(55) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS departments (
    department_id CHAR(36) PRIMARY KEY,
    department_name VARCHAR(55) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS shifts (
    shift_id CHAR(36) PRIMARY KEY,
    shift_name VARCHAR(55) NOT NULL,
    start_time timestamp NOT NULL,
    end_time timestamp NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id CHAR(36) PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    address VARCHAR(255),
    hire_date date,
    date_of_birth date,
    gender ENUM('Female', 'Male') NOT NULL,
    nationality varchar(20),
    emergency_contact varchar(20),
    emergency_contact_relationship varchar(55),
    job_type_id CHAR(36) NOT NULL,
    designation_id CHAR(36),
    job_code_id CHAR(36),
    department_id CHAR(36),
    shift_id CHAR(36),
    manager_id CHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (job_type_id) REFERENCES job_types(job_type_id),
    FOREIGN KEY (designation_id) REFERENCES designations(designation_id),
    FOREIGN KEY (job_code_id) REFERENCES job_codes(job_code_id),
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (shift_id) REFERENCES shifts(shift_id),
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS employee_salary (
    salary_id CHAR(36) PRIMARY KEY,
    salary_amount float NOT NULL,
    salary_currency varchar(45) NOT NULL,
    salary_start_date DATE NOT NULL,
    salary_end_date DATE NOT NULL,
    employee_id CHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS salary_components (
    component_id CHAR(36) PRIMARY KEY,
    component_name varchar(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS employee_salary_components (
    employee_component_id CHAR(36) PRIMARY KEY,
    component_id CHAR(36) NOT NULL,
    component_amount float,
    salary_id CHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (component_id) REFERENCES salary_components(component_id),
    FOREIGN KEY (salary_id) REFERENCES employee_salary(salary_id)
);

/* ======== leaves ======== */

CREATE TABLE IF NOT EXISTS leave_types (
    leave_type_id CHAR(36) PRIMARY KEY,
    leave_type_name VARCHAR(55) NOT NULL,
    description VARCHAR(255) NOT NULL,
    max_days_allowed int NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS employee_leaves (
    leave_id CHAR(36) PRIMARY KEY,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    comments varchar(255),
    employee_id CHAR(36) NOT NULL,
    leave_type_id CHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (status_id) REFERENCES statuses(status_id),
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (leave_type_id) REFERENCES leave_types(leave_type_id)
);

CREATE TABLE IF NOT EXISTS leave_approvals ( 
    approval_id CHAR(36) PRIMARY KEY,
    approval_date date,
    status_id CHAR(36) NOT NULL,
    leave_id CHAR(36) NOT NULL,
    approver_id CHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (status_id) REFERENCES statuses(status_id),
    FOREIGN KEY (leave_id) REFERENCES employee_leaves(leave_id),
    FOREIGN KEY (approver_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS employee_leave_balance (
    balance_id CHAR(36) PRIMARY KEY,
    employee_id CHAR(36) NOT NULL,
    leave_type_id CHAR(36) NOT NULL,
    leave_balance decimal(10,2) NOT NULL,
    year varchar(45) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    FOREIGN KEY (leave_type_id) REFERENCES leave_types(leave_type_id)
);

/* ======== attendance ======== */

CREATE TABLE IF NOT EXISTS employee_attendance (
    employee_attendance_id CHAR(36) PRIMARY KEY,
    employee_id CHAR(36) NOT NULL,
    attendance_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    absent BOOLEAN,
    leave_duration ENUM('First Half', 'Full Day', 'Second Half'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS swipes (
    swipe_id CHAR(36) PRIMARY KEY,
    employee_id CHAR(36) NOT NULL,
    swipe_time datetime,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

CREATE TABLE IF NOT EXISTS biometric (
    biometric_id CHAR(36) PRIMARY KEY,
    employee_id CHAR(36) NOT NULL,
    biometric_entry_id int,
    template_data text NOT NULL,
    entry_stamp timestamp,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

/* User Groups Table */
-- Stores information about different groups.
CREATE TABLE IF NOT EXISTS user_groups (
    group_id CHAR(36) PRIMARY KEY,  -- UUID stored as a CHAR(36)
    group_name VARCHAR(100) UNIQUE NOT NULL,
    description VARCHAR(1024),  -- Description length set to 1024 characters
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* User Group Members Table */
-- Tracks the members belonging to each group.
CREATE TABLE IF NOT EXISTS user_group_members (
    member_id CHAR(36) PRIMARY KEY,  -- UUID stored as a CHAR(36)
    group_id CHAR(36) NOT NULL,
    employee_id CHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES user_groups(group_id) ON DELETE CASCADE,
	FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
    UNIQUE (group_id, employee_id)
);

/* Task Priorities Table */
-- Stores possible priorities for tasks.
CREATE TABLE IF NOT EXISTS task_priorities (
    priority_id CHAR(36) PRIMARY KEY,
    priority_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Tasks Table */
-- Stores tasks assigned to users with their status, priority, and other details.
CREATE TABLE IF NOT EXISTS tasks (
    task_id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NULL,
    group_id CHAR(36) NULL,
    status_id CHAR(36) NOT NULL,
    priority_id CHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (status_id) REFERENCES statuses(status_id),
    FOREIGN KEY (priority_id) REFERENCES task_priorities(priority_id),
    FOREIGN KEY (group_id) REFERENCES user_groups(group_id)
);

/* Task Comments Table */
-- Stores comments on tasks by users.
CREATE TABLE IF NOT EXISTS task_comments (
    comment_id CHAR(36) PRIMARY KEY,
    task_id CHAR(36) NOT NULL,
    user_id CHAR(36) NOT NULL,
    comment_text varchar(1024) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

/* Task Attachments Table */
-- Stores file attachments related to tasks.
CREATE TABLE IF NOT EXISTS task_attachments (
    attachment_id CHAR(36) PRIMARY KEY,
    task_id CHAR(36) NOT NULL,
    attachment_name VARCHAR(255) NOT NULL,
    attachment_path VARCHAR(255) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id)
);

/* Task History Table */
-- Stores the history of status changes for tasks.
CREATE TABLE IF NOT EXISTS task_history (
    history_id CHAR(36) PRIMARY KEY,
    task_id CHAR(36) NOT NULL,
    status_id CHAR(36) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id CHAR(36) NULL,
    group_id CHAR(36) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id),
    FOREIGN KEY (status_id) REFERENCES statuses(status_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (group_id) REFERENCES user_groups(group_id)
);

/* Quick Packs Table */
-- Stores information about the quick packs associated with each customer.
CREATE TABLE IF NOT EXISTS quick_packs (
    quick_pack_id CHAR(36) PRIMARY KEY,
    customer_id CHAR(36),
    name VARCHAR(255) NOT NULL, 
    description VARCHAR(1024),
    active ENUM('N','Y'),
    lot_qty INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
 
/* Quick Pack Items Table */
-- Stores the items that are part of each quick pack.
CREATE TABLE IF NOT EXISTS quick_pack_items (
    quick_pack_item_id CHAR(36) PRIMARY KEY,
    quick_pack_id CHAR(36) NOT NULL,
    product_id CHAR(36) NOT NULL,
    size_id CHAR(36) NULL,
    color_id CHAR(36) NULL,
    quantity INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (quick_pack_id) REFERENCES quick_packs(quick_pack_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (size_id) REFERENCES sizes(size_id),
    FOREIGN KEY (color_id) REFERENCES colors(color_id)
);


/* ======== LEAD Management ======== */

/* lead_statuses Table */
-- Lookup table for lead statuses.
CREATE TABLE IF NOT EXISTS lead_statuses (
   lead_status_id CHAR(36) PRIMARY KEY,
   status_name VARCHAR(50) NOT NULL,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* interaction_types Table */
-- Lookup table for types of interactions with leads.
CREATE TABLE IF NOT EXISTS interaction_types (
   interaction_type_id CHAR(36) PRIMARY KEY,
   interaction_type VARCHAR(50) NOT NULL,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* leads Table */
-- Stores information about potential customers.
CREATE TABLE IF NOT EXISTS leads (
   lead_id CHAR(36) PRIMARY KEY,
   name VARCHAR(255) NOT NULL,
   email VARCHAR(255) NOT NULL,
   phone VARCHAR(20),
   lead_status_id CHAR(36) NOT NULL,
   assignee_id CHAR(36) NOT NULL,
   score INT DEFAULT 0,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   FOREIGN KEY (lead_status_id) REFERENCES lead_statuses(lead_status_id),
   FOREIGN KEY (assignee_id) REFERENCES employees(employee_id)
);


/* lead_interactions Table */
-- Stores interactions with leads.
CREATE TABLE IF NOT EXISTS lead_interactions (
   interaction_id CHAR(36) PRIMARY KEY,
   lead_id CHAR(36) NOT NULL,
   interaction_type_id CHAR(36) NOT NULL,
   interaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   notes TEXT,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   FOREIGN KEY (lead_id) REFERENCES leads(lead_id),
   FOREIGN KEY (interaction_type_id) REFERENCES interaction_types(interaction_type_id)
);

/* lead_assignment_history Table */
-- Stores history of lead assignments to sales representatives.
CREATE TABLE IF NOT EXISTS lead_assignment_history (
   history_id CHAR(36) PRIMARY KEY,
   lead_id CHAR(36) NOT NULL,
   assignee_id CHAR(36) NOT NULL,
   assignment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   end_date TIMESTAMP NULL,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   FOREIGN KEY (lead_id) REFERENCES leads(lead_id),
   FOREIGN KEY (assignee_id) REFERENCES employees(employee_id)
);

/* ======== Asset Management ======== */

/* asset_statuses Table */
-- Lookup table for asset statuses.
CREATE TABLE IF NOT EXISTS asset_statuses (
   asset_status_id CHAR(36) PRIMARY KEY,
   status_name VARCHAR(50) NOT NULL,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* asset_categories Table */
-- Lookup table for asset categories.
CREATE TABLE IF NOT EXISTS asset_categories (
   asset_category_id CHAR(36) PRIMARY KEY,
   category_name VARCHAR(50) NOT NULL,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* locations Table */
-- Lookup table for locations where assets are stored.
CREATE TABLE IF NOT EXISTS locations (
   location_id CHAR(36) PRIMARY KEY,
   location_name VARCHAR(50) NOT NULL,
   address VARCHAR(1024),
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* assets Table */
-- Stores information about assets.
CREATE TABLE IF NOT EXISTS assets (
   asset_id CHAR(36) PRIMARY KEY,
   name VARCHAR(100) NOT NULL,
   asset_category_id CHAR(36) NOT NULL,
   asset_status_id CHAR(36) NOT NULL,
   location_id CHAR(36) NOT NULL,
   unit_options_id CHAR(36),
   purchase_date DATE,
   price DECIMAL(10, 2),
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   FOREIGN KEY (asset_category_id) REFERENCES asset_categories(asset_category_id),
   FOREIGN KEY (asset_status_id) REFERENCES asset_statuses(asset_status_id),
   FOREIGN KEY (location_id) REFERENCES locations(location_id),
   FOREIGN KEY (unit_options_id) REFERENCES unit_options(unit_options_id)
);

/* asset_maintenance Table */
-- Stores information about asset maintenance activities.
CREATE TABLE IF NOT EXISTS asset_maintenance (
   asset_maintenance_id CHAR(36) PRIMARY KEY,
   asset_id CHAR(36) NOT NULL,
   maintenance_date DATE,
   maintenance_description VARCHAR(1024),
   cost DECIMAL(10, 2),
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

/* ======== Manufacturing/Production ======== */

CREATE TABLE IF NOT EXISTS bom (
    bom_id CHAR(36) PRIMARY KEY,
    bom_name VARCHAR(100) NOT NULL,
    product_id CHAR(36),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
    ); 

CREATE TABLE IF NOT EXISTS raw_materials (
   raw_material_id  CHAR(36) PRIMARY KEY,
   name VARCHAR(255) NOT NULL,
   description TEXT,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Production Statuses Table */
-- Stores possible statuses for production processes.
CREATE TABLE IF NOT EXISTS production_statuses (
    status_id CHAR(36) PRIMARY KEY,
    status_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Work Orders Table */
-- Tracks production orders, their statuses, and quantities.
CREATE TABLE IF NOT EXISTS work_orders (
    work_order_id CHAR(36) PRIMARY KEY,
    product_id CHAR(36),
    size_id CHAR(36) NULL,
    color_id CHAR(36) NULL,    
    quantity INT NOT NULL DEFAULT 0,
    completed_qty INT NULL DEFAULT 0,
    pending_qty INT NULL DEFAULT 0,
    status_id CHAR(36),
    start_date DATE,
    end_date DATE,
    sale_order_id CHAR(36) DEFAULT NULL,
    sync_qty BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (size_id) REFERENCES sizes(size_id),
    FOREIGN KEY (color_id) REFERENCES colors(color_id),  
    FOREIGN KEY (status_id) REFERENCES production_statuses(status_id),
    FOREIGN KEY (sale_order_id) REFERENCES sale_orders(sale_order_id)
);

CREATE TABLE IF NOT EXISTS completed_quantity (
    quantity_id CHAR(36) PRIMARY KEY,
    quantity INT NULL,
    sync_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    work_order_id CHAR(36) NOT NULL,
    FOREIGN KEY (work_order_id) REFERENCES work_orders(work_order_id)
    );

CREATE TABLE IF NOT EXISTS work_order_stages (
    work_stage_id CHAR(36) PRIMARY KEY,
    work_order_id CHAR(36),
    stage_name VARCHAR(255) NOT NULL,
    stage_description TEXT,
	stage_start_date DATE,
	stage_end_date DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (work_order_id) REFERENCES work_orders(work_order_id)
);

/* Bill of Materials (BOM) Table */
-- Stores the list of materials and components required to produce each product.
CREATE TABLE IF NOT EXISTS bill_of_materials (
    material_id CHAR(36) PRIMARY KEY,
    product_id  CHAR(36),
    size_id CHAR(36) NULL,
    color_id CHAR(36) NULL,
    quantity INT NOT NULL DEFAULT 0,
    unit_cost DECIMAL(10, 2) NOT NULL,
    total_cost DECIMAL(10, 2) NOT NULL,
    notes TEXT,  
    reference_id CHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (size_id) REFERENCES sizes(size_id),
    FOREIGN KEY (color_id) REFERENCES colors(color_id)
    );

/* Machines Table */
-- Stores information about the machines used in production.
CREATE TABLE IF NOT EXISTS machines (
    machine_id CHAR(36) PRIMARY KEY,
    machine_name VARCHAR(100) NOT NULL,
    description TEXT,
    status ENUM('Operational', 'Out of Service', 'Under Maintenance') DEFAULT 'Operational',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Default Machinery Table /
/ Stores default machinery assigned to each product */
CREATE TABLE IF NOT EXISTS default_machinery (
default_machinery_id CHAR(36) PRIMARY KEY,
product_id CHAR(36),
machine_id CHAR(36),
FOREIGN KEY (product_id) REFERENCES products(product_id),
FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
);

/* production_workers Table */
-- Tracks production_workers assignments and hours worked on production tasks.
CREATE TABLE IF NOT EXISTS production_workers (
worker_id CHAR(36) PRIMARY KEY,
employee_id CHAR(36) NOT NULL,
work_order_id CHAR(36) NOT NULL,
hours_worked DECIMAL(5, 2),
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
FOREIGN KEY (work_order_id) REFERENCES work_orders(work_order_id)
);


/* Workflow Stages Table */
-- Defines stages within each workflow, specifying the order and description for each stage.
CREATE TABLE IF NOT EXISTS workflowstages (
    workflow_stage_id CHAR(36) PRIMARY KEY,
    workflow_id CHAR(36) NOT NULL,
    stage_order INT NOT NULL,
    description VARCHAR(255),
    section_id CHAR(36) NOT NULL,
    flow_status_id CHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id),
    FOREIGN KEY (section_id) REFERENCES module_sections(section_id) ,
    FOREIGN KEY (flow_status_id) REFERENCES flow_status(flow_status_id)
);


/* Flow Status Table */
-- Defines different statuses within a workflow, such as "Pending," "In Progress," or "Completed."
CREATE TABLE IF NOT EXISTS flow_status (
    flow_status_id CHAR(36) PRIMARY KEY,    
    flow_status_name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


/* Sale Receipts Table */
-- Stores receipts associated with sale invoices.
CREATE TABLE IF NOT EXISTS sale_receipts (
    sale_receipt_id CHAR(36) PRIMARY KEY,
    sale_invoice_id CHAR(36) NOT NULL,
    receipt_name VARCHAR(255) NOT NULL,
    description VARCHAR(1024),
    receipt_path JSON DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sale_invoice_id) REFERENCES sale_invoice_orders(sale_invoice_id)
);

/* ======== FINANCE ======== */

/* Bank Accounts Table */
-- Stores details of bank accounts linked to the system.
CREATE TABLE IF NOT EXISTS bank_accounts (
    bank_account_id CHAR(36) PRIMARY KEY,
    account_name VARCHAR(100) NOT NULL,
    account_number VARCHAR(50) UNIQUE NOT NULL,
    bank_name VARCHAR(100) NOT NULL,
    branch_name VARCHAR(100),
    ifsc_code VARCHAR(100),
    account_type ENUM('Current', 'Savings') NOT NULL,
    balance DECIMAL(15, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Chart of Accounts Table */
-- Manages the financial accounts and their hierarchy.
CREATE TABLE IF NOT EXISTS chart_of_accounts (
    account_id CHAR(36) PRIMARY KEY,
    account_code VARCHAR(20) UNIQUE NOT NULL,
    account_name VARCHAR(100) NOT NULL,
    account_type ENUM('Asset', 'Equity', 'Expense',  'Liability', 'Revenue') NOT NULL,
    parent_account_id CHAR(36) NULL,
    is_active BOOLEAN DEFAULT TRUE,
    bank_account_id CHAR(36) NULL,  -- Link to bank accounts if applicable
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_account_id) REFERENCES chart_of_accounts(account_id),
    FOREIGN KEY (bank_account_id) REFERENCES bank_accounts(bank_account_id) -- Optional
);

/* Journal Entries Table */
-- Records the general journal entries for financial transactions.
CREATE TABLE IF NOT EXISTS journal_entries (
    journal_entry_id CHAR(36) PRIMARY KEY,
    entry_date DATE NOT NULL,
    reference VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Journal Entry Lines Table */
-- Stores individual debit and credit lines associated with journal entries.
CREATE TABLE IF NOT EXISTS journal_entry_lines (
    journal_entry_line_id CHAR(36) PRIMARY KEY,
    account_id CHAR(36),
    customer_id CHAR(36),
    vendor_id CHAR(36),
    voucher_no VARCHAR(20) NOT NULL
    debit DECIMAL(15, 2) DEFAULT 0.00,
    credit DECIMAL(15, 2) DEFAULT 0.00,
    description VARCHAR(1024),
    balance DECIMAL(15, 2) DEFAULT 0.00,  -- balance amt  
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
   -- journal_entry_id CHAR(36),     Needed in future
   -- FOREIGN KEY (journal_entry_id) REFERENCES journal_entries(journal_entry_id),
    FOREIGN KEY (account_id) REFERENCES chart_of_accounts(account_id)
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (vendor_id) REFERENCES vendor(vendor_id)
   
);

/*payment_transaction table
 stores transaction details of sales and purchase. */
CREATE TABLE IF NOT EXISTS payment_transaction (
    payment_id CHAR(36) PRIMARY KEY,
    invoice_id CHAR(36) NOT NULL,
    order_type ENUM('Purchase','Sale') NOT NULL,
    payment_date DATE NOT NULL,
    payment_method ENUM('Bank Transfer', 'Cash', 'Cheque', 'Credit Card') NOT NULL,
    payment_status ENUM('Completed', 'Failed', 'Pending') NOT NULL DEFAULT 'Pending',
    amount DECIMAL(15, 2) NOT NULL,
    reference_number VARCHAR(100),
    notes VARCHAR(512),
    currency VARCHAR(10),
    transaction_type ENUM('Credit', 'Debit') NOT NULL DEFAULT 'Credit',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Tax Configurations Table */
-- Stores the tax rates and types for financial transactions.
CREATE TABLE IF NOT EXISTS tax_configurations (
    tax_id CHAR(36) PRIMARY KEY,
    tax_name VARCHAR(100) NOT NULL,
    tax_rate DECIMAL(5, 2) NOT NULL,
    tax_type ENUM('Fixed', 'Percentage') NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Budgets Table */
-- Stores budget allocations and expenditures for accounts.
CREATE TABLE IF NOT EXISTS budgets (
    budget_id CHAR(36) PRIMARY KEY,
    account_id CHAR(36),
    fiscal_year YEAR NOT NULL,
    allocated_amount DECIMAL(15, 2) NOT NULL,
    spent_amount DECIMAL(15, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES chart_of_accounts(account_id)
);

/* Expense Claims Table */
-- Manages the expense claims submitted by employees.
CREATE TABLE IF NOT EXISTS expense_claims (
    expense_claim_id CHAR(36) PRIMARY KEY,
    employee_id CHAR(36),
    claim_date DATE NOT NULL,
    description VARCHAR(1024),
    total_amount DECIMAL(15, 2) NOT NULL,
    status ENUM('Approved', 'Pending', 'Rejected') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);

/* Financial Reports Table */
-- Stores the generated financial reports and their details.
CREATE TABLE IF NOT EXISTS financial_reports (
    report_id CHAR(36) PRIMARY KEY,
    report_name VARCHAR(100) NOT NULL,
    report_type ENUM('Balance Sheet', 'Cash Flow', 'Profit & Loss', 'Trial Balance') NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_path JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Sale Credit Notes Table */
-- Stores credit notes issued to customers for returns or adjustments.
CREATE TABLE IF NOT EXISTS sale_credit_notes (
    credit_note_id CHAR(36) PRIMARY KEY,
    sale_invoice_id CHAR(36) NOT NULL,
    credit_note_number VARCHAR(100) NOT NULL,
    credit_date DATE NOT NULL,
    customer_id CHAR(36) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    reason VARCHAR(1024),
    order_status_id CHAR(36),
    sale_return_id CHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sale_invoice_id) REFERENCES sale_invoice_orders(sale_invoice_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
	FOREIGN KEY (order_status_id) REFERENCES order_statuses(order_status_id),
    FOREIGN KEY (sale_return_id) REFERENCES sale_return_orders(sale_return_id)
);

/* Sale Credit Note Items Table */
-- Stores individual items that are part of a sale credit note.
CREATE TABLE IF NOT EXISTS sale_credit_note_items (
    credit_note_item_id CHAR(36) PRIMARY KEY,
    credit_note_id CHAR(36) NOT NULL,
    product_id CHAR(36) NOT NULL,
    quantity INT NOT NULL,
    price_per_unit DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (credit_note_id) REFERENCES sale_credit_notes(credit_note_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS field_types (
    field_type_id CHAR(36) PRIMARY KEY,
    field_type_name VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Entities Table */
-- Stores information about the entities that can have custom fields.
CREATE TABLE IF NOT EXISTS entities (
    entity_id CHAR(36) PRIMARY KEY, 
    entity_name VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);



/* Custom Fields Table */
-- Stores the definition of custom fields, including entity associations.
CREATE TABLE IF NOT EXISTS custom_fields (
    custom_field_id CHAR(36) PRIMARY KEY,
    field_name VARCHAR(255) NOT NULL,
    field_type_id CHAR(36) NOT NULL,
    entity_id CHAR(36) NOT NULL,
    is_required BOOLEAN DEFAULT FALSE,
    validation_rules JSON DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE (field_name),
    FOREIGN KEY (field_type_id) REFERENCES field_types(field_type_id),
    FOREIGN KEY (entity_id) REFERENCES entities(entity_id)
);



/* Custom Field Options Table */
-- Stores the options for fields of type Select or MultiSelect.
CREATE TABLE IF NOT EXISTS custom_field_options (
    option_id CHAR(36) PRIMARY KEY,
    custom_field_id CHAR(36) NOT NULL,
    option_value VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (custom_field_id) REFERENCES custom_fields(custom_field_id) 
);


/* Custom Field Values Table */
-- Stores the actual values of custom fields for specific entities.
CREATE TABLE IF NOT EXISTS custom_field_values (
    custom_field_value_id CHAR(36) PRIMARY KEY,
    custom_field_id CHAR(36) NOT NULL,
    custom_id CHAR(36) NOT NULL,
    entity_id CHAR(36) NOT NULL, 
    -- entity_data_id CHAR(36) DEFAULT NULL;
    field_value VARCHAR(255),
    field_value_type VARCHAR(50), 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (custom_field_id) REFERENCES custom_fields(custom_field_id),
    FOREIGN KEY (entity_id) REFERENCES entities(entity_id) 
    -- FOREIGN KEY (entity_data_id) REFERENCES customers(customer_id)
);


/* Sale Debit Notes Table */
-- Stores debit notes issued to customers for adjustments such as undercharges or additional fees.
CREATE TABLE IF NOT EXISTS sale_debit_notes (
    debit_note_id CHAR(36) PRIMARY KEY,
    sale_invoice_id CHAR(36) NOT NULL,
    debit_note_number VARCHAR(100) NOT NULL,
    debit_date DATE NOT NULL,
    customer_id CHAR(36) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    reason VARCHAR(1024),
    order_status_id CHAR(36),
    sale_return_id CHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sale_invoice_id) REFERENCES sale_invoice_orders(sale_invoice_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
	FOREIGN KEY (order_status_id) REFERENCES order_statuses(order_status_id),
    FOREIGN KEY (sale_return_id) REFERENCES sale_return_orders(sale_return_id),
	FOREIGN KEY (order_status_id) REFERENCES order_statuses(order_status_id)
);

/* Sale Debit Note Items Table */
-- Stores individual items that are part of a sale debit note.
CREATE TABLE IF NOT EXISTS sale_debit_note_items (
    debit_note_item_id CHAR(36) PRIMARY KEY,
    debit_note_id CHAR(36) NOT NULL,
    product_id CHAR(36) NOT NULL,
    quantity INT NOT NULL,
    price_per_unit DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (debit_note_id) REFERENCES sale_debit_notes(debit_note_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

/* Notification Frequencies Table */
-- Stores available notification frequencies for reminders.
CREATE TABLE IF NOT EXISTS notification_frequencies (
frequency_id CHAR(36) PRIMARY KEY,
frequency_name VARCHAR(50) NOT NULL UNIQUE,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Notification Methods Table */
-- Stores available notification methods for reminders and settings.
CREATE TABLE IF NOT EXISTS notification_methods (
method_id CHAR(36) PRIMARY KEY,
method_name VARCHAR(50) NOT NULL UNIQUE,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Reminder Types Table */
-- Stores different types of reminders.
CREATE TABLE IF NOT EXISTS reminder_types (
reminder_type_id CHAR(36) PRIMARY KEY,
type_name VARCHAR(100) NOT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

/* Reminders Table */
-- Stores the main reminder details.
CREATE TABLE IF NOT EXISTS reminders (
reminder_id CHAR(36) PRIMARY KEY,
reminder_type_id CHAR(36) NOT NULL,
subject VARCHAR(255) NOT NULL,
description TEXT,
reminder_date TIMESTAMP NOT NULL,
is_recurring BOOLEAN DEFAULT FALSE,
recurring_frequency ENUM('Daily', 'Monthly', 'Weekly', 'Yearly') NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
FOREIGN KEY (reminder_type_id) REFERENCES reminder_types(reminder_type_id)
);

/* Reminder Recipients Table */
-- Stores details of recipients for a reminder.
CREATE TABLE IF NOT EXISTS reminder_recipients (
recipient_id CHAR(36) PRIMARY KEY,
reminder_id CHAR(36) NOT NULL,
recipient_user_id CHAR(36) NOT NULL,
recipient_email VARCHAR(255),
notification_method_id CHAR(36) NOT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
FOREIGN KEY (reminder_id) REFERENCES reminders(reminder_id),
FOREIGN KEY (recipient_user_id) REFERENCES employees(employee_id),
FOREIGN KEY (notification_method_id) REFERENCES notification_methods(method_id)
);

/* Reminder Settings Table */
-- Stores settings related to how reminders are sent to users.
CREATE TABLE IF NOT EXISTS reminder_settings (
setting_id CHAR(36) PRIMARY KEY,
user_id CHAR(36) NOT NULL,
notification_frequency_id CHAR(36) NOT NULL,
notification_method_id CHAR(36) NOT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
FOREIGN KEY (user_id) REFERENCES employees(employee_id),
FOREIGN KEY (notification_frequency_id) REFERENCES notification_frequencies(frequency_id),
FOREIGN KEY (notification_method_id) REFERENCES notification_methods(method_id)
);

/* Reminder Logs Table */
-- Logs each reminder activity for tracking.
CREATE TABLE IF NOT EXISTS reminder_logs (
log_id CHAR(36) PRIMARY KEY,
reminder_id CHAR(36) NOT NULL,
log_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
log_action ENUM('Cancelled',  'Created', 'Dismissed', 'Rescheduled', 'Viewed') NOT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
FOREIGN KEY (reminder_id) REFERENCES reminders(reminder_id)
);

/* For Dashboard Reports*/
-- Storing Standard Queries For Chart
CREATE TABLE report_definition (
    query_id CHAR(36) PRIMARY KEY,
    query TEXT NOT NULL,
    query_name CHAR(50) NOT NULL,
    visualization_type CHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

/* stroing Hours configuration tables */
CREATE TABLE IF NOT EXISTS inventory_block_config (
    config_id INT AUTO_INCREMENT PRIMARY KEY,
    block_duration_hours INT DEFAULT 24 COMMENT 'Duration (in hours) to block inventory',
    product_id CHAR(36) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    FOREIGN KEY (product_id) REFERENCES products(product_id)

);

CREATE TABLE IF NOT EXISTS blocked_inventory (
    block_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_order_id CHAR(36) NOT NULL,
    product_id CHAR(36) NOT NULL,
    blocked_qty INT DEFAULT 0,
    expiration_time TIMESTAMP NOT NULL COMMENT 'Timestamp when the block expires',
    is_expired BOOLEAN DEFAULT FALSE COMMENT 'True if block duration has passed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (sale_order_id) REFERENCES sale_orders(sale_order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- * ExpenseCategories Table */

CREATE TABLE IF NOT EXISTS expense_categories (
    category_id CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    category_name VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    description VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
    account_id CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
    is_active TINYINT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (category_id),
    FOREIGN KEY (account_id) REFERENCES chart_of_accounts(account_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- * ExpenseItem Table */
-- Stores individual expense transactions with details
CREATE TABLE IF NOT EXISTS expense_items (
    expense_item_id CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    expense_date DATE NOT NULL,
    description VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
    amount DECIMAL(15,2) NOT NULL,
    receipt_image VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
    category_id CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
    bank_account_id CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
    vendor_id CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
    employee_id CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
    expense_claim_id CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
    status ENUM('Paid', 'Pending', 'Rejected') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT 'Pending',
    payment_method ENUM('Bank Transfer', 'Cash', 'Cheque', 'Credit Card') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
    reference_number VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
    budget_id CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
    tax_amount DECIMAL(15,2) DEFAULT 0.00,
    is_taxable TINYINT(1) DEFAULT 1,
    tax_id CHAR(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
    is_recurring TINYINT(1) DEFAULT 0,
    recurring_frequency ENUM('Daily', 'Weekly', 'Monthly', 'Quarterly', 'Yearly') CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
    next_recurrence_date DATE DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (expense_item_id),
    FOREIGN KEY (category_id) REFERENCES expense_categories(category_id) ON DELETE SET NULL,
    FOREIGN KEY (bank_account_id) REFERENCES bank_accounts(bank_account_id) ON DELETE SET NULL,
    FOREIGN KEY (vendor_id) REFERENCES vendor(vendor_id) ON DELETE SET NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE SET NULL,
    FOREIGN KEY (expense_claim_id) REFERENCES expense_claims(expense_claim_id) ON DELETE SET NULL,
    FOREIGN KEY (budget_id) REFERENCES budgets(budget_id) ON DELETE SET NULL,
    FOREIGN KEY (tax_id) REFERENCES tax_configurations(tax_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;